---
name: omh-run-efficiency
description: [omh] Report supplied local run efficiency while provider and host data stay unobserved. Use when the user says: run-efficiency, run efficiency report, local run efficiency, context utilization, tool duration report, 실행 효율 리포트, 컨텍스트 사용량, 도구 지연 시간.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, observability]
    category: observability
    phase: run-efficiency
    role: tracker
    quality_tier: workflow-surface-gated
---

# Run Efficiency

This is a Hermes-native `run-efficiency` workflow skill.

## Why This Exists

`run-efficiency` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: Show the local run efficiency report from this run's supplied context budget and timings.
- Expected behavior: Produce `show_run_efficiency_report` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: Claim this report proves provider billing, host load, or cron execution without observations.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- The run ID, context budget, surfaces, and supplied observations are explicit.
- Provider billing, cron, and host claims remain not_observed unless separately recorded.
- The report does not intercept, route, or execute provider or host work.

## Recovery Notes

- If provider metrics are unavailable, report only local metadata and mark provider truth not_observed.
- If cost or latency looks risky, surface a warning plus the next measurement rather than a completion claim.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `buzz`, `agent-board`, `gateway-intent-card`, `+34 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use for a bounded local efficiency report from supplied metadata with provider and host gaps explicit.

    Strong routing signals: `run-efficiency`, `run efficiency report`, `local run efficiency`, `context utilization`, `tool duration report`, `실행 효율 리포트`, `컨텍스트 사용량`, `도구 지연 시간`

## Catalog Metadata

Category: `observability`
Phase: `run-efficiency`
Hermes role: `tracker`
Quality tier: `workflow-surface-gated`
Reasoning demand: `standard`

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

- run_efficiency_report/v1
- context utilization
- not_observed provider and host gaps

Artifact expectations:

- run_efficiency_report/v1 metadata-only report

Safety rules:

- Run efficiency is supplied OMH-local metadata, not provider, billing, cron, or host evidence.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

## Runtime Evidence

Preferred harness for this skill: `run-efficiency`.

```sh
omh runtime record --skill run-efficiency --harness run-efficiency --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
