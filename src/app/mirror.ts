/**
 * app/mirror.ts — Types + orchestration.
 *
 * Layer contract:
 *   mirror.ts  →  pure decision logic + repo-level orchestration.
 *   tasks.ts   →  all runtime-facing operational helpers.
 */

import {
  isAVInterferenceError,
  makeTasks,
  UnsupportedRepoError,
} from "./tasks.ts";
import type {
  ManifestFileEntry,
  MirrorTasks,
  RequestedGitRef,
  ResolvedGitRef,
} from "./tasks.ts";
import { makeReporter, type Reporter } from "../support/output.ts";
import type { RuntimeAdapter } from "../support/runtime.ts";
import { processJobs } from "../support/pool.ts";
import { LiveDashboard } from "../support/dashboard.ts";
import { makeRepoSink } from "../support/sink.ts";

// ============================================================
// Global follow config
// ============================================================

export const GLOBAL_FOLLOW: FollowConfig = {
  includeExtensions: [".md"],
  linkedFromMarkdown: true,
};

// ============================================================
// Public types
// ============================================================

export type MirrorVars = {
  targetRoot?: string;
  repoUrlFormat?: string;
  targetDirFormat?: string;
  token?: string;
  cacheRoot?: string;
  [key: string]: string | undefined;
};

export type MirrorSource =
  | {
    vars?: MirrorVars;
    repo?: string;
    repos?: string[];
    mirror: MirrorSpec;
  }
  | {
    vars?: MirrorVars;
    query?: string;
    queries?: string[];
    limit?: number;
    sort?: "stars" | "updated";
    order?: "asc" | "desc";
    mirror: MirrorSpec;
  };

export type MirrorSpec = {
  sparse: { include: string[] };
  follow?: boolean | FollowConfig | false;
  targetDir?: string;
  ref?: RequestedGitRef;
};

export type FollowConfig = {
  includeExtensions?: string[];
  linkedFromMarkdown?: boolean;
};

export type MirrorConfig = {
  vars?: MirrorVars;
  cache?: MirrorCacheConfig;
  sources: MirrorSource[];
};

export type MirrorCacheConfig = {
  materialization?: { mode?: "reuse-if-current" | "always-refresh" };
};

// ============================================================
// Public entry point
// ============================================================

export function makeStartMirror(opts: {
  runtime: RuntimeAdapter;
  globalReporter: Reporter;
  globalTasks: MirrorTasks;
  repoConcurrency?: number;
}) {
  return async function startMirror(
    optsArg: { config: MirrorConfig },
  ): Promise<void> {
    const { config } = optsArg;
    const normalized = normalizeConfig(config);
    const jobs = await expandSources(
      normalized,
      opts.globalTasks,
      opts.globalReporter,
    );
    const repoConcurrency = Math.max(1, opts.repoConcurrency ?? 6);
    const dashboard = new LiveDashboard(
      opts.runtime,
      repoConcurrency,
      jobs.length,
    );
    const failures: { repo: string; error: string }[] = [];

    await processJobs(
      jobs,
      async (job, slot) => {
        const repoKey = `${job.owner}/${job.name}`;
        dashboard.startSlot(slot, repoKey);

        const reporter = makeReporter(
          opts.runtime,
          makeRepoSink(dashboard, slot),
        );
        const tasks = makeTasks(opts.runtime, reporter);

        try {
          await processRepoJob(job, tasks, reporter);
        } catch (err) {
          failures.push({
            repo: repoKey,
            error: err instanceof Error ? err.message : String(err),
          });
        }
      },
      { concurrency: repoConcurrency },
    );

    dashboard.finish(failures);
  };
}

// ============================================================
// Config normalization
// ============================================================

type NormalizedConfig = {
  vars:
    & RequiredKeys<
      MirrorVars,
      "targetRoot" | "repoUrlFormat" | "targetDirFormat" | "cacheRoot"
    >
    & Omit<
      MirrorVars,
      "targetRoot" | "repoUrlFormat" | "targetDirFormat" | "cacheRoot"
    >;
  cache:
    & RequiredKeys<MirrorCacheConfig, "materialization">
    & Omit<MirrorCacheConfig, "materialization">;
  sources: MirrorSource[];
};

type RequiredKeys<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>;

