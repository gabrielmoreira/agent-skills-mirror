---
name: "omh-skill-scout"
description: "[omh] Skill Scout workflow: prepare a metadata-only search-before-creation report for local, marketplace, GitHub, and web skill candidates with risk review and adoption options. Use when the user says: skill-scout, skill scout, skill candidate, skill candidate search, skill discovery, find a skill, find skills, top skills."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, operations]
    category: operations
    phase: skill-scout
    role: operator
    quality_tier: workflow-surface-gated
---

# Skill Scout

This is an OMH `skill-scout` workflow skill, projected for Agent Skills hosts (Claude Code, Codex, Cursor, opencode, OpenClaw, pi).

## Why This Exists

`skill-scout` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: skill-scout find existing skill candidates before we create a release-note workflow skill.
- Expected behavior: Produce `prepare_skill_scout` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: skill-scout install the best GitHub skill and copy it into the marketplace without review.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- Intent, keywords, source scope, and stop condition are explicit.
- Local and external search evidence is separated from planned search.
- No install, copy, write, credential, or trust claim is made without observed review or implementation.

## Recovery Notes

- If the request is about setup or installed skill repair, route to doctor.
- If the request is a portfolio health dashboard, route to skill-health.
- If the request is an approved skill mutation or creation task, route to skill or implementation after the scout decision.



## Use When

Use before creating or adapting a skill so OMH can compare existing local, marketplace, GitHub, or web candidates without installing, copying, or trusting them by default.

    Strong routing signals: `skill-scout`, `skill scout`, `skill candidate`, `skill candidate search`, `skill discovery`, `find a skill`, `find skills`, `top skills`, `popular skills`, `famous hermes skills`, `useful hermes skills`, `hermes skills/plugin`, `skills/plugin`, `agentskills.io top skills`, `is there a skill`, `existing skill`, `fork a skill`, `extend a skill`, `create skill after search`, `new skill search`, `skill adoption`, `스킬 스카우트`, `스킬 후보`, `스킬 찾기`, `스킬 검색`, `스킬 만들기 전`, `유명한 hermes skills`, `유명한 hermes skill`, `유용한 hermes skills`, `스킬 플러그인 후보`, `플러그인 찾아`, `플러그인 비교`, `없는 것 설치할지 비교`, `기존 스킬`

## Catalog Metadata

Category: `operations`
Phase: `skill-scout`
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

- skill_scout_query/v1
- local_skill_candidate_inventory/v1 when observed
- external_skill_candidate_risk_review/v1 when observed
- awesome_hermes_agent_coverage/v1 for upstream ecosystem comparison when requested
- skill_adoption_decision_matrix/v1
- skill_scout_recommendation/v1

Artifact expectations:

- skill_scout_query/v1 with intended workflow, triggers, domains/tools, and search keywords
- local_skill_candidate_inventory/v1 separating installed, bundled, marketplace, and repo-local matches when observed
- awesome_hermes_agent_coverage/v1 mapping upstream ecosystem entries to OMH covered, partial, or missing_candidate coverage statuses, matched OMH surfaces, rule_set_version, and matched_rule_id
- skill_adoption_decision_matrix/v1 ranking use existing, fork or extend, and create fresh options with trust gaps

Safety rules:

- A skill scout report is not skill installation, external source trust, marketplace mutation, file copy, network retrieval, credential use, implementation, review, CI, or proof that a candidate is safe to adopt.
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
