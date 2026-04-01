/**
 * app/tasks.ts — All operational / I/O helpers.
 *
 * All functions are created by makeTasks(runtime, reporter) and share the runtime
 * and reporter via closure.  No task ever receives them as parameters.
 *
 * Layer contract:
 *   tasks.ts   →  all runtime-facing operational helpers.
 *   mirror.ts  →  pure decision logic.  Zero I/O.
 */

import type { RuntimeAdapter } from "../support/runtime.ts";
import type { Reporter } from "../support/output.ts";

// ============================================================
// Shared types
// ============================================================

export type RepoState = {
  commit: string;
  configHash: string;
  mirroredAt: string;
  output?: "matched" | "no-matches" | "unsupported";
};

export type ManifestFileEntry = {
  path: string;
  default?: boolean;
  followed?: boolean;
};

export type RequestedGitRef =
  | { type: "branch"; name: string }
  | { type: "tag"; name: string }
  | { type: "commit"; sha: string };

export type ResolvedGitRef =
  | { type: "branch"; name: string; sha: string }
  | { type: "tag"; name: string; sha: string }
  | { type: "commit"; sha: string };

export type MirrorManifest = {
  repo: string;
  repoUrl: string;
  refType: ResolvedGitRef["type"];
  ref: string;
  sparsePatterns: {
    defaults: string[];
    followed: string[];
  };
  fileIndex: ManifestFileEntry[];
};

export class UnsupportedRepoError extends Error {
  readonly kind = "unsupported-repo";
  constructor(message: string) {
    super(message);
    this.name = "UnsupportedRepoError";
  }
}

function parseUnsupportedWindowsCheckout(stderr: string): string | null {
  const invalidPath = stderr.match(/error: invalid path '([^']+)'/i)?.[1];
  if (invalidPath) return `invalid path: ${invalidPath}`;

  const longFile = stderr.match(
    /error: unable to create file ([^:\r\n]+): Filename too long/i,
  )?.[1];
  if (longFile) return `path too long: ${longFile}`;

  const longDir = stderr.match(
    /fatal: cannot create directory at '([^']+)': Filename too long/i,
  )?.[1];
  if (longDir) return `path too long: ${longDir}`;

  if (/Filename too long/i.test(stderr)) return "path too long";
  return null;
}

function isLikelyWindowsLongPathCopyError(err: unknown, path: string): boolean {
  if (!path.includes("\\")) return false;
  if (path.length < 220) return false;

  const message = (err instanceof Error ? err.message : String(err))
    .toLowerCase();
  const code = (err as { code?: string })?.code;

  if (message.includes("filename too long")) return true;
  if (code === "ENAMETOOLONG") return true;

  const hasPathFailureSignal = message.includes("enoent") ||
    message.includes("no such file or directory") ||
    message.includes("cannot create");
  const isCopyOrChmod = message.includes("copy") || message.includes("chmod");

  if (hasPathFailureSignal && isCopyOrChmod) return true;
  if (code && ["ENOENT", "EINVAL", "UNKNOWN"].includes(code) && isCopyOrChmod) {
    return true;
  }

  return false;
}

/**
 * Returns true when an OS error was most likely caused by antivirus or security
 * software intercepting a file copy (e.g. Windows Defender quarantine).
 * These errors are transient — the repo itself is fine. Do not persist
 * an unsupported state; the next run should retry after the user adds an exclusion.
 */
export function isAVInterferenceError(err: unknown): boolean {
  if (!(err instanceof Error)) return false;
  const code = (err as { code?: string }).code;
  return code === "UNKNOWN" && err.message.includes("copyfile");
}

export type GitHubRepo = {
  full_name: string;
  name: string;
  owner: { login: string };
  default_branch: string;
};

// ============================================================
// Maker
// ============================================================

export type MirrorTasks = ReturnType<typeof makeTasks>;

