---
name: omh-skill-health
description: [omh] Skill Health workflow: prepare a metadata-only OMH skill portfolio dashboard with stale surfaces, observed failure signals, pending amendments, and top actions. Use when the user says: skill-health, skill health, skill portfolio health, skill dashboard, skill health dashboard, skill failure pattern dashboard, skill failure patterns, pending skill amendments.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, operations]
    category: operations
    phase: skill-health
    role: operator
    quality_tier: workflow-surface-gated
---

# Skill Health

This is a Hermes-native `skill-health` workflow skill.

## Why This Exists

`skill-health` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: skill-health show the OMH skill portfolio dashboard with stale surfaces, failure patterns, pending amendments, and top improvement actions.
- Expected behavior: Produce `prepare_skill_health` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: skill-health claim every skill is working and patch the failures automatically without observed signals or review.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- Dashboard scope, source surfaces, stale/duplicate criteria, and stop condition are explicit.
- Install/setup health is routed to doctor; catalog operations are routed to skill; failure retrospectives are routed to workflow-learning.
- No skill, prompt, doc, memory, or model behavior is claimed changed until a reviewed implementation records evidence.

## Recovery Notes

- If the request is about OMH setup, install, stale package paths, or command availability, route to doctor.
- If the request is a missed-route or self-improvement trace, route to workflow-learning before adding health actions.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `buzz`, `agent-board`, `gateway-intent-card`, `+34 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when operators need portfolio-level skill health without treating it as install repair, live execution success, or automatic skill mutation.

    Strong routing signals: `skill-health`, `skill health`, `skill portfolio health`, `skill dashboard`, `skill health dashboard`, `skill failure pattern dashboard`, `skill failure patterns`, `pending skill amendments`, `skill amendments`, `스킬 헬스`, `스킬 상태`, `스킬 대시보드`, `스킬 실패 패턴`, `스킬 개선 후보`, `스킬 보류 수정`

## Catalog Metadata

Category: `operations`
Phase: `skill-health`
Hermes role: `operator`
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

- skill_portfolio_health_dashboard/v1
- skill_failure_pattern_clusters/v1 when observed
- pending_skill_amendment_review/v1
- skill_health_action_plan/v1

Artifact expectations:

- skill_portfolio_health_dashboard/v1 with catalog, generated, reference, harness, and capability-surface status
- skill_failure_pattern_clusters/v1 only from supplied traces, tests, reviews, missed routes, or wrapper observations
- skill_health_action_plan/v1 with top actions, owner lane, verification path, and non-mutation boundary

Safety rules:

- A skill health dashboard is not install/setup health, live skill execution success, automatic skill mutation, model training, verification, review, CI, or proof that future routing is fixed.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

## Runtime Evidence

Preferred harness for this skill: `skill-health`.

```sh
omh runtime record --skill skill-health --harness skill-health --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
