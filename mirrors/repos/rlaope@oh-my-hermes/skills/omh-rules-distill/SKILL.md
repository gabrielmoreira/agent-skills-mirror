---
name: omh-rules-distill
description: [omh] Hermes Rules Distill workflow: extract repeated principles from skills, prompts, traces, reviews, and failures into reviewed rule candidates without auto-mutating guidance. Use when the user says: rules-distill, rules distill, distill rules, rule distillation, principle distill, skill principles, extract agent rules, turn traces into rules.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, knowledge]
    category: knowledge
    phase: rules-distillation
    role: memory-keeper
    quality_tier: rules-distillation-gated
---

# Rules Distill

This is a Hermes-native `rules-distill` workflow skill.

## Why This Exists

`rules-distill` gives OMH a disciplined way to learn from large skill ecosystems like ECC without wholesale copying: extract principles, review them, then patch OMH only through explicit verified work.

## Do Not Use When

- The user wants a single workflow route regression; use `workflow-learning`.
- The user wants durable factual project memory; use `wiki` or memory curation.
- The user already approved a concrete code/doc change; use the implementation workflow.

## Examples

Good example:

- Prompt: rules-distill 최근 실패 trace와 스킬들을 보고 OMH AGENTS에 넣을 만한 반복 원칙 후보만 뽑아줘.
- Expected behavior: Prepare principle_candidate_set/v1, duplication/conflict report, review queue, and approved patch handoff only after approval.
- Why: The request is meta-guidance learning and needs review before mutating rules.

Bad example:

- Prompt: rules-distill 한 번 본 실패를 바로 모든 스킬 규칙으로 써버려.
- Expected behavior: Keep it as a low-confidence candidate or regression case until repeated evidence and review approval exist.
- Why: Rule distillation should not turn one-off anecdotes into global behavior.

## Completion Checklist

- The durable fact, source evidence, retrieval hint, and staleness risk are recorded.
- Uncertain or conflicting knowledge is marked as review-needed rather than permanent truth.
- Separate coding or docs tasks are extracted instead of buried in notes.

## Recovery Notes

- If source evidence conflicts, route to memory or knowledge review before writing durable guidance.
- If the fact may be stale, record the staleness warning and next refresh action.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `buzz`, `agent-board`, `gateway-intent-card`, `+34 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when Hermes should turn repeated workflow lessons, skill behavior, review comments, or failure traces into candidate rules that humans can review before docs or catalog changes.

    Strong routing signals: `rules-distill`, `rules distill`, `distill rules`, `rule distillation`, `principle distill`, `skill principles`, `extract agent rules`, `turn traces into rules`, `policy distill`, `guidance distill`, `규칙 증류`, `원칙 추출`, `스킬 원칙`, `프롬프트 규칙`

## Catalog Metadata

Category: `knowledge`
Phase: `rules-distillation`
Hermes role: `memory-keeper`
Quality tier: `rules-distillation-gated`
Reasoning demand: `light`

Quality bar:

- Collect repeated evidence before proposing a rule.
- Deduplicate against existing guidance and name conflicts or narrower scopes.
- Use imperative, testable wording and include non-goals for each candidate.
- Require review approval before any patch handoff or generated-skill update.

Handoff policy:

Keep principle extraction and candidate review in Hermes. Editing AGENTS.md, catalog data, prompts, skills, or docs requires explicit approved implementation work and verification.

Required inputs:

- source corpus: skills, prompts, traces, reviews, failures, or docs
- destination boundary: AGENTS, skill catalog, prompt, docs, memory, or no-write review
- rule granularity and acceptance criteria
- reviewer or approval requirement

Expected outputs:

- rules_distillation_plan/v1
- principle_candidate_set/v1
- duplication_conflict_report/v1
- review_queue/v1
- approved_patch_handoff/v1 when approved
- not-evidence boundary

Artifact expectations:

- principle_candidate_set/v1 with source references, repeated pattern, candidate wording, scope, non-goals, and risk
- duplication_conflict_report/v1 with already-covered rules, conflicts, and stale guidance
- review_queue/v1 separating proposed, approved, rejected, deferred, and needs-evidence candidates

Safety rules:

- Do not silently mutate skills, prompts, AGENTS.md, docs, memory, or catalog data from a distillation result.
- Do not promote one-off preferences, weak anecdotes, or stale traces into global rules.
- Keep observed sources, inferred principles, candidate wording, review state, and implementation patches separate.

## Runtime Evidence

Preferred harness for this skill: `rules-distill`.

```sh
omh runtime record --skill rules-distill --harness rules-distill --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
