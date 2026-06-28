---
name: round-verification
description: Verify a CCB execution round and produce a machine-readable round result artifact.
---

# Round Verification

Use this skill after orchestrator returns a round summary and node reports.

## Inputs

- task packet
- planner verification contract
- orchestrator summary
- worker reports
- checker reports
- command/test evidence

## Output

The report must include:

```text
round result: pass|rework_node|partial|replan_required|global_blocker
```

## Rules

- `pass` requires evidence for the whole verification contract.
- `rework_node` is only for bounded node repair.
- `partial` preserves successful independent branches but marks dependent
  branches unfinished.
- `replan_required` means acceptance, design, split, or constraints must change
  outside the execution loop.
- `global_blocker` means no safe progress is possible without user/system
  intervention.
