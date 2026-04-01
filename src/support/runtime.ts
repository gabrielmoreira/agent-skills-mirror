import process from "node:process";
import { spawn } from "node:child_process";
import { promises as fs } from "node:fs";
import { Buffer } from "node:buffer";
import path from "node:path";
import { createDebug } from "./debug.ts";

const IS_WINDOWS = process.platform === "win32";
const debug = createDebug("mirror:runtime");

// ============================================================
// RuntimeAdapter interface
// ============================================================

export type RuntimeAdapter = {
  cwd(): string;
  exec(argv: string[], options?: RuntimeExecOptions): Promise<void>;
  runShell(command: string, options?: RuntimeExecOptions): Promise<void>;
  exists(path: string): Promise<boolean>;
  mkdir(path: string, options?: { recursive?: boolean }): Promise<void>;
  remove(
    path: string,
    options?: { recursive?: boolean; force?: boolean },
  ): Promise<void>;
  move(from: string, to: string): Promise<void>;
  copy(from: string, to: string): Promise<void>;
  readTextFile(path: string): Promise<string>;
  writeTextFile(path: string, content: string): Promise<void>;
  fetchText(url: string | URL | Request, init?: RequestInit): Promise<string>;
  fetchJson<T = unknown>(
    url: string | URL | Request,
    init?: RequestInit,
  ): Promise<T>;
  dirname(path: string): string;
  join(...parts: string[]): string;
  resolve(...parts: string[]): string;
  normalize(path: string): string;
  getEnv(key: string): string | undefined;
  getEnv(key: string, defaultValue: string): string;
  getEnv(key: string, defaultValue?: string): string | undefined;
  /** Spawn a process and stream stdout/stderr to provided callbacks. */
  spawnCapture(
    shell: string[],
    command: string,
    opts: RuntimeExecOptions & {
      onStdout?: (text: string) => void;
      onStderr?: (text: string) => void;
    },
  ): Promise<{ code: number | null; signal: string | null }>;
  /**
   * Spawn a process directly (no shell) and discard all output.
   * Used for silent git setup commands where shell redirection is not needed.
   */
  spawnDirect(
    argv: string[],
    opts?: RuntimeExecOptions,
  ): Promise<{ code: number | null }>;
  /** Access to the process terminal streams through the runtime abstraction. */
  terminal(): RuntimeTerminal;
  /** Resolves the discovered shell as an argv array, e.g. ['bash', '-lc']. */
  shellPath(): Promise<string[]>;
};

export type RuntimeExecOptions = {
  cwd?: string;
  env?: Record<string, string>;
};

export type RuntimeTextWriter = {
  write(text: string): void;
  isTTY(): boolean;
};

export type RuntimeTerminal = {
  stdout: RuntimeTextWriter;
  stderr: RuntimeTextWriter;
};

const _encoder = new TextEncoder();

type DenoStreamLike = {
  writeSync(data: Uint8Array): number;
  isTerminal?: () => boolean;
};

function _denoStream(name: "stdout" | "stderr"): DenoStreamLike | null {
  const denoObj = (globalThis as {
    Deno?: { stdout?: DenoStreamLike; stderr?: DenoStreamLike };
  }).Deno;
  return denoObj?.[name] ?? null;
}

function _makeWriter(
  name: "stdout" | "stderr",
  fallback: NodeJS.WriteStream,
): RuntimeTextWriter {
  const deno = _denoStream(name);
  return {
    write(text: string) {
      if (deno && typeof deno.writeSync === "function") {
        deno.writeSync(_encoder.encode(text));
        return;
      }
      fallback.write(text);
    },
    isTTY(): boolean {
      if (deno && typeof deno.isTerminal === "function") {
        try {
          return deno.isTerminal();
        } catch { /* ignore */ }
      }
      return fallback.isTTY === true;
    },
  };
}

// ============================================================
// Env helpers
// ============================================================

function getEnv(key: string): string | undefined;
function getEnv(key: string, defaultValue: string): string;
function getEnv(key: string, defaultValue?: string): string | undefined {
  return process.env[key] ?? defaultValue;
}

// ============================================================
// Shell discovery
// ============================================================

