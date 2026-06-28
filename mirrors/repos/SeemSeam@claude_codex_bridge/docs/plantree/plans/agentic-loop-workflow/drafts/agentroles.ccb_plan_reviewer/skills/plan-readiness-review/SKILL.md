---
name: plan-readiness-review
description: Review planner task packets for readiness without rewriting authoritative task state.
---

# Plan Readiness Review

Use this skill when a planner artifact needs an independent quality gate before
execution or clarification.

## Inputs

- task packet
- readiness recommendation
- candidate questions
- acceptance and verification contract
- prior round evidence if replanning

## Output

Return a planner review with one decision:

- `approve`
- `needs_revision`
- `needs_clarification`
- `blocked`

## Required Checks

- scope and non-goals are explicit;
- acceptance criteria are observable;
- verification can be executed or reviewed;
- unresolved risks are named;
- no hidden fallback or degradation is accepted;
- current-phase user questions are separated from deferrable questions.
