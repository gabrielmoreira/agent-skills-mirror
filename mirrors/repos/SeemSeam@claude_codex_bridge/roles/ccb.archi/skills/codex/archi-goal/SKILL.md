---
name: archi-goal
description: Produce goal-driven architecture guidance using Architec evidence plus code inspection. Use when the user has a specific architecture objective, boundary-stability goal, refactor target, subsystem redesign, or wants a plan for making future changes safer.
---

# Archi Goal

Use this skill when the user gives a specific architecture objective.

## Workflow

1. Restate the goal as an architecture constraint.
2. Identify the relevant modules, ownership boundaries, and runtime contracts.
3. Run `archi-full` when the goal depends on whole-project structure.
4. Run `archi-diff` when the goal is about the current patch.
5. Read `.architec/architec-summary.md` and targeted source files.
6. Return a staged plan with gates.

## Output

```text
Goal
- ...

Relevant Boundaries
- ...

Plan
1. ...
2. ...
3. ...

Risks
- ...

Gates
- ...
```

Keep the plan practical. Prefer preserving current working behavior over broad
rewrites.