const BASH_CANDIDATES = [
  // 1. Explicit override
  "%MIRROR_BASH%",

  // 2. Windows native bash (Git for Windows, MSYS2, Cygwin, Scoop)
  "%LOCALAPPDATA%\\Programs\\Git\\usr\\bin\\bash.exe",
  "%LOCALAPPDATA%\\Programs\\Git\\bin\\bash.exe",
  "%CLAUDE_CODE_GIT_BASH_PATH%",
  "%ProgramW6432%\\Git\\usr\\bin\\bash.exe",
  "%ProgramW6432%\\Git\\bin\\bash.exe",
  "%ProgramFiles%\\Git\\usr\\bin\\bash.exe",
  "%ProgramFiles%\\Git\\bin\\bash.exe",
  "%ProgramFiles(x86)%\\Git\\usr\\bin\\bash.exe",
  "%ProgramFiles(x86)%\\Git\\bin\\bash.exe",
  "%USERPROFILE%\\scoop\\apps\\git\\current\\usr\\bin\\bash.exe",
  "%USERPROFILE%\\scoop\\apps\\git\\current\\bin\\bash.exe",
  "%USERPROFILE%\\scoop\\apps\\git-with-openssh\\current\\usr\\bin\\bash.exe",
  "%USERPROFILE%\\scoop\\shims\\bash.exe",
  "%MSYS2_ROOT%\\usr\\bin\\bash.exe",
  "C:\\msys64\\usr\\bin\\bash.exe",
  "C:\\tools\\msys64\\usr\\bin\\bash.exe",
  "%LOCALAPPDATA%\\Programs\\MSYS2\\usr\\bin\\bash.exe",
  "%CYGWIN_ROOT%\\bin\\bash.exe",
  "C:\\cygwin64\\bin\\bash.exe",
  "C:\\tools\\cygwin64\\bin\\bash.exe",
  "%USERPROFILE%\\bin\\bash.exe",
  "C:\\tools\\bash\\bash.exe",
  "C:\\tools\\bin\\bash.exe",
  "D:\\tools\\bin\\bash.exe",

  // 3. macOS
  "/bin/bash",
  "/usr/bin/bash",
  "/opt/homebrew/bin/bash",
  "/usr/local/bin/bash",
  "/opt/local/bin/bash",

  // 4. Linux
  "/snap/bin/bash",
  "/var/lib/flatpak/exports/bin/bash",
  "~/.nix-profile/bin/bash",
  "/nix/var/nix/profiles/default/bin/bash",
  "/run/current-system/sw/bin/bash",
  "~/.local/bin/bash",
  "~/.asdf/shims/bash",
  "~/.local/share/mise/shims/bash",
  "~/.local/share/rtx/shims/bash",
  "/usr/pkg/bin/bash",
  "/opt/bin/bash",
  "/opt/bash/bin/bash",

  // 5. PATH search
  "%PATH%",
  "$PATH",

  // 6. WSL bridge (last resort)
  "%SystemRoot%\\System32\\wsl.exe",
  "C:\\Windows\\System32\\wsl.exe",
];

function expandVars(s: string): string {
  s = s.replace(/%([^%]+)%/g, (_, k) => process.env[k] ?? "");
  s = s.replace(/\$([A-Za-z_][A-Za-z0-9_]*)/g, (_, k) => process.env[k] ?? "");
  s = s.replace(
    /^~(?=[/\\]|$)/,
    process.env["HOME"] ?? process.env["USERPROFILE"] ?? "~",
  );
  return s;
}

function isWindowsNativePath(p: string): boolean {
  return p.includes("\\") || /\.(exe|cmd|bat)$/i.test(p);
}

function splitPathVar(raw: string, expanded: string): string[] {
  const upper = raw.toUpperCase();
  if (upper !== "%PATH%" && upper !== "$PATH") return [expanded];
  const sep = expanded.includes(";") ? ";" : ":";
  return expanded.split(sep).map((s) => s.trim()).filter(Boolean);
}

async function statSafe(
  p: string,
): Promise<import("node:fs").Stats | null> {
  try {
    return await fs.stat(p);
  } catch {
    return null;
  }
}

async function lstatSafe(
  p: string,
): Promise<import("node:fs").Stats | null> {
  try {
    return await fs.lstat(p);
  } catch {
    return null;
  }
}

