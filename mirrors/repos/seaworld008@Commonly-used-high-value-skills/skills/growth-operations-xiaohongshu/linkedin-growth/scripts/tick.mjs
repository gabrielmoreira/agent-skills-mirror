#!/usr/bin/env node
//
// The scheduler heartbeat, in two roles selected by the --account flag:
//
//   DISPATCHER (no --account): launched by the OS timer every few minutes. It is
//     lightweight and NEVER blocks. For each active account that is inside its active
//     window and not already being processed, it spawns a DETACHED worker and returns
//     immediately. Because it never waits on a worker, a slow account — or one that is busy
//     with another workflow the user launched on the same LinkedIn session — can never hold
//     up the next tick or any other account. Accounts are therefore processed in parallel.
//
//   WORKER (--account <name>): does the work for ONE account, holding a per-account lock for
//     its whole lifetime:
//       1. INVITE (top priority): if under the daily quota AND at least
//          `min_invite_interval_minutes` since the last successful send, send ONE invite.
//          It always runs BEFORE any pending work, so pending can never delay a connect.
//       2. PENDING (fills the rest): drain due pending checks in small batches until none
//          remain or a soft time budget elapses. The budget only decides whether to START
//          another batch — a batch already running is never interrupted.
//
// Nothing here is ever killed by a timeout. If an operation is slow because the account is
// busy, the worker simply keeps holding its lock; the next dispatcher ticks see a LIVE
// worker and skip that account, so no work piles up and nothing is force-terminated. When
// the op returns, the worker finishes and the normal cadence resumes on the next tick.
//
// The per-account lock is reclaimed ONLY when its owning process is actually dead (PID
// probe), never on a timer — so a long-but-alive run is never preempted or double-started,
// and a crashed run self-heals on the next tick. Each operation is persisted to the DB the
// moment it completes, and quotas are recomputed from the runs table each tick (bounded to
// the local calendar day), so state stays correct across interruptions.
//
import { randomUUID } from 'node:crypto';
import {
  appendFileSync,
  closeSync,
  constants,
  existsSync,
  fstatSync,
  openSync,
  readSync,
  realpathSync,
  readdirSync,
  statSync,
  unlinkSync,
} from 'node:fs';
import { join, resolve } from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

let withDb;
let ok;
let fail;
let parseArgs;
let dataDir;
let ensureDir;
let logsDir;
let SKILL_ROOT;
let defaults;
let startOfLocalDayUtc;
let localHHMM;
let parseDbUtc;
let minutesSince;

async function loadRuntime() {
  ({ withDb } = await import('./lib/db.mjs'));
  ({ ok, fail } = await import('./lib/output.mjs'));
  ({ parseArgs } = await import('./lib/args.mjs'));
  ({ dataDir, ensureDir, logsDir, SKILL_ROOT } = await import('./lib/paths.mjs'));
  ({ defaults } = await import('./lib/config.mjs'));
  ({ startOfLocalDayUtc, localHHMM, parseDbUtc, minutesSince } = await import('./lib/time.mjs'));
}

async function runCli() {
  try {
    await loadRuntime();
    const { flags } = parseArgs();
    if (flags.account) {
      await runWorker(String(flags.account));
    } else {
      dispatch();
    }
  } catch (err) {
    if (fail) {
      fail(err.message);
    } else {
      process.stderr.write(`error: ${err.message}\n`);
      process.exitCode = 1;
    }
  }
}

const isMain = Boolean(process.argv[1]) &&
  realpathSync(resolve(process.argv[1])) === realpathSync(fileURLToPath(import.meta.url));
if (isMain) {
  await runCli();
}

// Spawn one detached worker per eligible account, then exit. Never waits on a worker.
function dispatch() {
  ensureDir(dataDir());
  const now = new Date();
  const nowHHMM = localHHMM(now);

  const accounts = withDb(
    (db) =>
      db
        .prepare('SELECT name, active_start, active_end FROM accounts WHERE paused = 0 ORDER BY name')
        .all(),
    { readonly: true },
  );

  const dispatched = [];
  const skipped = {};
  for (const acc of accounts) {
    if (nowHHMM < acc.active_start || nowHHMM > acc.active_end) {
      skipped[acc.name] = 'outside_active_window';
    } else if (lockHeldByLiveProcess(acc.name)) {
      skipped[acc.name] = 'previous_run_still_active';
    } else {
      spawnWorker(acc.name);
      dispatched.push(acc.name);
    }
  }

  pruneLogs();
  ok({
    now: now.toISOString(),
    local_time: nowHHMM,
    dispatched,
    ...(Object.keys(skipped).length ? { skipped } : {}),
  });
}

