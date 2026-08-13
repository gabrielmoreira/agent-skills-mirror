---
name: omh-gateway-intent-card
description: [omh] Hermes gateway intent workflow: normalize Discord, Slack, Telegram, and other gateway sessions into origin, thread, delivery, silent, attachment, and status-update policy. Use when the user says: gateway-intent-card, gateway intent, discord thread, slack thread, telegram delivery, discord delivery policy, slack delivery policy, telegram delivery policy.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, gateway]
    category: gateway
    phase: intent-card
    role: guide
    quality_tier: workflow-surface-gated
---

# Gateway Intent Card

This is a Hermes-native `gateway-intent-card` workflow skill.

## Why This Exists

`gateway-intent-card` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: gateway-intent-card route this Discord thread update silently unless action is needed.
- Expected behavior: Produce `prepare_gateway_intent_card` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: gateway-intent-card prove the Telegram attachment was sent.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- The origin platform, thread/session boundary, delivery target, and update policy are named.
- Prepared card or command output is separate from platform registration, send, attachment, or delivery evidence.
- The next wrapper action is explicit and platform-safe.

## Recovery Notes

- If platform metadata is missing, keep the card platform-neutral and ask for the target surface.
- If send or registration evidence is unavailable, show the adapter-owned action instead of claiming delivery.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `buzz`, `agent-board`, `gateway-intent-card`, `+34 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when Hermes needs platform-neutral gateway policy for a chat session, thread, delivery target, attachment, or status update.

    Strong routing signals: `gateway-intent-card`, `gateway intent`, `discord thread`, `slack thread`, `telegram delivery`, `discord delivery policy`, `slack delivery policy`, `telegram delivery policy`, `discord status update`, `slack status update`, `telegram status update`, `gateway delivery`, `gateway notification`, `channel delivery`, `session delivery`, `silent update`, `attachment policy`, `status update policy`, `webhook delivery`, `게이트웨이`, `디스코드`, `슬랙`, `텔레그램`, `알림`, `전달`, `채널`, `조용히`, `스레드`, `보내줘`

## Catalog Metadata

Category: `gateway`
Phase: `intent-card`
Hermes role: `guide`
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

- gateway-intent-card/v1 card or guidance
- next action
- prepared-vs-observed boundary

Artifact expectations:

- gateway-intent-card/v1 metadata-only runtime or wrapper card when recorded

Safety rules:

- A gateway intent card is not platform login, message send, thread mutation, attachment upload, or delivery evidence.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

## Runtime Evidence

Preferred harness for this skill: `gateway-intent-card`.

```sh
omh runtime record --skill gateway-intent-card --harness gateway-intent-card --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
