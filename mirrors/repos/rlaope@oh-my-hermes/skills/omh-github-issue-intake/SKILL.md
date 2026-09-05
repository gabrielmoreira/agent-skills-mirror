---
name: "omh-github-issue-intake"
description: "[omh] GitHub issue intake workflow: turn a public chat report into a confirmed, verified issue package. Use when the user says: github-issue-intake, github issue intake, issue intake, file this as an issue, file a github issue, open a github issue, create a github issue, submit a github issue."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, github-ops]
    category: github-ops
    phase: issue-intake
    role: operator
    quality_tier: workflow-surface-gated
---

# Github Issue Intake

This is a Hermes-native `github-issue-intake` workflow skill.

## Why This Exists

`github-issue-intake` exists so a public support-chat report can become a verified GitHub issue through one bounded, confirmation-gated lane instead of ad hoc chat narration or an unscoped bot write.

## Do Not Use When

- The report only wants classification or signal clustering; use feedback-triage instead.
- The event concerns an already-existing issue, PR, review, or CI run; use github-event-ops instead.
- The user wants implementation; coding stays a separate follow-up lane with its own maintainer authority.
- The report describes a security vulnerability; redirect to the private SECURITY.md path.

## Examples

Good example:

- Prompt: please file this as an issue: omh setup fails on Windows
- Expected behavior: Classify the report, run the bounded interview, search duplicates, present the direction check, and prepare github_issue_intake/v1 for confirmation-gated connector handoff.
- Why: The request is an explicit pre-creation filing ask with a classifiable report and an explicit target.

Bad example:

- Prompt: github-issue-intake prove the issue was filed and labelled.
- Expected behavior: Report that creation, labeling, and any GitHub mutation stay unobserved until an authorized connector returns read-back evidence.
- Why: A prepared package is not issue creation, label application, or any GitHub mutation evidence.

## Completion Checklist

- Confirm the workflow target, evidence boundary, and stop condition are named.
- Report which outputs are prepared, observed, blocked, or missing.
- Name the smallest next verification or handoff instead of claiming completion from narration.

## Recovery Notes

- If required context is missing, ask one blocking question or route back to the narrower workflow.
- If runtime or wrapper evidence is unavailable, keep the status as not_observed and expose the next observable action.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `github-issue-intake`, `buzz`, `agent-board`, `+35 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when a public chat report should become a new GitHub issue: classify it, ask at most three decision-changing questions, search duplicates, confirm the direction, and hand the scoped creation to an authorized connector.

    Strong routing signals: `github-issue-intake`, `github issue intake`, `issue intake`, `file this as an issue`, `file a github issue`, `open a github issue`, `create a github issue`, `submit a github issue`, `report a bug as an issue`, `new github issue`, `이슈로 올려줘`, `깃허브 이슈로 올려줘`, `이슈 등록해줘`, `깃허브 이슈 등록해줘`, `깃허브 이슈 만들어줘`, `깃허브 이슈 생성해줘`, `버그 리포트 올려줘`, `새 이슈 만들어줘`

## Catalog Metadata

Category: `github-ops`
Phase: `issue-intake`
Hermes role: `operator`
Quality tier: `workflow-surface-gated`
Reasoning demand: `standard`

Quality bar:

- Classify the report from supplied or observed facts and separate observation from inference.
- Ask at most three unresolved, decision-changing questions; stop with a specific missing-evidence request instead of filing a vague issue.
- Present the direction check, require confirmation, and keep prepared packages distinct from observed creation.

Handoff policy:

Keep intake, direction check, and confirmation in Hermes; hand the confirmed package to an authorized Hermes-native/wrapper connector for the single scoped create_issue write, and hand implementation to a coding workflow only after separate maintainer authorization.

Required inputs:

- public report or summary
- source boundary
- explicit target repository
- desired outcome
- scope boundary
- missing evidence

Expert clarification questions:
- `desired outcome`
  - English: What is the smallest user-visible outcome this issue should ask for?
  - Korean: 이 이슈가 요구해야 할 가장 작은 사용자 관점 결과는 무엇인가요?
- `scope boundary`
  - English: What is explicitly included in this issue, and what is explicitly out of scope?
  - Korean: 이 이슈에 명시적으로 포함되는 범위와 명시적으로 제외되는 범위는 무엇인가요?
- `missing evidence`
  - English: Which reproduction steps, versions, or logs are still missing and would change the issue direction?
  - Korean: 이슈 방향을 바꿀 수 있는 재현 단계, 버전, 로그 중 아직 없는 증거는 무엇인가요?

Expected outputs:

- github_issue_intake/v1
- direction check
- duplicate status
- issue package or connector handoff
- read-back verification or explicit blocker

Artifact expectations:

- github_issue_intake/v1 metadata-only wrapper card when recorded

Safety rules:

- Investigation is read-only: repository and documentation exploration plus GitHub duplicate search; never mutate code, settings, branches, commits, PRs, releases, or deployments.
- No external mutation before the direction check and an explicit confirmation; a maintainer file-now requires authenticated-wrapper actor/evidence identity and never bypasses duplicate, template, security, or read-back gates.
- Confirmation requires a complete direction check - type, user-visible problem, source summary, smallest desired outcome, included and excluded scope, observed evidence versus inference, and duplicate status - plus a completed duplicate search; any blocker (security redirect, missing evidence, connector unavailable, or credentials missing) stops confirmation and handoff and cannot be cleared by a later observed result.
- A public reporter authorizes exactly one scoped create_issue against an explicit repository; code, configuration, branch, commit, PR, merge, deployment, and coding-executor mutations stay in their own maintainer-gated lanes.
- Security vulnerability reports redirect to the private SECURITY.md reporting path instead of a public issue.
- Core OMH never calls GitHub; only a checked-in issue-form builder can produce an authorized create_issue request. An authorized connector receives one stable idempotency-keyed request, must enforce that key externally, and returns observed result evidence bound to that request; dispatch consumes the core handoff, so dispatched or observed artifacts cannot hand off again.
- A prepared issue package is not creation evidence; only connector read-back of repository, author, title, body, labels, and URL is observed evidence.
- The target repository must be explicit or safely configured; never infer a cross-repository target from context.
- github_issue_intake/v1 persists bounded metadata, digests, and refs only: no raw title, body, transcript, platform event, credential, prompt, private log, or private content; the complete request remains transient for the connector.

## Runtime Evidence

Preferred harness for this skill: `github-issue-intake`.

```sh
omh runtime record --skill github-issue-intake --harness github-issue-intake --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
