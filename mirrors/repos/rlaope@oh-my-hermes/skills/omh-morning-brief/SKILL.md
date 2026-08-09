---
name: omh-morning-brief
description: [omh] Morning brief SETUP (one-time) - connects mail and calendar MCP with read-and-draft-only scope and diff approval; produces the configuration, not the daily brief itself. Use when the user says: morning-brief, morning brief, connect my email for a morning brief, set up morning brief, configure morning brief, connect mail for morning brief, connect calendar for morning brief, set up my morning brief.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, hermes-setup]
    category: hermes-setup
    phase: setup
    role: guide
    quality_tier: hermes-setup-gated
---

# Morning Brief

This is a Hermes-native `morning-brief` workflow skill.

## Why This Exists

`morning-brief` exists to connect mail and calendar access for an on-demand brief while keeping the connection strictly read and draft-only and the user's credentials unstored.

## Do Not Use When

- The user wants Hermes to check their email or calendar right now rather than set up the connection.
- The connection is already configured and the user only wants today's brief, not a setup walkthrough.
- The request needs a repository code change rather than a local MCP config edit.

## Examples

Good example:

- Prompt: connect my email for a morning brief — I want a daily summary of mail and calendar.
- Expected behavior: Check the MCP prerequisite, diagnose the current connection, guide OAuth/token issuance, show the read/draft-only diff, and apply only after approval.
- Why: The request is a mail/calendar integration setup and needs the shared setup contract plus the Send-permission guardrail.

Bad example:

- Prompt: morning-brief: check my email for anything urgent.
- Expected behavior: Route to a mail-reading task instead of starting a connection setup walkthrough.
- Why: A one-off email check is a task request, not an integration setup request.

## Completion Checklist

- If a prerequisite is unmet, mark that item "not applicable" and continue with the rest of the guide instead of blocking or guessing.
- Success is applicable-only: verification passes when every applicable item is confirmed complete, not when every possible item exists.
- The connection is confirmed read and draft-only, with Send permission never enabled, before the brief is reported ready.

## Recovery Notes

- If the mail or calendar prerequisite is unmet, mark that surface "not applicable" and offer the brief scoped to whichever surface is connected.
- If a pasted token fails validation, ask the user to reissue it rather than storing or retrying the same value silently.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `agent-board`, `gateway-intent-card`, `voice-operator`, `+33 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when the user wants Hermes to connect mail and calendar access for an on-demand morning brief, following the shared prerequisite-check, diagnose, guide, diff-approved apply, and verify contract.

    Strong routing signals: `morning-brief`, `morning brief`, `connect my email for a morning brief`, `set up morning brief`, `configure morning brief`, `connect mail for morning brief`, `connect calendar for morning brief`, `set up my morning brief`, `모닝 브리핑 설정해줘`, `모닝 브리핑 설정`, `아침 브리핑 설정`, `메일 연동해서 브리핑`

## Catalog Metadata

Category: `hermes-setup`
Phase: `setup`
Hermes role: `guide`
Quality tier: `hermes-setup-gated`
Reasoning demand: `light`

Quality bar:

- Prerequisite check: confirm the subscription, account, or capability the step needs exists before continuing; mark unmet prerequisites "not applicable" and skip them explicitly.
- Read-only diagnose: read the current Hermes config, `.env` keys, and installed version without writing anything.
- Guide: walk the user through any account creation, OAuth, or token issuance they must complete themselves.
- Diff-approved apply: show the exact config or `.env` diff and write only after the user explicitly approves it.
- Verify: re-read the updated config and report a completion checklist covering every applicable item.
- Keep the read/draft-only access boundary — never enable Send permission — as a hard constraint on every apply step, not an optional recommendation.

Handoff policy:

Run diagnosis and guidance directly in Hermes for the mail/calendar connection. Diagnosis only reads the existing Hermes config, `.env` keys, and installed version; it never writes anything on its own. Show the exact diff for any config or `.env` change and write it only after the user explicitly approves that diff. Secret values such as tokens and API keys are pasted by the user directly in chat and are never stored, logged, or echoed back beyond the immediate diff confirmation. Delegate to a selected coding executor only if the user needs a change outside chat-driven MCP config edits.

Required inputs:

- mail and calendar MCP connection status
- OAuth token or app password supplied by the user

Expected outputs:

- read-only diagnosis of the current mail/calendar MCP connection state
- diff-approved MCP config write scoped to read and draft-only access
- an on-demand morning brief once connection is verified

Artifact expectations:

- connection verification note when the wrapper captures it

Safety rules:

- Configure mail and calendar MCP access as read and draft only; never enable Send permission, even if the user asks — drafts stay for the user to send themselves.
- OAuth tokens or app passwords are pasted by the user directly in chat and are never stored, logged, or persisted beyond the immediate diff confirmation.
- Do not treat a prepared connection as an observed brief; only report a brief after the connection is verified.

## Runtime Evidence

Preferred harness for this skill: `coding-handling`.

```sh
omh runtime record --skill morning-brief --harness coding-handling --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
