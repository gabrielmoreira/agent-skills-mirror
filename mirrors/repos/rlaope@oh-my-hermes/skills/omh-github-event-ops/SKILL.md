---
name: omh-github-event-ops
description: [omh] Hermes GitHub event operations workflow: route PR, issue, CI, and review webhook events into triage, review, or fix handoff cards. Use when the user says: github-event-ops, github event ops, github ops, github triage, github pr, github review, github action, github actions.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, github-ops]
    category: github-ops
    phase: event-routing
    role: operator
    quality_tier: workflow-surface-gated
---

# Github Event Ops

This is a Hermes-native `github-event-ops` workflow skill.

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

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `buzz`, `agent-board`, `gateway-intent-card`, `+34 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when Hermes receives or is asked to reason about GitHub PR, issue, review, or CI events and must choose review, triage, or fix-handoff without claiming a bot ran.

    Strong routing signals: `github-event-ops`, `github event ops`, `github ops`, `github triage`, `github pr`, `github review`, `github action`, `github actions`, `pr opened`, `pull request opened`, `pull request review`, `pr review`, `ci failed`, `check failed`, `checks failed`, `failing checks`, `issue opened`, `issue triage`, `pull request webhook`, `github webhook`, `github issue`, `github issue to pr`, `auto review pr`, `label issue`, `label pr`, `ci analysis`, `fix handoff`, `review handoff`, `깃허브`, `깃허브 pr`, `깃허브 이슈`, `github issue 들어온`, `이슈 라벨`, `pr 리뷰`, `리뷰 라벨`, `픽스 핸드오프`, `ci 실패`

## Catalog Metadata

Category: `github-ops`
Phase: `event-routing`
Hermes role: `operator`
Quality tier: `workflow-surface-gated`
Reasoning demand: `standard`

Quality bar:

- Name the user-facing workflow objective, required context, next action, and stop condition.
- Separate prepared guidance from observed platform, runtime, connector, file, memory, or delivery evidence.
- Expose missing tools, credentials, targets, or observations as user-visible gaps.

Handoff policy:

Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded.

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

Preferred harness for this skill: `github-event-ops`.

```sh
omh runtime record --skill github-event-ops --harness github-event-ops --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