async function makeWritableRecursive(p: string): Promise<void> {
  const st = await lstatSafe(p);
  if (!st) return;

  if (st.isDirectory() && !st.isSymbolicLink()) {
    for (const entry of await fs.readdir(p)) {
      await makeWritableRecursive(path.join(p, entry));
    }
  }

  const mode = st.isDirectory() ? 0o777 : 0o666;
  await fs.chmod(p, mode).catch(() => {});
}

async function removePath(
  targetPath: string,
  options?: { recursive?: boolean; force?: boolean },
): Promise<void> {
  try {
    await fs.rm(targetPath, {
      recursive: options?.recursive ?? false,
      force: options?.force ?? false,
    });
  } catch (err: unknown) {
    if (
      typeof err === "object" && err !== null && "code" in err &&
      ["EPERM", "EACCES"].includes(
        String((err as NodeJS.ErrnoException).code),
      ) &&
      (options?.recursive === true || options?.force === true)
    ) {
      await makeWritableRecursive(targetPath);
      await fs.rm(targetPath, {
        recursive: options?.recursive ?? false,
        force: options?.force ?? false,
      });
      return;
    }
    throw err;
  }
}

async function tryResolved(p: string): Promise<string | null> {
  if (!p) return null;
  const st = await statSafe(p);
  if (!st) return null;
  if (st.isFile()) return p;
  if (st.isDirectory()) {
    const names = IS_WINDOWS ? ["bash.exe", "bash.cmd", "bash"] : ["bash"];
    for (const name of names) {
      const full = path.join(p, name);
      const fs2 = await statSafe(full);
      if (fs2?.isFile()) return full;
    }
  }
  return null;
}

async function discoverShell(): Promise<string | null> {
  const mirrorBashRaw = "%MIRROR_BASH%";

  for (const raw of BASH_CANDIDATES) {
    const expanded = expandVars(raw);
    if (!expanded) continue;

    if (!IS_WINDOWS && isWindowsNativePath(expanded)) continue;

    const isMirrorBash = raw === mirrorBashRaw;
    const entries = splitPathVar(raw, expanded);
    let foundAny = false;

    for (const entry of entries) {
      const found = await tryResolved(entry);
      if (found !== null) return found;
      if (entry) foundAny = true;
    }

    if (isMirrorBash && foundAny) {
      debug(
        "MIRROR_BASH=%s is not usable - falling back to discovery",
        process.env["MIRROR_BASH"],
      );
    }
  }

  return null;
}

// ============================================================
// Core exec (shell: false)
// ============================================================

async function exec(
  argv: string[],
  options?: RuntimeExecOptions,
): Promise<void> {
  if (argv.length === 0) throw new Error("Cannot execute an empty command.");

  await new Promise<void>((resolve, reject) => {
    const child = spawn(argv[0], argv.slice(1), {
      cwd: options?.cwd,
      env: options?.env ? { ...process.env, ...options.env } : process.env,
      stdio: "inherit",
      shell: false,
    });
    child.on("error", reject);
    child.on("exit", (code, signal) => {
      if (code === 0) {
        resolve();
        return;
      }
      reject(
        new Error(
          `Command failed: ${argv.join(" ")} (code=${code ?? "null"}, signal=${
            signal ?? "null"
          })`,
        ),
      );
    });
  });
}

// ============================================================
// Shell cache (lazy singleton)
// ============================================================

let _shell: string[] | undefined;
let _shellPending: Promise<string[]> | undefined;

function getShell(): Promise<string[]> {
  if (_shell !== undefined) return Promise.resolve(_shell);
  if (_shellPending !== undefined) return _shellPending;

  _shellPending = (async () => {
    const found = await discoverShell();

    if (found === null) {
      const fallback = IS_WINDOWS ? ["cmd", "/d", "/s", "/c"] : ["sh", "-c"];
      debug("no bash found, falling back to %s", fallback[0]);
      return (_shell = fallback);
    }

    const isWsl = /wsl\.exe$/i.test(found);
    if (isWsl) {
      debug("using WSL bridge: %s", found);
      return (_shell = [found, "-e", "bash", "-lc"]);
    }

    debug("using bash: %s", found);
    return (_shell = [found, "-lc"]);
  })();

  return _shellPending;
}

// ============================================================
// spawnCapture — the one process primitive used by Reporter
// ============================================================

