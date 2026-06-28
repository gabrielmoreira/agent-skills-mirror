---
name: planner-task-packet
description: Draft CCB workflow task packets, readiness recommendations, and candidate clarification questions without mutating authoritative state.
---

# Planner Task Packet

Use this skill when converting macro user intent or a frontdesk request into a
plan artifact for review.

## Inputs

- macro task request
- relevant plan-tree/source references
- explicit scope and non-goals
- current phase or prior round result if any

## Outputs

Produce these artifacts or equivalent sections:

- `task-packet.md`
- `readiness.json`
- `candidate-questions.jsonl` when user input may be needed

Readiness values are exactly:

- `ready`
- `needs_clarification`
- `blocked`
- `not_ready`

## Rules

- Do not mark task state directly.
- Do not start execution.
- Do not call workers, checkers, or orchestrator.
- Do not reduce acceptance criteria to make the task executable.
- Questions must be current-phase questions; defer later-phase questions.
