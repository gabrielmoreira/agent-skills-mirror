/**
 * src/main.ts — Mirror bootstrap entrypoint.
 *
 * Usage:
 *   deno run -A src/main.ts
 *
 * Or with a GitHub token:
 *   GH_TOKEN=$(gh auth token) deno run -A src/main.ts
 */

import { makeDefaultMirrorConfig } from "./app/config.ts";
import { bootstrap } from "./bootstrap.ts";

const { getEnv, start, reporter } = bootstrap({ fetchCacheTtl: 3_600_000 });
const token = getEnv("GH_TOKEN") ?? getEnv("GITHUB_TOKEN");

if (!token) {
  reporter.warn(
    "GH_TOKEN / GITHUB_TOKEN not set. GitHub search will be unauthenticated and rate-limited.",
  );
}

await start({ config: makeDefaultMirrorConfig() });
