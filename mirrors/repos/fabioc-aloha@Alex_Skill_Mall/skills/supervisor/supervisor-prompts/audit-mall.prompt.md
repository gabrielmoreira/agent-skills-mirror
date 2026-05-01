---
description: "Supervisor: Run a periodic audit of Alex_Skill_Mall — link-check, staleness scan, coherence with Edition"
application: "Monthly, or on-demand when heirs report Mall friction"
agent: Brain Ops
mode: agent
lastReviewed: 2026-04-30
---

# /audit-mall

Sweep `Alex_Skill_Mall` for staleness and coherence issues.

## Inputs

- `Alex_Skill_Mall/STORES.md` and `CATALOG.md` (sibling at `../Alex_Skill_Mall/`)
- `Alex_ACT_Edition/.github/` (sibling at `../Alex_ACT_Edition/`) — for coherence cross-references

## Steps

1. Load [mall-curation](../skills/mall-curation/SKILL.md) and [staleness-discipline](../skills/staleness-discipline/SKILL.md)
2. Run mechanical checks (when scripts exist):
   - `node scripts/mall-link-check.cjs` — link reachability
   - `node scripts/stores-staleness.cjs` — upstream activity scan
3. For each entry in STORES.md, evaluate against the staleness table and classify (Keep / Refresh / Prune)
4. For each prune candidate, grep `../Alex_ACT_Edition/.github/` for references — flag coherence violations
5. Verify counts: STORES.md count vs CATALOG.md count vs README badge
6. Run an ACT pass on the audit verdict (full pass — pruning is irreversible-by-default)
7. Emit the audit report using [mall-curation](../skills/mall-curation/SKILL.md) §Output Template
8. File one PR per prune (do not bundle), one Refresh PR may bundle related drift fixes
9. Record outcome in `decisions/curation-log.md` with M (mechanical) / S (semantic) classification

## Verify Before Proceeding

- ✅ At least one mechanical check ran (or its absence is documented as a blocker)
- ✅ Coherence cross-reference performed against `../Alex_ACT_Edition/`
- ✅ ACT pass markers visible in the report
- ✅ Curation log updated

## Output

The audit report goes to `decisions/audits/mall-YYYY-MM-DD.md`.

## Related

- `/add-store`, `/prune-store`
- [mall-maintenance-rules](../instructions/mall-maintenance-rules.instructions.md)
