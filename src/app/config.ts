/**
 * src/app/config.ts — Default mirror configuration.
 */

import type { MirrorConfig } from "./mirror.ts";
import { GLOBAL_FOLLOW } from "./mirror.ts";

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
] as const;

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
] as const;

// GitHub search allows max 5 boolean operators per query.
// Keep queries focused by intent, instead of trying to make one giant query.
export const REAL_SEARCH_QUERIES = [
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

  // 9) GitHub topic-based discovery must stay split per topic.
  //    GitHub search boolean operators apply to text terms, not qualifiers.
  "topic:claude-code fork:false archived:false",
  "topic:agent-skills fork:false archived:false",
  "topic:copilot-skills fork:false archived:false",

  // 10) instruction/plugin-style repos — copilot instructions,
  //     claude plugins, ai-tools, and similar patterns that don't
  //     use the word "skills" but serve the same purpose.
  '"copilot instructions" OR "claude plugins" OR "ai-tools" stars:>5 pushed:>2024-01-01 fork:false archived:false',
] as const;

export function makeDefaultMirrorConfig(): MirrorConfig {
  return {
    vars: {
      targetRoot: "mirrors/repos",
      cacheRoot: "cache",
    },
    cache: {
      materialization: { mode: "reuse-if-current" },
    },
    sources: [
      {
        queries: [...REAL_SEARCH_QUERIES],
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
}
