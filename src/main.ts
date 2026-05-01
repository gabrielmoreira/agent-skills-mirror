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
// - one for the "claw" family of openclaw forks
// - one for repos named "agent-skills" or "agent-skill" in their name
// - one for repos mentioning both "claude" and "skills"
// - one for GitHub topic-based discovery
// - one for copilot/plugin instruction repos
//
// Notes:
// - pushed: helps avoid dead repos
// - stars threshold varies by intent
// - fork:false + archived:false removes noise

const REAL_SEARCH_QUERIES = [
  // 1) broad/high-signal AI tooling baseline
  "(opencode OR omp OR qwen OR llama OR chatglm OR minimax) stars:>40 pushed:>2024-01-01 fork:false archived:false",

  // 2) agent frameworks / agent runtimes
  "(coding agent OR agent framework OR opencode OR pi-agent) stars:>25 pushed:>2024-01-01 fork:false archived:false",

  // 3) coding assistants / developer-focused AI tools
  "(coding assistant OR copilot OR codex OR claude OR gemini) stars:>20 pushed:>2024-01-01 fork:false archived:false",

  // 4) MCP / tool ecosystems
  "mcp stars:>10 pushed:>2024-01-01 fork:false archived:false",

  // 5) prompt / skills / instruction-oriented repos
  "skills prompts stars:>10 pushed:>2024-01-01 fork:false archived:false",

  // 6) claw
  "claw stars:>10 pushed:>2024-01-01 fork:false archived:false",

  // 7) repos named "agent-skills" or "agent-skill" — catches the
  //    large ecosystem of per-project agent skill collections.
  //    Low star threshold because many are legitimate but new.
  "agent-skills in:name stars:>1 pushed:>2024-01-01 fork:false archived:false",

  // 8) repos that explicitly mention both "claude" and "skills" —
  //    catches claude-skills, claude code skill collections, etc.
  "claude skills stars:>3 pushed:>2024-01-01 fork:false archived:false",

  // 9) GitHub topic-based discovery for the main ecosystems.
  //    Topics are curated by repo owners, so signal-to-noise is high.
  "topic:claude-code OR topic:agent-skills OR topic:copilot-skills fork:false archived:false",

  // 10) instruction/plugin-style repos — copilot instructions,
  //     claude plugins, ai-tools, and similar patterns that don't
  //     use the word "skills" but serve the same purpose.
  "\"copilot instructions\" OR \"claude plugins\" OR \"ai-tools\" stars:>5 pushed:>2024-01-01 fork:false archived:false",
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
