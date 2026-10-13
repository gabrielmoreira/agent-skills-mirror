---
name: restore-session
description: Restore a previously tombstoned Session Registry session owned by the current publisher.
---

# `restore-session` Agentic Skill

Use this skill to reverse a soft delete and make an owned session available again. Restoring does not create a new publication or share link.

## When to Use

Invoke when a user types `/restore-session` or asks to restore or undelete a session they previously deleted. Do not use this for a permanent purge.

## Transport Contract

The `session-registry` MCP tools are the only interface. Do not read the plugin's own files, run a package manager or build step, start the server, or write your own MCP client.

Operation names are MCP names, not guaranteed callable identifiers. Use the host's exact callable identifier and schema when already exposed. Otherwise use the host's tool search or discovery with the query template below. Codex may expose tools directly without a search tool; use its exact advertised namespace and operation as separate values. Do not concatenate them or invent a tool name or prefix. Tool search is not MCP resource discovery: never call `resources/list` or `list_mcp_resources`. An `unsupported call` is not evidence the server is disconnected. If unresolved, stop and report the routing error.

<!-- routing-operations: restore_session -->
<!-- routing:begin -->
Ops: `restore_session`
- Copilot name: `session-registry-<operation>`
- Copilot query: `session-registry-<operation>`
- Claude name: `mcp__plugin_session-registry_session-registry__<operation>`
- Claude query: `mcp__plugin_session-registry_session-registry__<operation>`
- Codex name: `namespace=<host-exposed namespace>, name=<operation>`
- Codex query (only when native tool search is available): `<operation>`
<!-- routing:end -->

## Execution Protocol

1. Resolve the immutable `sessionId` from the original `save_session` or `publish_session` result. It is not the harness session ID or the share-link ID. Never guess or reconstruct it.
1. Call `restore_session` with exactly `{ sessionId }`.
1. Report the returned outcome plainly. If the session remains inaccessible because its content is blocked, say so; do not claim it is available.

## Safety Rules

- Restore only when the user explicitly asks. A prior deletion does not
  authorize restoration.
- Ownership is checked by the server using the configured publisher credentials. Never substitute credentials or another user's session ID.
- If the original publish result is not visible, ask the user for the immutable `sessionId`; do not use the share URL or harness ID instead.

## Example

```text
User: restore the session I deleted earlier
```
