---
name: controlflow-orchestration
description: "Use when executing a multi-step repository task in phases, especially when progress should be tracked with gates, approvals, retries, localized replanning, or optional sub-agent delegation instead of one long monolithic run."
---

# ControlFlow Orchestration

## Overview

Execute an approved plan with explicit state, disciplined gates, bounded retries, and
local evidence. Keep ControlFlow's orchestration discipline without assuming VS Code agent
runtime contracts.

Invoke this skill via `/controlflow-claude-code:controlflow-orchestration`.

## Local Contract

- Start from a saved plan, preferably `plans/<task-slug>-plan.md`; create one with
  `/controlflow-claude-code:controlflow-planning` if needed.
- Confirm strict plan review before executing non-trivial work.
- Track current phase, last verification, blocker, and next action.
- Apply [../controlflow-planning/references/llm-behavior-guidelines.md](../controlflow-planning/references/llm-behavior-guidelines.md)
  for generic scope and verification discipline.

## Workflow

1. Confirm plan path, current phase, target files, validation command, and approval needs.
2. For non-trivial work, run or verify review routing first:
   - SMALL: plan-audit
   - MEDIUM/LARGE: plan-audit + assumption-verifier
   - LARGE: add executability-verifier
   - unresolved HIGH risk: include assumption-verifier
3. If review blocks, revise the plan before implementation.
4. Use wave execution only when write ownership is clearly disjoint; otherwise serialize
   phases.
5. Keep immediate blocking work in the current conversation context. Use Claude Code
   sub-agents only when the task benefit is clear and the user wants delegation.
6. Use [references/failure-taxonomy.md](references/failure-taxonomy.md) and
   [references/runtime-policy.json](references/runtime-policy.json) for retry and replan
   decisions.
7. Gate destructive or high-blast-radius actions behind explicit approval.
8. After each phase, run [references/phase-checklist.md](references/phase-checklist.md)
   checks and update user-visible state before moving on.
9. Save plan-review artifacts under `plans/artifacts/<task-slug>/` and keep them concise
   Markdown.

## Stop-the-Line Guidance

Stop the phase before starting the next one when verification fails, a plan assumption
proves false, a security/data/contract risk appears, or required approval is missing.
Retry only with a recorded diagnosis. Replan the affected phase when the fix changes
files, dependencies, acceptance criteria, phase order, or blast radius.

## Change Sizing Heuristic

Use roughly 100 changed lines per phase as a soft reviewability target. Split unrelated
concerns, overlapping write sets, or broad ownership crossings. Document exceptions for
mechanical fixture, generated, or documentation-heavy edits where verification remains
clear.

## Orchestration-Specific Failure Checks

- Do not continue after a failed phase without classification and diagnosis.
- Do not retry the same command repeatedly without changing the smallest relevant
  variable.
- Do not merge nearby but unrelated phase outcomes under one gate.
- Do not treat plan-review blockers as advisory.

## References

- `references/runtime-policy.json`
- `references/failure-taxonomy.md`
- `references/phase-checklist.md`
- `references/tdd-patterns.md`
- `../controlflow-planning/references/llm-behavior-guidelines.md`
