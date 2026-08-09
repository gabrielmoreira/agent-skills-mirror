---
name: omh-provider-profile-posture
description: [omh] Prepare provider-profile metadata without reading secrets or calling providers. Use when the user says: provider-profile-posture, provider profile posture, provider profile readiness, secret presence confirmation, connector profile posture, 공급자 프로필 상태, 시크릿 존재 확인, 커넥터 준비 상태.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, operations]
    category: operations
    phase: provider-profile-posture
    role: operator
    quality_tier: workflow-surface-gated
---

# Provider Profile Posture

This is a Hermes-native `provider-profile-posture` workflow skill.

## Why This Exists

`provider-profile-posture` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: Prepare provider profile posture for this connector using metadata-only secret presence.
- Expected behavior: Produce `prepare_provider_profile_posture` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: Read the secret, validate the credential, call the provider, or create a payment route.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- Provider ID, profile ID, requested capabilities, and secret-presence metadata are explicit.
- No secret value, credential validation, provider call, model route, wallet, or payment action is claimed.
- Any host observation reference remains supplied metadata, not a live connector check.

## Recovery Notes

- If required context is missing, ask one blocking question or route back to the narrower workflow.
- If runtime or wrapper evidence is unavailable, keep the status as not_observed and expose the next observable action.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `agent-board`, `gateway-intent-card`, `voice-operator`, `+33 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use for provider/profile capability and secret-presence preparation before connector or credential action.

    Strong routing signals: `provider-profile-posture`, `provider profile posture`, `provider profile readiness`, `secret presence confirmation`, `connector profile posture`, `공급자 프로필 상태`, `시크릿 존재 확인`, `커넥터 준비 상태`

## Catalog Metadata

Category: `operations`
Phase: `provider-profile-posture`
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

- provider_profile_posture/v1
- metadata-only secret requirements
- allowed and prohibited actions

Artifact expectations:

- provider_profile_posture/v1 metadata-only preparation record

Safety rules:

- Provider/profile posture is OMH-local preparation metadata; it is not credential validation, provider connectivity, model routing, payment/wallet, or host execution evidence.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

## Runtime Evidence

Preferred harness for this skill: `provider-profile-posture`.

```sh
omh runtime record --skill provider-profile-posture --harness provider-profile-posture --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
