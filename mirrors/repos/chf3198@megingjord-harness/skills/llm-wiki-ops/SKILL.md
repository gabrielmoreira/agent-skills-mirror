# llm-wiki-ops — LLM Wiki Operations Skill

## Purpose
Operate and maintain the LLM Wiki knowledge system. Use this
skill when ingesting sources, querying the wiki, diagnosing
health issues, or planning knowledge graph expansion.

## Global Access Model

| Mode | Scope | Path |
|---|---|---|
| **Read** | Any repo | `~/.copilot/wiki/` (deployed runtime) |
| **Write** | devenv-ops only | `wiki/` (source of truth) |
| **Search** | Any repo | `node ~/.copilot/scripts/wiki-search.js` |
| **Ingest** | devenv-ops only | `npm run wiki:ingest` |
| **Lint** | devenv-ops only | `npm run wiki:lint` |

## Architecture
```
devenv-ops/wiki/    ──deploy──▶  ~/.copilot/wiki/  (read-only)
devenv-ops/raw/     (stays local, not deployed)
scripts/wiki/       (dev tools, not deployed)
scripts/global/wiki-search.js ──deploy──▶ ~/.copilot/scripts/
```

## Operations

### Search (any repo)
```bash
node ~/.copilot/scripts/wiki-search.js "your question"
```
Keyword scoring → top 5 pages → shows matches with excerpts.

### Ingest (devenv-ops only)
```bash
npm run wiki:ingest -- raw/articles/<source>.md
```
Raw → LLM summary → wiki/sources/ page → index + log update.

### Lint (devenv-ops only)
```bash
npm run wiki:lint
```
Broken wikilinks, orphans, frontmatter, index sync.

## Fleet Routing
- **Ingest**: Fleet lane → OpenClaw (mistral → qwen2.5 fallback)
- **Search (LLM)**: Fleet lane → OpenClaw for synthesis
- **Lint**: Free lane → local only (no LLM)

## Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| Wiki not found | Not deployed | `npm run deploy:apply` in devenv-ops |
| Stale content | Not redeployed | Redeploy after wiki changes |
| Ingest timeout | Model cold start | `curl OpenClaw/health` |
| All LLMs fail | Network/Tailscale | `tailscale status` |

## Constraints
- `~/.copilot/wiki/` is read-only from non-devenv-ops repos
- Raw sources are immutable after ingest
- All scripts ≤100 lines (lint-enforced)
- Changes flow: devenv-ops → merge → deploy → ~/.copilot/
