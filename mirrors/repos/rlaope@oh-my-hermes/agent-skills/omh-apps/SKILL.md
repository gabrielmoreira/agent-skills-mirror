---
name: "omh-apps"
description: "[omh] External app actions - email, Slack, Discord, Notion, Linear, Jira, CRM, and similar providers, scoped with auth, payload, confirmation, and result-evidence gates. Use when the user says: connector-operator, connector operator, external app action, external connector action, saas action, api action, send email, email customer."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, connector]
    category: connector
    phase: connector-task
    role: guide
    quality_tier: workflow-surface-gated
---

# Connector Operator

This is an OMH `connector-operator` workflow skill, projected for Agent Skills hosts (Claude Code, Codex, Cursor, opencode, OpenClaw, pi).

## Why This Exists

`connector-operator` exists so Hermes users can ask for this workflow in chat and get a structured, checkable answer instead of an improvised one.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: connector-operator draft an email to the customer and prepare a confirmation gate before sending.
- Expected behavior: Produce `prepare_connector_operator_card` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: connector-operator send the Jira update with hidden credentials and claim it was delivered.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- Provider, target object, allowed action, payload summary, authority, confirmation policy, and stop condition are explicit.
- Credentials, missing connector setup, external writes, sends, ticket mutations, calendar invites, CRM updates, and webhook delivery are gated or marked missing.
- Message ids, ticket ids, provider responses, delivery receipts, and API effects are reported only from observed connector evidence.

## Recovery Notes

- If the connector, credentials, or permission is missing, route to toolbelt-readiness before preparing action success claims.
- If the request is only chat thread delivery policy for Discord, Slack, or Telegram, route to gateway-intent-card instead.
- If the external app action would create, send, invite, mutate, or delete provider state, require an explicit confirmation gate.



## Use When

Use when Hermes should prepare or supervise a provider-backed external app action without claiming connector availability, credentials, API mutation, delivery, or success.

    Strong routing signals: `connector-operator`, `connector operator`, `external app action`, `external connector action`, `saas action`, `api action`, `send email`, `email customer`, `gmail draft`, `gmail send`, `create linear ticket`, `create linear issue`, `linear ticket`, `linear issue`, `update linear`, `jira ticket`, `jira issue`, `create jira issue`, `open jira ticket`, `create jira`, `notion page`, `update notion`, `crm update`, `salesforce update`, `hubspot update`, `create calendar event`, `calendar invite`, `google calendar`, `send slack dm`, `slack dm`, `discord dm`, `post to discord`, `post to slack`, `discord post`, `slack post`, `connector action`, `linear ticket`, `이메일 보내`, `이메일 발송`, `메일 보내`, `gmail 초안`, `linear 티켓`, `linear 이슈`, `jira 티켓`, `jira 이슈`, `notion 페이지`, `노션 페이지`, `캘린더 초대`, `외부 앱`, `외부 커넥터`, `커넥터 액션`

## Catalog Metadata

Category: `connector`
Phase: `connector-task`
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

- connector_task_card/v1
- connector_scope/v1
- connector_auth_boundary/v1
- connector_confirmation_gate/v1 when mutating or sending
- connector_result_manifest/v1 when observed
- next action
- prepared-vs-observed boundary

Artifact expectations:

- connector_task_card/v1 metadata-only wrapper card when prepared
- connector_scope/v1 with provider, target object, allowed action, payload summary, and stop condition
- connector_auth_boundary/v1 separating missing connector, missing credentials, user-supplied authority, and credential-use prohibition
- connector_confirmation_gate/v1 for sending, ticket mutation, external write, webhook delivery, CRM/database update, or irreversible provider action
- connector_result_manifest/v1 only when provider response, message id, ticket id, API transcript, or delivery receipt is observed

Safety rules:

- A connector operator card is not connector availability, credential validation, API call, message send, ticket creation, ticket update, database/CRM mutation, external write, webhook delivery, or provider success evidence unless observed connector-result evidence records it.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

## Runtime Evidence

Use the current host's own tools and subagent/task mechanism when available;
otherwise run the same lanes sequentially or name the unavailable capability.
A prepared plan, handoff, checklist, or skill installation is not execution,
review, CI, merge-readiness, or merge evidence. Record actual tool results, or
`not_observed` / `not_available`, in the record; never invent dispatch or host
accounting.
Treat supplied context as advisory, not proof of hidden memory reads or writes.
State scope, constraints, verification, and the stop condition before work.
Reply in the user's own words and the host's own voice: OMH's record terms
(surface, lane, wrapper, handoff, evidence boundary, not_observed) stay in
records and tool calls, never in the sentence the user reads unless they ask
about one; and when a stop condition or a decision the user owns ends the turn,
offer the next action as a question rather than declaring what will not be done.
Supporting paths are relative to this skill directory; sibling skill paths are
relative to its parent. Resolve them from the host-provided skill base directory
(`{baseDir}` on hosts that provide it), never a hardcoded install location.
A named workflow not installed here is unavailable, not permission to emulate
its host-specific capabilities. Verify through the real surface before done.
