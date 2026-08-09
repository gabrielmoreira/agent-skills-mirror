---
name: omh-decision-recall
description: [omh] Recall scoped reviewed rejected decisions without elevating them to approved memory. Use when the user says: decision-recall, rejected decision recall, rejected decisions, why was this rejected, previously rejected alternative, 거절된 결정, 기각된 대안.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, memory]
    category: memory
    phase: decision-recall
    role: memory-keeper
    quality_tier: workflow-surface-gated
---

# Decision Recall

This is a Hermes-native `decision-recall` workflow skill.

## Why This Exists

`decision-recall` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: Show rejected decisions for this project before we choose an alternative.
- Expected behavior: Produce `show_rejected_decision_recall` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: Claim the recalled rejected decision is an approved memory write or proof the replacement ran.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- The query, scope, tags, stale policy, and match limit are explicit.
- Only reviewed rejected candidates are returned; expired candidates stay excluded.
- Recall output is not presented as approved memory, source freshness, or execution evidence.

## Recovery Notes

- If required context is missing, ask one blocking question or route back to the narrower workflow.
- If runtime or wrapper evidence is unavailable, keep the status as not_observed and expose the next observable action.

## Workflow Lane

- Current lane: **Retained knowledge** (`memory-new`, `memory-sync`, `decision-recall`, `wiki`) - memory, rejected alternatives, wiki notes, retrieval, and staleness.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use for scoped reviewed rejected-decision context; it is not approved memory or execution evidence.

    Strong routing signals: `decision-recall`, `rejected decision recall`, `rejected decisions`, `why was this rejected`, `previously rejected alternative`, `거절된 결정`, `기각된 대안`

## Catalog Metadata

Category: `memory`
Phase: `decision-recall`
Hermes role: `memory-keeper`
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

- rejected_decision_recall/v1
- scoped rejected-decision matches
- claim boundary

Artifact expectations:

- rejected_decision_recall/v1 metadata-only recall result

Safety rules:

- Rejected-decision context is reviewed OMH-local context, not approved memory, Hermes memory, or execution evidence.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

## Runtime Evidence

Preferred harness for this skill: `decision-recall`.

```sh
omh runtime record --skill decision-recall --harness decision-recall --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
