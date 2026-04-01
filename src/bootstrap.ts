import {
  createDefaultRuntimeAdapter,
  defaultCacheConfigFactory,
  makeCachedRuntime,
} from "./support/runtime.ts";
import { makeReporter, type Reporter } from "./support/output.ts";
import { makeGlobalSink } from "./support/sink.ts";
import { makeStartMirror } from "./app/mirror.ts";
import { makeTasks } from "./app/tasks.ts";

export type BootstrapOptions = {
  /** TTL for HTTP response cache (fetchJson / fetchText), in ms. Default: 1 hour. */
  fetchCacheTtl?: number;
  /** Directory for runtime HTTP cache files. Default: 'cache/runtime/'. */
  fetchCacheDir?: string;
};

export type Bootstrap = {
  runtime: ReturnType<typeof makeCachedRuntime>;
  tasks: ReturnType<typeof makeTasks>;
  start: ReturnType<typeof makeStartMirror>;
  reporter: Reporter;
  getEnv: (key: string, defaultValue?: string) => string | undefined;
};

const DEFAULT_REPO_CONCURRENCY = 8;

export function bootstrap(opts: BootstrapOptions = {}): Bootstrap {
  const runtime = createDefaultRuntimeAdapter();
  const cachedRuntime = makeCachedRuntime(
    runtime,
    opts.fetchCacheDir ?? "cache/runtime/",
    defaultCacheConfigFactory({ ttl: opts.fetchCacheTtl ?? 3_600_000 }),
  );

  const reporter = makeReporter(cachedRuntime, makeGlobalSink(cachedRuntime));
  const tasks = makeTasks(cachedRuntime, reporter);
  const rawConcurrency = cachedRuntime.getEnv(
    "MIRROR_CONCURRENCY",
    String(DEFAULT_REPO_CONCURRENCY),
  );
  const parsedConcurrency = Number.parseInt(rawConcurrency, 10);
  const repoConcurrency =
    Number.isFinite(parsedConcurrency) && parsedConcurrency > 0
      ? parsedConcurrency
      : DEFAULT_REPO_CONCURRENCY;
  const start = makeStartMirror({
    runtime: cachedRuntime,
    globalReporter: reporter,
    globalTasks: tasks,
    repoConcurrency,
  });

  return {
    runtime: cachedRuntime,
    tasks,
    start,
    reporter,
    getEnv: (key, defaultValue) =>
      defaultValue === undefined
        ? cachedRuntime.getEnv(key)
        : cachedRuntime.getEnv(key, defaultValue),
  };
}
