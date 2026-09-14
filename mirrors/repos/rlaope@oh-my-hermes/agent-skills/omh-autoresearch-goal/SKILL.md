---
name: "omh-autoresearch-goal"
description: "[omh] Hermes adaptation for durable research-goal execution. Use when the user says: autoresearch-goal, research goal, durable research, critic research."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, research]
    category: research
    phase: durable-research
    role: researcher
    quality_tier: validator-gated
---

# Autoresearch Goal

This is an OMH `autoresearch-goal` workflow skill, projected for Agent Skills hosts (Claude Code, Codex, Cursor, opencode, OpenClaw, pi).

## Why This Exists

`autoresearch-goal` exists to keep `research` work explicit, evidence-backed, and inside the Hermes/executor boundary instead of relying on ad hoc chat narration.

## Do Not Use When

- The request is casual chat, a status-only acknowledgement, or another workflow has stronger routing evidence.
- The user needs implementation, review, CI, merge, or external publishing evidence that has not been delegated or observed.

## Examples

Good example:

- Prompt: autoresearch-goal: keep researching AI agent memory practices until the evidence gaps are closed or logged.
- Expected behavior: Run a durable research loop with critic checks, source gaps, and a stop or checkpoint condition.
- Why: The request is research that needs persistence and review, not a one-shot brief.

Bad example:

- Prompt: autoresearch-goal: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `autoresearch-goal`.
- Why: The request lacks the required inputs or would overclaim work that Hermes did not observe.

## Completion Checklist

- The research question, source boundaries, recency assumptions, and confidence level are named.
- Observed sources, inference, synthesis, and unresolved retrieval gaps are separated.
- Follow-up planning or handoff uses the research summary without calling it execution evidence.

## Recovery Notes

- If sources cannot be accessed, state the retrieval gap and use only observed local context.
- If evidence is thin or one-sided, lower confidence and ask for a narrower source boundary.



## Use When

Use for validator-gated research that needs durable artifacts.

    Strong routing signals: `autoresearch-goal`, `research goal`, `durable research`, `critic research`

## Catalog Metadata

Category: `research`
Phase: `durable-research`
Quality tier: `validator-gated`
Reasoning demand: `standard`

Quality bar:

- Define validator criteria before gathering evidence.
- Run each cycle as evidence-gap closure: name the open gaps the cycle targets, then stop at the validator criteria or the declared iteration budget, whichever comes first.
- Keep durable research artifacts separate from coding execution evidence.
- Stop with next questions or a source-backed synthesis when validation is incomplete.

Required inputs:

- research objective
- validator criteria
- source boundaries

Expected outputs:

- research artifact
- validator result
- next questions

Artifact expectations:

- durable research ledger or checklist

Safety rules:

- Do not imply hidden Hermes runtime behavior.
- Use the smallest verification that can prove the claim.

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
