---
name: controlflow-plan
description: "Use when a non-trivial repository task needs a durable, execution-ready ControlFlow plan before coding, especially for cross-file changes, migrations, architectural uncertainty, or explicit risk review."
---

# ControlFlow Plan

## Overview

Produce a saved ControlFlow plan without replacing the host's native planning workflow.
In Codex, native `/plan` is the preferred place to gather context and clarify the task;
this skill adds the durable artifact format, complexity tiers, semantic-risk review, and
restartability discipline.

Select the skill explicitly. In Codex, invoke it with `$controlflow-plan`.

## Plan Contract Sources

1. If the active repository contains `schemas/planner.plan.schema.json` and
   `plans/templates/plan-document-template.md`, read both and treat them as authoritative.
2. Otherwise use [references/plan-format.md](references/plan-format.md), the bundled
   standalone fallback contract.
3. If repository canonical files conflict with the bundled fallback, repository files win
   and the difference must be noted under `## Discoveries`.

## Workflow

1. Read the repository before phase decomposition. Keep verified facts separate from
   assumptions.
2. Create a saved plan for `SMALL`, `MEDIUM`, or `LARGE` work; skip it for truly
   `TRIVIAL` work unless the user explicitly requests an artifact.
3. Save to `plans/<task-slug>-plan.md` unless the user names another path.
4. Map concrete files, tests, commands, dependencies, boundaries, and existing patterns.
5. Read [references/complexity-tiers.md](references/complexity-tiers.md) and assign one
   tier. Any unresolved applicable `HIGH` semantic risk forces `LARGE`.
6. Fill every semantic-risk category exactly once: `data_volume`, `performance`,
   `concurrency`, `access_control`, `migration_rollback`, `dependency`, `operability`.
7. Keep phases incremental and executable. Each phase names files, tests, acceptance
   criteria, quality gates, dependencies, failure expectations, and numbered prose steps.
8. Preserve the five living-document sections for non-trivial plans:
   `## Progress`, `## Discoveries`, `## Decision Log`, `## Outcomes`, and
   `## Idempotence & Recovery`.
9. Add compact Mermaid diagrams when required by the active contract. Keep each diagram
   at or below 30 source lines.
10. Use `ABSTAIN` or `REPLAN_REQUIRED` when evidence is insufficient or confidence is
    below the contract threshold.
11. Hand every non-trivial ready plan to `$controlflow-verify` before implementation.

## Native Host Boundary

- Do not implement a second router, task state machine, approval engine, retry scheduler,
  subagent lifecycle, or memory layer.
- Use native host plan tracking for live progress and the saved plan for durable state.
- The host owns sandboxing and approvals.
- The host owns subagent orchestration; use it only when the user explicitly requests
  subagents or parallel agent work.
- Host memories are optional ambient context, never repository evidence.
- See [references/inline-execution.md](references/inline-execution.md) for the small amount
  of execution guidance that remains useful after plan approval.

## Planning Failure Checks

- Do not invent requirements that change behavior, scope, architecture, or destructive
  risk.
- Do not duplicate the full plan contract inside `SKILL.md`.
- Do not mark a plan ready without concrete automated verification.
- Do not add plugin-level runtime controls that Codex already owns.

## References

- `references/plan-format.md`
- `references/complexity-tiers.md`
- `references/inline-execution.md`
- `references/llm-behavior-guidelines.md`
