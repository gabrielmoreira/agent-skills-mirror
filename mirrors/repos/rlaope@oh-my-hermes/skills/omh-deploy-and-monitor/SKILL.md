---
name: omh-deploy-and-monitor
description: [omh] Hermes Deploy-and-Monitor workflow: release checklist, deploy decision, health signals, rollback gate, and post-deploy status. Use when the user says: deploy-and-monitor, deploy and monitor, deploy monitor, deployment monitoring, release monitor, post deploy, post-deploy, rollback.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, monitoring]
    category: monitoring
    phase: release-ops
    role: operator
    quality_tier: release-gated
---

# Deploy And Monitor

This is a Hermes-native `deploy-and-monitor` workflow skill.

## Why This Exists

`deploy-and-monitor` exists to keep `monitoring` work explicit, evidence-backed, and inside the Hermes/executor boundary instead of relying on ad hoc chat narration.

## Do Not Use When

- The request is casual chat, a status-only acknowledgement, or another workflow has stronger routing evidence.
- The user needs implementation, review, CI, merge, or external publishing evidence that has not been delegated or observed.

## Examples

Good example:

- Prompt: deploy-and-monitor: prepare the release monitor, rollback signals, health checks, and post-deploy status card.
- Expected behavior: Create release monitoring guidance with deployment, metric, rollback, and observation boundaries.
- Why: The request is about deploy readiness and monitoring rather than code review alone.

Bad example:

- Prompt: deploy-and-monitor: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `deploy-and-monitor`.
- Why: The request lacks the required inputs or would overclaim work that Hermes did not observe.

## Completion Checklist

- Confirm the workflow target, evidence boundary, and stop condition are named.
- Report which outputs are prepared, observed, blocked, or missing.
- Name the smallest next verification or handoff instead of claiming completion from narration.

## Recovery Notes

- If required context is missing, ask one blocking question or route back to the narrower workflow.
- If runtime or wrapper evidence is unavailable, keep the status as not_observed and expose the next observable action.

## Workflow Lane

- Current lane: **Coding handoff** (`idea-to-deploy`, `cto-loop`, `deploy-and-monitor`, `code-review`, `build-failure-triage`, `verification-gate`, `security-safety-review`, `ultrawork`, `+7 more`) - coding owners, handoffs, review, CI, and merge evidence.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when Hermes should prepare or narrate a release operation with deploy checklist, health signals, rollback criteria, and post-deploy status without pretending to run infrastructure.

    Strong routing signals: `deploy-and-monitor`, `deploy and monitor`, `deploy monitor`, `deployment monitoring`, `release monitor`, `post deploy`, `post-deploy`, `rollback`, `rollback gate`, `health check`, `incident watch`, `release health`, `deploy this service`, `배포 모니터링`, `서비스 배포`, `프로덕션 배포`, `인프라에 배포`, `배포 감시`, `롤백`, `헬스 체크`, `장애 감시`, `릴리즈 모니터링`

## Catalog Metadata

Category: `monitoring`
Phase: `release-ops`
Hermes role: `operator`
Quality tier: `release-gated`
Reasoning demand: `light`

Quality bar:

- Name release scope, target environment, health signals, rollback criteria, and evidence owner.
- Show pre-deploy, deploy decision, monitor, rollback, and post-deploy record as distinct stages.
- Mark health and rollback status unknown until observed evidence arrives.
- Convert fix follow-ups into separate accepted plans or executor handoffs.

Handoff policy:

Keep release checklist, health criteria, rollback gates, and status narration in Hermes; record deploy, monitor, incident, or rollback evidence only when the wrapper or operator observes it.

Required inputs:

- release scope
- environment
- health signals
- rollback owner

Expected outputs:

- pre-deploy checklist
- deploy decision gate
- monitoring watchlist
- rollback criteria
- post-deploy status boundary

Artifact expectations:

- release operation status record when the wrapper captures deploy or monitor observations

Safety rules:

- Do not claim deployment, health checks, rollback, or incident response happened from a prepared checklist.
- Keep release readiness, deploy decision, monitor signals, and rollback as separate evidence steps.
- Route code fixes discovered during monitoring as later executor handoffs.

## Runtime Evidence

Preferred harness for this skill: `app-delivery-loop`.

```sh
omh runtime record --skill deploy-and-monitor --harness app-delivery-loop --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- When wrapper metadata includes `memory_review_card/v1` or `handoff_context_pack/v1`, treat it as reviewed OMH-local or wrapper-supplied context only. Use conflict-free context summaries to shape plans and handoffs, but do not claim Hermes internal memory was read or changed.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
