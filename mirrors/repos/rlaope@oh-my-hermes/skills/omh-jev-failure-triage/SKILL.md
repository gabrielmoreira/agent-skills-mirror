---
name: "omh-jev-failure-triage"
description: "[omh] Jev failure triage: retry, fix a dependency, ask for access, or change approach on a failing run. Use when the user says: jev-failure-triage, jev failure triage, ask jev if this failure is transient."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, review]
    category: review
    phase: jev-failure-triage
    role: reviewer
    quality_tier: evidence-gated
    requires_tools: [omh_jev_ask]
---

# Jev Failure Triage

Required: the failing command, an error excerpt, and the retry count. Output: `failure_triage/v1` next move with its rule.

Read `omh-routing/references/jev-rail.md` before the first ask: consent, what leaves the machine, limits, and non-answer statuses. Prepared OMH routing is not execution or approval. Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

Contract: `references/full-contract.md`. Preset: `references/preset.md`.

## Procedure

1. Name what leaves the machine: the command and an error excerpt (plus earlier attempt excerpts when repeating).
2. Call `omh_jev_ask` with `preset: failure_triage/v1`, `state` {error_excerpt, last_command, earlier_attempts}, and `attempts_so_far`.
3. Report `policy_result.outcome` and its rule beside the raw answers.
4. Hand the fix to `build-failure-triage` or `agent-debug`; a rerun still needs the host's approval.

## Completion Checklist

- Preserve workflow intent and stop conditions; load the full contract before claiming completion.
- Reply in the user's own words and the host's own voice: OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) stay in records and tool calls, never in the sentence the user reads unless they ask about one; and when a stop condition or a decision the user owns ends the turn, offer the next action as a question rather than declaring what will not be done.
- Report the tool's status, ask_id, served model, and cost source; a non-answer is `not_observed` with `rule: not_answered:<status>`, never Jev's answer.
- Record observed delegation results; use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

## Recovery Notes

- Tool missing, `consent_not_observed`, or refused: follow the rail's recovery section; never simulate an answer.

## Workflow Lane

advisory local context
