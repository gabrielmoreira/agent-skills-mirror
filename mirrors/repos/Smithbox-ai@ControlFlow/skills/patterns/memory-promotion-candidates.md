# Memory Promotion Candidates

Adapted from free-code-main extractMemories — this is a manual checklist for the agent to run, NOT a background task.

## Process

Scan the ongoing conversation/transcript to produce a structured list of candidate facts. Each candidate line MUST use this format:

- `subject`: short canonical fact subject (cross-plan, not task-specific)
- `proposed_classification`: one of `user`/`feedback`/`project`/`reference`
- `evidence_pointer`: file:line citation
- `recommend_promote`: `yes` / `no` / `defer`

The output of this skill feeds directly into Checklist C of `skills/patterns/repo-memory-hygiene.md`.

## Related

- [repo-memory-hygiene.md](repo-memory-hygiene.md)
- [MEMORY-ARCHITECTURE.md](../../docs/agent-engineering/MEMORY-ARCHITECTURE.md)
- [governance/runtime-policy.json#memory_hygiene](../../governance/runtime-policy.json)

## Skill-Proposal Candidate Criteria

When scanning a phase or completion transcript for memory candidates, also evaluate each candidate against the skill-proposal threshold:

| Criterion | Required Value | Notes |
| --------- | -------------- | ----- |
| `confidence` | ≥ 0.85 | Calculated by the scanning agent from evidence strength, reproducibility across ≥ 2 independent tasks, and applicability breadth. |
| `cross_plan_applicable` | true | The pattern must be applicable to at least one future plan unrelated to the current task. |
| `already_in_skills` | false | If the same pattern is already covered by an existing skill in `skills/patterns/`, do not propose a duplicate. Check `skills/index.md` first. |
| `actionable_without_task_context` | true | The skill must be useful to an agent with no knowledge of the current task slug. |

A candidate that meets ALL four criteria above should be recorded as a skill-proposal candidate using `plans/templates/skill-proposal-template.md`. Candidates that fail any criterion should be recorded as plain memory facts (if cross-plan) or dropped (if task-specific).

### Confidence Calculation

Confidence is estimated (not measured) using these signals:

- **Evidence strength**: the candidate is backed by at least two concrete file/line citations. (+0.2 per additional independent source above 1.)
- **Reproducibility**: the pattern appeared in ≥ 2 independent task executions or phases. (+0.3 for each additional independent occurrence.)
- **Breadth**: the pattern applies to ≥ 3 distinct agent roles or workflow contexts. (+0.2.)
- **No counter-evidence**: no known exception or anti-pattern in the current codebase. (+0.15.)

Sum the signals. If the total ≥ 0.85, the candidate passes the threshold.
