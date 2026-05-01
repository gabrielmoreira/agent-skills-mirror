---
description: "Supervisor: Evaluate and add a proposed store to Alex_Skill_Mall"
application: "When a store proposal lands in feedback/inbox/ or is suggested directly"
agent: Brain Ops
mode: agent
lastReviewed: 2026-04-30
---

# /add-store

Run the five-dimension store evaluation and, if it passes, add the store to STORES.md and CATALOG.md.

## Inputs

- Proposal source: `feedback/inbox/*store-proposal*.md` or inline argument
- Target: `../Alex_Skill_Mall/STORES.md` and `../Alex_Skill_Mall/CATALOG.md`

## Steps

1. Load [store-evaluation](../skills/store-evaluation/SKILL.md) and [mall-curation](../skills/mall-curation/SKILL.md)
2. Gather signal: upstream repo URL, license, last commit date, star count, recent releases
3. Score the five dimensions (Maintenance, Adoption, License, Fit, Documentation)
4. Apply the two-source rule — at least two of (heir feedback, upstream activity, adoption signal) must be present
5. Run an ACT pass — pruning, adding, and rejecting are all quality decisions
6. If accepted: update STORES.md, CATALOG.md, and README counts in `../Alex_Skill_Mall/`
7. Open a Mall PR titled `add: <store name> (score: x/10)`
8. Record in `decisions/curation-log.md` (S — semantic decision)
9. If rejected: write the verdict to `decisions/store-rejections/<name>-YYYY-MM-DD.md` so future similar proposals don't repeat the cycle

## Verify Before Proceeding

- ✅ Score ≥ 7 to accept; otherwise reject or defer
- ✅ Two-source rule satisfied
- ✅ ACT pass markers visible in the verdict
- ✅ Counts in `../Alex_Skill_Mall/` README match new totals

## Output

A verdict file (accepted or rejected) and, if accepted, a Mall PR.

## Related

- `/audit-mall`, `/prune-store`
- [mall-maintenance-rules](../instructions/mall-maintenance-rules.instructions.md)
