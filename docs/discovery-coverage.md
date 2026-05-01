# Discovery Coverage Report

This document records the discovery coverage of the GitHub search queries
against a reference list of known high-signal AI agent/skill repositories.

## Methodology

1. A reference list of target GitHub repositories was assembled from known
   AI agent skill ecosystems (Claude Code skills, Copilot instructions,
   agent-skills collections, MCP integrations, etc.).
2. Non-GitHub sources (`docs.stripe.com`, `open.feishu.cn`, `smithery.ai`)
   are excluded — they are out of scope for GitHub search.
3. The `mirrors/repos/` directory was scanned to see which targets had already
   been discovered and mirrored.
4. Coverage = matched repos / total GitHub targets × 100.

## Baseline (before query improvements)

Measured against the `mirrors/repos/` snapshot on 2026-05-01.

| Metric | Value |
|---|---|
| Total GitHub target repos | 244 |
| Found in mirror | 32 |
| Missed | 212 |
| **Coverage** | **~13%** |

### Repos found by baseline queries

The 32 matched repos were discovered primarily by queries 3, 5, and 6 (coding assistants / claude, skills+prompts, claw):

```
affaan-m/everything-claude-code
anthropics/claude-code
anthropics/claude-plugins-official
anthropics/skills
browser-use/browser-use
composiohq/awesome-claude-skills
coreyhaines31/marketingskills
epiral/bb-browser
forrestchang/andrej-karpathy-skills
garrytan/gstack
github/awesome-copilot
google-gemini/gemini-cli
google-labs-code/stitch-skills
googleworkspace/cli
heygen-com/hyperframes
juliusbrussee/caveman
kepano/obsidian-skills
langfuse/skills
langgenius/dify
mcp-use/mcp-use
mvanhorn/last30days-skill
obra/superpowers
othmanadi/planning-with-files
shubhamsaboo/awesome-llm-apps
sickn33/antigravity-awesome-skills
tanweai/pua
useai-pro/openclaw-skills-security
vercel-labs/agent-browser
vercel-labs/agent-skills
vercel-labs/skills
vercel/ai
wshobson/agents
```

## Root causes for misses (baseline)

### 1. Many repos are named `owner/skills` without companion keywords
Repos like `angular/skills`, `antfu/skills`, `cloudflare/skills`, `clerk/skills`, etc.
are framework-specific skill directories. Their description or README may not
contain "prompts" (required by query 5: `skills prompts stars:>10`), so they
fall through.

### 2. The `skills prompts` query requires both terms
Query 5 uses `skills prompts` (implicit AND). Many pure skill repos omit the
word "prompts". This dual-term requirement is too restrictive.

### 3. Star threshold too high for niche repos
Queries use `stars:>10` or `stars:>20` globally. Many legitimate low-star skill
repos (< 10 stars) are recent or domain-specific (e.g. `solana-dev-skill`,
`tushare-finance-skill-for-claude-code`).

### 4. `agent-skills` naming pattern not targeted directly
None of the baseline queries specifically look for repos with `agent-skills`
in their name. Repos like `apify/agent-skills`, `callstackincubator/agent-skills`,
`firebase/agent-skills`, `redis/agent-skills` are missed because "agent-skills"
does not appear as a standalone term in query 5.

### 5. `claude skills` compound not captured
Repos like `borghei/claude-skills`, `jeffallan/claude-skills`, `secondsky/claude-skills`
contain both "claude" and "skills" but not "prompts". Query 3 requires 20+ stars.

### 6. Some repos use "plugin" / "cli" terminology
`anthropics/knowledge-work-plugins`, `dotneet/claude-code-marketplace`,
`josiahsiegel/claude-plugin-marketplace` use "plugin" vocabulary instead of "skills".

### 7. Non-indexed or very new repos
Some repos are too new to appear in GitHub's search index at the time queries run.

## Improvements made

Four new queries were added to `src/main.ts` to address the above gaps:

| Query # | Intent | Key terms |
|---|---|---|
| 7 | Repos named "agent-skills" | `agent-skills in:name stars:>1` |
| 8 | Claude + skills compound | `claude skills stars:>3` |
| 9 | GitHub topic-based discovery | `topic:claude-code OR topic:agent-skills OR topic:copilot-skills` |
| 10 | Instruction/plugin repos | `"copilot instructions" OR "claude plugins" OR "ai-tools" stars:>5` |

### Expected coverage improvement

After the next full mirror run with the improved queries, coverage is expected to rise
significantly for the following categories:

- `*/agent-skills` repos: Query 7 directly targets these by name.
- `*/claude-skills` repos: Query 8 captures repos with both "claude" and "skills".
- Repos with topic tags: Query 9 finds repos that have been tagged by their owners.
- Plugin/instruction repos: Query 10 captures a different vocabulary cluster.

Exact post-improvement coverage will be measured on the next scheduled run.

## Repos expected to remain missed

Some repos in the target list are structurally hard to discover by query:

| Repo | Reason |
|---|---|
| `cloudflare/vinext` | Name has no AI/skill keyword; description may not match |
| `nuxt/ui` | General UI library, skills are secondary |
| `heroui-inc/heroui` | UI framework, skills are secondary |
| `slidevjs/slidev` | Presentation tool; skills are a small addition |
| `vercel/turborepo` | Monorepo tool; skill files may be incidental |
| `shadcn/ui` | UI component library |
| `resend/react-email` | Email library |
| `resend/email-best-practices` | Email best practices |
| `sentry/dev` | Dev tooling, not skill-focused |
| `haydenbleasel/ultracite` | Linting tool |

These repos contain skill/config files incidentally. They would only be discoverable
if we lowered star thresholds dramatically or used permissive `in:name` patterns
that would introduce significant noise.

## How to re-evaluate

```sh
# Run the coverage test to see current mirror vs target coverage
deno task test

# After running the mirror with updated queries:
GH_TOKEN=$(gh auth token) deno run -A src/main.ts

# Then re-run the test to see updated coverage
deno task test
```

## Non-GitHub sources (out of scope)

The following sources from the evaluation list are not GitHub repositories
and therefore cannot be discovered by GitHub search queries:

- `docs.stripe.com` — Stripe documentation
- `open.feishu.cn` — Lark/Feishu platform docs
- `smithery.ai` — MCP marketplace (not a GitHub repo)

These should be documented separately if their content is desired.
