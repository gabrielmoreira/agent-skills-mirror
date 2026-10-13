---
name: get-session-card
description: Retrieve the PR-Ready Share Card Markdown for an already-published Session Registry session, returned in a markdown code fence with no wrapping commentary.
---

# `get-session-card` Agentic Skill

Use this skill to fetch the copyable PR-Ready Share Card Markdown for a
session that has already been published, independent of the PR-creation
flow. This is useful whenever the card is needed somewhere other than a
freshly-created PR body — pasting into an existing PR/MR by hand, a Slack
message, a wiki page, or anywhere else a collaborator-facing card is
wanted.

## Transport Contract

The `session-registry` MCP tools are the only interface to this workflow. Do not read the plugin's own files, run a package manager or build step, start the MCP server yourself, or write your own MCP client.

Operation names are MCP names, not guaranteed callable identifiers. Use the host's exact callable identifier and schema when already exposed. Otherwise use the host's tool search or discovery with the query template below. Codex may expose tools directly without a search tool; use its exact advertised namespace and operation as separate values. Do not concatenate them or invent a tool name or prefix. Tool search is not MCP resource discovery: never call `resources/list` or `list_mcp_resources`. An `unsupported call` is not evidence the server is disconnected. If unresolved, stop and report the routing error; never write your own MCP client. Relay resolved tool errors as tool errors.


<!-- routing-operations: get_share_card -->
<!-- routing:begin -->
Ops: `get_share_card`
- Copilot name: `session-registry-<operation>`
- Copilot query: `session-registry-<operation>`
- Claude name: `mcp__plugin_session-registry_session-registry__<operation>`
- Claude query: `mcp__plugin_session-registry_session-registry__<operation>`
- Codex name: `namespace=<host-exposed namespace>, name=<operation>`
- Codex query (only when native tool search is available): `<operation>`
<!-- routing:end -->

## When to Use

Invoke this skill when a user:

- Types `/get-session-card`
- Asks to "get the share card", "give me the PR card markdown for this
  session", "show me the share card", or "get the share card for
  `<link>`"

## `linkId` Resolution

`get_share_card` takes exactly one input: `linkId` — the last path segment
of the collaborator share URL (`.../session/<harnessSessionId>/<linkId>`),
and also the literal `linkId` field present in any `save_session` or
`publish_session` tool result JSON.

Resolve it in this order, and **never** guess or fabricate a value:

1. **Explicit argument given.** If the user supplies a bare `linkId` or a
   full `shareUrl` directly (as an argument to the skill invocation),
   always use it — parsing the exact last path segment if a `shareUrl` was
   given. This takes priority over everything below and never triggers a
   question.
2. **No argument given — scan this conversation** for every
   `save_session`/`publish_session` tool result and collect each result's
   distinct `linkId` (dedupe exact matches; a retry of the same publish
   reuses the same `linkId` and is not a second distinct publish):
   - **Exactly one distinct `linkId` found:** infer it silently and
     proceed straight to calling `get_share_card`. Do **not** ask the user
     anything in this case — a single prior publish this conversation is
     unambiguous.
   - **Two or more distinct `linkId`s found:** ambiguous. Ask the user
     which session they mean, listing each known candidate (by title,
     summary, or share URL already visible from those earlier results) or
     accepting a `linkId`/`shareUrl` they supply directly.
   - **Zero found:** there is nothing to infer. Ask the user for the
     `linkId` or `shareUrl` directly, same as the ambiguous case.
3. Never reuse a `linkId` from a different conversation/session, and never
   assemble or approximate one from fragments of other identifiers.

## Execution Protocol

1. Resolve `linkId` per the rule above. In the single-candidate
   auto-inference case, skip straight to step 2 — do not ask a
   confirmation question first.
2. Call `get_share_card` with `{ linkId }`.
3. **If the result is `{ kind: "available", markdown }`:** reply with
   **only** the `markdown` field's content, copied verbatim,
   character-for-character, inside a fenced code block tagged `markdown`.
   Choose a fence delimiter longer than any backtick run in the returned
   markdown so the fence encloses the complete card. Do not add a leading
   sentence ("Here's your share card:"), a trailing note, or any other text
   in that same message. This is a hard requirement: never rationalize
   adding a short intro or confirmation line "just this once."
4. **If the result is `{ kind: "unavailable" }`:** there is no card content
   to protect from added prose, so respond in plain, brief text stating
   that the share card is not currently available (the link may have been
   revoked, expired, or is otherwise not resolvable) and that there is
   nothing to display.

## Safety Rules

- Ownership is enforced entirely server-side from the caller's configured
  bearer token; never ask the user to prove ownership some other way.
- Never fabricate, approximate, or partially reconstruct card markdown —
  only ever emit the exact `markdown` string returned by the tool.
- If the tool reports the link was not found or not owned by the caller,
  say so plainly rather than retrying with a different guessed `linkId`.

## Examples

```powershell
/get-session-card
```

```text
User: get me the share card for the session I just published
```

```text
User: get-session-card https://sessionregistry.io/session/abc123/def456
```
