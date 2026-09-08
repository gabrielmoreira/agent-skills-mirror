---
name: "omh-decision-prototype"
description: "[omh] Bounded decision prototype workflow: resolve one uncertain interaction, API, performance, or integration choice with a disposable, isolated experiment whose observed result feeds planning. Use when the user says: decision-prototype, decision prototype, prototype this uncertain choice before planning, prototype before planning, prototype the uncertain choice, run a small spike, small spike, spike solution."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, planning]
    category: planning
    phase: decision-prototype
    role: planner
    quality_tier: decision-gated
---

# Decision Prototype

Required: one decision, a bounded experiment, an isolated scratch boundary, and a measurement method. Output: a decision record, prepared handoff, observation ledger, and receipt.

**HOLD:** Missing inputs or failed contract gates. Prepared OMH routing is not execution or approval. **Completion:** Follow the full-contract checklist.

Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

Agent/operator: `omh runtime workflow-artifact decision-prototype prepare --input <json-file-or->` prepares bounded metadata only. Shared operator reference: `omh-routing/references/workflow-artifacts.md`.

Contract: `references/full-contract.md`. Procedure: `references/procedure.md`.

## Completion Checklist

- Preserve workflow intent and stop conditions; load the full contract before claiming completion.
- Record observed delegation results; otherwise return `not_available` or `not_observed`.
- Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

## Recovery Notes

- If a required input, authority, or runtime capability is unavailable, HOLD and name the smallest safe next action; do not invent observation or approval.

## Workflow Lane

advisory local context
