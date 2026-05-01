/**
 * src/eval-coverage.test.ts — Coverage evaluation for GitHub search queries.
 *
 * This file serves two purposes:
 *   1. A regression test ensuring the query set meets structural constraints
 *      (boolean-operator limit, no static owner/repo hardcoding, etc.).
 *   2. A coverage report comparing the set of currently mirrored repositories
 *      against a reference target list of known high-signal repositories.
 *
 * Run with:
 *   deno test src/eval-coverage.test.ts
 *   deno task test
 */

import { assertEquals, assertLess, assert } from "jsr:@std/assert";
import { join } from "node:path";
import { REAL_SEARCH_QUERIES } from "./app/config.ts";

// ─── Reference target list ───────────────────────────────────────────────────
// These are known high-signal repositories that the queries should discover.
// Non-GitHub sources (docs.stripe.com, open.feishu.cn, smithery.ai, etc.) are
// excluded — they are out of scope for GitHub search.
// This list is used as an *evaluation fixture only* — it must not appear in
// the production search config.

const GITHUB_TARGET_REPOS: string[] = [
  "199-biotechnologies/claude-deep-research-skill",
  "aaron-he-zhu/seo-geo-claude-skills",
  "addyosmani/web-quality-skills",
  "adjfks/corner-skills",
  "affaan-m/everything-claude-code",
  "agentix-cloud/skills",
  "agentspace-so/agent-skills",
  "agentspace-so/runcomfy-agent-skills",
  "agentspace-so/skills",
  "alchaincyf/darwin-skill",
  "alchaincyf/huashu-design",
  "alchaincyf/nuwa-skill",
  "alchaincyf/steve-jobs-skill",
  "analogjs/angular-skills",
  "angular/skills",
  "antfu/skills",
  "anthropics/claude-code",
  "anthropics/claude-plugins-official",
  "anthropics/knowledge-work-plugins",
  "anthropics/skills",
  "antibrow/anti-detect-browser-skills",
  "apify/agent-skills",
  "apollographql/skills",
  "aradotso/trending-skills",
  "arvindrk/extract-design-system",
  "asksurf-ai/surf-skills",
  "ast-grep/agent-skill",
  "astrolicious/agent-skills",
  "autogame-17/capability-evolver",
  "avdlee/swift-concurrency-agent-skill",
  "avdlee/swiftui-agent-skill",
  "bahayonghang/drawio-skills",
  "benjitaylor/agentation",
  "better-auth/better-icons",
  "better-auth/skills",
  "billionsnetwork/verified-agent-identity",
  "binance/binance-skills-hub",
  "bobmatnyc/claude-mpm-skills",
  "borghei/claude-skills",
  "brianlovin/claude-config",
  "brightdata/skills",
  "browser-use/browser-use",
  "callstackincubator/agent-device",
  "callstackincubator/agent-skills",
  "calm-north/seojuice-skills",
  "ccheney/robust-skills",
  "cclank/news-aggregator-skill",
  "charon-fan/agent-playbook",
  "claude-office-skills/skills",
  "clerk/skills",
  "cloudai-x/threejs-skills",
  "cloudflare/skills",
  "cloudflare/vinext",
  "coinbase/agentic-wallet-skills",
  "coleam00/excalidraw-diagram-skill",
  "composiohq/awesome-claude-skills",
  "coreyhaines31/marketingskills",
  "currents-dev/playwright-best-practices-skill",
  "cyxzdev/uncodixfy",
  "czlonkowski/n8n-skills",
  "dammyjoy93/interface-design",
  "deckardger/tanstack-agent-skills",
  "degausai/wonda",
  "dimillian/skills",
  "dontbesilent2025/dbskill",
  "dotneet/claude-code-marketplace",
  "ejirocodes/agent-skills",
  "elevenlabs/skills",
  "elysiajs/skills",
  "emblemcompany/agent-skills",
  "emblemcompany/emblemai-agentwallet",
  "emilkowalski/skill",
  "epiral/bb-browser",
  "expo/skills",
  "eze-is/web-access",
  "figma/mcp-server-guide",
  "firebase/agent-skills",
  "firecrawl/cli",
  "firecrawl/skills",
  "flutter/skills",
  "fluxa-agent-payment/fluxa-ai-wallet-mcp",
  "forrestchang/andrej-karpathy-skills",
  "franalgaba/grimoire",
  "garrytan/gstack",
  "genkit-ai/skills",
  "get-convex/agent-skills",
  "getsentry/skills",
  "github/awesome-copilot",
  "giuseppe-trisciuoglio/developer-kit",
  "gmgnai/gmgn-skills",
  "google-gemini/gemini-cli",
  "google-gemini/gemini-skills",
  "google-labs-code/stitch-skills",
  "google/agents-cli",
  "googleworkspace/cli",
  "gracefullight/stock-checker",
  "greensock/gsap-skills",
  "halthelobster/proactive-agent",
  "haydenbleasel/ultracite",
  "heredotnow/skill",
  "heroui-inc/heroui",
  "hexiaochun/seedance2-api",
  "heygen-com/hyperframes",
  "hugmouse/skills",
  "hyf0/vue-skills",
  "iamzhihuix/happy-claude-skills",
  "ibelick/ui-skills",
  "infsh-skills/skills",
  "insforge/agent-skills",
  "intellectronica/agent-skills",
  "jackwener/opencli",
  "jakubkrehel/make-interfaces-feel-better",
  "jamditis/claude-skills-journalism",
  "jeffallan/claude-skills",
  "jeremylongshore/claude-code-plugins-plus-skills",
  "jimliu/baoyu-skills",
  "joeseesun/opencli-skill",
  "josiahsiegel/claude-plugin-marketplace",
  "juliusbrussee/caveman",
  "kadajett/agent-nestjs-skills",
  "kepano/obsidian-skills",
  "kimny1143/claude-code-template",
  "langchain-ai/langchain-skills",
  "langfuse/skills",
  "langgenius/dify",
  "larksuite/cli",
  "leonxlnx/taste-skill",
  "ljagiello/ctf-skills",
  "lllllllama/ai-paper-reproduction-skill",
  "madteacher/mad-agents-skills",
  "magicseek/nblm",
  "mastra-ai/skills",
  "mattpocock/skills",
  "mblode/agent-skills",
  "mcp-use/mcp-use",
  "microsoft/azure-skills",
  "microsoft/github-copilot-for-azure",
  "microsoft/playwright-cli",
  "millionco/react-doctor",
  "mindrally/skills",
  "minimax-ai/cli",
  "minimax-ai/skills",
  "molezzz/openclaw-stock-skill",
  "momentic-ai/skills",
  "msmps/opentui-skill",
  "mvanhorn/last30days-skill",
  "napoleond/clawdirect",
  "napoleond/instaclaw",
  "neondatabase/agent-skills",
  "nextlevelbuilder/ui-ux-pro-max-skill",
  "nodnarbnitram/claude-code-extensions",
  "noizai/skills",
  "nozomio-labs/nia-skill",
  "nuxt/ui",
  "obra/episodic-memory",
  "obra/superpowers",
  "okx/agent-skills",
  "okx/onchainos-skills",
  "onmax/nuxt-skills",
  "op7418/claude-to-im-skill",
  "op7418/humanizer-zh",
  "openai/skills",
  "othmanadi/planning-with-files",
  "parcadei/continuous-claude-v3",
  "parthjadhav/app-store-screenshots",
  "patricio0312rev/skills",
  "patrickporto/desktop-agent",
  "pbakaus/impeccable",
  "pexoai/pexo-skills",
  "planetscale/database-skills",
  "pleaseprompto/notebooklm-skill",
  "pluginagentmarketplace/custom-plugin-java",
  "prisma/skills",
  "pskoett/self-improving-agent",
  "railwayapp/railway-skills",
  "redis/agent-skills",
  "refoundai/lenny-skills",
  "remorses/playwriter",
  "remotion-dev/skills",
  "replicas-group/skill",
  "resciencelab/opc-skills",
  "resend/email-best-practices",
  "resend/react-email",
  "resend/resend-skills",
  "rivet-dev/skills",
  "runablehq/mini-browser",
  "sanity-io/agent-toolkit",
  "sanyuan0704/code-review-expert",
  "schpet/linear-cli",
  "scrapegraphai/just-scrape",
  "secondsky/claude-skills",
  "sentry/dev",
  "shadcn/ui",
  "shirenchuang/web-content-fetcher",
  "shopify/shopify-ai-toolkit",
  "shubhamsaboo/awesome-llm-apps",
  "sickn33/antigravity-awesome-skills",
  "sleekdotdesign/agent-skills",
  "slidevjs/slidev",
  "softaworks/agent-toolkit",
  "solana-foundation/solana-dev-skill",
  "soultrace-ai/soultrace-skill",
  "squirrelscan/skills",
  "stanleychanh/tushare-finance-skill-for-claude-code",
  "starchild-ai-agent/official-skills",
  "steipete/clawdis",
  "stripe/ai",
  "sugarforever/01coder-agent-skills",
  "sundial-org/awesome-openclaw-skills",
  "supabase/agent-skills",
  "supercent-io/skills-template",
  "superdesigndev/superdesign-skill",
  "sveltejs/ai-tools",
  "tanweai/pua",
  "tavily-ai/skills",
  "trailofbits/skills",
  "tw93/waza",
  "twostraws/swift-concurrency-agent-skill",
  "twostraws/swift-testing-agent-skill",
  "twostraws/swiftdata-agent-skill",
  "twostraws/swiftui-agent-skill",
  "useai-pro/openclaw-skills-security",
  "veithly/tavily-search",
  "vercel-labs/agent-browser",
  "vercel-labs/agent-skills",
  "vercel-labs/next-browser",
  "vercel-labs/next-skills",
  "vercel-labs/skills",
  "vercel/ai",
  "vercel/ai-elements",
  "vercel/chat",
  "vercel/components.build",
  "vercel/turborepo",
  "vintasoftware/django-ai-plugins",
  "vuejs-ai/skills",
  "waynesutton/convexskills",
  "wecomteam/wecom-cli",
  "whatevertogo/feishuskill",
  "wondelai/skills",
  "wshobson/agents",
  "xiaoyiv/douyin-skill",
  "xixu-me/skills",
  "xixu-me/xget",
  "yizhiyanhua-ai/fireworks-tech-graph",
  "yusukebe/hono-skill",
  "zhanghandong/rust-skills",
  "zhjiang22/openclaw-xhs",
];

