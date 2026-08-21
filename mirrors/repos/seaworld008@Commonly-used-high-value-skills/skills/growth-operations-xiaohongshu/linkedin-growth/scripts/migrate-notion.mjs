#!/usr/bin/env node
//
// ONE-OFF migration: Notion "Lead" DB (under the "Social selling" page) -> skill SQLite.
//
// Mapping rules (agreed with the user):
//   - A lead PROCESSED by a real account (status Connected/Pending/Withdrawn/Error) is tied
//     to that real account (vlad / kiril). If both processed it, priority decides the owner:
//       Connected > Pending > Withdrawn > Error
//     Status map: Connected->connected, Pending->pending, Withdrawn->exhausted, Error->error.
//   - A lead NOT processed by either account (both "Not connected") -> not_connected, owner
//     assigned round-robin across the chosen accounts (default: non-paused accounts).
//   - Dedup by hashed_url, both within Notion (same person across lists) and vs the existing DB.
//   - For every account that actually sent a request, a synthetic `runs` invite row is written
//     (started_at = original send date, so it never counts toward TODAY's quota). This makes
//     the cross-account retry attribution correct for migrated `pending` leads.
//
// DRY-RUN by default (no writes). Pass --apply to write.
// Flags: --apply  --refetch  --rr=vlad,alex,maksim  --pending=keep|exhaust
//
import { randomUUID } from 'node:crypto';
import {
  chmodSync,
  closeSync,
  constants,
  fchmodSync,
  fstatSync,
  fsyncSync,
  lstatSync,
  mkdirSync,
  openSync,
  readFileSync,
  realpathSync,
  renameSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import { basename, dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HOME = process.env.HOME;
const DATA_DIR = join(HOME, '.local/share/linkedapi-linkedin-growth');
const TOKEN_PATH = join(DATA_DIR, '.notion-token');
const DB_PATH = join(DATA_DIR, 'db.sqlite');
const CACHE = join(DATA_DIR, 'tmp/notion-leads-cache.json');
const PREVIEW = join(DATA_DIR, 'tmp/migration-preview.json');
export const NOTION_QUERY_URL =
  'https://api.notion.com/v1/databases/28665216-8ab0-809c-a8dc-d8fe366d0266/query';
const HIST = '2026-01-01 00:00:00'; // fallback historical timestamp (safely before today)

const args = process.argv.slice(2);
const APPLY = args.includes('--apply');
const REFETCH = args.includes('--refetch');
const rrArg = (args.find((a) => a.startsWith('--rr=')) || '').split('=')[1];
const pendingMode = (args.find((a) => a.startsWith('--pending=')) || '').split('=')[1] || 'keep';

const rt = (p) => (p?.rich_text || []).map((t) => t.plain_text).join('');
const ti = (p) => (p?.title || []).map((t) => t.plain_text).join('');
const norm = (s) => (s || '').trim().toLowerCase();
const RANK = { connected: 4, pending: 3, withdrawn: 2, error: 1 };

function ensurePrivateDirectory(directoryPath) {
  mkdirSync(directoryPath, { recursive: true, mode: 0o700 });
  const stat = lstatSync(directoryPath);
  if (!stat.isDirectory() || stat.isSymbolicLink()) {
    throw new Error(`refusing non-directory cache path: ${directoryPath}`);
  }
  chmodSync(directoryPath, 0o700);
}

export function readJsonCache(filePath) {
  let fd;
  try {
    const noFollow = constants.O_NOFOLLOW || 0;
    fd = openSync(filePath, constants.O_RDONLY | noFollow);
    const stat = fstatSync(fd);
    if (!stat.isFile()) {
      throw new Error(`cache is not a regular file: ${filePath}`);
    }
    fchmodSync(fd, 0o600);
    return JSON.parse(readFileSync(fd, 'utf8'));
  } catch (error) {
    if (error?.code === 'ENOENT') return null;
    throw error;
  } finally {
    if (fd !== undefined) closeSync(fd);
  }
}

export function writePrivateJsonAtomic(filePath, value, space = 0) {
  const directoryPath = dirname(filePath);
  ensurePrivateDirectory(directoryPath);
  const temporaryPath = join(
    directoryPath,
    `.${basename(filePath)}.${process.pid}.${randomUUID()}.tmp`,
  );
  let fd;
  try {
    fd = openSync(
      temporaryPath,
      constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL | (constants.O_NOFOLLOW || 0),
      0o600,
    );
    fchmodSync(fd, 0o600);
    writeFileSync(fd, JSON.stringify(value, null, space), 'utf8');
    fsyncSync(fd);
    closeSync(fd);
    fd = undefined;
    renameSync(temporaryPath, filePath);
    chmodSync(filePath, 0o600);
  } finally {
    if (fd !== undefined) closeSync(fd);
    rmSync(temporaryPath, { force: true });
  }
}

function mapStatus(oldStatus) {
  const n = norm(oldStatus);
  if (n === 'connected') return 'connected';
  if (n === 'pending') return pendingMode === 'exhaust' ? 'exhausted' : 'pending';
  if (n === 'withdrawn') return 'exhausted';
  if (n === 'error') return 'error';
  return 'not_connected';
}

export async function fetchAll({
  cachePath = CACHE,
  fetchImpl = globalThis.fetch,
  refetch = REFETCH,
  token,
} = {}) {
  ensurePrivateDirectory(dirname(cachePath));
  if (!refetch) {
    const cached = readJsonCache(cachePath);
    if (cached !== null) {
      if (!Array.isArray(cached)) throw new Error(`invalid Notion cache payload: ${cachePath}`);
      process.stderr.write(`using cache (${cached.length} rows); pass --refetch to refresh\n`);
      return cached;
    }
  }
  if (!token) throw new Error('Notion token is required when refreshing the cache');
  if (typeof fetchImpl !== 'function') throw new Error('fetch is unavailable');
  const headers = {
    Authorization: `Bearer ${token}`,
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json',
  };
  let cursor;
  const rows = [];
  do {
    const body = { page_size: 100 };
    if (cursor) body.start_cursor = cursor;
    const r = await fetchImpl(NOTION_QUERY_URL, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
      redirect: 'error',
    });
    const j = await r.json();
    if (!r.ok) throw new Error(`Notion HTTP ${r.status}: ${j?.message || 'request failed'}`);
    if (j.object === 'error') throw new Error('Notion error: ' + j.message);
    if (!Array.isArray(j.results)) throw new Error('Notion response is missing results');
    for (const row of j.results) {
      const p = row.properties;
      rows.push({
        full_name: ti(p['Full Name']),
        hashed_url: rt(p['Hashed URL']).trim(),
        public_url: rt(p['Public URL']).trim(),
        list_name: rt(p['List Name']).trim(),
        reasoning: rt(p['Reasoning']),
        basic_info: rt(p['Basic Info']),
        st_vlad: p['Status with Vlad']?.status?.name || '',
        st_kiril: p['Status with Kiril']?.status?.name || '',
        sent_vlad: p['Sent from Vlad']?.date?.start || null,
        sent_kiril: p['Sent from Kiril']?.date?.start || null,
      });
    }
    cursor = j.has_more ? j.next_cursor : undefined;
    process.stderr.write(`\rfetched ${rows.length}...`);
  } while (cursor);
  process.stderr.write('\n');
  writePrivateJsonAtomic(cachePath, rows);
  return rows;
}

function bestFor(rowsArr, stKey, sentKey) {
  let bestRank = 0;
  let bestStatus = '';
  let sent = null;
  for (const r of rowsArr) {
    const rk = RANK[norm(r[stKey])] ?? 0;
    if (rk > bestRank) { bestRank = rk; bestStatus = r[stKey]; }
    if (r[sentKey] && (!sent || r[sentKey] < sent)) sent = r[sentKey];
  }
  return { rank: bestRank, status: bestStatus, sent };
}

function extractPositionLocation(basicInfo) {
  if (!basicInfo) return { position: null, location: null };
  try {
    const parsed = JSON.parse(basicInfo);
    const d = parsed.data ?? parsed;
    return { position: d.position ?? d.headline ?? null, location: d.location ?? null };
  } catch {
    return { position: null, location: null };
  }
}

function firstNonEmpty(rowsArr, key) {
  for (const r of rowsArr) if (r[key]) return r[key];
  return null;
}

async function main() {
  const token = readFileSync(TOKEN_PATH, 'utf8').trim();
  const rows = await fetchAll({ token });
  const { default: Database } = await import('better-sqlite3');

  // --- collapse by hashed_url ---
  const groups = new Map();
  let noHash = 0;
  for (const r of rows) {
    if (!r.hashed_url) { noHash++; continue; }
    let g = groups.get(r.hashed_url);
    if (!g) { g = []; groups.set(r.hashed_url, g); }
    g.push(r);
  }

  // --- existing DB state ---
  const db = new Database(DB_PATH, { readonly: !APPLY });
  db.pragma('foreign_keys = ON');
  const existing = new Set(db.prepare('SELECT hashed_url FROM leads').all().map((r) => r.hashed_url));
  const accountNames = new Set(db.prepare('SELECT name FROM accounts').all().map((r) => r.name));
  let rr = rrArg
    ? rrArg.split(',').map((s) => s.trim()).filter(Boolean)
    : db.prepare('SELECT name FROM accounts WHERE paused = 0 ORDER BY name').all().map((r) => r.name);
  for (const a of rr) if (!accountNames.has(a)) throw new Error(`--rr account '${a}' not in DB`);
  if (rr.length === 0) throw new Error('no round-robin accounts available');
  const cursor = db.prepare('SELECT last_assigned_account FROM import_state WHERE id = 1').get()?.last_assigned_account ?? null;
  let rrIdx = cursor && rr.includes(cursor) ? (rr.indexOf(cursor) + 1) % rr.length : 0;

  // --- build planned rows ---
  const planned = [];
  const runs = [];
  let skippedExisting = 0;
  let multiList = 0;
  const byStatus = {};
  const byOwner = {};
  const rrSplit = {};
  let lastAssigned = cursor;

  for (const [hashed_url, gRows] of groups) {
    if (existing.has(hashed_url)) { skippedExisting++; continue; }

    const v = bestFor(gRows, 'st_vlad', 'sent_vlad');
    const k = bestFor(gRows, 'st_kiril', 'sent_kiril');
    const cands = [{ acct: 'vlad', ...v }, { acct: 'kiril', ...k }];
    const maxRank = Math.max(v.rank, k.rank);

    let owner;
    let status;
    let sent_at = null;
    if (maxRank > 0) {
      const winners = cands.filter((c) => c.rank === maxRank).sort((a, b) => {
        const ad = a.sent ? 0 : 1;
        const bd = b.sent ? 0 : 1;
        if (ad !== bd) return ad - bd;
        if (a.sent && b.sent) return a.sent < b.sent ? -1 : 1;
        return a.acct < b.acct ? -1 : 1;
      });
      const w = winners[0];
      owner = w.acct;
      status = mapStatus(w.status);
      sent_at = w.sent;
      if (status === 'pending' && !sent_at) sent_at = HIST; // keep it checkable
    } else {
      status = 'not_connected';
      owner = rr[rrIdx];
      rrIdx = (rrIdx + 1) % rr.length;
      rrSplit[owner] = (rrSplit[owner] || 0) + 1;
      lastAssigned = owner;
    }

    // synthetic invite runs for each account that actually sent a request
    for (const c of cands) {
      if (c.rank > 0) {
        runs.push({
          hashed_url,
          account: c.acct,
          success: norm(c.status) === 'error' ? 0 : 1,
          started_at: c.sent || HIST,
        });
      }
    }

    const { position, location } = extractPositionLocation(firstNonEmpty(gRows, 'basic_info'));
    const distinctLists = new Set(gRows.map((r) => r.list_name).filter(Boolean));
    if (distinctLists.size > 1) multiList++;

    planned.push({
      hashed_url,
      public_url: firstNonEmpty(gRows, 'public_url'),
      full_name: firstNonEmpty(gRows, 'full_name') || '(unknown)',
      position,
      location,
      list_name: firstNonEmpty(gRows, 'list_name'),
      reasoning: firstNonEmpty(gRows, 'reasoning'),
      owner_account: owner,
      basic_info_json: firstNonEmpty(gRows, 'basic_info'),
      status,
      sent_at,
      error_type: status === 'error' ? 'migrated' : null,
      error_message: status === 'error' ? 'Migrated from Notion (status: Error)' : null,
    });
    byStatus[status] = (byStatus[status] || 0) + 1;
    byOwner[owner] = (byOwner[owner] || 0) + 1;
  }

  // --- report ---
  const summary = {
    apply: APPLY,
    pending_mode: pendingMode,
    rr_accounts: rr,
    notion_rows: rows.length,
    rows_without_hash_skipped: noHash,
    distinct_people: groups.size,
    duplicates_collapsed: rows.length - noHash - groups.size,
    skipped_already_in_db: skippedExisting,
    to_insert: planned.length,
    by_status: byStatus,
    by_owner: byOwner,
    round_robin_split: rrSplit,
    synthetic_runs: runs.length,
    multi_list_people: multiList,
  };
  console.log(JSON.stringify(summary, null, 2));
  writePrivateJsonAtomic(PREVIEW, { summary, sample: planned.slice(0, 25) }, 2);
  console.log(`\npreview (summary + 25 sample rows) written to: ${PREVIEW}`);

  if (!APPLY) {
    console.log('\nDRY-RUN only. Re-run with --apply to write.');
    db.close();
    return;
  }

  // --- apply ---
  const insLead = db.prepare(
    `INSERT OR IGNORE INTO leads
       (hashed_url, public_url, full_name, position, location, list_name, reasoning,
        owner_account, basic_info_json, status, sent_at, status_updated_at, error_type, error_message)
     VALUES (@hashed_url, @public_url, @full_name, @position, @location, @list_name, @reasoning,
        @owner_account, @basic_info_json, @status, @sent_at, @status_updated_at, @error_type, @error_message)`,
  );
  const insRun = db.prepare(
    `INSERT INTO runs (lead_hashed_url, account, action, started_at, finished_at, success, raw_response_json, error_message)
     VALUES (?, ?, 'invite', ?, ?, ?, NULL, 'migrated from Notion')`,
  );
  let inserted = 0;
  const tx = db.transaction(() => {
    for (const p of planned) {
      const res = insLead.run({ ...p, status_updated_at: p.sent_at || HIST });
      if (res.changes === 1) inserted++;
    }
    for (const r of runs) insRun.run(r.hashed_url, r.account, r.started_at, r.started_at, r.success);
    if (lastAssigned) db.prepare('UPDATE import_state SET last_assigned_account = ? WHERE id = 1').run(lastAssigned);
  });
  tx();
  console.log(`\nAPPLIED: inserted ${inserted} leads, ${runs.length} synthetic runs. rr cursor -> ${lastAssigned}`);
  db.close();
}

const isMain = Boolean(process.argv[1]) &&
  realpathSync(resolve(process.argv[1])) === realpathSync(fileURLToPath(import.meta.url));
if (isMain) {
  main().catch((e) => { console.error('FAILED:', e.message); process.exit(1); });
}
