---
name: controlflow-spec
description: "Use before planning non-trivial work when requirements, acceptance criteria, boundaries, constraints, or success measures are not yet clear enough for a safe implementation plan."
---

# ControlFlow Spec

## Overview

Capture a short, durable specification before `/controlflow-claude-code:controlflow-planning`.
The spec records the outcome, exclusions, success proof, constraints, and unresolved questions
so planning does not infer requirements from loose chat context.

Invoke this skill via `/controlflow-claude-code:controlflow-spec`.

## When to Use

Use this skill before planning when:

- work is SMALL, MEDIUM, or LARGE and no accepted spec exists
- acceptance criteria, boundaries, constraints, risks, or success metrics are still implied
- the work crosses multiple files, plugin surfaces, schemas, or documentation paths
- planning would require inventing priorities, exclusions, or verification gates

Skip this skill for TRIVIAL fixes where the expected behavior and verification command are
already explicit.

## Workflow

1. Restate the requested outcome in one or two sentences.
2. Ask one clarification round only for requirements that would change scope, acceptance,
   constraints, or risk handling.
3. Save a Markdown spec artifact, usually at `plans/artifacts/<task-slug>/spec.md`, unless
   the user gives another path.
4. Keep the spec focused on requirements and proof of completion; do not decompose
   implementation phases.
5. Hand off to `/controlflow-claude-code:controlflow-planning` with `spec_path` and
   intended `plan_path`.

## Spec Capture Template

```
# Spec: <task name>

## Objective
What outcome is needed and why it matters.

## In-Scope
Files, workflows, behaviors, or artifacts that planning may include.

## Out-of-Scope
Related work that must not be absorbed into this effort.

## Acceptance Criteria
Observable conditions that must be true when the work is done.

## Constraints
Compatibility, governance, source-use, security, dependency, schedule, or verification limits.

## Success Metrics
Commands, review gates, artifacts, or measurable outcomes that prove completion.

## Risks/Open Questions
Unresolved assumptions, unknowns, and questions that block or shape planning.
```

## Handoff to Planning

After writing the spec artifact, invoke `/controlflow-claude-code:controlflow-planning`
with a concise handoff that includes:

- `spec_path`: the saved Markdown spec artifact
- `plan_path`: the intended plan artifact, usually `plans/<task-slug>-plan.md`
- objective summary
- in-scope and out-of-scope boundaries
- acceptance criteria and success metrics
- constraints and verification commands
- risks/open questions that must become research, clarification, or explicit assumptions
  in the plan

Example handoff phrasing:

Use `/controlflow-claude-code:controlflow-planning` to create `plans/<task-slug>-plan.md`
from `plans/artifacts/<task-slug>/spec.md`.

## Stop Condition

If the request is still ambiguous after one clarification round, stop before planning.
Ask the smallest set of blocking questions, explain which planning decision each answer
controls, and do not call planning until the answer is available or the user explicitly
accepts a documented assumption.
