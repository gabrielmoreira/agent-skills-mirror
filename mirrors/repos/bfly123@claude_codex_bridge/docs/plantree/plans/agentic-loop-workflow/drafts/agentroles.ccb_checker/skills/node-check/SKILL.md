---
name: node-check
description: Verify one CCB worker node and reject hidden fallback, degradation, scope shrinkage, or missing evidence.
---

# Node Check

Use this skill after a worker returns a node result.

## Inputs

- worker result
- task packet reference
- assigned node scope
- acceptance criteria
- verification expectation

## Output

Return exactly one result class:

- `pass`
- `rework_required`
- `blocked`
- `non_converged`

Include check plan, evidence reviewed, findings, and required rework.
