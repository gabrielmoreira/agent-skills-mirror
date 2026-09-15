---
name: research-lead-sidecar
description: Use when the user wants multi-agent division of labor for research-led work and the lead should stay on the critical path while 1-2 bounded sidecars handle low-coupling tasks. Do not use this for tiny tasks, fully sequential debugging, or overlapping refactors.
---

# Research Lead Sidecar

## Overview

Use this skill for research-led work where implementation and evidence gathering are coupled, but the main agent should remain the lead. It keeps the critical path local while bounded sidecars handle non-blocking scout, worker, verifier, or writer tasks.

After the user approves an execution contract, use this as the default delegation shape: one lead owns framing, synthesis, and user-facing updates while 1-2 bounded sidecars help without taking over the mission.

## Rules

- Keep the lead responsible for framing, synthesis, and final decisions.
- If the sidecar plan has not been approved yet, do not launch sidecars. First encode the roles and scopes in the execution contract.
- Delegate only tasks that are non-blocking, bounded, inspectable, and recoverable.
- Prefer 1-2 sidecars with clear roles instead of spawning a crowd by default.
- The lead should keep moving on the critical path instead of waiting idly for sidecars.
- Allow write sidecars only when ownership and file scope are explicit and disjoint. If scopes overlap, keep sidecars read-only.
- Use milestone verification and durable workspace state only when the task span justifies them.
- Each sidecar should return something the lead can inspect quickly: a patch, result summary, failure analysis, evidence table, or focused recommendation.
- The lead owns integration: accept, adapt, or reject sidecar results instead of delegating away final judgment.

## When to Use

Use when:

- the user explicitly wants 多智能体分工, research-led multi-agent work, or long-task governance with a lead agent
- there is one critical path plus a small number of low-coupling side tasks
- sidecars can return artifacts the lead can inspect quickly
- low-touch continuous execution is desired, but full handoff would be too lossy

Do not use when:

- the task is tiny, fully sequential, or blocked on each previous result
- several agents would need to touch the same hot files or same narrow context
- handoff cost is higher than simply doing the work locally

## Execution Contract

When using this skill under an approved execution contract, keep the protocol aligned:

- During alignment:
  - say why `lead-sidecar` is the chosen lane
  - name the likely sidecar roles
  - state what remains on the lead's critical path
  - wait for approval before spawning
- After approval:
  - the lead may spawn bounded sidecars without asking again for each ordinary delegation
  - the lead should continue on the critical path while sidecars run
  - sidecar outputs should be integrated at checkpoint boundaries, not left dangling
- During continuation:
  - brief follow-ups such as `继续` should resume the active lead-plus-sidecar lane
  - do not spawn duplicate sidecars if a still-relevant one is already active

## Checkpoint Contract

At each meaningful checkpoint, the lead should be able to state:

- current mission / phase
- current critical-path task
- active sidecars and their scopes
- what has returned and what still matters
- the next integration step
