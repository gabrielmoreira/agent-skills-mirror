---
name: clarification-broker
description: Compress planner candidate questions into a compact frontdesk-facing clarification batch and normalize answers back to planner.
---

# Clarification Broker

Use this skill for staged clarification between planner and frontdesk.

## Inputs

- candidate questions
- task packet draft
- existing decisions and user constraints
- previous answers if any

## Outputs

- user-facing question batch
- defaults applied
- deferred questions
- normalized answers when user response is provided

## Rules

- Prefer one stage-batched question set over many interruptions.
- Remove duplicates and already-answerable questions.
- Defer later-phase questions instead of overloading frontdesk.
- Do not alter authoritative task state directly.
