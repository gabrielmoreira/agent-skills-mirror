---
name: "omh-jev-review-gate"
description: "[omh] Jev review flags for a diff: auth, tests, migration risk, severity; flags only, never approves a merge. Use when the user says: jev-review-gate, jev review gate, ask jev to review this diff."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, review]
    category: review
    phase: jev-review-gate
    role: reviewer
    quality_tier: evidence-gated
    requires_tools: [omh_jev_ask]
---

# Jev Review Gate

Required: one file's diff per ask. Output: `review_flags/v1` advisory flags and severity; never an approval.

Read `omh-routing/references/jev-rail.md` before the first ask: consent, what leaves the machine, limits, and non-answer statuses. Prepared OMH routing is not execution or approval. Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

Contract: `references/full-contract.md`. Preset: `references/preset.md`.

## Procedure

1. State the files and the cost before the first ask; source diffs leave the machine.
2. Call `omh_jev_ask` with `preset: review_flags/v1` and `state` {file, diff}, one file per ask, at most 8.
3. Report each file's flags, the union of flags, and the highest severity as advisory (Jev) lines in the review.

## Completion Checklist

- Preserve workflow intent and stop conditions; load the full contract before claiming completion.
- Reply in the user's own words and the host's own voice: OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) stay in records and tool calls, never in the sentence the user reads unless they ask about one; and when a stop condition or a decision the user owns ends the turn, offer the next action as a question rather than declaring what will not be done.
- Report the tool's status, ask_id, served model, and cost source; a non-answer is `not_observed` with `rule: not_answered:<status>`, never Jev's answer.
- Record observed delegation results; use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

## Recovery Notes

- Tool missing, `consent_not_observed`, or refused: follow the rail's recovery section; never simulate an answer.

## Workflow Lane

advisory local context
