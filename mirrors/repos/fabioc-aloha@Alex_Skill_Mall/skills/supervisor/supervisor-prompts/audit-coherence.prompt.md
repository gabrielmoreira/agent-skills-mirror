---
description: "Supervisor: Run cross-repo coherence audit between Alex_ACT_Edition and Alex_Skill_Mall"
application: "Monthly, before any Mall prune of a referenced store, and as a preflight for Edition releases"
agent: Brain Ops
mode: agent
lastReviewed: 2026-04-30
---

# /audit-coherence

Detect drift between the Edition (brain) and the Mall (marketplace).

## Inputs

- `../Alex_ACT_Edition/.github/` — brain artifacts that may reference Mall stores
- `../Alex_Skill_Mall/STORES.md` and `CATALOG.md` — current Mall catalog

## Steps

1. Load [coherence-audit](../skills/coherence-audit/SKILL.md)
2. Run `node scripts/coherence-check.cjs` — mechanical sweep of Check 1 (broken references) and partial Check 2 (tag mismatch)
3. For each finding, classify as Hard / Soft / False positive per the skill's decision matrix
4. Run an ACT pass — coherence fixes touch both repos and may set policy precedent
5. Decide which side fixes per the catalog-of-record rules:
   - Names/URLs disagree → Mall wins, Edition fixes
   - Capability/doctrine disagrees → Edition wins, Mall fixes
6. Open coordinated PRs when both sides change; sequence so the merge order doesn't break consumers
7. Emit the audit report using [coherence-audit](../skills/coherence-audit/SKILL.md) §Output Template
8. Record outcome in `decisions/curation-log.md` with M/S classification per finding

## Verify Before Proceeding

- ✅ Mechanical sweep ran and exit code recorded (0 / 1 / 2)
- ✅ Every false-positive finding has a one-line rationale
- ✅ Catalog-of-record rule applied to each disagreement
- ✅ ACT pass markers visible in the report
- ✅ Curation log updated

## Output

The audit report goes to `decisions/audits/coherence-YYYY-MM-DD.md`. If hard violations exist, this prompt also opens (or queues) the necessary Edition + Mall PRs.

## Related

- `/audit-mall`, `/prune-store`, `/cut-release`
- [coherence-audit](../skills/coherence-audit/SKILL.md)