// ─── Query constraints ────────────────────────────────────────────────────────

const SEARCH_QUERIES_UNDER_TEST = [...REAL_SEARCH_QUERIES];

/** Count boolean operators (OR, AND, NOT) in a GitHub search query string. */
function countBooleanOperators(query: string): number {
  // Strip quoted strings so quoted OR/AND/NOT inside phrases don't count.
  const stripped = query.replace(/"[^"]*"/g, "");
  const matches = stripped.match(/\b(OR|AND|NOT)\b/g);
  return matches ? matches.length : 0;
}

/** Return true if the query contains a hard-coded owner/repo string like "owner/repo". */
function containsHardcodedRepo(query: string): boolean {
  // Pattern: two slugs separated by /, not preceded by topic: or in: qualifiers.
  // This is a heuristic — genuine "path:foo/bar" patterns should be caught too.
  return /\brepo:[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+\b/.test(query);
}

/**
 * GitHub repository search allows boolean operators only for text terms.
 * Qualifier-only operands like `topic:foo OR topic:bar` are rejected with HTTP 422.
 */
function hasQualifierOperandBooleanOperator(query: string): boolean {
  const tokens = query
    .replace(/"[^"]*"/g, " __TEXT__ ")
    .replace(/[()]/g, " $& ")
    .split(/\s+/)
    .filter(Boolean);

  for (let i = 0; i < tokens.length; i++) {
    if (!/^(OR|AND|NOT)$/.test(tokens[i])) continue;

    let left = i - 1;
    while (left >= 0 && /^[()]$/.test(tokens[left])) left--;

    let right = i + 1;
    while (right < tokens.length && /^[()]$/.test(tokens[right])) right++;

    if (left < 0 || right >= tokens.length) return true;
    if (isQueryQualifier(tokens[left]) || isQueryQualifier(tokens[right])) {
      return true;
    }
  }

  return false;
}

function isQueryQualifier(token: string): boolean {
  return /^-?[a-z][\w.-]*:[^\s]+$/i.test(token);
}

// ─── Mirror coverage helpers ──────────────────────────────────────────────────

/** Normalize a repo string to lowercase "owner/name". */
function normalizeRepo(repo: string): string {
  return repo.toLowerCase().trim();
}

/**
 * Read the set of currently mirrored repos from the mirrors/repos/ directory.
 * Directory names use the format "owner@name".
 */
async function readMirroredRepos(mirrorsRoot: string): Promise<Set<string>> {
  const result = new Set<string>();
  try {
    for await (const entry of Deno.readDir(mirrorsRoot)) {
      if (entry.isDirectory) {
        // Convert "owner@name" → "owner/name"
        const normalized = entry.name.replace("@", "/");
        result.add(normalizeRepo(normalized));
      }
    }
  } catch {
    // mirrors/repos/ may not exist in CI or fresh clone — treat as empty
  }
  return result;
}

/** Deduplicate an array of repo strings (case-insensitive). */
function deduplicateRepos(repos: string[]): string[] {
  const seen = new Set<string>();
  return repos.filter((r) => {
    const key = normalizeRepo(r);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

/** Compute coverage metrics. */
function computeCoverage(
  targets: string[],
  mirrored: Set<string>,
): {
  total: number;
  found: number;
  missed: string[];
  percentage: number;
} {
  const found: string[] = [];
  const missed: string[] = [];
  for (const repo of targets) {
    if (mirrored.has(normalizeRepo(repo))) {
      found.push(repo);
    } else {
      missed.push(repo);
    }
  }
  const percentage = targets.length > 0
    ? Math.round((found.length / targets.length) * 100)
    : 0;
  return { total: targets.length, found: found.length, missed, percentage };
}

// ─── Tests: query structural constraints ────────────────────────────────────

Deno.test("queries: boolean operator count ≤ 5", () => {
  for (const query of SEARCH_QUERIES_UNDER_TEST) {
    const count = countBooleanOperators(query);
    assertLess(
      count,
      6,
      `Query exceeds 5 boolean operators (got ${count}): ${query}`,
    );
  }
});

Deno.test("queries: no hardcoded repo references", () => {
  for (const query of SEARCH_QUERIES_UNDER_TEST) {
    assertEquals(
      containsHardcodedRepo(query),
      false,
      `Query contains a hardcoded repo qualifier: ${query}`,
    );
  }
});

Deno.test("queries: boolean operators are not applied to qualifiers", () => {
  for (const query of SEARCH_QUERIES_UNDER_TEST) {
    assertEquals(
      hasQualifierOperandBooleanOperator(query),
      false,
      `Query applies a boolean operator to a qualifier operand: ${query}`,
    );
  }
});

Deno.test("queries: no duplicate query strings", () => {
  const deduped = deduplicateRepos(SEARCH_QUERIES_UNDER_TEST);
  assertEquals(
    deduped.length,
    SEARCH_QUERIES_UNDER_TEST.length,
    "Duplicate query strings found",
  );
});

// ─── Tests: normalization and deduplication helpers ──────────────────────────

Deno.test("normalizeRepo: lowercases and trims", () => {
  assertEquals(normalizeRepo("Owner/Repo"), "owner/repo");
  assertEquals(normalizeRepo("  antfu/skills  "), "antfu/skills");
  assertEquals(normalizeRepo("VERCEL/AI"), "vercel/ai");
});

Deno.test("deduplicateRepos: removes case-insensitive duplicates", () => {
  const input = ["antfu/skills", "ANTFU/SKILLS", "vercel/ai", "Vercel/AI"];
  const result = deduplicateRepos(input);
  assertEquals(result, ["antfu/skills", "vercel/ai"]);
});

Deno.test("deduplicateRepos: preserves unique entries", () => {
  const input = ["antfu/skills", "vercel/ai", "github/awesome-copilot"];
  assertEquals(deduplicateRepos(input), input);
});

// ─── Tests: coverage evaluation ─────────────────────────────────────────────

Deno.test("countBooleanOperators: counts OR/AND/NOT correctly", () => {
  assertEquals(countBooleanOperators("foo OR bar"), 1);
  assertEquals(countBooleanOperators("foo OR bar OR baz"), 2);
  assertEquals(countBooleanOperators("foo AND bar NOT baz OR qux"), 3);
  assertEquals(countBooleanOperators('"foo OR bar" baz'), 0); // quoted, doesn't count
  assertEquals(countBooleanOperators("no operators here"), 0);
});

Deno.test("hasQualifierOperandBooleanOperator: flags qualifier-only operands", () => {
  assertEquals(
    hasQualifierOperandBooleanOperator(
      "topic:claude-code OR topic:agent-skills fork:false archived:false",
    ),
    true,
  );
  assertEquals(
    hasQualifierOperandBooleanOperator(
      '"copilot instructions" OR "claude plugins" stars:>5 pushed:>2024-01-01',
    ),
    false,
  );
});

Deno.test("computeCoverage: basic metrics", () => {
  const targets = ["antfu/skills", "vercel/ai", "github/awesome-copilot"];
  const mirrored = new Set(["antfu/skills", "vercel/ai"]);
  const result = computeCoverage(targets, mirrored);
  assertEquals(result.total, 3);
  assertEquals(result.found, 2);
  assertEquals(result.missed, ["github/awesome-copilot"]);
  assertEquals(result.percentage, 67);
});

Deno.test("computeCoverage: case-insensitive matching", () => {
  const targets = ["Antfu/Skills", "VERCEL/AI"];
  const mirrored = new Set(["antfu/skills", "vercel/ai"]);
  const result = computeCoverage(targets, mirrored);
  assertEquals(result.found, 2);
  assertEquals(result.missed, []);
});

// ─── Coverage report (informational — always passes) ────────────────────────

Deno.test("coverage report: mirror vs target list", async (t) => {
  const repoRoot = join(import.meta.dirname!, "..");
  const mirrorsRoot = join(repoRoot, "mirrors", "repos");
  const mirrored = await readMirroredRepos(mirrorsRoot);
  const targets = deduplicateRepos(GITHUB_TARGET_REPOS);
  const coverage = computeCoverage(targets, mirrored);

  // Print a human-readable report to the test output
  await t.step("print report", () => {
    console.log("\n── Discovery Coverage Report ──────────────────────────────");
    console.log(`  Total GitHub targets : ${coverage.total}`);
    console.log(`  Found in mirror      : ${coverage.found}`);
    console.log(`  Missed               : ${coverage.missed.length}`);
    console.log(`  Coverage             : ${coverage.percentage}%`);

    if (coverage.missed.length > 0) {
      console.log("\n  Missed repos:");
      for (const repo of coverage.missed.slice(0, 40)) {
        console.log(`    - ${repo}`);
      }
      if (coverage.missed.length > 40) {
        console.log(`    ... and ${coverage.missed.length - 40} more`);
      }
    }
    console.log("────────────────────────────────────────────────────────────");
  });

  // The coverage test is informational — it does NOT assert a specific threshold
  // because coverage depends on running the mirror with a live GitHub token first.
  // Structural query constraints (operator count, no hardcoded repos) are the
  // hard assertions enforced by the tests above.
  assert(coverage.total > 0, "Target list must not be empty");
  assert(mirrored.size >= 0, "Mirrored set is valid (may be empty)");
});
