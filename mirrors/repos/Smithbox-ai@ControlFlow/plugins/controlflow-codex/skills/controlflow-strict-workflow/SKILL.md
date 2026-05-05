---
name: controlflow-strict-workflow
description: "Use when you want the full ControlFlow-Codex process as one strict workflow, especially for non-trivial repository work that should move from saved plan to plan review to execution to code review with durable artifacts at each step."
---

# ControlFlow Strict Workflow

## Overview

This is the recommended entry point when you want ControlFlow-Codex to behave like a system rather than a loose bag of skills. It coordinates the strict sequence of planning, pre-execution review, execution, and final review.

## Workflow

1. Start by routing the task if needed with `controlflow-router`.
2. Write a saved plan with `controlflow-planning` at `plans/<task-slug>-plan.md`.
3. Run the pre-execution review pipeline based on complexity:
   - `TRIVIAL`: optional strict review
   - `SMALL`: `controlflow-plan-audit`
   - `MEDIUM`: `controlflow-plan-audit` + `controlflow-assumption-verifier`
   - `LARGE`: `controlflow-plan-audit` + `controlflow-assumption-verifier` + `controlflow-executability-verifier`
   - unresolved `HIGH` semantic risk: include `controlflow-assumption-verifier`, and strongly consider `controlflow-executability-verifier`
4. Save reviewer outputs in `plans/artifacts/<task-slug>/`.
5. If review blocks the plan, revise the plan first. Do not skip ahead to execution.
6. Execute the approved plan with `controlflow-orchestration`.
7. Review completed implementation with `controlflow-review`.
8. Use `controlflow-memory-hygiene` throughout long-running work when repo memory or persistent notes need discipline.

## Default Artifact Set

- `plans/<task-slug>-plan.md`
- `plans/artifacts/<task-slug>/plan-audit.md`
- `plans/artifacts/<task-slug>/assumption-verifier.md`
- `plans/artifacts/<task-slug>/executability-verifier.md`

Only create the artifacts required for the current tier and risk profile.

## Completion Gate

Before calling the workflow complete:

1. Run the repository verification command that actually proves the claim.
2. Confirm plan review artifacts exist for the required tier.
3. Confirm execution results line up with the approved plan or document scope drift.
4. Run `controlflow-review` for code-level findings.
5. Confirm the plan's lifecycle sections (`## Progress`, `## Discoveries`, `## Decision Log`, `## Outcomes`, `## Idempotence & Recovery`) are current: `## Progress` reflects all completed phases, `## Discoveries` records any unexpected findings, `## Decision Log` captures key execution decisions, `## Outcomes` describes what was achieved or deferred, and `## Idempotence & Recovery` notes which phases are safe to re-run. Update these sections at each phase boundary during execution and again at final review.

## Common Mistakes

- Treating the workflow as optional ceremony for `SMALL+` tasks.
- Running orchestration before plan review is resolved.
- Forgetting to persist reviewer outputs as artifacts.
- Claiming success without fresh verification evidence.

## References

- `../../USAGE.md`
- `../../templates/plan-audit-report-template.md`
- `../../templates/assumption-verifier-report-template.md`
- `../../templates/executability-verifier-report-template.md`
