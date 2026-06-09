# WIKI Typology, Fleet Routing, and Constraints

> Companion to `wiki/WIKI.md`. Covers three-wiki typology, fleet routing for
> inference operations, namespace isolation, and operational constraints.

## Three-wiki typology (detail)

### Code wiki (`wiki/code/`)

**Purpose**: annotated understanding of this repo's own source code.
**Content**: module-level summaries, interface contracts, known edge cases.
**Update trigger**: significant code change merged to `main`.
**Consumer**: `wiki-search.js` when answering "how does X work?" queries.

### Work-log wiki (`wiki/work-log/`)

**Purpose**: session audit trail and governed ticket history.
**Content**: per-session summaries, ticket decisions, baton outcomes.
**Update trigger**: every governed PR merge (Admin posts entry).
**Mutation rule**: append-only — never edit past entries; corrections go in new entries.

### Wisdom wiki (`wiki/wisdom/`)

**Purpose**: distilled external knowledge and cross-system insights.
**Content**: source summaries, concept pages, R&D syntheses, fleet entity pages.
**Update trigger**: after raw source ingest or research synthesis.
**Sub-paths**: `global/` (harness-wide); `project/` (per-project knowledge).

## Namespace isolation

Pages in one sub-wiki **must not** wikilink to pages in another sub-wiki
unless the link is an explicit cross-wiki reference:

| Prefix       | Meaning                  | Example                            |
| ------------ | ------------------------ | ---------------------------------- |
| _(none)_     | Same sub-wiki reference  | `[[github-native-layer2]]`         |
| `code::`     | Reference to code wiki   | `code::[[cascade-dispatch-js]]`    |
| `work-log::` | Reference to work-log    | `work-log::[[session-2026-06-08]]` |
| `wisdom::`   | Reference to wisdom wiki | `wisdom::[[hamr-failover-map]]`    |

Cross-wiki links must be justified in the page frontmatter `related:` annotation.

## Fleet routing (inference operations)

| Operation                      | Primary host          | Failover               |
| ------------------------------ | --------------------- | ---------------------- |
| Ingest (summarise + cross-ref) | OpenClaw (7B, M3 Max) | Groq, Cerebras         |
| Query (synthesis)              | OpenClaw (7B)         | Copilot Pro            |
| Lint (structural checks)       | Local Node.js scripts | — (never pay for lint) |
| Anneal (link pass)             | Local Node.js scripts | —                      |

Fleet availability is checked via `scripts/health-check.js` before dispatching.
If the primary host is unreachable, routing falls back to the next available
tier (G6 Resilience). Lint and anneal are local-only; G3 Zero Cost is non-negotiable
for structural operations.

## Constraints

- Wiki files ≤100 lines (lint-enforced for `wiki/*.md`; `wiki/wisdom/` is exempt)
- Split with a companion file if content naturally exceeds 100 lines — do not truncate
- Markdown only; no binary files in `wiki/`
- `wiki/index.md` and `wiki/log.md` are exempt from the 100-line limit by design
- Git tracks `wiki/`; `raw/` sources are the source of truth; wiki is derived and rebuild-safe

## Special pages

| File                      | Purpose                                                   | Mutability                    |
| ------------------------- | --------------------------------------------------------- | ----------------------------- |
| `wiki/index.md`           | Catalog of every page, grouped by type; updated on ingest | LLM rewrites freely           |
| `wiki/log.md`             | Append-only chronological ops record                      | Append only                   |
| `wiki/WIKI.md`            | Schema and conventions                                    | Co-owned; change by agreement |
| `wiki/WIKI-operations.md` | Ingest/query/lint procedures                              | LLM updates                   |
| `wiki/WIKI-typology.md`   | This file — typology and routing                          | LLM updates                   |
