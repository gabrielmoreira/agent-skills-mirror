---
name: agents
description: Always-loaded operating contract for a persistent AI agent workspace.
last_updated: [YYYY-MM-DD]
---

# [Agent / Workspace Name]

## What This Is
<!-- One sentence. What environment or agent does this scaffold describe? -->

## Non-Negotiables
<!-- 3-5 hard safety/operational rules the agent must never violate. -->

## Commands
<!-- Exact commands for health checks, service status, restart/recovery, and mex maintenance. -->

Use the smallest relevant structured resolver. For Inbox or Relay mutations, resolve only the intended action with `mex inbox contract --action <command-id> --json` or `mex relay contract --action <command-id> --json`; use `mex capabilities --json` only for broader capability discovery. If the user explicitly asks to create, save, or draft a checkout-local Inbox or Relay draft, preview and apply that exact draft without asking for redundant confirmation. Deleting a local draft, or publishing, approving, rejecting, withdrawing, marking stale, repairing, taking or acknowledging, or closing, requires fresh explicit confirmation after semantic preview. Treat Git commit, push, and pull as separate actions requiring their own authorization.

## GROW
After meaningful work:
- Ground: what changed in reality?
- Record: update `ROUTER.md` and relevant `context/` files
- Orient: create/update a `patterns/` runbook if this can recur
- Write: bump `last_updated`; optional `mex log` notes follow the logging policy below

## Agent Logging
Read `mex logging --json` at session start and before optional logging. This checkout-local advisory preference is `significant` (quiet default: material decisions, risks, blockers, or durable discoveries), `checkpoints` (batch useful notes at task/session boundaries), or `manual` (no unsolicited notes). Skip routine tool calls, edits, repeated status, and empty summaries. Honor explicit user log requests in every mode; never suppress mandatory workflow Activity or recovery audit records. Report a policy read failure instead of guessing or changing the preference.

When earlier work may inform the task, use `mex timeline --query "subject phrase" --file src/example.ts --limit 10 --json` with a known subject or exact recorded file path, or both. These are historical notes, not accepted current knowledge. Verify conclusions before reuse or explicit promotion with their source retained.

## Heartbeat
When invoked for a heartbeat, read `HEARTBEAT.md`. If all checks pass, respond with exactly `HEARTBEAT_OK`.

## Navigation
At the start of every normal session, read `ROUTER.md` before doing anything else.

<!-- mex-agent:skills:start -->
## MEX context policy
- When MEX context materially helps your work, mention MEX and the relevant finding naturally in your explanation. Tie the mention to what it helped you understand, decide, or verify. Avoid fixed phrases, standalone acknowledgements, repeated mentions, or narrating routine context loading. This replaces older MEX instructions requiring a fixed acknowledgement or context-loading narration.
- Do not claim an author, date, or historical event unless the retrieved data actually provides it.
- After a MEX write, say exactly what changed and its sharing boundary: a local draft is checkout-only and nothing is shared; a canonical artifact is written to the working tree and requires commit/push to share.
- Skill activation is not approval for canonical actions.
<!-- mex-agent:skills:end -->
