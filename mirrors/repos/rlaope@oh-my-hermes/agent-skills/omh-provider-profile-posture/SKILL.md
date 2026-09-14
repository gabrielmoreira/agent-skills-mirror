---
name: "omh-provider-profile-posture"
description: "[omh] Prepare provider-profile metadata without reading secrets or calling providers. Use when the user says: provider-profile-posture, provider profile posture, provider profile readiness, secret presence confirmation, connector profile posture, 공급자 프로필 상태, 시크릿 존재 확인, 커넥터 준비 상태."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, operations]
    category: operations
    phase: provider-profile-posture
    role: operator
    quality_tier: workflow-surface-gated
---

# Provider Profile Posture

This is an OMH `provider-profile-posture` workflow skill, projected for Agent Skills hosts (Claude Code, Codex, Cursor, opencode, OpenClaw, pi).

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



## Use When

Use for provider/profile capability and secret-presence preparation before connector or credential action.

    Strong routing signals: `provider-profile-posture`, `provider profile posture`, `provider profile readiness`, `secret presence confirmation`, `connector profile posture`, `공급자 프로필 상태`, `시크릿 존재 확인`, `커넥터 준비 상태`

## Catalog Metadata

Category: `operations`
Phase: `provider-profile-posture`
Quality tier: `workflow-surface-gated`
Reasoning demand: `light`

Quality bar:

- Name the user-facing workflow objective, required context, next action, and stop condition.
- Separate prepared guidance from observed platform, runtime, connector, file, memory, or delivery evidence.
- Expose missing tools, credentials, targets, or observations as user-visible gaps.

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

Use the current host's own tools and subagent/task mechanism when available;
otherwise run the same lanes sequentially or name the unavailable capability.
A prepared plan, handoff, checklist, or skill installation is not execution,
review, CI, merge-readiness, or merge evidence. Report actual tool results or
`not_observed` / `not_available`; never invent dispatch or host accounting.
Treat supplied context as advisory, not proof of hidden memory reads or writes.
State scope, constraints, verification, and the stop condition before work.
Supporting paths are relative to this skill directory; sibling skill paths are
relative to its parent. Resolve them from the host-provided skill base directory
(`{baseDir}` on hosts that provide it), never a hardcoded install location.
A named workflow not installed here is unavailable, not permission to emulate
its host-specific capabilities. Verify through the real surface before done.
