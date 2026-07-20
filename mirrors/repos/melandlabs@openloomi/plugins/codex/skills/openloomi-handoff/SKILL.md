---
name: openloomi-handoff
description: "Use OpenLoomi handoff workflows from Codex to send current tasks to Loomi for follow-up, reminders, delegation, or later attention. Trigger when users ask to hand off, delegate, queue, remind, or follow up through Loomi."
allowed-tools: "Bash(node $SKILL_DIR/../../scripts/loomi-bridge.mjs *)"
---

# OpenLoomi Handoff

Use this skill as a thin wrapper for OpenLoomi handoff workflows. Do not build a
separate task queue, reminder store, or persistence layer inside the Codex
plugin.

First, load workflow guidance:

```bash
node "$SKILL_DIR/../../scripts/loomi-bridge.mjs" workflow-guidance --workflow openloomi-handoff
```

Then check readiness:

```bash
node "$SKILL_DIR/../../scripts/loomi-bridge.mjs" setup-status
```

If `ready: false`, follow the reported `nextAction` before attempting handoff.
When `ready: true`, use the documented OpenLoomi handoff or scheduling API for
the requested action. The generic `loomi-bridge run` command no longer exists.
Include enough task context for OpenLoomi to create a follow-up, but do not
include secrets. OpenLoomi runtime owns handoff persistence and notification
routing.

---

## Sandbox and network

If `setup-status`, `workflow-guidance`, or any handoff/scheduling API call
fails with a network error (`ECONNREFUSED`, `ETIMEDOUT`, "unreachable"),
check whether Codex is running inside a sandbox before concluding OpenLoomi
is stopped. Codex network sandboxing can block loopback access to the
host's `localhost` (e.g. `http://localhost:3414`) and outbound traffic to
the scheduling/notification channels OpenLoomi uses for follow-up delivery.
Request approval and retry the same command outside the sandbox. If the
outside-sandbox retry succeeds, treat the in-sandbox failure as a sandbox
artifact and continue. See `openloomi` for the canonical
`loopbackAccess.verification.commands` probe.