// Fire-and-forget: the worker is detached and fully owns its lifetime. The dispatcher does
// not keep a handle to it, so the dispatcher (the OS-timer job) exits right away.
function spawnWorker(account) {
  const child = spawn(
    process.execPath,
    [join(SKILL_ROOT, 'scripts', 'tick.mjs'), '--account', account, '--json'],
    { detached: true, stdio: 'ignore' },
  );
  child.unref();
}

async function runWorker(account) {
  if (!acquireLock(account)) {
    ok({ account, skipped: 'already_running' });
    return;
  }
  try {
    const now = new Date();
    const nowHHMM = localHHMM(now);
    const dayStartUtc = startOfLocalDayUtc(now);

    const acc = withDb(
      (db) => db.prepare('SELECT * FROM accounts WHERE name = ? AND paused = 0').get(account),
      { readonly: true },
    );
    if (!acc) {
      ok({ account, skipped: 'not_active' });
      return;
    }
    if (nowHHMM < acc.active_start || nowHHMM > acc.active_end) {
      ok({ account, skipped: 'outside_active_window' });
      return;
    }

    const stats = readStats(acc, dayStartUtc);
    const did = [];
    const skipped = {};

    // 1) INVITE — highest priority, before any pending work so it can never be delayed.
    if (stats.notConnected === 0) {
      skipped.invite = 'no_not_connected_leads';
    } else if (stats.sentToday >= acc.daily_invite_limit) {
      skipped.invite = 'daily_quota_reached';
    } else {
      const elapsed = minutesSince(parseDbUtc(stats.lastSentAt), now);
      if (elapsed >= acc.min_invite_interval_minutes) {
        await runChild('network-invite.mjs', account, ['--limit', '1']);
        did.push({ op: 'invite', sent_today_before: stats.sentToday, daily_limit: acc.daily_invite_limit });
      } else {
        skipped.invite = `paced_waiting (${Math.round(acc.min_invite_interval_minutes - elapsed)}min left)`;
      }
    }

    // 2) PENDING — drain due checks; never count-capped, only bounded by a soft time budget
    //    that gates STARTING another batch. A batch already running is never interrupted.
    const budgetMs = defaults().pending_tick_budget_seconds * 1000;
    const batch = defaults().pending_drain_batch;
    const startMs = Date.now();
    let due = stats.duePending;
    let prevDue = Infinity;
    let drained = 0;
    while (due > 0 && due < prevDue && Date.now() - startMs < budgetMs) {
      await runChild('network-pending.mjs', account, ['--limit', String(batch)]);
      prevDue = due;
      due = readDuePending(acc);
      drained += Math.max(0, prevDue - due);
    }
    if (drained > 0 || stats.duePending > 0) {
      did.push({ op: 'pending', drained, due_remaining: due });
    } else {
      skipped.pending = 'no_due_pending';
    }

    logWorker(account, { did, ...(Object.keys(skipped).length ? { skipped } : {}) });
    ok({ account, did, ...(Object.keys(skipped).length ? { skipped } : {}) });
  } finally {
    releaseLock(account);
  }
}

function readStats(acc, dayStartUtc) {
  return withDb(
    (db) => ({
      sentToday: db
        .prepare(
          `SELECT COUNT(*) AS c FROM runs
           WHERE account = ? AND action = 'invite' AND success = 1 AND started_at >= ?`,
        )
        .get(acc.name, dayStartUtc).c,
      // Pace on the last SUCCESSFUL send, not on any attempt. A transient/failed attempt did
      // not send a request, so it must not consume the interval — otherwise a cold first run
      // stalls the account for a full interval.
      lastSentAt: db
        .prepare(
          `SELECT MAX(started_at) AS t FROM runs
           WHERE account = ? AND action = 'invite' AND success = 1 AND started_at >= ?`,
        )
        .get(acc.name, dayStartUtc).t,
      notConnected: db
        .prepare(`SELECT COUNT(*) AS c FROM leads WHERE owner_account = ? AND status = 'not_connected'`)
        .get(acc.name).c,
      duePending: readDuePending(acc),
    }),
    { readonly: true },
  );
}

