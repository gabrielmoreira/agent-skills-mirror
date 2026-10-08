---
name: skills-bank
description: |
  Master router — use curated hubs, ignore raw cache.
---

# Skills Bank — Agent Guardrail

> **DO NOT scan `lib/` (2.1G, 10k SKILL.md, 122 repos). It is raw clone cache, not curated.**

## Canonical Discovery (3 hops, not 122)

1. Open `skills-aggregated/AGENTS.md` — pick hub from 4 (business, code-quality, frontend, server-side)
2. Open `skills-aggregated/<hub>/SKILL.md` — pick sub-hub (16 total, not 122)
3. Open `skills-aggregated/<hub>/<sub-hub>/routing.csv` — find `skill_id` by description, read `src_path` (points to `lib/.../SKILL.md`) or symlink `<sub-hub>/<skill_id>/SKILL.md`

## Opencode Native (if synced)

When synced, hubs are also available via `skill` tool as 4 entries (business, code-quality, frontend, server-side) — 120 tokens, not 3840. Load hub via `skill`, then follow routing.csv.

## Anti-Patterns

- NEVER `Glob **/SKILL.md` on repo root (hits `lib/` → 212k tokens)
- NEVER read `lib/SKILL.md` (deleted router, was 122 repos)
- ALWAYS use `skills-aggregated/` routers + `src_path` source-of-truth

<!-- code-review-graph MCP tools -->
## MCP Tools: code-review-graph

**This project has a knowledge graph. Start with the code-review-graph
MCP tools to narrow scope, then read the source.** The graph is cheaper than scanning files and
gives you structural context (callers, dependents, test coverage) that file search cannot.

### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes_tool` or `query_graph_tool` instead of Grep
- **Understanding impact**: `get_impact_radius_tool` instead of manually tracing imports
- **Code review**: `detect_changes_tool` + `get_review_context_tool` instead of reading entire files
- **Finding relationships**: `query_graph_tool` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview_tool` + `list_communities_tool`

### Verify in the source

- Narrow scope with the graph, then read the source. Do not change code from graph output alone.
- For any non-trivial change, read the implementation and the relevant tests before concluding.
- Verify the exact source when touching behavior, database logic, migrations, retries, fallbacks,
  recovery, or compatibility code.
- When the graph and the source disagree, the source wins. The graph may be stale or may not
  model that relationship.
- An empty graph result can mean "not indexed" or "not statically visible", not "does not exist".

### Key Tools

| Tool | Use when |
| ------ | ---------- |
| `detect_changes_tool` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context_tool` | Need source snippets for review — token-efficient |
| `get_impact_radius_tool` | Understanding blast radius of a change |
| `get_affected_flows_tool` | Finding which execution paths are impacted |
| `query_graph_tool` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes_tool` | Finding functions/classes by name or keyword |
| `get_architecture_overview_tool` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (via hooks).
2. Use `detect_changes_tool` for code review.
3. Use `get_affected_flows_tool` to understand impact.
4. Use `query_graph_tool` pattern="tests_for" to check coverage.
<!-- /code-review-graph MCP tools -->
