---
name: "omh-toolbelt-readiness"
description: "[omh] Toolbelt readiness - inventory which MCP servers, CLIs, APIs, credentials, and connectors a workflow needs; use external-connector-readiness to assess one named integration and executor-runtime-readiness to choose the coding owner. Use when the user says: toolbelt-readiness, mcp readiness, tool readiness, plugin readiness, connector readiness, needed mcp, api credential, missing cli."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, tools]
    category: tools
    phase: readiness-check
    role: tracker
    quality_tier: workflow-surface-gated
---

# Toolbelt Readiness

This is an OMH `toolbelt-readiness` workflow skill, projected for Agent Skills hosts (Claude Code, Codex, Cursor, opencode, OpenClaw, pi).

## Why This Exists

`toolbelt-readiness` exists so Hermes users can ask for this workflow in chat and get a structured, checkable answer instead of an improvised one.

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



## Use When

Use when a workflow depends on MCP, CLI, API credentials, or connectors and Hermes must show installed, missing, optional, and unsafe tools.

    Strong routing signals: `toolbelt-readiness`, `mcp readiness`, `tool readiness`, `plugin readiness`, `connector readiness`, `needed mcp`, `api credential`, `missing cli`, `missing plugin`, `missing connector`, `external connector`, `external tool`, `mcp server`, `mcp servers`, `mcp tool`, `mcp tools`, `toolbelt`, `github cli`, `linear cli`, `jira cli`, `notion connector`, `google drive connector`, `gmail connector`, `slack api`, `browser tool`, `image generator connector`, `mcp`, `credential`, `외부 도구`, `외부 연결`, `커넥터`, `플러그인`, `자격증명`

## Catalog Metadata

Category: `tools`
Phase: `readiness-check`
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

- toolbelt-readiness/v1 card or guidance
- next action
- prepared-vs-observed boundary

Artifact expectations:

- toolbelt-readiness/v1 metadata-only runtime or wrapper card when recorded

Safety rules:

- A toolbelt readiness card is not MCP server installation, credential validation, API access, connector invocation, or successful workflow execution evidence.
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
