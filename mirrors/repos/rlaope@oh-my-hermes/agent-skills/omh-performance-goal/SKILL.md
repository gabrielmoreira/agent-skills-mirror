---
name: "omh-performance-goal"
description: "[omh] Hermes adaptation for measurable performance-goal execution. Use when the user says: performance-goal, performance goal, latency, throughput, benchmark."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, optimization]
    category: optimization
    phase: measurement
    role: tracker
    quality_tier: measurement-gated
---

# Performance Goal

This is an OMH `performance-goal` workflow skill, projected for Agent Skills hosts (Claude Code, Codex, Cursor, opencode, OpenClaw, pi).

## Why This Exists

`performance-goal` exists to keep `optimization` work explicit, evidence-backed, and inside the Hermes/executor boundary instead of relying on ad hoc chat narration.

## Do Not Use When

- The ask is to find where performance problems are, or to fix multiple unscoped hotspots across domains; use `ultraperf`.

## Examples

Good example:

- Prompt: performance-goal: benchmark recommendation latency, optimize hot paths safely, and prove no regressions.
- Expected behavior: Create a measurement-led optimization loop with baseline, change, verification, and regression evidence.
- Why: The request is performance optimization and needs measured before/after proof.

Bad example:

- Prompt: performance-goal: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `performance-goal`.
- Why: The request lacks the required inputs or would overclaim work that Hermes did not observe.

## Completion Checklist

- Confirm the workflow target, evidence boundary, and stop condition are named.
- Report which outputs are prepared, observed, blocked, or missing.
- Name the smallest next verification or handoff instead of claiming completion from narration.

## Recovery Notes

- If required context is missing, ask one blocking question or route back to the narrower workflow.
- If runtime or wrapper evidence is unavailable, keep the status as not_observed and expose the next observable action.



## Use When

Use when the goal is measurable performance improvement with evaluator evidence.

    Strong routing signals: `performance-goal`, `performance goal`, `latency`, `throughput`, `benchmark`

## Catalog Metadata

Category: `optimization`
Phase: `measurement`
Quality tier: `measurement-gated`
Reasoning demand: `heavy`

Quality bar:

- Name the metric, baseline, budget, and benchmark command before optimizing.
- Treat code-level optimization as executor work when edits are required.
- Report deltas only from observed benchmark evidence.

Required inputs:

- metric
- baseline
- budget
- benchmark command

Expected outputs:

- measurement delta
- implementation summary
- benchmark evidence

Artifact expectations:

- baseline and final benchmark evidence

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
