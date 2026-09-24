---
name: "omh-jev-done-check"
description: "[omh] Jev done check: does the gathered evidence support the completion claim? It can only object. Use when the user says: jev-done-check, jev done check, ask jev if this is done, jev evidence check."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, review]
    category: review
    phase: jev-done-check
    role: reviewer
    quality_tier: evidence-gated
    requires_tools: [omh_jev_ask]
---

# Jev Done Check

Required: each completion claim, observed evidence, and the goal. Output: objections per claim, or no_objection.

Read `omh-routing/references/jev-rail.md` before the first ask: consent, what leaves the machine, limits, and non-answer statuses. Prepared OMH routing is not execution or approval. Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

Contract: `references/full-contract.md`. Preset: `references/preset.md`.

## Procedure

1. Name what leaves the machine: each claim, an excerpt of observed output, and the goal.
2. Call `omh_jev_ask` with `preset: done_check/v1` and `state` {claim, evidence_excerpt, goal}, one ask per claim, at most 6.
3. Report each objection with its claim and rule; fix or withdraw an objected claim before reporting completion.

## Completion Checklist

- Preserve workflow intent and stop conditions; load the full contract before claiming completion.
- Reply in the user's own words and the host's own voice: OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) stay in records and tool calls, never in the sentence the user reads unless they ask about one; and when a stop condition or a decision the user owns ends the turn, offer the next action as a question rather than declaring what will not be done.
- Report the tool's status, ask_id, served model, and cost source; a non-answer is `not_observed` with `rule: not_answered:<status>`, never Jev's answer.
- Record observed delegation results; use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

## Recovery Notes

- Tool missing, `consent_not_observed`, or refused: follow the rail's recovery section; never simulate an answer.

## Workflow Lane

advisory local context
