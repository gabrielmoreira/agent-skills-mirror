---
name: "omh-run-efficiency"
description: "[omh] Report supplied local run efficiency while provider and host data stay unobserved. Use when the user says: run-efficiency, run efficiency report, local run efficiency, context utilization, tool duration report, 실행 효율 리포트, 컨텍스트 사용량, 도구 지연 시간."
compatibility: "Requires the omh CLI on PATH (pip install oh-my-hermes)."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, observability]
    category: observability
    phase: run-efficiency
    role: tracker
    quality_tier: workflow-surface-gated
---

# Run Efficiency

This is an OMH `run-efficiency` workflow skill, projected for Agent Skills hosts (Claude Code, Codex, Cursor, opencode, OpenClaw, pi).

## Why This Exists

`run-efficiency` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: Show the local run efficiency report from this run's supplied context budget and timings.
- Expected behavior: Produce `show_run_efficiency_report` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: Claim this report proves provider billing, host load, or cron execution without observations.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- The run ID, context budget, surfaces, and supplied observations are explicit.
- Provider billing, cron, and host claims remain not_observed unless separately recorded.
- The report does not intercept, route, or execute provider or host work.

## Recovery Notes

- If provider metrics are unavailable, report only local metadata and mark provider truth not_observed.
- If cost or latency looks risky, surface a warning plus the next measurement rather than a completion claim.



## Use When

Use for a bounded local efficiency report from supplied metadata with provider and host gaps explicit.

    Strong routing signals: `run-efficiency`, `run efficiency report`, `local run efficiency`, `context utilization`, `tool duration report`, `실행 효율 리포트`, `컨텍스트 사용량`, `도구 지연 시간`

## Catalog Metadata

Category: `observability`
Phase: `run-efficiency`
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

- run_efficiency_report/v1
- context utilization
- not_observed provider and host gaps

Artifact expectations:

- run_efficiency_report/v1 metadata-only report
- supplied `session_activity_receipt/v1` when available; unavailable metrics stay unavailable, never zero

Safety rules:

- Run efficiency is supplied OMH-local metadata, not provider, billing, cron, or host evidence.
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