function readDuePending(acc) {
  return withDb(
    (db) =>
      db
        .prepare(
          `SELECT COUNT(*) AS c FROM leads
           WHERE owner_account = ? AND status = 'pending' AND sent_at IS NOT NULL
             AND sent_at < datetime('now', ?)`,
        )
        .get(acc.name, `-${acc.max_pending_days} days`).c,
    { readonly: true },
  );
}

// Run a child script for this account and wait for it to finish. No timeout: a slow op
// (e.g. the account is busy with another workflow) is allowed to take as long as it needs —
// the per-account lock keeps later ticks from starting a second op in the meantime.
function runChild(script, account, extraArgs) {
  return new Promise((resolve) => {
    const logFile = join(
      ensureDir(logsDir()),
      `${account}-${new Date().toISOString().slice(0, 10)}.log`,
    );
    appendFileSync(logFile, `\n=== ${new Date().toISOString()} ${account} ${script} ===\n`);
    const child = spawn(
      process.execPath,
      [join(SKILL_ROOT, 'scripts', script), '--account', account, '--json', ...extraArgs],
      { stdio: ['ignore', 'pipe', 'pipe'] },
    );
    let out = '';
    let err = '';
    child.stdout.on('data', (b) => (out += b.toString()));
    child.stderr.on('data', (b) => (err += b.toString()));
    child.on('error', (e) => {
      appendFileSync(logFile, `spawn error: ${e.message}\n`);
      resolve(-1);
    });
    child.on('close', (code) => {
      if (out) appendFileSync(logFile, out);
      if (err) appendFileSync(logFile, err);
      appendFileSync(logFile, `\n--- exit ${code} ---\n`);
      resolve(code);
    });
  });
}

function logWorker(account, summary) {
  try {
    const logFile = join(
      ensureDir(logsDir()),
      `${account}-${new Date().toISOString().slice(0, 10)}.log`,
    );
    appendFileSync(logFile, `\n[worker ${new Date().toISOString()}] ${JSON.stringify(summary)}\n`);
  } catch {
    /* logging is best-effort */
  }
}

// --- Per-account lock: SQLite IMMEDIATE transaction, never time-based. ---
const LOCK_MAX_BYTES = 1024;
const ownedLockTokens = new Map();

function lockPath(account) {
  return join(dataDir(), `tick-${account}.lock`);
}

function isProcessAlive(pid) {
  if (!Number.isSafeInteger(pid) || pid <= 0) return false;
  try {
    process.kill(pid, 0);
    return true;
  } catch (e) {
    return e.code === 'EPERM'; // exists but owned by another user
  }
}

function parseLockRecord(rawValue, { allowLegacyPid = false } = {}) {
  const raw = String(rawValue ?? '');
  try {
    const parsed = JSON.parse(raw);
    if (
      Number.isSafeInteger(parsed?.pid) &&
      parsed.pid > 0 &&
      typeof parsed?.token === 'string' &&
      parsed.token.length >= 8 &&
      parsed.token.length <= 256
    ) {
      return { pid: parsed.pid, token: parsed.token };
    }
  } catch {
    // Legacy PID-only files are parsed below.
  }
  if (allowLegacyPid) {
    const pid = Number(raw.trim());
    if (Number.isSafeInteger(pid) && pid > 0) return { pid, token: null };
  }
  return null;
}

export function readLegacyLockSnapshot(filePath) {
  let fd;
  try {
    fd = openSync(filePath, constants.O_RDONLY | (constants.O_NOFOLLOW || 0));
  } catch (error) {
    if (error?.code === 'ENOENT') return null;
    return { invalid: true, recoverable: false };
  }
  try {
    const before = fstatSync(fd, { bigint: true });
    if (!before.isFile()) {
      return { invalid: true, recoverable: false };
    }
    if (before.size <= 0n || before.size > BigInt(LOCK_MAX_BYTES)) {
      return { invalid: true, recoverable: true };
    }
    const buffer = Buffer.alloc(Number(before.size));
    let offset = 0;
    while (offset < buffer.length) {
      const count = readSync(fd, buffer, offset, buffer.length - offset, offset);
      if (count === 0) break;
      offset += count;
    }
    const after = fstatSync(fd, { bigint: true });
    if (
      offset !== buffer.length ||
      before.dev !== after.dev ||
      before.ino !== after.ino ||
      before.size !== after.size ||
      before.mtimeNs !== after.mtimeNs ||
      before.ctimeNs !== after.ctimeNs
    ) {
      return { invalid: true, recoverable: false };
    }
    const record = parseLockRecord(buffer.toString('utf8'), { allowLegacyPid: true });
    return record
      ? { invalid: false, record }
      : { invalid: true, recoverable: true };
  } finally {
    closeSync(fd);
  }
}

