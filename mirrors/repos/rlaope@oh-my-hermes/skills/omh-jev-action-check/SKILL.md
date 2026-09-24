---
name: "omh-jev-action-check"
description: "[omh] Jev action check before a risky command: secrets, outbound sends, blast radius; can only add a hold. Use when the user says: jev-action-check, jev action check, ask jev if this command is safe, jev risk check."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, review]
    category: review
    phase: jev-action-check
    role: reviewer
    quality_tier: evidence-gated
    requires_tools: [omh_jev_ask]
---

# Jev Action Check

Required: the command, working directory, and stated task. Output: hold, refuse_recommended, or no_extra_hold with its rule.

Read `omh-routing/references/jev-rail.md` before the first ask: consent, what leaves the machine, limits, and non-answer statuses. Prepared OMH routing is not execution or approval. Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

Contract: `references/full-contract.md`. Preset: `references/preset.md`.

## Procedure

1. Name what leaves the machine: the command, the working directory, and the stated task.
2. Call `omh_jev_ask` with `preset: action_check/v1` and `state` {command, cwd, stated_task} before anything runs.
3. Report the outcome and rule; on `hold` or `refuse_recommended` ask the user before running, and on `no_extra_hold` the host's normal approval still applies.

## Completion Checklist

- Preserve workflow intent and stop conditions; load the full contract before claiming completion.
- Reply in the user's own words and the host's own voice: OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) stay in records and tool calls, never in the sentence the user reads unless they ask about one; and when a stop condition or a decision the user owns ends the turn, offer the next action as a question rather than declaring what will not be done.
- Report the tool's status, ask_id, served model, and cost source; a non-answer is `hold` with `rule: not_answered:<status>`, never Jev's answer.
- Record observed delegation results; use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

## Recovery Notes

- Tool missing, `consent_not_observed`, or refused: follow the rail's recovery section; never simulate an answer.

## Workflow Lane

advisory local context