export function makeTasks(
  rt: RuntimeAdapter,
  reporter: Reporter,
) {
  // ============================================================
  // Git helpers
  // ============================================================

  /**
   * Managed repos are identified by a valid .git/config under the target dir.
   */
  async function repoExists(targetDir: string): Promise<boolean> {
    return await rt.exists(rt.join(targetDir, ".git", "config"));
  }

  /** Final exported mirrors should exist without any nested .git state. */
  async function exportDirReady(targetDir: string): Promise<boolean> {
    return await rt.exists(targetDir) &&
      !(await rt.exists(rt.join(targetDir, ".git")));
  }

  function stageDirFor(exportDir: string): string {
    return `${exportDir}.__mirror_tmp__`;
  }

  function shellQuote(value: string): string {
    return `'${value.replace(/'/g, `'\\''`)}'`;
  }

  function formatResolvedRef(ref: ResolvedGitRef): string {
    if (ref.type === "branch") return `branch ${ref.name}`;
    if (ref.type === "tag") return `tag ${ref.name}`;
    return `commit ${ref.sha}`;
  }

  function shortSha(sha: string): string {
    return sha.slice(0, 12);
  }

  async function tryResolveNamedRef(
    repoUrl: string,
    fullRef: string,
    opts: { includePeeled?: boolean } = {},
  ): Promise<string | null> {
    const flags = opts.includePeeled
      ? "--quiet --exit-code"
      : "--quiet --refs --exit-code";
    const result = await reporter.run(
      { silent: true },
      `git ls-remote ${flags} ${shellQuote(repoUrl)} ${shellQuote(fullRef)}`,
    );
    if (result.code === 2) return null;
    if (result.code !== 0) {
      throw new Error(
        `git ls-remote failed for ${fullRef} (${result.code ?? "null"})`,
      );
    }
    const line = result.stdout.split("\n").map((l: string) => l.trim()).find(
      Boolean,
    );
    return line ? line.split(/\s+/)[0] : null;
  }

  async function resolveNamedRef(
    repoUrl: string,
    fullRef: string,
  ): Promise<string> {
    const sha = await tryResolveNamedRef(repoUrl, fullRef);
    if (!sha) throw new Error(`Remote ref not found: ${fullRef}`);
    return sha;
  }

  async function resolveTagRef(
    repoUrl: string,
    tagName: string,
  ): Promise<string> {
    const peeled = await tryResolveNamedRef(
      repoUrl,
      `refs/tags/${tagName}^{}`,
      { includePeeled: true },
    );
    if (peeled) return peeled;
    const direct = await tryResolveNamedRef(repoUrl, `refs/tags/${tagName}`);
    if (direct) return direct;
    throw new Error(`Remote tag not found: ${tagName}`);
  }

  async function resolveGitRef(
    repoUrl: string,
    requested?: RequestedGitRef,
  ): Promise<ResolvedGitRef> {
    if (!requested) {
      const result = await reporter.run(
        { silent: true },
        `git ls-remote --quiet --symref ${shellQuote(repoUrl)} HEAD`,
      );
      if (result.code !== 0) {
        throw new Error(
          `git ls-remote --symref failed (${result.code ?? "null"})`,
        );
      }
      const lines = result.stdout.split("\n").map((l: string) => l.trim())
        .filter(Boolean);
      const symref = lines.find((l: string) =>
        l.startsWith("ref:") && /\sHEAD$/.test(l)
      );
      const head = lines.find((l: string) => /^[0-9a-f]{40}\s+HEAD$/i.test(l));
      const match = symref?.match(/^ref:\s+(\S+)\s+HEAD$/);
      if (!match || !head) {
        throw new Error(
          `Unable to resolve remote default branch for ${repoUrl}`,
        );
      }
      const fullRef = match[1];
      if (!fullRef.startsWith("refs/heads/")) {
        throw new Error(`Remote HEAD did not resolve to a branch: ${fullRef}`);
      }
      return {
        type: "branch",
        name: fullRef.slice("refs/heads/".length),
        sha: head.split(/\s+/)[0],
      };
    }

    if (requested.type === "branch") {
      return {
        type: "branch",
        name: requested.name,
        sha: await resolveNamedRef(repoUrl, `refs/heads/${requested.name}`),
      };
    }

    if (requested.type === "tag") {
      return {
        type: "tag",
        name: requested.name,
        sha: await resolveTagRef(repoUrl, requested.name),
      };
    }

    return { type: "commit", sha: requested.sha };
  }

  /**
   * Initialize or clone a sparse-compatible git repo in the cache and configure the remote.
   */
  async function sparseInit(
    repoUrl: string,
    repoDir: string,
    ref: ResolvedGitRef,
  ): Promise<{ needsFetch: boolean; checkoutRevision: string }> {
    const gitDir = rt.join(repoDir, ".git");
    const gitConfig = rt.join(gitDir, "config");
    const repoDirExists = await rt.exists(repoDir);
    const hasGit = await rt.exists(gitDir);
    const isValid = hasGit && await rt.exists(gitConfig);

    if (!isValid) {
      if (!repoDirExists && ref.type === "branch") {
        reporter.startStage(
          "init",
          `cloning ${formatResolvedRef(ref)} into cache (no checkout)`,
        );
        await rt.mkdir(rt.dirname(repoDir), { recursive: true });
        const result = await reporter.run(
          {},
          `git clone --filter=blob:none --depth=1 --single-branch --branch ${
            shellQuote(ref.name)
          } --no-checkout ${shellQuote(repoUrl)} ${shellQuote(repoDir)}`,
        );
        reporter.finishStage({
          ok: result.code === 0,
          elapsed: result.elapsed,
          code: result.code,
        });
        if (result.code !== 0) {
          throw new Error(`git clone failed (${result.code ?? "null"})`);
        }
        return { needsFetch: false, checkoutRevision: "HEAD" };
      }

      if (hasGit) {
        reporter.startStage("init", "reinitializing broken cache repo");
        await rt.remove(gitDir, { recursive: true, force: true });
      } else {
        reporter.startStage(
          "init",
          repoDirExists ? "resetting stale cache dir" : "creating cache repo",
        );
        if (repoDirExists) {
          await rt.remove(repoDir, { recursive: true, force: true });
        }
      }
      await rt.mkdir(repoDir, { recursive: true });
      await reporter.execQuiet(["git", "init", "--initial-branch=main"], {
        cwd: repoDir,
      });
      reporter.finishStage({ ok: true, elapsed: 0 });
    }

    await reporter.execQuiet([
      "git",
      "config",
      "extensions.partialclone",
      "origin",
    ], { cwd: repoDir });
    await reporter.execQuiet([
      "git",
      "config",
      "core.partialclonefilter",
      "blob:none",
    ], { cwd: repoDir });
    await reporter.execQuiet(["git", "remote", "remove", "arbitrary"], {
      cwd: repoDir,
    }).catch(() => {});
    await reporter.execQuiet(["git", "remote", "remove", "origin"], {
      cwd: repoDir,
    }).catch(() => {});
    await reporter.execQuiet(["git", "remote", "add", "origin", repoUrl], {
      cwd: repoDir,
    });
    return { needsFetch: true, checkoutRevision: "FETCH_HEAD" };
  }

  /**
   * Fetch the resolved ref into FETCH_HEAD.
   */
  async function sparseFetch(
    repoDir: string,
    ref: ResolvedGitRef,
  ): Promise<string> {
    const command = ref.type === "branch"
      ? `git fetch --depth=1 --filter=blob:none origin ${shellQuote(ref.name)}`
      : ref.type === "tag"
      ? `git fetch --depth=1 --filter=blob:none origin tag ${
        shellQuote(ref.name)
      }`
      : `git fetch --depth=1 --filter=blob:none origin ${shellQuote(ref.sha)}`;
    const label = ref.type === "branch"
      ? `fetch origin/${ref.name}`
      : ref.type === "tag"
      ? `fetch tag/${ref.name}`
      : `fetch commit ${shortSha(ref.sha)}`;

    reporter.startStage("fetch", label);
    const result = await reporter.run({ cwd: repoDir }, command);
    reporter.finishStage({
      ok: result.code === 0,
      elapsed: result.elapsed,
      code: result.code,
    });
    if (result.code !== 0) {
      throw new Error(
        `git fetch failed for ${formatResolvedRef(ref)} (${
          result.code ?? "null"
        })`,
      );
    }
    return "FETCH_HEAD";
  }

  /**
   * Write exact gitignore-style include patterns via sparse-checkout (non-cone mode).
   * Patterns are written to a temp file inside .git and fed via shell redirect.
   */
  async function sparseSetPatterns(
    repoDir: string,
    patterns: string[],
  ): Promise<void> {
    const tmpName = "sparse-checkout-patterns.txt";
    const tmpPath = rt.join(repoDir, ".git", tmpName);
    await rt.writeTextFile(tmpPath, patterns.join("\n") + "\n");

    try {
      reporter.startStage("sparse", "apply sparse patterns");
      const result = await reporter.run(
        { cwd: repoDir },
        `git sparse-checkout set --no-cone --stdin < .git/${tmpName}`,
      );
      reporter.finishStage({
        ok: result.code === 0,
        elapsed: result.elapsed,
        code: result.code,
      });
      if (result.code !== 0) {
        throw new Error(
          `git sparse-checkout set failed (${result.code ?? "null"})`,
        );
      }
    } finally {
      await rt.remove(tmpPath, { force: true }).catch(() => {});
    }
  }

  /**
   * Update working tree to the requested revision after sparse rules are in place.
   */
  async function sparseCheckout(
    repoDir: string,
    revision: string,
  ): Promise<void> {
    reporter.startStage("checkout", `checkout ${revision}`);
    const result = await reporter.run(
      { cwd: repoDir },
      `git reset --hard ${shellQuote(revision)}`,
    );
    reporter.finishStage({
      ok: result.code === 0,
      elapsed: result.elapsed,
      code: result.code,
    });
    if (result.code !== 0) {
      const unsupportedReason = parseUnsupportedWindowsCheckout(result.stderr);
      if (unsupportedReason) {
        throw new UnsupportedRepoError(`on Windows (${unsupportedReason})`);
      }
      throw new Error(
        `git reset --hard failed for ${revision} (${result.code ?? "null"})`,
      );
    }
  }

  /** Remove stale export directories when no export should be created. */
  async function removeExportDirs(dirs: string[]): Promise<void> {
    for (const dir of dirs) {
      await rt.remove(dir, { recursive: true, force: true });
    }
  }

  /**
   * Export the currently materialized sparse tree into a clean mirror directory.
   */
  async function publishMirror(
    repoDir: string,
    exportDir: string,
    repoRelativePaths: string[],
    manifest: MirrorManifest,
  ): Promise<void> {
    const stageDir = stageDirFor(exportDir);
    const backupDir = `${exportDir}.__mirror_prev__`;
    await rt.remove(stageDir, { recursive: true, force: true });
    await rt.remove(backupDir, { recursive: true, force: true });
    await rt.mkdir(stageDir, { recursive: true });

    for (const relPath of repoRelativePaths) {
      const sourcePath = rt.join(repoDir, ...relPath.split("/"));
      const destPath = rt.join(stageDir, ...relPath.split("/"));
      try {
        await rt.copy(sourcePath, destPath);
      } catch (err) {
        if (isLikelyWindowsLongPathCopyError(err, destPath)) {
          throw new UnsupportedRepoError(
            `on Windows (path too long: ${relPath})`,
          );
        }
        throw err;
      }
    }

    await writeManifest(stageDir, manifest);

    if (await rt.exists(exportDir)) {
      await rt.move(exportDir, backupDir);
    }
    await rt.move(stageDir, exportDir);
    await rt.remove(backupDir, { recursive: true, force: true });
  }

  /**
   * Get the current commit SHA in the repo.
   * Handles detached HEAD state (what we use after fetch + reset).
   */
  async function getCurrentCommitSha(repoDir: string): Promise<string> {
    const result = await reporter.run(
      { cwd: repoDir, silent: true },
      "git rev-parse HEAD",
    );
    if (result.code !== 0) {
      throw new Error(`git rev-parse failed: ${result.code}`);
    }
    return result.stdout.trim();
  }

  /**
   * List files currently checked out via `git ls-files`.
   */
  async function listCheckedOutFiles(repoDir: string): Promise<string[]> {
    const tmpName = ".mirror-ls-files.txt";
    const tmpPath = rt.join(repoDir, ".git", tmpName);
    await reporter.run(
      { cwd: repoDir, silent: true },
      `git ls-files | tr -d $'\r' > .git/${tmpName}`,
    );
    const raw = await rt.readTextFile(tmpPath);
    await rt.remove(tmpPath, { force: true });
    return raw.split("\n").map((l: string) => l.trim()).filter(Boolean);
  }

  // ============================================================
  // GitHub API helpers
  // ============================================================

  function buildGithubHeaders(token?: string): Record<string, string> {
    const h: Record<string, string> = {
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    };
    if (token) h["Authorization"] = `Bearer ${token}`;
    return h;
  }

  /**
   * Search GitHub for repositories.
   */
  async function searchRepos(
    query: string,
    opts: { limit?: number; sort?: string; order?: string; token?: string } =
      {},
  ): Promise<GitHubRepo[]> {
    const limit = Math.min(opts.limit ?? 100, 1000);
    const sort = opts.sort ?? "stars";
    const order = opts.order ?? "desc";
    const token = opts.token ?? rt.getEnv("GH_TOKEN") ??
      rt.getEnv("GITHUB_TOKEN");
    const headers = buildGithubHeaders(token ?? undefined);
    const perPage = 100;
    const pages = Math.ceil(limit / perPage);
    const results: GitHubRepo[] = [];

    for (let page = 1; page <= pages; page++) {
      const fetched = await rt.fetchJson<{ items: GitHubRepo[] }>(
        `https://api.github.com/search/repositories?q=${
          encodeURIComponent(query)
        }&sort=${sort}&order=${order}&per_page=${perPage}&page=${page}`,
        { headers },
      );
      results.push(...fetched.items);
      if (fetched.items.length < perPage) break;
    }

    return results.slice(0, limit);
  }

  // ============================================================
  // Cache helpers
  // ============================================================

  async function readRepoState(
    cacheRoot: string,
    owner: string,
    name: string,
  ): Promise<RepoState | null> {
    const path = rt.join(cacheRoot, "state", owner, `${name}.json`);
    if (!(await rt.exists(path))) return null;
    try {
      return JSON.parse(await rt.readTextFile(path)) as RepoState;
    } catch {
      return null;
    }
  }

  async function writeRepoState(
    cacheRoot: string,
    owner: string,
    name: string,
    state: RepoState,
  ): Promise<void> {
    await rt.mkdir(rt.join(cacheRoot, "state", owner), { recursive: true });
    const path = rt.join(cacheRoot, "state", owner, `${name}.json`);
    await rt.writeTextFile(path, JSON.stringify(state, null, 2));
  }
  async function listKnownRepos(targetRoot: string): Promise<string[]> {
    const repos = new Set<string>();

    for (const entry of await rt.listDir(targetRoot)) {
      const match = /^([^@]+)@([^@]+)$/.exec(entry);
      if (!match) continue;

      const manifestPath = rt.join(targetRoot, entry, "MIRROR-MANIFEST.md");
      if (!(await rt.exists(manifestPath))) continue;

      repos.add(`${match[1]}/${match[2]}`);
    }

    return [...repos].sort((a, b) => a.localeCompare(b));
  }

  // ============================================================
  // Manifest
  // ============================================================
  /**
   * Write the mirror manifest as a readable markdown file.
   */
  async function writeManifest(
    targetDir: string,
    manifest: MirrorManifest,
  ): Promise<void> {
    const manifestName = "MIRROR-MANIFEST.md";
    const { fileIndex, sparsePatterns } = manifest;

    const sorted = [...fileIndex].sort((a, b) => {
      if (a.default && !b.default) return -1;
      if (!a.default && b.default) return 1;
      return a.path.localeCompare(b.path);
    });

    const pathRows = sorted.length === 0
      ? "_No files materialized._"
      : sorted.map((entry, i) => {
        const status = entry.default ? "✓" : "→";
        const p = entry.path;
        const url = p.replace(/ /g, "%20");
        const display = `\`${p}\``;
        return `| ${i + 1} | ${status} | [${display}](${url}) |`;
      }).join("\n");

    const defaultRows = sparsePatterns.defaults.length === 0
      ? "_None._"
      : sparsePatterns.defaults.map((p) => `- \`${p}\``).join("\n");

    const followedRows = sparsePatterns.followed.length === 0
      ? "_None._"
      : sparsePatterns.followed.map((p) => `- \`${p}\``).join("\n");

    const body = [
      "---",
      `repo: ${manifest.repo}`,
      `repoUrl: ${manifest.repoUrl}`,
      `refType: ${manifest.refType}`,
      `ref: ${manifest.ref}`,
      "---",
      "",
      "# Mirror Manifest",
      "",
      `Mirror of \`${manifest.repo}\` — ${sparsePatterns.defaults.length} default patterns, ${sparsePatterns.followed.length} followed patterns, ${fileIndex.length} file(s) materialized.`,
      "",
      "## Metadata",
      "",
      "| Field         | Value |",
      "|---------------|-------|",
      `| Repo          | \`${manifest.repo}\` |`,
      `| Ref Type      | \`${manifest.refType}\` |`,
      `| Ref           | \`${manifest.ref}\` |`,
      `| Default pats  | ${sparsePatterns.defaults.length} |`,
      `| Followed pats | ${sparsePatterns.followed.length} |`,
      `| Files         | ${fileIndex.length} |`,
      "",
      "## Default Sparse Patterns  *(included from config)*",
      "",
      defaultRows,
      "",
      "## Followed Sparse Patterns  *(discovered via markdown refs)*",
      "",
      followedRows,
      "",
      "## File Index",
      "",
      "Legend: **✓** = default pattern · **→** = followed via markdown",
      "",
      "| # | S | File |",
      "|---|---|------|",
      pathRows,
      "",
      "---",
      "",
      "*Generated by mirror — do not edit manually*",
    ].join("\n");

    await rt.writeTextFile(rt.join(targetDir, manifestName), body);
  }

  // ============================================================
  // Local file helpers
  // ============================================================

  /**
   * Read multiple markdown files from the local sparse checkout.
   */
  async function readLocalMarkdownFiles(
    targetDir: string,
    repoRelativePaths: string[],
  ): Promise<Map<string, string>> {
    const result = new Map<string, string>();
    for (const relPath of repoRelativePaths) {
      const abs = rt.join(targetDir, ...relPath.split("/"));
      if (await rt.exists(abs)) {
        try {
          result.set(relPath, await rt.readTextFile(abs));
        } catch {
          // Binary or unreadable — skip
        }
      }
    }
    return result;
  }

  /**
   * List files that physically exist on disk after sparse checkout.
   */
  async function filterToDiskFiles(targetDir: string): Promise<string[]> {
    // tr -d $'\r' strips carriage returns emitted by git on Windows (core.autocrlf).
    const result = await reporter.run(
      { cwd: targetDir, silent: true },
      `git ls-files | tr -d $'\r' | while IFS= read -r f; do if [ -f "$f" ]; then echo "$f"; fi; done`,
    );
    if (result.code !== 0) {
      throw new Error(`git ls-files failed (${result.code ?? "null"})`);
    }
    return result.stdout.split("\n").map((l: string) => l.trim()).filter(
      Boolean,
    );
  }

  /** Filter a list of repo-relative paths to only those that exist on disk. */
  async function filterExistingPaths(
    targetDir: string,
    repoRelativePaths: string[],
  ): Promise<string[]> {
    const existing: string[] = [];
    for (const relPath of repoRelativePaths) {
      if (await rt.exists(rt.join(targetDir, ...relPath.split("/")))) {
        existing.push(relPath);
      }
    }
    return existing;
  }

  // ============================================================
  // Pure helpers
  // ============================================================

  /**
   * Extract local markdown file references from markdown content.
   */
  function extractMarkdownRefs(text: string): string[] {
    const refs: string[] = [];
    const linkRe = /\[([^\]]*)\](?:\(([^)]+)\)|\[([^\]]+)\])/g;
    let m: RegExpExecArray | null;
    while ((m = linkRe.exec(text)) !== null) {
      const url = (m[2] || m[3] || "").trim();
      if (
        !url || url.startsWith("#") || url.startsWith("mailto:") ||
        /^https?:\/\//i.test(url)
      ) {
        continue;
      }
      refs.push(url);
    }
    return refs;
  }

  function computeConfigHash(spec: {
    sparse: { include: string[] };
    follow?: unknown;
    ref?: unknown;
    [key: string]: unknown;
  }): string {
    return hashCacheKey(JSON.stringify({
      include: [...spec.sparse.include].sort(),
      follow: spec.follow,
      ref: spec.ref ?? { type: "default" },
    }));
  }

  // ============================================================
  // Return the complete tasks object
  // ============================================================

  return {
    repoExists,
    exportDirReady,
    resolveGitRef,
    sparseInit,
    sparseFetch,
    sparseSetPatterns,
    sparseCheckout,
    removeExportDirs,
    publishMirror,
    getCurrentCommitSha,
    listCheckedOutFiles,
    searchRepos,
    buildGithubHeaders,
    readRepoState,
    writeRepoState,
    listKnownRepos,
    writeManifest,
    readLocalMarkdownFiles,
    filterToDiskFiles,
    filterExistingPaths,
    extractMarkdownRefs,
    computeConfigHash,
  };
}

// ============================================================
// Pure utilities (no runtime dependency)
// ============================================================

/** FNV-1a 48-bit hash → lowercase hex string. */
function hashCacheKey(input: string): string {
  let hash = 0xcbf29ce484222325n;
  for (let i = 0; i < input.length; i++) {
    hash ^= BigInt(input.charCodeAt(i));
    hash = (hash * 0x100000001b3n) & 0xffffffffffffffffn;
  }
  return (hash >> 16n).toString(16);
}
