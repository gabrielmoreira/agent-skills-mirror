---
name: "omh-github-event-ops"
description: "[omh] Hermes GitHub event operations workflow: route PR, issue, CI, and review webhook events into triage, review, or fix handoff cards. Use when the user says: github-event-ops, github event ops, github ops, github triage, github pr, github review, github action, github actions."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, github-ops]
    category: github-ops
    phase: event-routing
    role: operator
    quality_tier: workflow-surface-gated
---

# Github Event Ops

This is an OMH `github-event-ops` workflow skill, projected for Agent Skills hosts (Claude Code, Codex, Cursor, opencode, OpenClaw, pi).

## Why This Exists

`github-event-ops` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: github-event-ops PR opened with failing CI; triage whether this needs review or fix handoff.
- Expected behavior: Produce `prepare_github_event_ops_card` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: github-event-ops prove the issue was labelled and CI was rerun.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- Confirm the workflow target, evidence boundary, and stop condition are named.
- Report which outputs are prepared, observed, blocked, or missing.
- Name the smallest next verification or handoff instead of claiming completion from narration.

## Recovery Notes

- If required context is missing, ask one blocking question or route back to the narrower workflow.
- If runtime or wrapper evidence is unavailable, keep the status as not_observed and expose the next observable action.



## Use When

Use when Hermes receives or is asked to reason about GitHub PR, issue, review, or CI events and must choose review, triage, or fix-handoff without claiming a bot ran.

    Strong routing signals: `github-event-ops`, `github event ops`, `github ops`, `github triage`, `github pr`, `github review`, `github action`, `github actions`, `pr opened`, `pull request opened`, `pull request review`, `pr review`, `ci failed`, `check failed`, `checks failed`, `failing checks`, `issue opened`, `issue triage`, `pull request webhook`, `github webhook`, `github issue`, `github issue to pr`, `auto review pr`, `label issue`, `label pr`, `ci analysis`, `fix handoff`, `review handoff`, `깃허브`, `깃허브 pr`, `깃허브 이슈`, `github issue 들어온`, `이슈 라벨`, `pr 리뷰`, `리뷰 라벨`, `픽스 핸드오프`, `ci 실패`

## Catalog Metadata

Category: `github-ops`
Phase: `event-routing`
Quality tier: `workflow-surface-gated`
Reasoning demand: `standard`

Quality bar:

- Name the user-facing workflow objective, required context, next action, and stop condition.
- Separate prepared guidance from observed platform, runtime, connector, file, memory, or delivery evidence.
- Expose missing tools, credentials, targets, or observations as user-visible gaps.

Required inputs:

- user request
- target context
- delivery or status expectation
- known missing evidence

Expected outputs:

- github-event-ops/v1 card or guidance
- next action
- prepared-vs-observed boundary

Artifact expectations:

- github-event-ops/v1 metadata-only runtime or wrapper card when recorded

Safety rules:

- A GitHub event ops card is not webhook delivery, GitHub API mutation, review completion, label application, CI rerun, or fix execution evidence. When a fix is owned by Hermes coding, read `hermes_coding_harness/v1` before reporting build, review, CI, PR, or merge state.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

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
