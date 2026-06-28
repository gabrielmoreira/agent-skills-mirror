---
name: bounded-work-item
description: Execute one bounded CCB work item and report evidence without changing workflow authority.
---

# Bounded Work Item

Use this skill when orchestrator assigns a single work node.

## Inputs

- node id
- task packet reference
- assigned scope and non-goals
- acceptance criteria
- verification expectation

## Output

Return exactly one result class:

- `done`
- `blocked`
- `needs_rework`

Include files touched, commands run, verification evidence, and unresolved
blockers.
