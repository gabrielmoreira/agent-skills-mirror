---
name: omh-achievements
description: [omh] Hermes achievements observation workflow: summarize hermes-achievements badges, tiers, recent unlocks, and progress from local plugin artifacts. Use when the user says: achievements, achievement, badges, badge, my badges, show achievements, achievement summary, unlocked badges.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, observability]
    category: observability
    phase: telemetry-card
    role: tracker
    quality_tier: workflow-surface-gated
---

# Achievements

This is a Hermes-native `achievements` workflow skill.

## Why This Exists

`achievements` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: achievements show my unlocked badges and what is closest to the next tier.
- Expected behavior: Produce `show_achievements_summary` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: achievements recompute my session history and grant the missing badges.
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

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `buzz`, `agent-board`, `gateway-intent-card`, `+34 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when the user asks which achievements or badges they unlocked, badge progress or tiers, recent unlocks, or wants an achievements section prepared for a report.

    Strong routing signals: `achievements`, `achievement`, `badges`, `badge`, `my badges`, `show achievements`, `achievement summary`, `unlocked badges`, `badge progress`, `achievement tier`, `recent unlocks`, `badge share card`, `업적`, `배지`, `뱃지`, `도전과제`, `업적 요약`, `実績`, `バッジ`, `成就`, `徽章`

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

- hermes_achievements_observation/v1 summary or badge list
- recent unlocks and progress hints
- next action
- prepared-vs-observed boundary

Artifact expectations:

- hermes_achievements_observation/v1 metadata-only payload from `omh achievements` when recorded

Safety rules:

- An achievements card reflects only locally observed hermes-achievements plugin artifacts; it is not a session-history rescan, badge recomputation, unlock proof beyond those artifacts, or productivity evidence.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

## Runtime Evidence

Preferred harness for this skill: `coding-handling`.

```sh
omh runtime record --skill achievements --harness coding-handling --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
