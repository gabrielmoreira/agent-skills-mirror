---
description: "Supervisor: Prune a stale or broken store from Alex_Skill_Mall using staleness-discipline"
application: "When a Mall entry fails the staleness gate or a heir reports persistent breakage"
agent: Brain Ops
mode: agent
lastReviewed: 2026-04-30
---

# /prune-store

Remove a stale entry from `Alex_Skill_Mall` while preserving history and fleet coherence.

## Inputs

- Entry to prune: STORES.md line or CATALOG.md ID
- Reason: which staleness signal fired

## Steps

1. Load [staleness-discipline](../skills/staleness-discipline/SKILL.md) and [mall-curation](../skills/mall-curation/SKILL.md)
2. Confirm the staleness signal is real — re-run the mechanical check or revisit the upstream evidence
3. Coherence check: grep `../Alex_ACT_Edition/.github/` for references to the entry
   - If references exist: open Edition PR fixing them *first*; do not proceed until merged
4. Run a full ACT pass (pruning is irreversible-by-default; full pass mandatory)
5. Comment out (do not delete) the entry in STORES.md and CATALOG.md
6. Add `pruned: YYYY-MM-DD reason: <reason>` above the commented line
7. Update README counts in `../Alex_Skill_Mall/`
8. Open a Mall PR titled `prune: <entry> (<reason>)`
9. If the prune sets a class precedent, write an ADR in `decisions/`
10. Record in `decisions/curation-log.md` (S — semantic decision)

## Verify Before Proceeding

- ✅ Coherence check complete; Edition references fixed first
- ✅ Entry commented out, not deleted
- ✅ Counts updated
- ✅ ACT pass markers visible
- ✅ ADR written if class precedent

## Output

A Mall PR (and possibly an Edition PR pair) plus an optional ADR.

## Related

- `/audit-mall`, `/add-store`
- [mall-maintenance-rules](../instructions/mall-maintenance-rules.instructions.md)
