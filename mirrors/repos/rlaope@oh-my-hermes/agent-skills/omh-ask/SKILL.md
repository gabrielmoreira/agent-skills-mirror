---
name: "omh-ask"
description: "[omh] Hermes adaptation for consulting an external advisor when configured. Use when the user says: ask, external advisor, ask claude, ask gemini, consult claude, consult gemini, opinion from claude, opinion from gemini."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, review]
    category: review
    phase: external-advice
    role: reviewer
    quality_tier: evidence-gated
---

# Ask

This is an OMH `ask` workflow skill, projected for Agent Skills hosts (Claude Code, Codex, Cursor, opencode, OpenClaw, pi).

## Why This Exists

`ask` exists to keep `review` work explicit, evidence-backed, and inside the Hermes/executor boundary instead of relying on ad hoc chat narration.

## Do Not Use When

- The request is casual chat, a status-only acknowledgement, or another workflow has stronger routing evidence.
- The user needs implementation, review, CI, merge, or external publishing evidence that has not been delegated or observed.

## Examples

Good example:

- Prompt: ask: ask Claude as an external advisor to critique this plugin bridge plan before implementation.
- Expected behavior: Prepare an advisor prompt, capture the response boundary, and summarize reusable critique.
- Why: The user wants outside review before committing to a direction.

Bad example:

- Prompt: ask: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `ask`.
- Why: The request lacks the required inputs or would overclaim work that Hermes did not observe.

## Completion Checklist

- Findings or no-issue results are grounded in concrete file, artifact, command, or source evidence.
- Open questions, residual risk, and missing verification are named.
- Fixes or follow-up work are separate handoffs unless the user explicitly asked to implement them.

## Recovery Notes

- If the reviewed target is missing, inspect the requested artifact or ask one target question.
- If independent verification is unavailable, report the gap and avoid an approval-style claim.



## Use When

Use only when an external advisor is configured and would materially improve the answer.

    Strong routing signals: `ask`, `$ask`, `external advisor`, `ask claude`, `ask gemini`, `consult claude`, `consult gemini`, `opinion from claude`, `opinion from gemini`, `second opinion`, `claude 의견`, `gemini 의견`

## Catalog Metadata

Category: `review`
Phase: `external-advice`
Quality tier: `evidence-gated`
Reasoning demand: `standard`

Quality bar:

- Name the workflow target, constraints, validation evidence, and stop condition.
- Separate Hermes guidance from executor or wrapper behavior unless evidence proves the step happened.

Required inputs:

- question
- context summary
- why external advice helps

Expected outputs:

- advisor summary
- accepted/rejected advice
- decision note

Artifact expectations:

- advisor transcript reference only when explicitly captured

Safety rules:

- Use only when configured and materially useful.
- Treat advisor output as evidence to evaluate, not authority.
- Do not send secrets or private prompts without explicit opt-in.

## Runtime Evidence

Use the current host's own tools and subagent/task mechanism when available;
otherwise run the same lanes sequentially or name the unavailable capability.
A prepared plan, handoff, checklist, or skill installation is not execution,
review, CI, merge-readiness, or merge evidence. Report actual tool results or
`not_observed` / `not_available`; never invent dispatch or host accounting.
Treat supplied context as advisory, not proof of hidden memory reads or writes.
State scope, constraints, verification, and the stop condition before work.
Supporting paths are relative to this skill directory; sibling skill paths are
relative to its parent. Resolve them from the host-provided skill base directory
(`{baseDir}` on hosts that provide it), never a hardcoded install location.
A named workflow not installed here is unavailable, not permission to emulate
its host-specific capabilities. Verify through the real surface before done.
