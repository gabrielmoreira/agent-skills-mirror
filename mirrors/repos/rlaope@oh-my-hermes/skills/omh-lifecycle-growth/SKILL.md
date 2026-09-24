---
name: "omh-lifecycle-growth"
description: "[omh] Turn an observed onboarding, activation, retention, re-engagement, referral, or monetization problem into one consent-safe in-app journey or growth experiment plan with a bounded readout and an explicit decision. Use when the user says: lifecycle-growth, lifecycle growth, lifecycle marketing, lifecycle messaging, in-app journey, in-app message campaign, onboarding journey, onboarding nudge."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, strategy]
    category: strategy
    phase: lifecycle-growth
    role: operator
    quality_tier: decision-gated
---

# Lifecycle Growth

Required: lifecycle objective, audience/events, consent, budget, and owner. Output: a brief, audience/safety policy, experiment, readout, and handoff.

**HOLD:** Missing inputs or failed contract gates. Prepared OMH routing is not execution or approval. **Completion:** Follow the full-contract checklist.

Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

Agent/operator: `omh runtime workflow-artifact lifecycle-growth build --input <json-file-or->` builds bounded metadata only. Shared operator reference: `omh-routing/references/workflow-artifacts.md`.

Contract: `references/full-contract.md`. Procedure: `references/procedure.md`.

## Completion Checklist

- Preserve workflow intent and stop conditions; load the full contract before claiming completion.
- Reply in the user's own words and the host's own voice: OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) stay in records and tool calls, never in the sentence the user reads unless they ask about one; and when a stop condition or a decision the user owns ends the turn, offer the next action as a question rather than declaring what will not be done.
- Record observed delegation results; otherwise return `not_available` or `not_observed`.
- Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

## Recovery Notes

- If a required input, authority, or runtime capability is unavailable, HOLD and name the smallest safe next action; do not invent observation or approval.

## Workflow Lane

advisory local context
