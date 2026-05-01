---
mode: agent
description: "Supervisor: Run release preflight gates on Alex_ACT_Edition before cutting a release"
lastReviewed: 2026-04-30
---

# /preflight-release

Run the pre-release mechanical gates on `Alex_ACT_Edition`. This is the gate before `/cut-release`.

## Steps

1. Load skills: [release-preflight](../skills/release-preflight/SKILL.md), [version-management](../skills/version-management/SKILL.md), [coherence-audit](../skills/coherence-audit/SKILL.md)
2. Run `node scripts/coherence-check.cjs` — Edition ↔ Mall coherence must be clean
3. Verify the proposed bump matches the change set per [version-management.instructions.md](../instructions/version-management.instructions.md)
4. Confirm CHANGELOG entry exists and follows the format
5. Confirm any deprecations in the prior release have either matured (this is the major) or remain (this is still a minor)
6. Report: `READY` or `BLOCKED: <reasons>`

If `BLOCKED`, do not proceed to `/cut-release`. Fix the gates first.