/**
 * Spawn a shell command and stream stdout/stderr through callbacks.
 *
 * Unlike exec() which inherits all stdio, this pipes stdout and stderr
 * so callers can capture or format the output.  The key design point:
 * stderr is routed to the onStderr callback which writes to our stdout
 * (not process.stderr).  This avoids the Windows bash pipe deadlock where
 * bash blocks on stderr when the stderr pipe buffer fills up while the
 * parent is blocked writing to stderr inside a 'data' handler.
 */
async function spawnCapture(
  shell: string[],
  command: string,
  opts: RuntimeExecOptions & {
    onStdout?: (text: string) => void;
    onStderr?: (text: string) => void;
  },
): Promise<{ code: number | null; signal: string | null }> {
  const { onStdout, onStderr, cwd, env } = opts;

  const child = spawn(shell[0], [...shell.slice(1), command], {
    cwd,
    env: env ? { ...process.env, ...env } : process.env,
    stdio: ["ignore", "pipe", "pipe"],
  });

  const stdoutDone = child.stdout
    ? new Promise<void>((resolve) => {
      child.stdout!.on("data", (chunk: Buffer) => {
        onStdout?.(chunk.toString());
      });
      child.stdout!.on("end", resolve);
    })
    : Promise.resolve();

  const stderrDone = child.stderr
    ? new Promise<void>((resolve) => {
      child.stderr!.on("data", (chunk: Buffer) => {
        // Route to onStderr (typically our stdout) to avoid buffer deadlock.
        onStderr?.(chunk.toString());
      });
      child.stderr!.on("end", resolve);
    })
    : Promise.resolve();

  const [code, signal] = await new Promise<[number | null, string | null]>(
    (resolve) => {
      child.on("exit", (c, s) => resolve([c, s]));
      child.on("error", () => resolve([-1, null]));
    },
  );

  await Promise.all([stdoutDone, stderrDone]);
  return { code, signal };
}

// ============================================================
// Default adapter factory
// ============================================================

export function createDefaultRuntimeAdapter(): RuntimeAdapter {
  const terminal: RuntimeTerminal = {
    stdout: _makeWriter("stdout", process.stdout),
    stderr: _makeWriter("stderr", process.stderr),
  };

  return {
    cwd: () => process.cwd(),
    exec,
    shellPath: getShell,

    async runShell(command, options) {
      const shell = await getShell();
      await exec([...shell, command], options);
    },

    async exists(targetPath) {
      try {
        await fs.stat(targetPath);
        return true;
      } catch (err: unknown) {
        if (
          typeof err === "object" && err !== null && "code" in err &&
          (err as NodeJS.ErrnoException).code === "ENOENT"
        ) return false;
        throw err;
      }
    },

    async mkdir(targetPath, options) {
      await fs.mkdir(targetPath, { recursive: options?.recursive ?? true });
    },

    async remove(targetPath, options) {
      await removePath(targetPath, options);
    },
    async readTextFile(targetPath) {
      return await fs.readFile(targetPath, "utf8");
    },

    async writeTextFile(targetPath, content) {
      await fs.writeFile(targetPath, content, "utf8");
    },

    async move(from, to) {
      await fs.mkdir(path.dirname(to), { recursive: true });
      try {
        await fs.rename(from, to);
      } catch (err: unknown) {
        if (
          typeof err === "object" && err !== null && "code" in err &&
          ["EXDEV", "EPERM", "EACCES"].includes(
            String((err as NodeJS.ErrnoException).code),
          )
        ) {
          await fs.cp(from, to, { recursive: true, force: true });
          await removePath(from, { recursive: true, force: true });
          return;
        }
        throw err;
      }
    },

    async copy(from, to) {
      await fs.mkdir(path.dirname(to), { recursive: true });
      await fs.cp(from, to, { recursive: true, force: true });
    },

    async fetchText(url: string | URL, init?: RequestInit): Promise<string> {
      const res = await fetch(url, init);
      if (!res.ok) {
        throw new Error(`HTTP ${res.status} for ${url} (${res.statusText})`);
      }
      return res.text();
    },

    async fetchJson<T>(url: string | URL, init?: RequestInit): Promise<T> {
      const text = await this.fetchText(url, init);
      try {
        return JSON.parse(text) as T;
      } catch (err) {
        throw new Error(
          `Invalid JSON from ${String(url)}: ${
            err instanceof Error ? err.message : String(err)
          }`,
        );
      }
    },

    dirname: (p) => path.dirname(p),
    join: (...parts) => path.join(...parts),
    resolve: (...parts) => path.resolve(...parts),
    normalize: (p) => path.normalize(p),

    getEnv,
    terminal() {
      return terminal;
    },

    spawnCapture(shell, command, opts) {
      return spawnCapture(shell, command, opts);
    },

    spawnDirect(
      argv: string[],
      opts?: RuntimeExecOptions,
    ): Promise<{ code: number | null }> {
      return new Promise((resolve, reject) => {
        const child = spawn(argv[0], argv.slice(1), {
          cwd: opts?.cwd,
          env: opts?.env ? { ...process.env, ...opts.env } : process.env,
          stdio: "ignore",
        });
        child.on("error", reject);
        child.on("exit", (code) => resolve({ code }));
      });
    },
  };
}

