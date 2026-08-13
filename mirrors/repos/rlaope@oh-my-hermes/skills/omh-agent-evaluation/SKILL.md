---
name: omh-agent-evaluation
description: [omh] Hermes Agent Evaluation workflow: compare executor or agent choices on reproducible tasks using quality, cost, time, tool, and evidence metrics. Use when the user says: agent-evaluation, agent evaluation, agent eval, agent benchmark, executor evaluation, executor benchmark, compare agents, compare codex claude.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, operations]
    category: operations
    phase: agent-evaluation
    role: operator
    quality_tier: agent-eval-gated
---

# Agent Evaluation

This is a Hermes-native `agent-evaluation` workflow skill.

## Why This Exists

`agent-evaluation` gives OMH a way to improve executor choice empirically, not by vibes, while preserving executor-neutral product language across Codex, Claude Code, Hermes, and generic runtimes.

## Do Not Use When

- The user needs current runtime readiness only; use `executor-runtime-readiness`.
- The user already selected an executor and wants implementation; use the coding handoff or delivery workflow.
- The user asks for workflow learning from a single failed route; use `workflow-learning`.
- The ask is to find and fix runtime, memory, cost, or rendering hotspots rather than score executor or model output quality; use `ultraperf`.

## Examples

Good example:

- Prompt: agent-evaluation Codex와 Claude Code를 같은 버그 수정 태스크로 비교해서 어떤 런타임을 기본으로 둘지 판단해줘.
- Expected behavior: Prepare task_benchmark_set/v1, run_result_matrix/v1 requirements, scorecard/v1, and scenario-specific recommendation.
- Why: The request compares executor choices and needs fair evaluation boundaries.

Bad example:

- Prompt: agent-evaluation 실행 증거 없이 Codex가 항상 최고라고 결론내줘.
- Expected behavior: Reject universal ranking and require observed runs or mark the recommendation as ungrounded.
- Why: Agent evaluation must be reproducible and evidence-backed.

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

Use when Hermes should design or summarize a fair comparison of Codex, Claude Code, Hermes coding, or generic executors for a bounded task set.

    Strong routing signals: `agent-evaluation`, `agent evaluation`, `agent eval`, `agent benchmark`, `executor evaluation`, `executor benchmark`, `compare agents`, `compare codex claude`, `agent tournament`, `which agent is better`, `에이전트 평가`, `에이전트 비교`, `실행자 평가`, `코덱스 클로드 비교`

## Catalog Metadata

Category: `operations`
Phase: `agent-evaluation`
Hermes role: `operator`
Quality tier: `agent-eval-gated`
Reasoning demand: `light`

Quality bar:

- Define tasks, rubric, isolation, budgets, and stop rules before comparing agents.
- Use the same inputs and success criteria across candidates unless the difference is the variable under test.
- Report quality, correctness, time, cost, tool coverage, verification, and review gaps separately.
- Recommend executor choice per scenario and confidence, not as a universal ranking.

Handoff policy:

Keep evaluation design and scoring in Hermes. Actual executor runs, costs, timings, tool calls, code edits, and review results must come from observed runtime or supplied artifacts.

Required inputs:

- candidate executors or agents
- task set and fixtures
- success criteria and scoring rubric
- allowed tools, budget, timebox, and isolation policy
- observed run artifacts when comparing completed attempts

Expected outputs:

- agent_eval_plan/v1
- task_benchmark_set/v1
- run_result_matrix/v1 when observed
- scorecard/v1
- selection_recommendation/v1
- not-evidence boundary

Artifact expectations:

- task_benchmark_set/v1 with reproducible tasks, fixtures, budgets, allowed tools, and acceptance criteria
- run_result_matrix/v1 with quality, correctness, time, cost, context, tool, verification, and review evidence when observed
- selection_recommendation/v1 with confidence, caveats, and winner-by-scenario rather than global mythology

Safety rules:

- Do not claim an executor is better from anecdotes, brand names, or unobserved runs.
- Do not send secrets, credentials, private data, or production tasks into evaluation without explicit authority.
- Keep benchmark design, observed run evidence, scoring, and executor selection separate.

## Runtime Evidence

Preferred harness for this skill: `agent-evaluation`.

```sh
omh runtime record --skill agent-evaluation --harness agent-evaluation --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
