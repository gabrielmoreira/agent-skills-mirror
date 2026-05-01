# agent-skills-mirror

A Deno script that automatically discovers and mirrors AI agent skill repositories from GitHub.

## What it does

`agent-skills-mirror` runs GitHub search queries to find repositories that contain AI agent skills, coding assistant instructions, Claude skills, Copilot instructions, MCP tool integrations, and related configuration files. For each discovered repository it performs a **sparse checkout** — pulling only the specific files relevant to skill/prompt/instruction consumption — and writes the results to a local `mirrors/` directory.

## Why it exists

The AI coding assistant ecosystem (Claude Code, GitHub Copilot, Cursor, Continue, Windsurf, MCP tools, etc.) has produced hundreds of high-signal skill and instruction repositories scattered across GitHub. This project aggregates them into one place so that:

- Tooling can consume skill files without cloning hundreds of repos.
- Humans can browse relevant instructions and prompts in one directory tree.
- Coverage can be measured and improved over time.

## What kinds of repositories it discovers

The search queries target repositories that contain:

- **Agent skills** — `SKILL.md`, `skills/**`, `skill/**` files for Claude Code, GitHub Copilot agent mode, or custom coding agents.
- **Copilot instructions** — `.github/instructions/**`, `.github/prompts/**`, `copilot-instructions.md`.
- **Claude/LLM config** — `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `LLMs.txt`.
- **Cursor / Windsurf / Continue rules** — `.cursorrules`, `.cursor/rules/**`, `.windsurfrules`, `.continue/**`.
- **MCP integrations** — `.mcp/**`, `mcp/**` directories.
- **Prompt collections** — `prompts/**`, `prompt/**`.

Non-GitHub sources (e.g. docs.stripe.com, open.feishu.cn, smithery.ai) are **not** indexed by this tool and should be consulted separately.

## How to run

### Prerequisites

- [Deno](https://deno.land/) ≥ 2.x
- Git (for sparse checkout)
- A GitHub personal access token (recommended to avoid rate-limits)

### Basic run

```sh
deno run -A src/main.ts
```

### With a GitHub token

```sh
# Using gh CLI
GH_TOKEN=$(gh auth token) deno run -A src/main.ts

# Or exporting directly
export GH_TOKEN=ghp_...
deno run -A src/main.ts

# GITHUB_TOKEN is also accepted
export GITHUB_TOKEN=ghp_...
deno run -A src/main.ts
```

Without a token, GitHub search is unauthenticated and heavily rate-limited (10 requests/min). With a token the limit is 30 requests/min for search.

### Using the Deno task

```sh
deno task mirror
```

### Running tests

```sh
deno task test
```

### Controlling concurrency

```sh
MIRROR_CONCURRENCY=4 deno run -A src/main.ts
```

Default concurrency is 8 parallel repo checkouts.

## What is mirrored and where

Mirrored files are written under `mirrors/repos/<owner>@<name>/` — for example:

```
mirrors/repos/vercel-labs@agent-skills/
  skills/
    vercel-v0/SKILL.md
  .github/prompts/
    ...
  manifest.json
```

Each directory contains:
- The sparse-checked-out files matching the configured patterns.
- A `manifest.json` describing the repo, ref, patterns used, and file index.

The `cache/` directory holds bare git clones and per-repo state files used to avoid redundant fetches between runs.

## Sparse checkout patterns

Instead of cloning full repositories, the tool uses `git sparse-checkout` to pull only the files that match the configured include patterns. The global patterns are:

| Pattern | Purpose |
|---|---|
| `**/AGENTS.md`, `**/CLAUDE.md`, `**/GEMINI.md` | Top-level agent/LLM config |
| `**/SKILL.md`, `**/skills.md` | Skill definition files |
| `**/LLMs.txt`, `**/llms.txt` | LLM compatibility hints |
| `**/copilot-instructions.md` | Copilot instruction files |
| `**/.cursorrules`, `**/.cursor/rules/**` | Cursor editor rules |
| `**/.windsurfrules` | Windsurf editor rules |
| `**/.continue/**` | Continue extension config |
| `.github/instructions/**`, `.github/prompts/**` | GitHub Copilot agent instructions |
| `.agents/**`, `agents/**` | Agent-level instruction dirs |
| `skills/**`, `skill/**` | Skill directories |
| `prompts/**`, `prompt/**` | Prompt directories |
| `.cursor/**`, `.continue/**`, `.mcp/**`, `mcp/**` | Tool-specific config |

Additionally, the **markdown-follow** feature (`follow.linkedFromMarkdown: true`) discovers additional files linked from Markdown documents and adds them to the checkout.

## Cache / materialization

The tool keeps a persistent bare-clone cache at `cache/repos/` and per-repo state files at `cache/state/`. On each run:

1. The GitHub API is queried to resolve the current HEAD SHA.
2. If the repo's HEAD SHA and config hash match the stored state, the repo is **skipped** (`reuse-if-current` mode).
3. Otherwise, the bare clone is updated (or created) and a new sparse export is written to `mirrors/`.

This means reruns are fast — only changed or newly-discovered repos are re-exported. To force a full refresh, set `materialization.mode` to `"always-refresh"` in the config, or delete `cache/`.

## How to tune search queries

Search queries are defined in `REAL_SEARCH_QUERIES` in `src/main.ts`. Each query is a standard [GitHub repository search](https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories) query string.

Guidelines:
- Keep queries focused on a single intent (agent skills, copilot instructions, MCP, etc.).
- GitHub allows **max 5 boolean operators** (`OR`, `AND`, `NOT`) per query.
- Use `stars:>N` to filter noise. Tune N based on the target population.
- Use `pushed:>YYYY-MM-DD` to exclude stale repositories.
- Use `fork:false archived:false` to exclude forks and archived repos.
- Use `in:name` to target repos where the keyword appears in the repo name.
- Use `topic:X` to target repos with a specific GitHub topic label.

Example of adding a new query:

```ts
// Find repos with "my-skill" in the name
"my-skill in:name stars:>1 pushed:>2024-01-01 fork:false archived:false",
```

## Known limitations of GitHub search

- **Max 5 boolean operators** per query — complex multi-term queries must be split.
- **Search index lag** — newly created repos may not appear immediately.
- **Description/README indexing** — some repos are discovered via name matching only if the README is not yet indexed.
- **Rate limits** — unauthenticated: 10 req/min; authenticated: 30 req/min for search.
- **Private repos** — only public repos are visible.
- **Fork and archive exclusion** — `fork:false archived:false` is recommended but means forked skill collections are skipped.
- **Star threshold** — repos below the star threshold will not appear even if highly relevant. Tune per query.
- **Non-GitHub sources** — docs.stripe.com, open.feishu.cn, smithery.ai and other non-GitHub skill sources are outside the scope of this tool.

## How to evaluate discovery coverage

A coverage test is included in `src/eval-coverage.test.ts`. It compares a reference target list of known high-signal repositories against the set of currently mirrored repositories.

```sh
deno task test
```

The test reports:
- Total GitHub target repos in the reference list
- Repos found in the mirror
- Repos missed
- Coverage percentage

The coverage report is informational — it does not assert a specific threshold because coverage depends on running the mirror with a live GitHub token first.

To run coverage evaluation without running all tests:

```sh
deno test src/eval-coverage.test.ts
```

You can also check coverage manually:

```sh
# List all currently mirrored repos
ls mirrors/repos/ | sed 's/@/\//'

# Compare against a reference list
comm -23 <(sort reference.txt) <(ls mirrors/repos/ | sed 's/@/\//;s/.*/\L&/' | sort)
```

## Short example workflow

```sh
# 1. Clone the repo
git clone https://github.com/gabrielmoreira/agent-skills-mirror
cd agent-skills-mirror

# 2. Run the mirror with your GitHub token
GH_TOKEN=$(gh auth token) deno run -A src/main.ts

# 3. Browse the mirrored files
ls mirrors/repos/

# 4. Check a specific skill repo
cat mirrors/repos/vercel-labs@agent-skills/skills/vercel-v0/SKILL.md

# 5. Run coverage evaluation
deno task test
```

The workflow runs nightly via GitHub Actions (`.github/workflows/mirror.yml`) and commits updated mirrors to the `main` branch automatically.
