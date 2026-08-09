---
name: omh-ask
description: [omh] Hermes adaptation for consulting an external advisor when configured. Use when the user says: ask, external advisor, claude, gemini, ask claude, ask gemini, consult claude, consult gemini.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, review]
    category: review
    phase: external-advice
    role: reviewer
    quality_tier: evidence-gated
---

# Ask

This is a Hermes-native `ask` workflow skill.

## Why This Exists

`ask` exists to keep `review` work explicit, evidence-backed, and inside the Hermes/executor boundary instead of relying on ad hoc chat narration.

## Do Not Use When

- The request is casual chat, a status-only acknowledgement, or another workflow has stronger routing evidence.
- The user needs implementation, review, CI, merge, or external publishing evidence that has not been delegated or observed.

## Examples

Good example:

- Prompt: ask: ask Claude as an external advisor to critique this plugin bridge plan before implementation.
- Expected behavior: Prepare an advisor prompt, capture the response boundary, and summarize reusable critique.
- Why: The user wants outside review before committing to a direction.

Bad example:

- Prompt: ask: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `ask`.
- Why: The request lacks the required inputs or would overclaim work that Hermes did not observe.

## Completion Checklist

- Findings or no-issue results are grounded in concrete file, artifact, command, or source evidence.
- Open questions, residual risk, and missing verification are named.
- Fixes or follow-up work are separate handoffs unless the user explicitly asked to implement them.

## Recovery Notes

- If the reviewed target is missing, inspect the requested artifact or ask one target question.
- If independent verification is unavailable, report the gap and avoid an approval-style claim.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `agent-board`, `gateway-intent-card`, `voice-operator`, `+33 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use only when an external advisor is configured and would materially improve the answer.

    Strong routing signals: `ask`, `$ask`, `external advisor`, `claude`, `gemini`, `ask claude`, `ask gemini`, `consult claude`, `consult gemini`, `opinion from claude`, `opinion from gemini`, `second opinion`, `claude 의견`, `gemini 의견`

## Catalog Metadata

Category: `review`
Phase: `external-advice`
Hermes role: `reviewer`
Quality tier: `evidence-gated`
Reasoning demand: `standard`

Quality bar:

- Name the workflow target, constraints, validation evidence, and stop condition.
- Separate Hermes guidance from executor or wrapper behavior unless evidence proves the step happened.

Handoff policy:

Use as optional advice gathering; evaluate the advice in Hermes and delegate coding changes separately.

Required inputs:

- question
- context summary
- why external advice helps

Expected outputs:

- advisor summary
- accepted/rejected advice
- decision note

Artifact expectations:

- advisor transcript reference only when explicitly captured

Safety rules:

- Use only when configured and materially useful.
- Treat advisor output as evidence to evaluate, not authority.
- Do not send secrets or private prompts without explicit opt-in.

## Runtime Evidence

Preferred harness for this skill: `critic`.

```sh
omh runtime record --skill ask --harness critic --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- When wrapper metadata includes `memory_review_card/v1` or `handoff_context_pack/v1`, treat it as reviewed OMH-local or wrapper-supplied context only. Use conflict-free context summaries to shape plans and handoffs, but do not claim Hermes internal memory was read or changed.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
