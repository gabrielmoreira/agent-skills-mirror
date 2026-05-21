---
name: breaking-change-recovery
version: "1.0.0"
description: >
  Execute the six-phase breaking-change recovery workflow.
  Invoked from workflow-resilience Tier-3 escalation or manually when a merged
  commit breaks the runtime, schema, or governance pipeline.
triggers:
  - breaking change detected
  - runtime crash after merge
  - schema regression
  - CI gate newly failing after merge
deploy:
  copilot: ~/.copilot/skills/breaking-change-recovery/
  agents: ~/.agents/skills/breaking-change-recovery/
---

# Breaking-Change Recovery Skill

Reference: `instructions/breaking-change-recovery.instructions.md`

## When to invoke

- Any role detects a P0/P1 runtime or schema breakage after a merge.
- Consultant Tier-3 escalation hands off to this skill.

## Quick-start

1. **Identify** the breaking commit SHA and causal issue number.
2. **Post** `INCIDENT_OPEN` on the causal issue with severity + blocked teams.
3. **Revert** with `git revert <sha> --no-edit` — merge immediately.
4. **File** triage ticket: `fix: [regression description]` with `type:bug`.
5. **Fix** on branch `fix/<triage-ticket#>-<slug>`; add regression test.
6. **Post** `SMOKE_EVIDENCE` before re-merge.
7. **Re-author** casualties: close original (`resolution:superseded`), refile.

## Smoke evidence block template

```
## SMOKE_EVIDENCE
fix_pr: #N
breaking_sha: <sha>
- [x] runtime starts without error
- [x] regression test passes
- [ ] governance hook fires correctly (schema/hook fixes)
- [ ] affected team confirms unblocked (P0 only)

Signed-by: <alias>
Team&Model: <team>:<model>@<substrate>
Role: admin
```

## Worked example

Chain: #1917 (cause) → #1951 (triage) → #1952 / `c857ce8` (fix)
→ #1953 (casualty closed) → #1954 (casualty refiled).

See full narrative in `instructions/breaking-change-recovery.instructions.md`
Phase 6 "Worked Example" section.

## Escalation path

If the fix cannot be completed within one session, the Manager must post a
`BLOCKER_NOTE` on the triage ticket and elevate severity to P0.
