---
name: purge-session
description: Permanently and irreversibly hard-delete one already-tombstoned Session Registry session by its published sessionId, including best-effort blob cleanup.
---

# `purge-session` Agentic Skill

Use this skill to permanently, irreversibly hard-delete one previously
published session that has **already been tombstoned** by `delete-session`.
This is destructive: unlike `delete-session`, there is no restore path
after a purge succeeds. Treat every invocation as a one-way action and make
that unmissable to the user before calling the tool.

## Transport Contract

The `session-registry` MCP tools are the only interface to this workflow. Do not read the plugin's own files, run a package manager or build step, start the MCP server yourself, or write your own MCP client.

Operation names are MCP names, not guaranteed callable identifiers. Use the host's exact callable identifier and schema when already exposed. Otherwise use the host's tool search or discovery with the query template below. Codex may expose tools directly without a search tool; use its exact advertised namespace and operation as separate values. Do not concatenate them or invent a tool name or prefix. Tool search is not MCP resource discovery: never call `resources/list` or `list_mcp_resources`. An `unsupported call` is not evidence the server is disconnected. If unresolved, stop and report the routing error; never write your own MCP client. Relay resolved tool errors as tool errors.


<!-- routing-operations: purge_session -->
<!-- routing:begin -->
Ops: `purge_session`
- Copilot name: `session-registry-<operation>`
- Copilot query: `session-registry-<operation>`
- Claude name: `mcp__plugin_session-registry_session-registry__<operation>`
- Claude query: `mcp__plugin_session-registry_session-registry__<operation>`
- Codex name: `namespace=<host-exposed namespace>, name=<operation>`
- Codex query (only when native tool search is available): `<operation>`
<!-- routing:end -->

## When to Use

Invoke this skill when a user:

- Types `/purge-session`
- Asks to "permanently delete this session", "hard-delete my session",
  "purge this session", or "actually remove this session for good"

If the user's wording only implies taking a session offline (not permanent
removal), use `delete-session` instead and confirm which one they meant if
genuinely ambiguous.

## `sessionId` Disambiguation (read this first)

`purge_session` takes exactly one input: `sessionId`, the **opaque id
returned by the original `publish_session` or `save_session` tool result**
(the JSON field literally named `sessionId`). This is **not**:

- `harnessSessionId` — the native harness's own session identifier, also
  present in that same result.
- The `linkId` segment embedded in the collaborator share URL
  (`.../session/<harnessSessionId>/<linkId>`).

If the user only has a share URL or remembers the harness session id, do
not guess or substitute one of those other values as `sessionId`. Read it
from the original publish/save result earlier in this conversation, or ask
the user to supply it directly.

## Precondition: the session must already be tombstoned

`purge_session` only succeeds on a session that `delete_session` has
already tombstoned. If the target session is still active (never deleted),
the call fails with a not-tombstoned error. Do not treat that as a reason
to call `delete_session` and then immediately purge in the same breath —
surface the precondition to the user and let them decide whether they
actually want the session deleted first, then purged separately.

## Execution Protocol

1. Resolve the true `sessionId` per the disambiguation rule above.
2. **Warn explicitly before calling the tool**: state plainly that this
   permanently and irreversibly deletes the session's data and cannot be
   undone, and give the user a chance to back out, unless they have
   already made the destructive intent unambiguous in the same message
   (e.g. "yes, permanently delete session sess_... now").
3. Call `purge_session` with `{ sessionId }`.
4. Report the result, distinguishing:
   - `outcome: "purged"` — fully removed, including all associated blobs.
   - `outcome: "purged_with_blob_cleanup_failures"` — the session row is
     gone and cannot be recovered, but list which blobs (from
     `blobResults`) could not be deleted immediately and note this is a
     best-effort background cleanup concern, not something the user needs
     to act on.
5. If the call fails because the session was not found, not owned by the
   caller, or not yet tombstoned, relay that specific reason plainly —
   never retry with a different guessed id or silently fall back to
   `delete_session`.

## Safety Rules

- Never call this tool speculatively "just in case" or as an automatic
  follow-up to `delete-session` — purging is always a separate, deliberate
  user decision.
- Ownership is enforced entirely server-side from the caller's configured
  bearer token; never attempt to purge a session on another user's behalf.
- Blob cleanup is best-effort and shared blobs are intentionally preserved
  when still referenced elsewhere — a `purged_with_blob_cleanup_failures`
  outcome means the session itself is already gone, not that the purge
  can be retried or resumed.

## Examples

```powershell
/purge-session
```

```text
User: permanently purge session sess_3f9c1e2a-..., I already deleted it last week
```
