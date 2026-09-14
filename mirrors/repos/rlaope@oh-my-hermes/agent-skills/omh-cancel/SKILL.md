---
name: "omh-cancel"
description: "[omh] Hermes adaptation for ending active workflow state cleanly. Use when the user says: cancel, stop the workflow, abort the run, cancel the loop."
compatibility: "Requires the omh CLI on PATH (pip install oh-my-hermes)."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, operator]
    category: operator
    phase: state-cleanup
    role: tracker
    quality_tier: evidence-gated
---

# Cancel

This is an OMH `cancel` workflow skill, projected for Agent Skills hosts (Claude Code, Codex, Cursor, opencode, OpenClaw, pi).

## Why This Exists

`cancel` exists to keep `operator` work explicit, evidence-backed, and inside the Hermes/executor boundary instead of relying on ad hoc chat narration.

## Do Not Use When

- The request is casual chat, a status-only acknowledgement, or another workflow has stronger routing evidence.
- The user needs implementation, review, CI, merge, or external publishing evidence that has not been delegated or observed.

## Examples

Good example:

- Prompt: cancel: handle a operator request that needs explicit evidence boundaries and a clear stop condition.
- Expected behavior: Run `cancel` only after naming the target, evidence boundary, and stop condition.
- Why: The request matches the catalog use case and keeps observed evidence separate from prepared guidance.

Bad example:

- Prompt: cancel: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `cancel`.
- Why: The request lacks the required inputs or would overclaim work that Hermes did not observe.

## Completion Checklist

- The local command, managed path, config surface, and state artifact inspected are named.
- Blocking issues, warnings, and optional surfaces are separated.
- The next repair action is explicit and does not claim a reload or runtime observation.

## Recovery Notes

- If a managed path or config key is missing, route to setup/update repair instead of editing hidden state.
- If a reload or plugin load was not observed, keep the diagnostic result as local health evidence only.



## Use When

Use to cleanly end active adapted workflow state.

    Strong routing signals: `cancel`, `$cancel`, `stop the workflow`, `abort the run`, `cancel the loop`

## Catalog Metadata

Category: `operator`
Phase: `state-cleanup`
Quality tier: `evidence-gated`
Reasoning demand: `light`

Quality bar:

- Name the workflow target, constraints, validation evidence, and stop condition.
- Separate Hermes guidance from executor or wrapper behavior unless evidence proves the step happened.

Required inputs:

- active workflow state
- cancellation intent

Expected outputs:

- cleared state
- safe stop summary

Artifact expectations:

- state clear record when state exists

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
