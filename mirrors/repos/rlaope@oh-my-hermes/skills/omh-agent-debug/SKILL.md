---
name: omh-agent-debug
description: [omh] Agent Debug workflow: capture a stuck, looping, drifting, or repeatedly failing agent run, diagnose the likely failure pattern, and prepare the smallest safe recovery action. Use when the user says: agent-debug, agent debug, agent debugging, agent introspection, agent self-debug, self-debug, self debugging, looping agent.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, operations]
    category: operations
    phase: agent-debug
    role: operator
    quality_tier: workflow-surface-gated
---

# Agent Debug

This is a Hermes-native `agent-debug` workflow skill.

## Why This Exists

`agent-debug` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: agent-debug capture why this agent is looping on the same tool and prepare the smallest safe recovery action.
- Expected behavior: Produce `prepare_agent_debug` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: agent-debug silently reset the executor, patch the environment, and claim the future loop is fixed.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- Failure state, intended goal, recent tool sequence, and context pressure are captured.
- Diagnosis distinguishes repeated command/tool loops, context drift, environment mismatch, service errors, and wrong-hypothesis tests.
- Recovery action is contained, reversible, and does not claim implementation, verification, CI, merge, or future-loop fixes.

## Recovery Notes

- If the request is install/setup health, route to doctor.
- If the request is a manager status or throughput review, route to agent-ops-review.
- If the request is a durable self-improvement record after diagnosis, route to workflow-learning.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `buzz`, `agent-board`, `gateway-intent-card`, `+34 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when an agent run is stuck, looping on tools, burning tokens without progress, drifting from the objective, losing context, or failing on recoverable environment/tool assumptions.

    Strong routing signals: `agent-debug`, `agent debug`, `agent debugging`, `agent introspection`, `agent self-debug`, `self-debug`, `self debugging`, `looping agent`, `agent loop failure`, `agent run stuck`, `agent failure capture`, `tool retry loop`, `repeated tool calls`, `context drift`, `prompt drift`, `token burn`, `에이전트 디버그`, `에이전트 실패`, `에이전트 반복 실패`, `반복 실패`, `도구 반복`, `컨텍스트 드리프트`, `토큰 낭비`

## Catalog Metadata

Category: `operations`
Phase: `agent-debug`
Hermes role: `operator`
Quality tier: `workflow-surface-gated`
Reasoning demand: `light`

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

- agent_debug_report/v1
- agent_failure_capture/v1
- agent_failure_pattern_hypothesis/v1
- contained_recovery_action/v1

Artifact expectations:

- agent_debug_report/v1 with failure pattern, recent tool sequence, goal/context pressure, environment assumptions, recovery action, and evidence status
- agent_failure_capture/v1 separating observed errors and tool loops from inferred root-cause hypotheses
- contained_recovery_action/v1 with the smallest safe next action and explicit escalation boundary

Safety rules:

- An agent debug report is not executor reset, hidden state mutation, tool repair, implementation, verification, CI, merge-readiness, merge, or proof that future loops are fixed. Record only observed failure evidence, diagnosis hypotheses, contained recovery actions, and remaining blockers.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

## Runtime Evidence

Preferred harness for this skill: `agent-debug`.

```sh
omh runtime record --skill agent-debug --harness agent-debug --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
