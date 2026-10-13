---
name: delete-session
description: Soft-delete (tombstone) a previously published Session Registry session by its collaborator-facing share URL, so it stops resolving for viewers while remaining recoverable.
---

# `delete-session` Agentic Skill

Use this skill to tombstone one previously published session so its share
link and download stop resolving for collaborators. This is a **soft**
delete: the session's row and stored content are preserved, and the
tombstone can later be undone (via the registry's restore capability) or
made permanent (via `purge-session`/`purge-sessions`). Deleting is not the
same as purging — never conflate the two when talking to the user.

## Transport Contract

The `session-registry` MCP tools are the only interface to this workflow. Do not read the plugin's own files, run a package manager or build step, start the MCP server yourself, or write your own MCP client.

Operation names are MCP names, not guaranteed callable identifiers. Use the
host's exact callable identifier and schema when already exposed. Otherwise use
the host's tool search or discovery with the query template below. Codex may
expose tools directly without a search tool; use its exact advertised namespace
and operation as separate values. Do not concatenate them or invent a tool name
or prefix. Tool search is not MCP resource discovery: never call `resources/list`
or `list_mcp_resources`. An `unsupported call` is not evidence the server is disconnected.
If unresolved, stop and report the routing error; never write your own MCP
client. Relay resolved tool errors as tool errors.


<!-- routing-operations: delete_session -->
<!-- routing:begin -->
Ops: `delete_session`
- Copilot name: `session-registry-<operation>`
- Copilot query: `session-registry-<operation>`
- Claude name: `mcp__plugin_session-registry_session-registry__<operation>`
- Claude query: `mcp__plugin_session-registry_session-registry__<operation>`
- Codex name: `namespace=<host-exposed namespace>, name=<operation>`
- Codex query (only when native tool search is available): `<operation>`
<!-- routing:end -->

## When to Use

Invoke this skill when a user:

- Types `/delete-session`
- Asks to "delete my published session", "unpublish this session", "take
  this session down", or "stop sharing this session"

Do not invoke `purge-session` or `purge-sessions` in response to these
phrases — those are separate, irreversible operations.

## `shareUrl` (read this first)

`delete_session` accepts exactly one input: `shareUrl`, the
collaborator-facing share URL a viewer was given
(`.../session/<harnessSessionId>/<linkId>`), exactly as it appears in a
publish result or `get_share_card` output. The server resolves this to
the owning session's internal id itself, enforcing the same
ownership check the delete itself performs — it never trusts the URL's
identity, only what the caller's bearer token proves they own. There is
no opaque-sessionId input; never dig one out of an old tool result or
guess at one.

Never confuse `shareUrl` with the distinct identifier also present in a
publish result:

- `harnessSessionId` — the native harness's own session identifier
  (e.g. `COPILOT_AGENT_SESSION_ID`).

If the user only remembers the harness session id and does not have the
share URL, do not guess. Instead:

- If the original `publish_session`/`save_session` tool result (or a
  `shareUrl` the user was given) is still visible earlier in this
  conversation, use it directly.
- Otherwise, ask the user to paste the share URL they were given — not
  the harness session id.

A malformed or unrecognized `shareUrl` (wrong shape, different site, typo)
is rejected before any request reaches the backend; report that plainly
and ask the user to re-paste the URL rather than guessing at a fix.

## Execution Protocol

1. Resolve the `shareUrl` the user actually has. Do not call the tool
   with a guessed or substituted identifier.
2. Call `delete_session` with `{ shareUrl }`.
3. Report the result plainly, distinguishing the two possible outcomes:
   - `outcome: "deleted"` — the session is now tombstoned; its share link
     and download will stop resolving for viewers.
   - `outcome: "already_tombstoned"` — no-op; the session was already
     deleted. State this rather than implying a fresh delete happened.
4. Remind the user, briefly, that this is reversible and does not free
   storage — a permanent purge is a separate, deliberate action
   (`/purge-session` or `/purge-sessions`), not an automatic follow-up.

## Safety Rules

- Ownership is enforced entirely server-side from the caller's configured
  bearer token — never ask the user to prove ownership some other way,
  and never attempt to delete a session on another user's behalf by
  supplying a different credential.
- If the tool reports the share link a `shareUrl` resolved to was not
  found or not owned by the caller, say so plainly — do not retry with a
  different guessed URL.
- Never describe this action as permanent, irreversible, or as freeing
  storage/blob space — that is `purge-session`/`purge-sessions`, not this
  tool.

## Examples

```powershell
/delete-session
```

```text
User: delete this one — https://registry.example.com/session/hs1/link_9f2c
```
