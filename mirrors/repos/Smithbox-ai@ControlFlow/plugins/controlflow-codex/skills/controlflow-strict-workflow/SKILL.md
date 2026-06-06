---
name: controlflow-strict-workflow
description: "Use when you want the full ControlFlow-Codex process as one strict workflow, especially for non-trivial repository work that should move from saved plan to plan review to execution to code review with durable artifacts at each step."
---

# ControlFlow Strict Workflow

## Overview

Use this entry point when ControlFlow-Codex should run as a strict local workflow: plan, pre-execution review, execution, final review, and durable artifacts.

## Workflow

1. Route the task if needed with `controlflow-router`.
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
8. Use `controlflow-memory-hygiene` during long work when repo memory or persistent notes need discipline.

## Verification Story

Every phase claim needs evidence: command output, artifact path, review result, test result, or documented skip reason. Do not mark a phase complete from confidence, local intuition, or unstated inspection alone. Generic anti-rationalization rules live in [../controlflow-planning/references/llm-behavior-guidelines.md](../controlflow-planning/references/llm-behavior-guidelines.md).

## Default Artifact Set

- `plans/<task-slug>-plan.md`
- `plans/artifacts/<task-slug>/plan-audit.md`
- `plans/artifacts/<task-slug>/assumption-verifier.md`
- `plans/artifacts/<task-slug>/executability-verifier.md`

Only create the artifacts required for the current tier and risk profile.

## Completion Gate

Before calling the workflow complete, run the repository verification command, confirm required review artifacts exist, compare the aggregate changed scope to the approved plan, run `controlflow-review`, and update the lifecycle sections. The final review must reconcile out-of-scope changes, apply a novelty filter against prior phase findings, and re-check affected verified items. The exact lifecycle headings are `## Progress`, `## Discoveries`, `## Decision Log`, `## Outcomes`, and `## Idempotence & Recovery`; keep them current at each phase boundary and final review.

## References

- `../../USAGE.md`
- `../../templates/plan-audit-report-template.md`
- `../../templates/assumption-verifier-report-template.md`
- `../../templates/executability-verifier-report-template.md`
