---
name: "omh-jev-route"
description: "[omh] Jev route pick: answer an OMH route question about which workflow fits, recorded without re-routing. Use when the user says: jev-route, ask jev which workflow, jev pick the workflow."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, gateway]
    category: gateway
    phase: jev-route
    role: guide
    quality_tier: evidence-gated
    requires_tools: [omh_jev_ask]
---

# Jev Route

Required: an undecidable route's `route_question` block and the user's message. Output: Jev's pick as a clarification and a recorded answer.

Read `omh-routing/references/jev-rail.md` before the first ask: consent, what leaves the machine, limits, and non-answer statuses. Prepared OMH routing is not execution or approval. Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

Contract: `references/full-contract.md`.

## Procedure

1. Confirm the route carries `route_question` and the ladder lists `omh_jev_ask`; tell the user their message leaves the machine.
2. Call `omh_jev_ask` with the block unchanged as `route_question` and the message as `state`.
3. Offer Jev's top pick to the user as a question; the block's thresholds only shape the wording.
4. Record it with `omh_route_answer`, `answered_by: omh_jev_ask`, and the returned `ask_id`.

## Completion Checklist

- Preserve workflow intent and stop conditions; load the full contract before claiming completion.
- Reply in the user's own words and the host's own voice: OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) stay in records and tool calls, never in the sentence the user reads unless they ask about one; and when a stop condition or a decision the user owns ends the turn, offer the next action as a question rather than declaring what will not be done.
- Report the tool's status, ask_id, served model, and cost source; a non-answer is reported as its status and is never an answer.
- Record observed delegation results; use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

## Recovery Notes

- Tool missing, `consent_not_observed`, or refused: follow the rail's recovery section; never simulate an answer.

## Workflow Lane

advisory local context