function normalizeConfig(config: MirrorConfig): NormalizedConfig {
  const gv = config.vars ?? {};
  return {
    vars: {
      targetRoot: gv.targetRoot ?? "mirrors",
      repoUrlFormat: gv.repoUrlFormat ??
        "https://github.com/{owner}/{name}.git",
      targetDirFormat: gv.targetDirFormat ?? "{targetRoot}/{owner}@{name}",
      cacheRoot: gv.cacheRoot ?? "cache",
      ...gv,
    },
    cache: {
      materialization: config.cache?.materialization ??
        { mode: "reuse-if-current" },
    },
    sources: config.sources,
  };
}

// ============================================================
// Source expansion
// ============================================================

type ResolvedRepoJob = {
  owner: string;
  name: string;
  repoUrl: string;
  cacheRepoDir: string;
  targetDir: string;
  vars: MirrorVars;
  mirror: MirrorSpec;
  sourceIndex: number;
};

async function expandSources(
  config: NormalizedConfig,
  tasks: MirrorTasks,
  reporter: Reporter,
): Promise<ResolvedRepoJob[]> {
  const jobs: ResolvedRepoJob[] = [];
  const seen = new Set<string>();

  for (let si = 0; si < config.sources.length; si++) {
    const source = config.sources[si];
    const mergedVars: MirrorVars = { ...config.vars, ...source.vars };

    if (isStaticSource(source)) {
      const repoList = source.repo ? [source.repo] : (source.repos ?? []);
      for (const repo of repoList) {
        if (seen.has(repo)) continue;
        seen.add(repo);
        jobs.push(resolveRepoJob(repo, mergedVars, source.mirror, si));
      }
    } else if (isDynamicSource(source)) {
      const queries = source.query ? [source.query] : (source.queries ?? []);
      const limit = source.limit ?? 100;
      reporter.startStage("search", `GitHub search (limit=${limit})`);
      const startedAt = Date.now();
      try {
        for (const q of queries) {
          reporter.info(`query: ${q}`);
          const repos = await tasks.searchRepos(q, {
            limit,
            sort: source.sort ?? "stars",
            order: source.order ?? "desc",
          });
          for (const repoInfo of repos) {
            const key = `${repoInfo.owner.login}/${repoInfo.name}`;
            if (seen.has(key)) continue;
            seen.add(key);
            jobs.push(resolveRepoJob(key, mergedVars, source.mirror, si));
          }
        }
        reporter.finishStage({ ok: true, elapsed: Date.now() - startedAt });
      } catch (err) {
        reporter.finishStage({
          ok: false,
          elapsed: Date.now() - startedAt,
          error: err instanceof Error ? err.message : String(err),
        });
        throw err;
      }
    }
  }

  return jobs;
}

function isStaticSource(
  s: MirrorSource,
): s is MirrorSource & { repo?: string; repos?: string[] } {
  return "repo" in s || "repos" in s;
}

function isDynamicSource(
  s: MirrorSource,
): s is MirrorSource & { query?: string; queries?: string[] } {
  return "query" in s || "queries" in s;
}

function resolveRepoJob(
  repo: string,
  vars: MirrorVars,
  mirror: MirrorSpec,
  sourceIndex: number,
): ResolvedRepoJob {
  const parts = repo.split("/");
  if (parts.length !== 2 || !parts[0] || !parts[1]) {
    throw new Error(`Invalid repo "${repo}" — expected "owner/name".`);
  }
  const [owner, name] = parts;
  const repoUrl = interpolate(vars.repoUrlFormat!, { owner, name, ...vars });
  const host = extractRepoHost(repoUrl);
  const cacheRepoDir = interpolate("{cacheRoot}/repos/{host}/{owner}@{name}", {
    ...vars,
    cacheRoot: vars.cacheRoot,
    host,
    owner,
    name,
  });
  const targetDir = interpolate(mirror.targetDir ?? vars.targetDirFormat!, {
    owner,
    name,
    ...vars,
  });
  return {
    owner,
    name,
    repoUrl,
    cacheRepoDir,
    targetDir,
    vars,
    mirror,
    sourceIndex,
  };
}

function extractRepoHost(repoUrl: string): string {
  try {
    return new URL(repoUrl).hostname;
  } catch {
    const ssh = repoUrl.match(/^[^@]+@([^:]+):/);
    if (ssh?.[1]) return ssh[1];
    throw new Error(`Unable to extract host from repo URL: ${repoUrl}`);
  }
}

function interpolate(
  template: string,
  vars: Record<string, string | undefined>,
): string {
  return template.replace(/\{(\w+)\}/g, (_, key) => vars[key] ?? `{${key}}`);
}

// ============================================================
// Follow config resolution
// ============================================================

function resolveFollowConfig(
  v: boolean | FollowConfig | false | undefined,
): FollowConfig | null {
  if (v === false || v === undefined) return null;
  if (v === true) return { ...GLOBAL_FOLLOW };
  return { ...v };
}

