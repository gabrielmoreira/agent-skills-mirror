---
name: omh-toolbelt-readiness
description: [omh] Toolbelt readiness - inventory which MCP servers, CLIs, APIs, credentials, and connectors a workflow needs; use external-connector-readiness to assess one named integration and executor-runtime-readiness to choose the coding owner. Use when the user says: toolbelt-readiness, mcp readiness, tool readiness, plugin readiness, connector readiness, needed mcp, api credential, missing cli.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, tools]
    category: tools
    phase: readiness-check
    role: tracker
    quality_tier: workflow-surface-gated
---

# Toolbelt Readiness

This is a Hermes-native `toolbelt-readiness` workflow skill.

## Why This Exists

`toolbelt-readiness` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: toolbelt-readiness what MCP or CLI tools do I need for weekly Linear and GitHub triage?
- Expected behavior: Produce `prepare_toolbelt_readiness` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: toolbelt-readiness claim Gmail access works without an observed credential check.
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

Use when a workflow depends on MCP, CLI, API credentials, or connectors and Hermes must show installed, missing, optional, and unsafe tools.

    Strong routing signals: `toolbelt-readiness`, `mcp readiness`, `tool readiness`, `plugin readiness`, `connector readiness`, `needed mcp`, `api credential`, `missing cli`, `missing plugin`, `missing connector`, `external connector`, `external tool`, `mcp server`, `mcp servers`, `mcp tool`, `mcp tools`, `toolbelt`, `github cli`, `linear cli`, `jira cli`, `notion connector`, `google drive connector`, `gmail connector`, `slack api`, `browser tool`, `image generator connector`, `외부 도구`, `외부 연결`, `mcp`, `커넥터`, `플러그인`, `자격증명`, `credential`

## Catalog Metadata

Category: `tools`
Phase: `readiness-check`
Hermes role: `tracker`
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

- toolbelt-readiness/v1 card or guidance
- next action
- prepared-vs-observed boundary

Artifact expectations:

- toolbelt-readiness/v1 metadata-only runtime or wrapper card when recorded

Safety rules:

- A toolbelt readiness card is not MCP server installation, credential validation, API access, connector invocation, or successful workflow execution evidence.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

## Runtime Evidence

Preferred harness for this skill: `toolbelt-readiness`.

```sh
omh runtime record --skill toolbelt-readiness --harness toolbelt-readiness --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
