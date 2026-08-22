---
name: skills-bank
description: |
  Master router — use curated hubs, ignore raw cache.
---

# Skills Bank — Agent Guardrail

> **DO NOT scan `lib/` (2.1G, 10k SKILL.md, 122 repos). It is raw clone cache, not curated.**

## Canonical Discovery (ponytail: 3 hops, not 122)

1. Open `skills-aggregated/AGENTS.md` — pick hub from 4 (business, code-quality, frontend, server-side)
2. Open `skills-aggregated/<hub>/SKILL.md` — pick sub-hub (16 total, not 122)
3. Open `skills-aggregated/<hub>/<sub-hub>/routing.csv` — find `skill_id` by description, read `src_path` (points to `lib/.../SKILL.md`) or symlink `<sub-hub>/<skill_id>/SKILL.md`

## Opencode Native (if synced)

When synced, hubs are also available via `skill` tool as 4 entries (business, code-quality, frontend, server-side) — 120 tokens, not 3840. Load hub via `skill`, then follow routing.csv.

## Anti-Patterns

- NEVER `Glob **/SKILL.md` on repo root (hits `lib/` → 212k tokens)
- NEVER read `lib/SKILL.md` (deleted router, was 122 repos)
- ALWAYS use `skills-aggregated/` routers + `src_path` source-of-truth
