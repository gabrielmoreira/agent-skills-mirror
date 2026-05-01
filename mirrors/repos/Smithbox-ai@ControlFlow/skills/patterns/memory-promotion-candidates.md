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
