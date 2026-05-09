---
name: controlflow-orchestration
description: "Use when executing a multi-step repository task in phases, especially when progress should be tracked with gates, approvals, retries, localized replanning, or optional subagent delegation instead of one long monolithic run."
---

# ControlFlow Orchestration

## Overview

Run a plan with explicit state, disciplined gates, bounded retries, and mandatory pre-execution plan review for non-trivial work. This skill ports the most useful parts of ControlFlow's Orchestrator into Codex without pretending Codex supports the same runtime contracts or tool surfaces.

## Workflow

1. Start from a saved plan artifact, preferably `plans/<task-slug>-plan.md`, or write one with `controlflow-planning`.
2. For non-trivial work, do not execute immediately. Run the strict plan review pipeline first:
   - `SMALL`: `controlflow-plan-audit`
   - `MEDIUM` and `LARGE`: `controlflow-plan-audit` and `controlflow-assumption-verifier`
   - `LARGE`: add `controlflow-executability-verifier` before execution
   - unresolved `HIGH` semantic risk: always include `controlflow-assumption-verifier`
3. If plan review returns blocking issues, revise the plan before implementation. Do not treat plan review as advisory noise.
4. Track state continuously: current phase, last completed verification, blocker, and next action. Update the user when switching phases or encountering risk.
5. Use wave execution only when ownership is clearly disjoint. Otherwise prefer sequential delivery.
6. Before each phase, run a pre-flight:
   - confirm scope
   - confirm targeted files
   - confirm validation command
   - note whether approval is required
7. Keep immediate blocking work local. Use subagents only when delegation is available and the user explicitly wants it.
8. Read [references/failure-taxonomy.md](references/failure-taxonomy.md) and [references/runtime-policy.json](references/runtime-policy.json). Retry transients carefully, give fix hints for small correctable failures, and replan only the affected phase when scope remains valid.
9. Gate destructive or high-blast-radius actions behind explicit approval, even if the surrounding phase is otherwise routine.
10. After each phase, run the relevant completion checks from [references/phase-checklist.md](references/phase-checklist.md). Do not move on while validation is still ambiguous.
11. Save plan-review artifacts under `plans/artifacts/<task-slug>/`.
12. Keep artifacts local and concise; use Markdown notes rather than raw JSON status dumps.

## Stop-the-Line Guidance

Stop the phase before starting the next one when verification fails, a plan assumption proves false, a security/data/contract risk appears, or required approval is missing. Retry only when the failure is transient or narrowly fixable within the approved scope and a concrete diagnosis is recorded. Replan the affected phase when the fix changes files, dependencies, acceptance criteria, phase order, or blast radius.

## Change Sizing Heuristic

Use roughly 100 changed lines per phase as a soft reviewability target. Split phases that mix unrelated concerns, cross many ownership boundaries, or would force reviewers to reason about too much state at once. Document exceptions for mechanical fixture, generated, or documentation-heavy edits where the verification story remains clear.

## Anti-Rationalization Table

| Pattern | Why It Fails | Required Action |
| ------- | ------------ | --------------- |
| Continue after a failed phase because the next phase looks independent | Later work can hide or compound the invalid state from the failed phase. | Stop, classify the failure, and either retry, replan locally, or escalate. |
| Retry the same command repeatedly without a new diagnosis | Blind retries consume retry budget and obscure root cause. | Record the cause being tested and change only the smallest relevant variable. |
| Merge several phases because the edits are nearby | Review and verification lose signal when unrelated outcomes share one gate. | Keep phases near the soft size target or split by behavior boundary. |
| Treat plan-review findings as advisory noise | Known plan defects become implementation defects. | Resolve blocking findings or revise the plan before execution. |
| Parallelize work with overlapping write sets | Concurrent edits can collide and invalidate verification evidence. | Serialize overlapping phases or split ownership so write sets are disjoint. |

## Adaptation Notes

- ControlFlow's original Orchestrator assumed a larger fixed subagent roster and tighter tool contracts than Codex guarantees.
- In Codex, keep the discipline, not the ceremony: state tracking, approvals, plan review, retries, and per-phase verification matter more than reproducing every schema field.
- When a phase stalls, prefer localized replanning over rewriting the whole plan.

## Common Mistakes

- Launching parallel work with overlapping write sets.
- Executing a `SMALL+` plan before running the strict plan review pipeline.
- Calling a phase "done" before running the actual verification command.
- Treating retries as free instead of diagnosing why a phase is looping.
- Translating ControlFlow's agent roster into Codex literally instead of using the available local tools and team conventions.

## References

- `references/runtime-policy.json`
- `references/failure-taxonomy.md`
- `references/phase-checklist.md`
- `references/tdd-patterns.md`
- `../controlflow-planning/references/llm-behavior-guidelines.md`
