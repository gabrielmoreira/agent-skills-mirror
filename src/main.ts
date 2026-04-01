/**
 * src/main.ts — Mirror config + bootstrap.
 *
 * Usage:
 *   deno run -A src/main.ts
 *
 * Or with a GitHub token:
 *   GH_TOKEN=$(gh auth token) deno run -A src/main.ts
 */

import { bootstrap } from "./bootstrap.ts";
import type { MirrorConfig } from "./app/mirror.ts";
import { GLOBAL_FOLLOW } from "./app/mirror.ts";

// ─── Global sparse patterns ────────────────────────────────────────────────────

const GLOBAL_SPARSE_PATTERNS = [
  "**/AGENTS.md",
  "**/CLAUDE.md",
  "**/claude.md",
  "**/gemini.md",
  "**/GEMINI.md",
  "**/SKILL.md",
  "**/skills.md",
  "**/LLMs.txt",
  "**/llms.txt",
  "**/copilot-instructions.md",
  "**/.cursorrules",
  "**/.cursor/rules/**",
  "**/.windsurfrules",
  "**/.continue/**",
];

const COMMON_SKILL_FOLDERS_PATTERNS = [
  ".github/instructions/**",
  ".github/prompts/**",
  ".agents/**",
  "agents/**",
  "skills/**",
  "skill/**",
  "prompts/**",
  "prompt/**",
  ".cursor/**",
  ".continue/**",
  ".mcp/**",
  "mcp/**",
];

// ─── Search queries ────────────────────────────────────────────────────────────
// GitHub search allows max 5 boolean operators per query.
// Keep queries focused by intent, instead of trying to make one giant query.
//
// Strategy:
// - one broad/high-signal query for generally popular repos
// - one for agent frameworks / agent runtimes
// - one for coding assistants / dev tools
// - one for MCP / tool integration ecosystems
// - one for prompt / skills / instruction-heavy repos
//
// Notes:
// - pushed: helps avoid dead repos
// - stars threshold varies by intent
// - fork:false + archived:false removes noise

const REAL_SEARCH_QUERIES = [
  // 1) broad/high-signal AI tooling baseline
  "(opencode OR cline OR qwen OR llama OR chatglm OR minimax) stars:>40 pushed:>2024-01-01 fork:false archived:false",

  // 2) agent frameworks / agent runtimes
  "(coding agent OR agent framework OR opencode OR cline) stars:>25 pushed:>2024-01-01 fork:false archived:false",

  // 3) coding assistants / developer-focused AI tools
  "(coding assistant OR copilot OR codex OR claude OR gemini) stars:>20 pushed:>2024-01-01 fork:false archived:false",

  // 4) MCP / tool ecosystems
  "mcp stars:>10 pushed:>2024-01-01 fork:false archived:false",

  // 5) prompt / skills / instruction-oriented repos
  "skills prompts stars:>10 pushed:>2024-01-01 fork:false archived:false",
];

const config = {
  vars: {
    targetRoot: "mirrors/repos",
    cacheRoot: "cache",
  },

  cache: {
    materialization: { mode: "reuse-if-current" },
  },

  sources: [
    {
      queries: REAL_SEARCH_QUERIES,
      // Per query. Cross-query dedup should happen after merge.
      limit: 150,
      sort: "stars",
      order: "desc",
      mirror: {
        sparse: {
          include: [
            ...GLOBAL_SPARSE_PATTERNS,
            ...COMMON_SKILL_FOLDERS_PATTERNS,
          ],
        },
        follow: GLOBAL_FOLLOW,
      },
    },
  ],
} satisfies MirrorConfig;

// ─── Bootstrap ───────────────────────────────────────────────────────────────

const { getEnv, start, reporter } = bootstrap({ fetchCacheTtl: 3_600_000 });

const token = getEnv("GH_TOKEN") ?? getEnv("GITHUB_TOKEN");
if (!token) {
  reporter.warn(
    "GH_TOKEN / GITHUB_TOKEN not set. GitHub search will be unauthenticated and rate-limited.",
  );
}

// ─── Run ─────────────────────────────────────────────────────────────────────

await start({ config });
