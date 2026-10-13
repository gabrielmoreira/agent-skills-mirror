---
name: purge-sessions
description: Preview and, after confirmation, permanently purge all of the caller's currently tombstoned Session Registry sessions in one bulk operation.
---

# `purge-sessions` Agentic Skill

Use this skill to permanently, irreversibly hard-delete **every one of the
caller's currently tombstoned published sessions** in a single bulk
operation. This is the bulk counterpart to `purge-session`: it never
accepts an id list, and it always previews the exact set before deleting
anything.

## Transport Contract

The `session-registry` MCP tools are the only interface to this workflow. Do not read the plugin's own files, run a package manager or build step, start the MCP server yourself, or write your own MCP client.

Operation names are MCP names, not guaranteed callable identifiers. Use the host's exact callable identifier and schema when already exposed. Otherwise use the host's tool search or discovery with the query template below. Codex may expose tools directly without a search tool; use its exact advertised namespace and operation as separate values. Do not concatenate them or invent a tool name or prefix. Tool search is not MCP resource discovery: never call `resources/list` or `list_mcp_resources`. An `unsupported call` is not evidence the server is disconnected. If unresolved, stop and report the routing error; never write your own MCP client. Relay resolved tool errors as tool errors.


<!-- routing-operations: purge_sessions -->
<!-- routing:begin -->
Ops: `purge_sessions`
- Copilot name: `session-registry-<operation>`
- Copilot query: `session-registry-<operation>`
- Claude name: `mcp__plugin_session-registry_session-registry__<operation>`
- Claude query: `mcp__plugin_session-registry_session-registry__<operation>`
- Codex name: `namespace=<host-exposed namespace>, name=<operation>`
- Codex query (only when native tool search is available): `<operation>`
<!-- routing:end -->

## When to Use

Invoke this skill when a user:

- Types `/purge-sessions`
- Asks to "purge all my tombstoned sessions", "empty my session trash",
  "permanently remove all the sessions I've deleted", or similar
  all-tombstoned-sessions phrasing

If the user names one specific session, use `purge-session` instead — do
not use this bulk tool for a single target.

## How This Tool Differs From `purge-session`

`purge_sessions` takes **no input at all** (its schema is `{}`, strict — do
not attempt to pass a `sessionId` or an id list). In one call, the tool
itself:

1. Computes the caller's current tombstoned session set server-side.
2. If nothing is tombstoned, returns immediately with no confirmation step.
3. Otherwise, asks for confirmation **through the MCP elicitation
   mechanism** (a form the host renders, listing every session in the
   fixed previewed set with its title, id, and tombstoned date).
4. Only on explicit acceptance does it purge exactly that previewed set —
   never a set computed fresh at purge time, so nothing tombstoned after
   the preview was shown gets swept in unexpectedly.

Because the confirmation is server-driven, do not fabricate your own
confirmation prompt, do not ask the user to approve before calling the
tool, and do not summarize or shorten the preview list yourself — call the
tool and let its own elicitation request reach the user verbatim.

## Execution Protocol

1. Call `purge_sessions` with `{}` (no arguments).
2. If the host surfaces an elicitation/confirmation prompt from the tool,
   let it reach the user as-is; do not intercept, rewrite, or pre-answer
   it.
3. Report the final result based on `confirmation`:
   - `not_needed` — say plainly that there were no tombstoned sessions to
     purge; nothing happened.
   - `unavailable` — say plainly that this host doesn't support the
     in-call confirmation form needed for a bulk purge, so nothing was
     purged; suggest `purge-session` one at a time as an alternative if
     the user still wants specific sessions gone.
   - `cancelled` / `declined` — say plainly that the purge was cancelled
     or declined and nothing was deleted.
   - `accepted` — report the per-session outcome breakdown from
     `outcomes`: counts of `purged`, `purged_with_blob_cleanup_failures`,
     `skipped` (with each `reason`, e.g. already purged or no longer
     tombstoned), and `failed` (with each `reason`). Do not just report a
     single aggregate number if any sessions were skipped or failed —
     name them.

## Safety Rules

- Never pass any input to this tool; it always operates on the server's
  own freshly computed tombstoned-session preview, not on ids you supply.
- Never treat a prior `delete-session` call in the same conversation as
  implicit authorization to also run `purge-sessions` — always requires
  its own explicit user request and its own confirmation step.
- This is irreversible for every session in the confirmed set. If the
  user seems unsure how many sessions this affects, let the tool's own
  preview answer that rather than guessing or precounting yourself.

## Examples

```powershell
/purge-sessions
```

```text
User: I'm cleaning up — permanently remove every session I've deleted so far
```