// ============================================================
// Per-repo processing
// ============================================================

async function processRepoJob(
  job: ResolvedRepoJob,
  tasks: MirrorTasks,
  reporter: Reporter,
): Promise<void> {
  const { owner, name, repoUrl, cacheRepoDir, targetDir, mirror, vars: eff } =
    job;
  const repoKey = `${owner}/${name}`;
  const followCfg = resolveFollowConfig(mirror.follow);
  const requestedRef = mirror.ref;
  const configHash = tasks.computeConfigHash({
    sparse: mirror.sparse,
    follow: followCfg,
    ref: requestedRef ?? { type: "default" },
  });
  let repoFinished = false;
  let resolvedRef: ResolvedGitRef | null = null;

  try {
    resolvedRef = await tasks.resolveGitRef(repoUrl, requestedRef);
    const priorState = await tasks.readRepoState(
      eff.cacheRoot ?? "cache",
      owner,
      name,
    );

    const [cacheRepoReady, targetExportReady] = await Promise.all([
      tasks.repoExists(cacheRepoDir),
      tasks.exportDirReady(targetDir),
    ]);
    const expectedOutput = priorState?.output;
    const isIntentionallyEmpty = expectedOutput === "no-matches" &&
      !targetExportReady;
    const isIntentionallyUnsupported = expectedOutput === "unsupported" &&
      !targetExportReady;

    if (
      priorState &&
      expectedOutput &&
      priorState.commit === resolvedRef.sha &&
      priorState.configHash === configHash &&
      cacheRepoReady &&
      (targetExportReady || isIntentionallyEmpty || isIntentionallyUnsupported)
    ) {
      reporter.finishRepo({
        repo: repoKey,
        files: 0,
        followed: 0,
        unsupported: isIntentionallyUnsupported
          ? "on Windows (invalid path in repository)"
          : undefined,
        skipped: !isIntentionallyUnsupported,
      });
      repoFinished = true;
      return;
    }

    const initResult = await tasks.sparseInit(
      repoUrl,
      cacheRepoDir,
      resolvedRef,
    );
    let checkoutRevision = initResult.checkoutRevision;
    if (initResult.needsFetch) {
      checkoutRevision = await tasks.sparseFetch(cacheRepoDir, resolvedRef);
    }

    const defaultPatterns = mirror.sparse.include;
    await tasks.sparseSetPatterns(cacheRepoDir, defaultPatterns);
    await tasks.sparseCheckout(cacheRepoDir, checkoutRevision);

    const currentSha = await tasks.getCurrentCommitSha(cacheRepoDir);

    let followedPatterns: string[] = [];
    if (followCfg?.linkedFromMarkdown) {
      const startedAt = Date.now();
      reporter.startStage("follow", "markdown refs");
      try {
        followedPatterns = await followMarkdownRefs(
          cacheRepoDir,
          followCfg,
          tasks,
          defaultPatterns,
          checkoutRevision,
        );
        reporter.finishStage({
          ok: true,
          elapsed: Date.now() - startedAt,
          detail: followedPatterns.length > 0
            ? `discovered ${followedPatterns.length} path(s) via markdown links`
            : "no additional markdown refs",
        });
      } catch (err) {
        reporter.finishStage({
          ok: false,
          elapsed: Date.now() - startedAt,
          error: err instanceof Error ? err.message : String(err),
        });
        throw err;
      }
    }

    const allPatterns = [...defaultPatterns, ...followedPatterns];
    const allPatternSet = new Set(allPatterns);
    if (
      followedPatterns.length > 0 && allPatternSet.size > defaultPatterns.length
    ) {
      await tasks.sparseSetPatterns(cacheRepoDir, [...allPatternSet]);
      await tasks.sparseCheckout(cacheRepoDir, checkoutRevision);
    }

    const filesOnDisk = await tasks.filterToDiskFiles(cacheRepoDir);
    const filesSet = new Set(filesOnDisk);
    const followedOnDisk = followedPatterns.filter((p) => filesSet.has(p));

    if (filesOnDisk.length === 0) {
      await tasks.removeExportDirs([targetDir]);
      const now = new Date().toISOString();
      await tasks.writeRepoState(eff.cacheRoot ?? "cache", owner, name, {
        commit: currentSha,
        configHash,
        mirroredAt: now,
        output: "no-matches",
      });
      reporter.finishRepo({ repo: repoKey, files: 0, followed: 0 });
      repoFinished = true;
      return;
    }

    const followedSet = new Set(followedOnDisk);
    const fileIndex: ManifestFileEntry[] = filesOnDisk.map((path: string) => {
      if (followedSet.has(path)) return { path, followed: true };
      return { path, default: true };
    });

    const manifest = buildManifest(
      owner,
      name,
      repoUrl,
      resolvedRef,
      {
        defaults: defaultPatterns,
        followed: followedOnDisk,
      },
      fileIndex,
    );
    await tasks.publishMirror(cacheRepoDir, targetDir, filesOnDisk, manifest);
    await tasks.writeRepoState(eff.cacheRoot ?? "cache", owner, name, {
      commit: currentSha,
      configHash,
      mirroredAt: new Date().toISOString(),
      output: "matched",
    });

    reporter.finishRepo({
      repo: repoKey,
      files: filesOnDisk.length,
      followed: followedOnDisk.length,
    });
    repoFinished = true;
  } catch (err) {
    if (!repoFinished) {
      if (err instanceof UnsupportedRepoError) {
        await tasks.removeExportDirs([targetDir]);
        const now = new Date().toISOString();
        await tasks.writeRepoState(eff.cacheRoot ?? "cache", owner, name, {
          commit: resolvedRef?.sha ?? "unknown",
          configHash,
          mirroredAt: now,
          output: "unsupported",
        });
        reporter.finishRepo({
          repo: repoKey,
          files: 0,
          followed: 0,
          unsupported: err.message,
        });
        repoFinished = true;
        return;
      }

      if (isAVInterferenceError(err)) {
        // Staging dir may be partially populated — clean it up.
        // The suffix '.__mirror_tmp__' mirrors the stageDirFor convention in tasks.ts.
        await tasks.removeExportDirs([targetDir + ".__mirror_tmp__"]);
        // Do NOT write state: this is a transient platform event, not a repo fault.
        // The next run will retry; the user should add an AV exclusion for the cache dir.
        reporter.finishRepo({
          repo: repoKey,
          files: 0,
          followed: 0,
          error: `platform interference (possible antivirus quarantine): ${
            (err as Error).message
          }`,
        });
        repoFinished = true;
        throw err;
      }

      const message = err instanceof Error ? err.message : String(err);
      reporter.finishRepo({
        repo: repoKey,
        files: 0,
        followed: 0,
        error: message,
      });
      repoFinished = true;
    }
    throw err;
  }
}