export function legacyLockBlocks(filePath, processAlive = isProcessAlive) {
  const snapshot = readLegacyLockSnapshot(filePath);
  if (snapshot === null) return false;
  if (snapshot.invalid) return !snapshot.recoverable;
  return processAlive(snapshot.record.pid);
}

function schedulerLockKey(account) {
  return `scheduler_lock:${account}`;
}

function validateOwner(pid, token) {
  if (!Number.isSafeInteger(pid) || pid <= 0) throw new Error('lock PID must be positive');
  if (typeof token !== 'string' || token.length < 8 || token.length > 256) {
    throw new Error('lock ownership token is invalid');
  }
}

export function claimSchedulerLock(
  db,
  account,
  pid,
  token,
  processAlive = isProcessAlive,
) {
  validateOwner(pid, token);
  const key = schedulerLockKey(account);
  const claim = db.transaction(() => {
    const currentValue = db.prepare('SELECT value FROM settings WHERE key = ?').get(key)?.value;
    if (currentValue !== undefined && currentValue !== null && String(currentValue).trim()) {
      const current = parseLockRecord(currentValue);
      if (!current || processAlive(current.pid)) return false;
    }
    db.prepare(
      `INSERT INTO settings (key, value) VALUES (?, ?)
       ON CONFLICT(key) DO UPDATE SET value = excluded.value`,
    ).run(key, JSON.stringify({ pid, token }));
    return true;
  });
  return claim.immediate();
}

export function releaseSchedulerLock(db, account, pid, token) {
  validateOwner(pid, token);
  const key = schedulerLockKey(account);
  const release = db.transaction(() => {
    const currentValue = db.prepare('SELECT value FROM settings WHERE key = ?').get(key)?.value;
    const current = parseLockRecord(currentValue);
    if (!current || current.pid !== pid || current.token !== token) return false;
    return db.prepare('DELETE FROM settings WHERE key = ?').run(key).changes === 1;
  });
  return release.immediate();
}

function databaseLockHeldByLiveProcess(account) {
  return withDb(
    (db) => {
      const value = db
        .prepare('SELECT value FROM settings WHERE key = ?')
        .get(schedulerLockKey(account))?.value;
      if (value === undefined || value === null || !String(value).trim()) return false;
      const record = parseLockRecord(value);
      return !record || isProcessAlive(record.pid);
    },
    { readonly: true },
  );
}

function lockHeldByLiveProcess(account) {
  if (legacyLockBlocks(lockPath(account))) return true;
  return databaseLockHeldByLiveProcess(account);
}

function acquireLock(account) {
  if (legacyLockBlocks(lockPath(account))) return false;
  const token = randomUUID();
  const acquired = withDb(
    (db) => claimSchedulerLock(db, account, process.pid, token),
  );
  if (!acquired) return false;
  ownedLockTokens.set(account, token);
  return true;
}

function releaseLock(account) {
  const token = ownedLockTokens.get(account);
  if (!token) return;
  try {
    withDb((db) => releaseSchedulerLock(db, account, process.pid, token));
  } catch {
    /* release is best-effort; token mismatch never deletes a newer owner */
  } finally {
    ownedLockTokens.delete(account);
  }
}

function pruneLogs() {
  const dir = logsDir();
  if (!existsSync(dir)) return;
  const cutoff = Date.now() - defaults().log_retention_days * 86400 * 1000;
  for (const f of readdirSync(dir)) {
    const path = join(dir, f);
    try {
      if (statSync(path).mtimeMs < cutoff) unlinkSync(path);
    } catch {
      /* ignore */
    }
  }
}
