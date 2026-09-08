---
name: "omh-sales-pipeline-review"
description: "[omh] Turn a supplied CRM export or pipeline snapshot into an evidence-bound pipeline health, forecast, and follow-up review. Aliases: pipeline-review, forecast-review, deal-review. Use when the user says: sales-pipeline-review, sales pipeline review, pipeline review, pipeline health, pipeline coverage, deal review, deal health, sales forecast review."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, operations]
    category: operations
    phase: sales-pipeline-review
    role: operator
    quality_tier: decision-gated
---

# Sales Pipeline Review

Required: supplied snapshot and as-of time, definitions, prior outcomes, and owner. Output: scope, health, forecast, supported annexes, and follow-up handoff.

**HOLD:** Missing inputs or failed contract gates. Prepared OMH routing is not execution or approval. **Completion:** Follow the full-contract checklist.

Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

Agent/operator: `omh runtime workflow-artifact sales-pipeline-review prepare --input <json-file-or->` prepares bounded metadata only. Shared operator reference: `omh-routing/references/workflow-artifacts.md`.

Contract: `references/full-contract.md`. Procedure: `references/procedure.md`.

## Completion Checklist

- Preserve workflow intent and stop conditions; load the full contract before claiming completion.
- Record observed delegation results; otherwise return `not_available` or `not_observed`.
- Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

## Recovery Notes

- If a required input, authority, or runtime capability is unavailable, HOLD and name the smallest safe next action; do not invent observation or approval.

## Workflow Lane

advisory local context