// ============================================================
// Follow markdown refs
// ============================================================

async function followMarkdownRefs(
  targetDir: string,
  cfg: FollowConfig,
  tasks: MirrorTasks,
  seedPatterns: string[],
  checkoutRevision: string,
): Promise<string[]> {
  const exts = cfg.includeExtensions ?? [".md"];
  const isMd = (p: string) => exts.some((e: string) => p.endsWith(e));
  const normalize = (p: string) =>
    p.replace(/^\.[/\\]/, "").replace(/\\/g, "/");

  const discovered = new Set<string>();
  const read = new Set<string>();

  const allFiles = await tasks.filterToDiskFiles(targetDir);
  let candidates = allFiles.filter(isMd);

  while (candidates.length > 0) {
    for (const p of candidates) read.add(p);

    const content = await tasks.readLocalMarkdownFiles(targetDir, candidates);
    const newRefs: string[] = [];

    for (const [, text] of content) {
      for (const ref of tasks.extractMarkdownRefs(text)) {
        newRefs.push(normalize(ref));
      }
    }

    const newMd = newRefs.filter(isMd).filter((p) =>
      !read.has(p) && !discovered.has(p)
    );
    if (newMd.length === 0) break;

    for (const p of newMd) discovered.add(p);
    await tasks.sparseSetPatterns(targetDir, [...seedPatterns, ...discovered]);
    await tasks.sparseCheckout(targetDir, checkoutRevision);
    candidates = (await tasks.filterExistingPaths(targetDir, newMd)).filter(
      isMd,
    );
  }

  return [...discovered];
}

// ============================================================
// Manifest builder
// ============================================================

function buildManifest(
  owner: string,
  name: string,
  repoUrl: string,
  resolvedRef: ResolvedGitRef,
  sparsePatterns: { defaults: string[]; followed: string[] },
  fileIndex: ManifestFileEntry[],
) {
  return {
    repo: `${owner}/${name}`,
    repoUrl,
    refType: resolvedRef.type,
    ref: resolvedRef.type === "commit" ? resolvedRef.sha : resolvedRef.name,
    sparsePatterns,
    fileIndex,
  };
}
