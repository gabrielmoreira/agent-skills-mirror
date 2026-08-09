---
name: omh-model-setup
description: [omh] Hermes Model Setup workflow: diagnose role-slot model configuration, guide provider connection, and apply changes only after diff approval. Use when the user says: model-setup, hermes model setup, set up my models, set up my model, configure my models, configure model provider, connect my model provider, set up model role slots.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, hermes-setup]
    category: hermes-setup
    phase: setup
    role: guide
    quality_tier: hermes-setup-gated
---

# Model Setup

This is a Hermes-native `model-setup` workflow skill.

## Why This Exists

`model-setup` exists to turn role-slot model configuration into a guided, read-before-write walkthrough instead of an unreviewed config edit.

## Do Not Use When

- The user is asking which model Hermes currently is, not asking to change or connect one.
- The request needs a repository code change rather than a local Hermes config or `.env` edit.
- No role slot, provider, or session-switch intent is named yet.

## Examples

Good example:

- Prompt: Help me set up my models — I want to connect a new provider for the main role slot.
- Expected behavior: Check the provider prerequisite, read-only diagnose the current main-slot assignment, guide account/token setup, show the config diff, and apply only after approval.
- Why: The request is role-slot model configuration and needs the shared setup contract.

Bad example:

- Prompt: model-setup: what model are you running right now?
- Expected behavior: Answer the identity question directly instead of starting a setup walkthrough.
- Why: A status question is not a configuration request and should not trigger a write-capable guide.

## Completion Checklist

- If a prerequisite is unmet, mark that item "not applicable" and continue with the rest of the guide instead of blocking or guessing.
- Success is applicable-only: verification passes when every applicable item is confirmed complete, not when every possible item exists.
- Every touched role slot was diagnosed, guided, diff-approved, and re-verified before being reported complete.

## Recovery Notes

- If a provider prerequisite is unmet, mark that role slot "not applicable" and continue with the remaining slots.
- If the diagnosed config cannot be read, report the read failure and stop before proposing a diff.
- If the user rejects a shown diff, keep the prior config as verified state and ask what to change.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `agent-board`, `gateway-intent-card`, `voice-operator`, `+33 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when the user wants Hermes to check or configure role-slot model assignments (main, realtime-search, design), connect a model provider, or switch the session model, following the shared prerequisite-check, diagnose, guide, diff-approved apply, and verify contract.

    Strong routing signals: `model-setup`, `hermes model setup`, `set up my models`, `set up my model`, `configure my models`, `configure model provider`, `connect my model provider`, `set up model role slots`, `switch my session model`, `모델 설정 도와줘`, `모델 설정`, `모델 연결`, `모델 프로바이더 설정`, `모델 슬롯 설정`

## Catalog Metadata

Category: `hermes-setup`
Phase: `setup`
Hermes role: `guide`
Quality tier: `hermes-setup-gated`
Reasoning demand: `light`

Quality bar:

- Prerequisite check: confirm the subscription, account, or capability the step needs exists before continuing; mark unmet prerequisites "not applicable" and skip them explicitly.
- Read-only diagnose: read the current Hermes config, `.env` keys, and installed version without writing anything.
- Guide: walk the user through any account creation, OAuth, or token issuance they must complete themselves.
- Diff-approved apply: show the exact config or `.env` diff and write only after the user explicitly approves it.
- Verify: re-read the updated config and report a completion checklist covering every applicable item.
- Treat each role slot (main, realtime-search, design) as an independent prerequisite/diagnose/apply unit instead of one combined change.

Handoff policy:

Run diagnosis and guidance directly in Hermes for role-slot model setup. Diagnosis only reads the existing Hermes config, `.env` keys, and installed version; it never writes anything on its own. Show the exact diff for any config or `.env` change and write it only after the user explicitly approves that diff. Secret values such as tokens and API keys are pasted by the user directly in chat and are never stored, logged, or echoed back beyond the immediate diff confirmation. Delegate to a selected coding executor only if the user needs a change outside chat-driven config edits.

Required inputs:

- current Hermes config file path
- target role slot (main, realtime-search, or design)
- provider account or API credential status

Expected outputs:

- read-only diagnosis of current role-slot model assignments
- diff-approved config write for the requested role slot
- verification checklist confirming the applied slot change

Artifact expectations:

- setup verification note when the wrapper captures it

Safety rules:

- Do not name or assume a specific model, provider tier, or price; ask the user which provider and role slot they want and read the current assignment instead of guessing.
- Keep prerequisite check, diagnosis, guidance, apply, and verify as separate, explicit steps.

## Runtime Evidence

Preferred harness for this skill: `coding-handling`.

```sh
omh runtime record --skill model-setup --harness coding-handling --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
