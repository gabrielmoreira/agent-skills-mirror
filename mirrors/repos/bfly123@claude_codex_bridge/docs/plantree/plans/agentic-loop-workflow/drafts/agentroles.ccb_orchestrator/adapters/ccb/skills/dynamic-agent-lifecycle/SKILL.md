---
name: dynamic-agent-lifecycle
description: Historical reference for script-owned dynamic-agent lifecycle actions. Do not use from provider sessions.
---

# Dynamic Agent Lifecycle Reference

This reference is retained for rolepack history only. It is not projected as an
active provider skill for `agentroles.ccb_orchestrator`.

Dynamic-agent lifecycle changes are runner-owned. The orchestrator may identify
that a helper or execution role is needed, blocked, or ready for release, but
the supervisor/runner script performs all lifecycle commands and authority
writes.

## Provider Boundary

- Do not run CCB commands.
- Do not add, hide, park, resume, remove, release, or inspect agents from the
  provider session.
- Do not edit `.ccb` runtime files, provider state, panes, leases, sockets,
  mailbox records, or topology files.
- Do not choose windows, panes, or placement values.

## Reply Shape

When lifecycle information is needed, reply with semantic evidence only:

- requested role/profile and reason;
- known blockers or missing evidence;
- readiness or release recommendation;
- citations to task packet, execution contract, and supplied runtime evidence.

The runner owns command execution and treats provider replies as evidence only.
