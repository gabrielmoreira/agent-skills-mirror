---
name: "omh-agent-board"
description: "[omh] Hermes agent board workflow: coordinate multiple Hermes profiles or agents with task, handoff, heartbeat, blocker, and completion states. Use when the user says: agent-board, agent board, kanban, multi-agent, multi agent, multi agent board, multiple hermes agents, multiple hermes profiles."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, agent-coordination]
    category: agent-coordination
    phase: board-status
    role: tracker
    quality_tier: workflow-surface-gated
---

# Agent Board

This is a Hermes-native `agent-board` workflow skill.

## Why This Exists

`agent-board` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: agent-board coordinate PM, CTO, QA, and release agents on this launch checklist.
- Expected behavior: Produce `prepare_agent_board_card` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: agent-board mark the other agent complete without an observed heartbeat or result.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- Choose the coordination from the request: `durable` (restart survival, cross-profile pickup) prepares a `kanban_*` action on the named board; `bounded_research` prepares one `delegate_task` action. Never substitute one route for the other when its surface is missing.
- Call `omh_agent_board` `prepare`, then invoke the returned `native_action` through the normal Hermes tool loop; OMH never calls a native tool itself and grants no host permission.
- Report the request state exactly: `prepared`, `unavailable` (named `missing_capabilities`, zero native calls), `denied`, `observed`, or `failed`. A `complete` receipt implies no review approval, CI, or merge; a `running` readback is a claim, not dispatch proof.
- Agent/operator reference: docs/AGENT-BOARD.md; wrapper actions example: examples/agent-board/native-actions.json.

## Recovery Notes

- If `prepare` returns `unavailable`, name the missing capability (tool, schema, hook, host identity, board binding, or native compare-and-swap) and keep the card prepared-only.
- If a receipt is `failed` or `requires_reconciliation`, run an observed `show` on the same task before the next mutation; never retry a `create` automatically. Repeating a `create` with the same `request_id` returns the already observed task.
- No native `kanban_dispatch` tool exists: dispatch stays `unavailable` and an operator claim is the observed path. A positive `request_changes` needs a review-claimed run from the host's own review dispatcher.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `github-issue-intake`, `buzz`, `agent-board`, `+35 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when multiple Hermes profiles, agents, or targets need a board-shaped status contract for collaborative work.

    Strong routing signals: `agent-board`, `agent board`, `kanban`, `multi-agent`, `multi agent`, `multi agent board`, `multiple hermes agents`, `multiple hermes profiles`, `hermes profiles`, `subagent`, `subagents`, `sub agent`, `sub agents`, `agent coordination`, `agent task board`, `task board`, `roles and board`, `role board`, `heartbeat`, `blocker`, `agent blocker`, `agent heartbeat`, `agent handoff`, `handoff board`, `interviewer reviewer builder`, `reviewer builder`, `칸반`, `멀티 에이전트`, `서브에이전트`, `서브 에이전트`, `여러 에이전트`, `Hermes agent 여러 명`, `여러 명이 같이 일`, `에이전트 보드`, `작업 배분`, `역할 배분`, `작업 보드`, `역할과 보드`, `역할 보드`

## Catalog Metadata

Category: `agent-coordination`
Phase: `board-status`
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

- agent-board/v1 card or guidance
- agent_board_request/v1 record from the `omh_agent_board` plugin tool
- next action
- prepared-vs-observed boundary

Artifact expectations:

- agent-board/v1 metadata-only runtime or wrapper card when recorded
- agent_board_state/v1 bounded board snapshot under the OMH home: request digests, receipts, and task references only; never raw bodies, comments, attachments, or host identity

Safety rules:

- An agent board card is not proof that another Hermes agent accepted, executed, heartbeat-ed, or completed work unless target-specific evidence exists.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

## Runtime Evidence

Preferred harness for this skill: `agent-board`.

```sh
omh runtime record --skill agent-board --harness agent-board --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
