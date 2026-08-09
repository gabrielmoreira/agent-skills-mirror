---
name: omh-workflow-learning
description: [omh] Hermes workflow learning workflow: classify and review self-improvement store routes as an auxiliary review lane before durable writes, then record workflow attempts as metadata-only traces, evals, review queues, patch proposals, regression cases, audits, indexes, and exports. Use when the user says: workflow-learning, workflow learning, route-signal, self-improvement store routing, store route review, memory skill wiki routing, learning trace, learning audit.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, optimization]
    category: optimization
    phase: workflow-learning
    role: tracker
    quality_tier: workflow-surface-gated
---

# Workflow Learning

This is a Hermes-native `workflow-learning` workflow skill.

## Why This Exists

`workflow-learning` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: workflow-learning route this self-improvement note before deciding whether it is memory, skill, wiki, failure-retrospective, or automation material.
- Expected behavior: Produce `record_workflow_learning_trace` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: workflow-learning silently patch the skill and claim future behavior is fixed.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- Confirm the workflow target, evidence boundary, and stop condition are named.
- Report which outputs are prepared, observed, blocked, or missing.
- Name the smallest next verification or handoff instead of claiming completion from narration.

## Recovery Notes

- If required context is missing, ask one blocking question or route back to the narrower workflow.
- If runtime or wrapper evidence is unavailable, keep the status as not_observed and expose the next observable action.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `agent-board`, `gateway-intent-card`, `voice-operator`, `+33 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use after a Hermes/OMH workflow attempt should become inspectable, evaluable, routed to memory/skill/wiki/failure-retrospective/automation review, persisted as a metadata-only store-route decision, queued for review, audited, replayable as a regression, converted to a patch handoff, exported, repaired after index drift, or captured as a missed-route signal without raw prompts. Store-route records are an auxiliary review lane surfaced by `learning review` and `learning store-routes`; they are not canonical learning index/export records until a reviewed destination produces its own artifact.

    Strong routing signals: `workflow-learning`, `workflow learning`, `route-signal`, `self-improvement store routing`, `store route review`, `memory skill wiki routing`, `learning trace`, `learning audit`, `self improvement store routing`, `store routing`, `where should this learning go`, `audit learning`, `learning review`, `review queue`, `review-route`, `store-routes`, `learning readiness`, `learning export`, `export bundle`, `learning index`, `index rebuild`, `execution trace`, `skill improvement`, `improvement candidate`, `regression corpus`, `GEPA`, `VPRM`, `process supervision`, `why did this route`, `missed route`, `missed workflow`, `did not use OMH`, `OMH was not used`, `learn from this run`, `이번 실행 학습`, `스킬 개선`, `회귀 케이스`, `실행 기록`, `학습 기록`, `학습 점검`, `학습 준비 상태`, `학습 내보내기`, `OMH 안 썼어`, `워크플로 누락`, `라우팅 누락`

## Catalog Metadata

Category: `optimization`
Phase: `workflow-learning`
Hermes role: `tracker`
Quality tier: `workflow-surface-gated`
Reasoning demand: `heavy`

Quality bar:

- Name the user-facing workflow objective, required context, next action, and stop condition.
- Separate prepared guidance from observed platform, runtime, connector, file, memory, or delivery evidence.
- Expose missing tools, credentials, targets, or observations as user-visible gaps.

Handoff policy:

Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded.

Required inputs:

- user request
- target context
- delivery or status expectation
- known missing evidence

Expected outputs:

- workflow-learning/v1 card or guidance
- next action
- prepared-vs-observed boundary

Artifact expectations:

- workflow-learning/v1 metadata-only runtime or wrapper card when recorded

Safety rules:

- A workflow learning trace, self-improvement store route, patch proposal, or export is process evidence for review. It is not automatic model training, memory mutation, skill mutation, wiki write, automation creation, execution, verification, CI, or merge evidence.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

## Runtime Evidence

Preferred harness for this skill: `workflow-learning`.

```sh
omh runtime record --skill workflow-learning --harness workflow-learning --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
