---
mode: agent
description: "Supervisor: Audit brain files for stale currency stamps, broken external refs, and outdated version assertions"
lastReviewed: 2026-04-30
---

# /audit-currency

Sweep the Supervisor brain for stale content. The Supervisor's whole job is checking what's stale; do this monthly or before any release.

## Steps

1. Load skills: [currency-audit](../skills/currency-audit/SKILL.md), [doc-hygiene](../skills/doc-hygiene/SKILL.md)
2. Scan `.github/skills/`, `.github/instructions/`, `.github/prompts/` for `currency:` frontmatter older than 90 days
3. For each stale file, ask: is the content still accurate as of today, or does it need a refresh?
4. Run `scripts/coherence-check.cjs` and `scripts/mall-link-check.cjs` for external-ref hygiene
5. Run `node scripts/sync-from-master.cjs` for pinned-instruction drift
6. Report findings as a table: file · last currency · proposed action (refresh / keep / retire)
7. For each file marked `refresh`, update the body and bump the `currency:` stamp only after verifying content
8. Record decisions in `decisions/curation-log.md` with `M` or `S` classification

**Do not stamp without verifying.** Stamping a stale file without reviewing it defeats the audit.
