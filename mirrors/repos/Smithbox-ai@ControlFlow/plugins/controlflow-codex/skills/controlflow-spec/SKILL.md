---
name: controlflow-spec
description: "Use before planning non-trivial Codex work when the requirements, acceptance criteria, boundaries, constraints, or success measures are not yet clear enough for a safe implementation plan."
---

# ControlFlow Spec

## Overview

Capture a short, durable specification before invoking `$controlflow-planning`. The spec is the requirements boundary for the plan: it records what outcome is needed, what is excluded, how success will be judged, and which questions must be answered before planning can proceed.

Use this skill for non-trivial repository work where Codex would otherwise need to infer scope or acceptance criteria from loose chat context.

## When to Use

Use `$controlflow-spec` before `$controlflow-planning` when:

- the task is `SMALL`, `MEDIUM`, or `LARGE` and no accepted spec exists
- the user describes a goal, feature, migration, cleanup, or policy change without crisp acceptance criteria
- scope boundaries, constraints, risks, or success metrics are still implied rather than written
- the work crosses multiple files, plugin surfaces, schemas, agents, or documentation paths
- planning would require Codex to invent priorities, exclusions, or verification gates

Skip this skill for `TRIVIAL` fixes where the expected behavior and verification command are already explicit.

## Workflow

1. Restate the requested outcome in one or two sentences.
2. Ask one clarification round only for requirements that would change scope, acceptance, constraints, or risk handling.
3. Save a Markdown spec artifact, usually at `plans/artifacts/<task-slug>/spec.md`, unless the user gives a different path.
4. Keep the spec focused on requirements and proof of completion. Do not decompose implementation phases here.
5. Hand off to `$controlflow-planning` with both the spec artifact path and the intended `plan_path`.

## Spec Capture Template

```markdown
# Spec: <task name>

## Objective
<What outcome is needed and why it matters.>

## In-Scope
<Files, workflows, behaviors, or artifacts that planning may include.>

## Out-of-Scope
<Related work that must not be absorbed into this effort.>

## Acceptance Criteria
<Observable conditions that must be true when the work is done.>

## Constraints
<Compatibility, governance, source-use, security, dependency, schedule, or verification limits.>

## Success Metrics
<Commands, review gates, artifacts, or measurable outcomes that prove completion.>

## Risks/Open Questions
<Unresolved assumptions, unknowns, and questions that block or shape planning.>
```

## Anti-Rationalization Table

| Pattern | Why It Fails | Required Action |
| ------- | ------------ | --------------- |
| Skip spec because requirements feel obvious | Familiar requests can still hide boundary, priority, or acceptance assumptions. | Write the smallest spec that records objective, scope, criteria, and constraints. |
| Inline spec into chat instead of artifact | Chat-only requirements are hard to review, link, update, or hand to planning. | Save the spec as Markdown and pass its path into the planning handoff. |
| Treat planning as the place to discover requirements | A plan should sequence known work, not decide what the user meant. | Resolve requirement-level uncertainty before `$controlflow-planning`. |
| Fill gaps with plausible defaults | Silent defaults become scope drift when later reviewers compare evidence to intent. | Mark assumptions and ask the single clarification round before proceeding. |
| Keep success criteria as broad intent | Words like "better" or "cleaner" do not tell execution what to verify. | Convert each success claim into a check, artifact, gate, or measurable condition. |

## Handoff to Planning

After writing the spec artifact, invoke `$controlflow-planning` with a concise handoff that includes:

- `spec_path`: the saved Markdown spec artifact
- `plan_path`: the intended plan artifact, usually `plans/<task-slug>-plan.md`
- objective summary
- in-scope and out-of-scope boundaries
- acceptance criteria and success metrics
- constraints and verification commands
- risks/open questions that must become research, clarification, or explicit assumptions in the plan

Example handoff phrasing:

`Use $controlflow-planning to create plan_path=plans/<task-slug>-plan.md from spec_path=plans/artifacts/<task-slug>/spec.md.`

## Stop Condition

If the request is still ambiguous after one clarification round, stop before planning. Prompt the user directly in Codex for the missing requirement, mirroring a `vscode_askQuestions` escalation: ask the smallest set of blocking questions, explain which planning decision each answer controls, and do not call `$controlflow-planning` until the answer is available or the user explicitly accepts a documented assumption.
