# Spec-Driven Development

> **Decision rule:** Use once scope/acceptance criteria must be written down (escalation from `idea-to-prompt.md`). If the request is still a vague idea with no concrete scope, start with `idea-to-prompt.md` first.

## Purpose

Use this skill when a request is large enough that planning would require silent choices about scope, acceptance, constraints, or success. A spec is the pre-planning contract: it records the problem, the boundary, and the evidence that will prove the work is done.

For TRIVIAL fixes with clear inputs and expected output, proceed directly to planning or implementation. For anything ambiguous, cross-cutting, or high-risk, write the spec first.

## Decision Triggers

| Situation | Required Action |
| --------- | --------------- |
| The request contains vague goals, broad verbs, or undefined success words such as "improve", "modernize", or "make better" | Write a spec before planning. Convert the goal into testable acceptance criteria. |
| The work affects multiple modules, agents, schemas, governance files, or user-visible workflows | Write a spec before planning. Capture ownership, affected surfaces, and verification gates. |
| The plan would need to invent constraints, priorities, or out-of-scope boundaries | Write a spec before planning. Surface assumptions and unresolved questions. |
| The task is small, localized, and already has clear expected behavior plus a known verification command | Proceed to planning or implementation. Keep the acceptance criteria in the task notes. |
| The request is urgent but unclear | Write a short spec, not no spec. Use the smallest artifact that removes ambiguity. |

## Required Spec Elements

| Element | What It Must Capture |
| ------- | -------------------- |
| Objectives | What outcome is being pursued, who benefits, and why this change matters. |
| Scope Boundaries | What files, systems, workflows, or behaviors are in scope, including any known ownership limits. |
| Acceptance Criteria | Observable conditions that must be true for the work to be accepted. Prefer testable statements over intent. |
| Out-of-Scope | Related work that is explicitly excluded so later planning does not absorb it by inertia. |
| Key Constraints | Technical, governance, security, compatibility, schedule, source-use, or verification constraints that shape the solution. |
| Success Metrics | The evidence that will be used to judge completion, such as passing commands, schema checks, performance targets, or review gates. |

## Anti-Rationalization Deltas

Apply the canonical Anti-Rationalization Table in `skills/patterns/llm-behavior-guidelines.md` for silent assumptions and generic scope rationalizations. For spec work, also enforce these local deltas:

| Pattern | Required Action |
| ------- | --------------- |
| Skip the spec because requirements feel obvious | Write a short spec with scope, acceptance criteria, and constraints. |
| Treat the implementation plan as the spec | Capture objectives and boundaries before sequencing tasks. |
| Leave success criteria as broad intent | Rewrite each success claim as a test, gate, metric, or artifact requirement. |
| Delay the spec until after implementation | Spec first, then plan, then execute against the accepted boundary. |

## Handoff To Planner

Produce a Markdown spec artifact before Planner creates or revises the implementation plan. Store task-specific specs under `plans/artifacts/<task-slug>/spec.md` unless the conductor names a more specific artifact path.

The handoff should include:

- `trace_id` or task slug, if available.
- Objective and short context summary.
- Scope in and scope out.
- Acceptance criteria and success metrics.
- Key constraints and verification commands.
- Open questions, with a clear `NEEDS_INPUT` signal if planning cannot proceed safely.

Planner consumes the spec as the source for phases, dependencies, skill references, and verification gates. If Planner discovers that the spec is incomplete, it must return to clarification rather than inventing missing boundaries.
