---
name: "omh-product-discovery-validation"
description: "[omh] Test whether a customer problem, segment, and business hypothesis deserve product investment, ending in kill, pivot, persevere, or inconclusive before any PRD. Use when the user says: product-discovery-validation, product discovery validation, product discovery, customer discovery, customer discovery plan, zero to one validation, validate the problem before building, problem solution interview."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, planning]
    category: planning
    phase: product-discovery-validation
    role: planner
    quality_tier: decision-gated
---

# Product Discovery Validation

Required: problem, segment/evidence, owner, learning budget, and criteria. Output: a decision frame, evidence and customer plan, test portfolio, receipt, and GTM hypothesis.

**HOLD:** Missing inputs or failed contract gates. Prepared OMH routing is not execution or approval. **Completion:** Follow the full-contract checklist.

Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

Agent/operator: `omh runtime workflow-artifact product-discovery-validation build --input <json-file-or->` builds bounded metadata only. Shared operator reference: `omh-routing/references/workflow-artifacts.md`.

Contract: `references/full-contract.md`. Procedure: `references/procedure.md`.

## Completion Checklist

- Preserve workflow intent and stop conditions; load the full contract before claiming completion.
- Record observed delegation results; otherwise return `not_available` or `not_observed`.
- Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

## Recovery Notes

- If a required input, authority, or runtime capability is unavailable, HOLD and name the smallest safe next action; do not invent observation or approval.

## Workflow Lane

advisory local context
