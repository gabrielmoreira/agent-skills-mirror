---
name: openloomi-connectors
description: "Use OpenLoomi connector readiness guidance from Codex for Slack, Gmail, Calendar, GitHub, and other integrations. Trigger when users ask whether connectors are configured, need setup, or block a Loomi workflow. Pair with the composio skill to also list composio-linked accounts."
allowed-tools: "Bash(node $SKILL_DIR/../../scripts/loomi-bridge.mjs *)"
---

# OpenLoomi Connectors

Use this skill as a thin wrapper for connector readiness guidance. Do not
implement connector protocols in Codex and do not ask users to paste OAuth
tokens, API keys, bot tokens, cookies, or connector secrets into Codex chat.

First, load workflow guidance:

```bash
node "$SKILL_DIR/../../scripts/loomi-bridge.mjs" workflow-guidance --workflow openloomi-connectors
```

Then check readiness:

```bash
node "$SKILL_DIR/../../scripts/loomi-bridge.mjs" setup-status
```

Report connector state as status and next action only. If a connector is
missing or unavailable, guide the user to OpenLoomi-owned setup surfaces. If the
runtime is ready and the user asks for a connector-backed task, pass the request
over stdin:

```bash
printf "%s" "<user connector request>" | node "$SKILL_DIR/../../scripts/loomi-bridge.mjs" run
```

Keep connector authentication, sync, message access, and platform-specific
actions inside OpenLoomi runtime.

When `setup-status` includes `connectorStatusAvailable: true`, report only the
status-only connector fields such as `id`, `connected`, and `accountCount`. When
it includes `connectorSetupRecommended: true`, treat
`recommendedNextAction: "configure_connectors"` as a non-blocking setup
recommendation and hand the user to the reported OpenLoomi `/connectors` URL.
Do not treat this as core runtime failure when `ready: true`.

`setup-status` may merge Loop connector rows with OpenLoomi native integration
accounts (for example Gmail or QQbot) as status-only connector rows. Report that
connected state when present, but keep all authentication, sync, and account
management inside OpenLoomi.

For accounts connected through **Composio** (a broader 1000+ apps surface),
treat the `composio` skill as a sibling status-only source. When the user asks
"what am I connected to?" or "list all linked accounts", invoke the `composio`
skill in parallel (`composio-cli list-connections`, or
`mcp__composio__COMPOSIO_MANAGE_CONNECTIONS` with `action: "list"`) and merge
its results with the `setup-status` connector rows before reporting. Keep
authentication, OAuth, and disconnect flows native to each skill — do not route
Composio auth or connection management through OpenLoomi.
