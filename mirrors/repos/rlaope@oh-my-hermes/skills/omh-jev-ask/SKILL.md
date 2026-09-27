---
name: "omh-jev-ask"
description: "[omh] User named Jev for yes/no or pick-one probabilities: Jev ask: typed yes/no, pick-one, or scored questions to Jev with your own key; returns probabilities, never prose. Use when the user says: jev-ask, ask jev, jev question, jev score."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, gateway]
    category: gateway
    phase: jev-ask
    role: guide
    quality_tier: evidence-gated
    requires_tools: [omh_jev_ask]
---

# Jev Ask

Required: text to judge and independent typed questions. Output: Jev's probabilities, served model, and cost, or a non-answer status.

Read `omh-routing/references/jev-rail.md` before the first ask: consent, what leaves the machine, limits, and non-answer statuses. Prepared OMH routing is not execution or approval. Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

Contract: `references/full-contract.md`.

## Procedure

1. Check the rail: the user asked for Jev in this turn, and say in one line what `state` will carry.
2. Write independent, self-contained questions over one `state`: Noul with `criteria.true`/`criteria.false`, Choice with an `unknown` option, Score with ordered levels.
3. Call `omh_jev_ask` with `questions` (default model `jev-latest`; pin `jev-1.13.0` when a threshold was tuned).
4. Report each number verbatim with the served model, attempts, and `cost_usd` plus `cost_source`; 0.4 to 0.6 is uncertain.

## Completion Checklist

- Preserve workflow intent and stop conditions; load the full contract before claiming completion.
- Reply in the user's own words and the host's own voice: OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) stay in records and tool calls, never in the sentence the user reads unless they ask about one; and when a stop condition or a decision the user owns ends the turn, offer the next action as a question rather than declaring what will not be done.
- Report the tool's status, ask_id, served model, and cost source; a non-answer is reported as its status and is never an answer.
- Record observed delegation results; use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

## Recovery Notes

- Tool missing, `consent_not_observed`, or refused: follow the rail's recovery section; never simulate an answer.

## Workflow Lane

advisory local context
