---
name: omh-agent-ops-review
description: [omh] Hermes agent ops review workflow: help managers inspect AI-agent progress, blockers, quality gates, and throughput levers. Use when the user says: agent-ops-review, agent ops review, agent productivity, operator productivity, manager view, quality dashboard, throughput review, agent work quality.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, operator]
    category: operator
    phase: manager-review
    role: tracker
    quality_tier: workflow-surface-gated
---

# Agent Ops Review

This is a Hermes-native `agent-ops-review` workflow skill.

## Why This Exists

`agent-ops-review` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: agent-ops-review show quality, blockers, and throughput for AI-agent work.
- Expected behavior: Produce `prepare_agent_ops_review` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: agent-ops-review claim Codex finished and CI passed because a handoff exists.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- The local command, managed path, config surface, and state artifact inspected are named.
- Blocking issues, warnings, and optional surfaces are separated.
- The next repair action is explicit and does not claim a reload or runtime observation.

## Recovery Notes

- If a managed path or config key is missing, route to setup/update repair instead of editing hidden state.
- If a reload or plugin load was not observed, keep the diagnostic result as local health evidence only.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `agent-board`, `gateway-intent-card`, `voice-operator`, `+33 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when Hermes should explain AI-agent work: quality gates, progress, blockers, next actions, and throughput.

    Strong routing signals: `agent-ops-review`, `agent ops review`, `agent productivity`, `operator productivity`, `manager view`, `quality dashboard`, `throughput review`, `agent work quality`, `coding progress quality`, `coding progress`, `where is codex`, `what's going on`, `status update please`, `what are you doing`, `what are you working on`, `where are we`, `今何してる`, `现在在做什么`, `qué está pasando`, `qu'est-ce qui se passe`, `was ist los`, `ai agent manager`, `관리자 입장`, `Codex 작업`, `Codex 작업이 어디까지`, `코덱스 작업`, `작업이 어디까지`, `진행됐는지`, `진행되었는지`, `처리량`, `작업 품질`, `진행상황`, `무슨일이노`, `뭔일임`, `무슨 일이야`, `뭐해`, `지금 뭐 하고 있어`, `작업상황 브리핑`, `어디까지 됐어`, `리서치 코딩 리뷰`

## Catalog Metadata

Category: `operator`
Phase: `manager-review`
Hermes role: `tracker`
Quality tier: `workflow-surface-gated`
Reasoning demand: `light`

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

- agent-ops-review/v1 card or guidance
- next action
- prepared-vs-observed boundary

Artifact expectations:

- agent-ops-review/v1 metadata-only runtime or wrapper card when recorded

Safety rules:

- An agent ops review card is not source retrieval, executor dispatch, coding progress, implementation, review, verification, CI, merge, platform delivery, provider billing, or live runtime telemetry evidence. If Hermes is the coding owner, summarize `hermes_coding_harness/v1` stage, lane owner, next action, and missing evidence.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

## Runtime Evidence

Preferred harness for this skill: `agent-ops-review`.

```sh
omh runtime record --skill agent-ops-review --harness agent-ops-review --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
