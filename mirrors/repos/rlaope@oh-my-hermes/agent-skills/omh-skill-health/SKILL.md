---
name: "omh-skill-health"
description: "[omh] Skill Health workflow: prepare a metadata-only OMH skill portfolio dashboard with stale surfaces, observed failure signals, pending amendments, and top actions. Use when the user says: skill-health, skill health, skill portfolio health, skill dashboard, skill health dashboard, skill failure pattern dashboard, skill failure patterns, pending skill amendments."
compatibility: "Requires the omh CLI on PATH (pip install oh-my-hermes)."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, operations]
    category: operations
    phase: skill-health
    role: operator
    quality_tier: workflow-surface-gated
---

# Skill Health

This is an OMH `skill-health` workflow skill, projected for Agent Skills hosts (Claude Code, Codex, Cursor, opencode, OpenClaw, pi).

## Why This Exists

`skill-health` exists so Hermes users can ask for this workflow in chat and get a structured, checkable answer instead of an improvised one.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: skill-health show the OMH skill portfolio dashboard with stale surfaces, failure patterns, pending amendments, and top improvement actions.
- Expected behavior: Produce `prepare_skill_health` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: skill-health claim every skill is working and patch the failures automatically without observed signals or review.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- Dashboard scope, source surfaces, stale/duplicate criteria, and stop condition are explicit.
- Install/setup health is routed to doctor; catalog operations are routed to skill; failure retrospectives are routed to workflow-learning.
- No skill, prompt, doc, memory, or model behavior is claimed changed until a reviewed implementation records evidence.

## Recovery Notes

- If the request is about OMH setup, install, stale package paths, or command availability, route to doctor.
- If the request is a missed-route or self-improvement trace, route to workflow-learning before adding health actions.



## Use When

Use when operators need portfolio-level skill health without treating it as install repair, live execution success, or automatic skill mutation.

    Strong routing signals: `skill-health`, `skill health`, `skill portfolio health`, `skill dashboard`, `skill health dashboard`, `skill failure pattern dashboard`, `skill failure patterns`, `pending skill amendments`, `skill amendments`, `스킬 헬스`, `스킬 상태`, `스킬 대시보드`, `스킬 실패 패턴`, `스킬 개선 후보`, `스킬 보류 수정`

## Catalog Metadata

Category: `operations`
Phase: `skill-health`
Quality tier: `workflow-surface-gated`
Reasoning demand: `light`

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

- catalog, generated, reference, harness, and capability-surface status
- observed failure signals, or an explicit statement that none were supplied
- pending amendment review slots and top safe actions with owner lane and verification path

Artifact expectations:

- skill_health_card/v1 metadata-only wrapper card recording surface status, observed-only failure signals, pending amendments, and the non-mutation boundary

Safety rules:

- A skill health dashboard is not install/setup health, live skill execution success, automatic skill mutation, model training, verification, review, CI, or proof that future routing is fixed.
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
