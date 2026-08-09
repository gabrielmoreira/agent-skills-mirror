---
name: omh-voice-input
description: [omh] Terse voice and mobile-style requests - turn short spoken-style asks into clarify, plan, status, handoff, or confirmation actions. Use when the user says: voice-operator, voice operator, voice-first, voice command, mobile command, short command, dictated command, dictated request.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, accessibility]
    category: accessibility
    phase: voice-routing
    role: guide
    quality_tier: workflow-surface-gated
---

# Voice Operator

This is a Hermes-native `voice-operator` workflow skill.

## Why This Exists

`voice-operator` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: voice-operator 'release before lunch, check risky parts' from mobile.
- Expected behavior: Produce `prepare_voice_operator_card` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: voice-operator assume the user approved a destructive action from a vague voice note.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- The short-input or voice-like request is clarified enough to avoid accidental action.
- The next action is readable, reversible when possible, and confirmation-gated when risky.
- Delivery, notification, or platform behavior is not claimed without wrapper evidence.

## Recovery Notes

- If transcript confidence or intent is weak, ask one short clarification before action.
- If platform delivery is unavailable, keep the response in chat and mark delivery not_observed.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `agent-board`, `gateway-intent-card`, `voice-operator`, `+33 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when Hermes receives terse voice/mobile-style requests and should produce concise clarification, plan, or status UX.

    Strong routing signals: `voice-operator`, `voice operator`, `voice-first`, `voice command`, `mobile command`, `short command`, `dictated command`, `dictated request`, `spoken request`, `speech command`, `accessibility`, `hands free`, `hands-free`, `phone command`, `phone request`, `push command`, `음성`, `음성으로`, `음성 명령`, `모바일 명령`, `모바일 음성`, `핸드폰`, `폰으로`, `말로`, `말로 한 요청`, `접근성`, `짧은 명령`, `짧게 말한 요청`

## Catalog Metadata

Category: `accessibility`
Phase: `voice-routing`
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

- voice-operator/v1 card or guidance
- next action
- prepared-vs-observed boundary

Artifact expectations:

- voice-operator/v1 metadata-only runtime or wrapper card when recorded

Safety rules:

- A voice operator card is not speech recognition, mobile notification delivery, platform action, or accepted execution evidence.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

## Runtime Evidence

Preferred harness for this skill: `voice-operator`.

```sh
omh runtime record --skill voice-operator --harness voice-operator --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
