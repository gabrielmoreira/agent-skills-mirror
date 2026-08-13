---
name: omh-browser
description: [omh] Policy overlay for browser tasks - add auth, confirmation, and observed-trace gates after preferring the native browser for ordinary URL, click, login, and form actions. Use when the user says: browser-operator, browser operator, browser task, browser operation, browser automation, browser session, webpage operation, web page operation.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, browser]
    category: browser
    phase: browser-task
    role: guide
    quality_tier: workflow-surface-gated
---

# Browser Operator

This is a Hermes-native `browser-operator` workflow skill.

## Why This Exists

`browser-operator` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: browser-operator open the staging checkout URL, click login, fill the form, and capture blockers.
- Expected behavior: Produce `prepare_browser_operator_card` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: browser-operator use saved credentials and submit the production payment form without confirmation.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- The target URL, allowed interactions, prohibited interactions, auth boundary, and stop condition are explicit.
- Credentials, login, payment, purchase, destructive submission, scraping, and data export are gated or marked missing.
- Screenshots, DOM state, console/network logs, and click/form traces are reported only from observed browser evidence.

## Recovery Notes

- If no URL or target page is supplied, ask for the smallest target needed before opening a browser task.
- If login, payment, destructive mutation, or credential use is requested, require an explicit confirmation gate and do not proceed from vague intent.
- If the request is visual correctness rather than general page operation, route to visual-qa instead.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `buzz`, `agent-board`, `gateway-intent-card`, `+34 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when Hermes should prepare or supervise a browser/page interaction request such as opening a URL, clicking, logging in, filling forms, or capturing page blockers without claiming browser execution.

    Strong routing signals: `browser-operator`, `browser operator`, `browser task`, `browser operation`, `browser automation`, `browser session`, `webpage operation`, `web page operation`, `open url`, `open the url`, `open page`, `open the page`, `visit url`, `visit page`, `navigate url`, `navigate page`, `click page`, `click this page`, `click button`, `click login`, `login page`, `fill form`, `fill the form`, `submit form`, `checkout url`, `capture blockers`, `page blockers`, `interactive page`, `browser trace`, `browser observation`, `playwright task`, `웹페이지`, `웹 페이지`, `브라우저`, `브라우저 작업`, `브라우저 조작`, `페이지 열고`, `url 열고`, `링크 열고`, `클릭`, `로그인`, `로그인 폼`, `폼 작성`, `폼 입력`, `캡처`, `막히는 부분`

## Catalog Metadata

Category: `browser`
Phase: `browser-task`
Hermes role: `guide`
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

- browser_task_card/v1
- browser_interaction_scope/v1
- browser_auth_boundary/v1
- browser_observation_manifest/v1 when observed
- browser_confirmation_gate/v1 when destructive
- next action
- prepared-vs-observed boundary

Artifact expectations:

- browser_task_card/v1 metadata-only wrapper card when prepared
- browser_interaction_scope/v1 with target URL, allowed actions, stop condition, and prohibited actions
- browser_auth_boundary/v1 separating supplied credentials, missing credentials, and credential-use prohibition
- browser_observation_manifest/v1 only when screenshots, DOM notes, console/network traces, or click traces are observed

Safety rules:

- A browser operator card is not browser launch, login, credential validation, page mutation, form submission, purchase/payment/destructive action, screenshot, scraping, or successful interaction evidence unless an observed browser trace records it.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

## Runtime Evidence

Preferred harness for this skill: `browser-operator`.

```sh
omh runtime record --skill browser-operator --harness browser-operator --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
