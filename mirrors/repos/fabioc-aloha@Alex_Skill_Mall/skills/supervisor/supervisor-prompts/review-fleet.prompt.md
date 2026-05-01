---
mode: agent
description: "Supervisor: Review the ACT-Edition fleet — heir registry, version drift, recent activity, fleet health"
lastReviewed: 2026-04-30
---

# /review-fleet

Periodic check on the ACT-Edition fleet. The Supervisor's first job is governance; this prompt produces the monthly health report.

## Steps

1. Load skills: [fleet-management](../skills/fleet-management/SKILL.md), [status-reporting](../skills/status-reporting/SKILL.md), [version-management](../skills/version-management/SKILL.md)
2. Run `node scripts/fleet-inventory.cjs` (or `--root <path>` for a non-default scan root). The script discovers heirs by scanning for `.github/.act-heir.json` markers — heirs declare themselves; the Supervisor never writes into heir repos.
3. Capture the resulting inventory: heir_id, edition_version, days-since-last-sync, owner.
4. Cross-reference with prior `decisions/fleet-review-*.md` to detect changes since last review.
5. Compute: heirs on latest, heirs N-1, heirs N-2+, heirs with stale `last_sync_at` (>90d), heirs with invalid markers.
6. Identify: heirs that should upgrade, heirs that have stalled, breaking changes that haven't propagated.
7. Produce report:
   - Distribution table (version → count)
   - Heirs needing attention (with reason)
   - Trends since last review
   - Recommended actions
8. File the report under `decisions/fleet-review-<YYYY-MM-DD>.md`.

**Calibrate severity.** A heir on N-1 is normal. A heir on N-3 with no recent activity is a question. A heir reporting a breaking-change miss is an incident — escalate via `/escalate-to-master`.