// ============================================================
// Cached runtime wrapper
// ============================================================

export type CacheConfig = { ttl: number };

export function defaultCacheConfigFactory(_opts: CacheConfig): CacheConfig {
  return { ttl: _opts.ttl };
}

/** Tagged union for cache results. */
type CacheResult<T> = { hit: true; data: T } | { hit: false };

/** FNV-1a 48-bit hash → lowercase hex string. */
function hashKey(input: string): string {
  let h = 0xcbf29ce484222325n;
  for (let i = 0; i < input.length; i++) {
    h ^= BigInt(input.charCodeAt(i));
    h = (h * 0x100000001b3n) & 0xffffffffffffffffn;
  }
  return (h >> 16n).toString(16);
}

function cacheKeyForRequest(
  url: string | URL | Request,
  init?: RequestInit,
): string {
  const headers = new Headers(init?.headers ?? undefined);
  const headerPairs = [...headers.entries()].sort(([a], [b]) =>
    a.localeCompare(b)
  );
  return hashKey(JSON.stringify({
    url: String(url),
    method: init?.method ?? "GET",
    headers: headerPairs,
  }));
}

type CacheEntry<T> = { data: T; expiresAt: number };

function tryCache<T>(
  cache: Map<string, CacheEntry<T>>,
  key: string,
  now: number,
): CacheResult<T> {
  const entry = cache.get(key);
  if (!entry) return { hit: false };
  if (entry.expiresAt < now) {
    cache.delete(key);
    return { hit: false };
  }
  return { hit: true, data: entry.data };
}


export function makeCachedRuntime(
  base: RuntimeAdapter,
  _cacheDir: string,
  config: CacheConfig,
): RuntimeAdapter {
  const textCache = new Map<string, CacheEntry<string>>();
  const jsonCache = new Map<string, CacheEntry<unknown>>();

  async function persistCache(_key: string, _data: string): Promise<void> {
    // Cache persistence is optional; in-memory cache is sufficient for this use case.
  }

  return {
    ...base,
    cwd: base.cwd.bind(base),
    exec: base.exec.bind(base),
    runShell: base.runShell.bind(base),
    shellPath: base.shellPath.bind(base),
    terminal: base.terminal.bind(base),
    spawnCapture: base.spawnCapture.bind(base),
    spawnDirect: base.spawnDirect.bind(base),
    move: base.move.bind(base),
    copy: base.copy.bind(base),
    async fetchText(url, init) {
      const now = Date.now();
      const key = cacheKeyForRequest(url, init);
      const hit = tryCache(textCache, key, now);
      if (hit.hit) return hit.data;
      const data = await base.fetchText(url, init);
      textCache.set(key, { data, expiresAt: now + config.ttl });
      persistCache(key, data).catch(() => {});
      return data;
    },

    async fetchJson<T>(url: string | URL, init?: RequestInit): Promise<T> {
      const now = Date.now();
      const key = cacheKeyForRequest(url, init);
      const hit = tryCache(jsonCache, key, now);
      if (hit.hit) return hit.data as T;
      const data = await base.fetchJson<T>(url, init);
      jsonCache.set(key, { data, expiresAt: now + config.ttl });
      return data;
    },
  };
}
