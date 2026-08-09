---
name: omh-ops-observability-card
description: [omh] Hermes ops observability workflow: prepare an operations command-board for wrapper-safe token, cost, latency, run history, queue, failure-mode, external metric-provider, and service-quality evidence boundaries. Use when the user says: ops-observability-card, observability card, operations command board, ops command board, service quality board, service quality, external metric provider, metric provider.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, observability]
    category: observability
    phase: telemetry-card
    role: tracker
    quality_tier: workflow-surface-gated
---

# Ops Observability Card

This is a Hermes-native `ops-observability-card` workflow skill.

## Why This Exists

`ops-observability-card` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: ops-observability-card show token, cost, latency, supplied Prometheus/Grafana metrics, and missing service-quality evidence for this loop.
- Expected behavior: Produce `prepare_ops_observability_card` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: ops-observability-card claim exact provider billing, healthy SLO, incident closure, or remediation completion from local estimates.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- The run or workflow scope, metric window, failure modes, and cost/latency boundary are named.
- Local telemetry, provider truth, billing truth, and completion evidence are separate states.
- Warnings name the next measurement or operator review action.

## Recovery Notes

- If provider metrics are unavailable, report only local metadata and mark provider truth not_observed.
- If cost or latency looks risky, surface a warning plus the next measurement rather than a completion claim.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `agent-board`, `gateway-intent-card`, `voice-operator`, `+33 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when automation, loops, gateway work, executor handoffs, or service operations need a safe command-board for cost, latency, token, history, failure-mode, supplied metric-provider, and service-quality visibility.

    Strong routing signals: `ops-observability-card`, `observability card`, `operations command board`, `ops command board`, `service quality board`, `service quality`, `external metric provider`, `metric provider`, `prometheus metrics`, `grafana metrics`, `cost telemetry`, `latency telemetry`, `token telemetry`, `run history`, `loop telemetry`, `failure mode`, `monitor tokens`, `service health`, `slo dashboard`, `비용`, `토큰`, `지연시간`, `관측성`, `운영 지휘판`, `서비스 품질`, `메트릭`, `프로메테우스`, `그라파나`

## Catalog Metadata

Category: `observability`
Phase: `telemetry-card`
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

- ops-observability-card/v1 card or guidance
- external_metric_provider/v1 payload contract
- external_metric_provider_adapter/v1 adapter contract
- ops_service_quality_board/v1 service-quality board
- typed service-quality downgrade gaps
- next action
- prepared-vs-observed boundary

Artifact expectations:

- ops-observability-card/v1 metadata-only runtime or wrapper card when recorded
- external_metric_provider/v1 supplied metric payload when available
- external_metric_provider_adapter/v1 connector-ready adapter metadata when available
- ops_service_quality_board/v1 evidence-gated service-quality board

Safety rules:

- An ops observability card is not billing truth, provider quota truth, live metric-provider access, complete tracing, SLO pass, incident closure, root-cause proof, remediation completion, performance proof, or successful workflow completion evidence.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

## Runtime Evidence

Preferred harness for this skill: `ops-observability-card`.

```sh
omh runtime record --skill ops-observability-card --harness ops-observability-card --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
