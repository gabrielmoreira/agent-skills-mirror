---
name: orchestrator-capacity
description: Historical reference for script-owned loop capacity requests. Do not use from provider sessions.
---

# Orchestrator Capacity Reference

This reference is retained for rolepack history only. It is not projected as an
active provider skill for `agentroles.ccb_orchestrator`.

Loop capacity is now runner-owned. The orchestrator may recommend the semantic
need for capacity, but the supervisor/runner script performs any actual
capacity ensure, status, release, routing, and cleanup.

## Provider Boundary

- Do not run CCB commands.
- Do not inspect runtime capacity from the provider session.
- Do not release agents, mutate task status, import artifacts, or route work.
- Do not invent agent names, windows, panes, provider profiles, or topology.

## Reply Shape

When capacity information is needed, reply with semantic evidence only:

- requested profiles and counts;
- task packet and verification refs;
- blockers or missing evidence;
- release-readiness recommendation based on supplied worker/reviewer evidence.

The runner owns command execution and treats provider replies as evidence only.
