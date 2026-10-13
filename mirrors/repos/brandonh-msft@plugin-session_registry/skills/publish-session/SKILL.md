---
name: publish-session
description: Publish current Copilot, Claude, or Codex CLI sessions, or VS Code chats.
---

# Publish a native session

Use for `/publish-session` or explicit sharing, not local-capture-only requests.

For every live chat or slash command use `interactionMode: "interactive"`.
Never skip secret decisions or the metadata form.

## Transport Contract - Resolve the host tool first

Use the host's **exact callable identifier and schema** when already exposed. Otherwise use the host's tool search or discovery with the query template below. Codex may expose tools directly without a search tool; use its exact advertised namespace and operation as separate values. Do not concatenate them or invent a tool name or prefix. Host discovery is not MCP resource discovery; never call `resources/list` or `list_mcp_resources`. An `unsupported call` is not evidence the server is disconnected: resolve the actual identifier or stop and report the routing failure. Claim disconnection only on host evidence; relay tool errors unchanged.

The MCP tools are the only interface. Do not read the plugin's own files, run a package manager or build step, start the server, or write your own MCP client; never replace native capture or forms.

<!-- routing-operations: save_session, prepare_session_capture, publish_session -->
<!-- routing:begin -->
Ops: `save_session`, `prepare_session_capture`, `publish_session`
- Copilot name: `session-registry-<operation>`
- Copilot query: `session-registry-<operation>`
- Claude name: `mcp__plugin_session-registry_session-registry__<operation>`
- Claude query: `mcp__plugin_session-registry_session-registry__<operation>`
- Codex name: `namespace=<host-exposed namespace>, name=<operation>`
- Codex query (only when native tool search is available): `<operation>`
<!-- routing:end -->

## Capture and publish

1. Identify the harness: `github-copilot-cli`, `claude-code`, or `codex-cli`.
   In VS Code Copilot Chat use `vscode-copilot-chat` with no selector.
   Publish only the current session; selectors never override host identity.
   Copilot uses its profile-guarded runtime ID; Codex requires a verified thread
   ID; Claude's hook supplies current ID/path, which the server checks against
   its native journal. Without a host ID, pass absolute `workingDirectory` and
   the newest exact `verificationWindow`: 3-6 ordered, verbatim `{role, text}`
   turns (two distinct user turns and one assistant; 32 KiB max).
   `recentUserMessage` is the last user turn. Exclude excerpts, summaries, tool
   output, and candidate journals; join text blocks with newlines. Never ask
   for IDs or paths.
1. Call `save_session` with harness, interaction mode, source selector, a drafted
   title (1-120 characters), and summary (1-500 characters). Honor owner edits;
   the server rescans and truncates metadata.
   Every invocation is a fresh publication about the substantive task, outcome,
   and decisions. Never title
   or summarize the slash command, publication request/process, prior receipt,
   or share link.
   `prepare_session_capture` is for local capture only, with the interactive
   **Codex App** exception; never a bypass of
   `save_session` for `github-copilot-cli`, `claude-code`, or Codex CLI.
1. Preserve requested access and expiry. Otherwise default to anyone with the link
   (`audiencePolicy: {accessMode: "anonymous"}` or omit it) and 14 days (omit `expiresAt`).
   `expiresAt: null` means never expire. Never invent recipients or downgrade
   restricted access.
1. Let the server capture, scan, drive owner decisions, and upload only approved
   native content. Report the finding count.

## Owner-facing forms

For Codex CLI, GHCP, and Claude, **the server renders every form in this phase itself**
through host elicitation. Do not pre-answer, recreate, merge, or replace its forms with chat questions.
Never bundle fields into a single run-on prompt.

1. **Secret decision gate**, when findings exist: the owner chooses bulk redaction,
   individual review, or explicit unredacted override. Individual review offers
   redact, keep, or custom replacement.
   Never decide findings, redactions, or overrides on the owner's behalf.
1. **One-shot metadata form**: prefilled title, summary, audience, expiration,
   and optional `additionalRedactions`. Each target becomes an exact-text rule
   applied to native content and metadata.
1. **Codex CLI only**: after its sequential metadata questions, show the
   non-editable recap and require native Accept before upload.

For interactive Codex App or a no-elicitation proposal, show these fields and wait:

```markdown
**Title**: <prefilled title>
**Summary**: <prefilled summary>
**Audience**: <prefilled audience>
**Expiration**: <prefilled expiration>
**Additional redactions** (optional, blank means none): <prefilled value>
```

Never compress these into one paragraph or question. Resolve findings first; rendering
never skips the secret gate. For GHCP or Claude, the reply is final approval; retry
`save_session` with the returned request and edits. For Codex, show the non-editable
recap and wait again. Only its explicit publish response authorizes `publish_session` with that
`captureId`, confirmed values, resolutions, `confirmed: true`, and
`additionalRedactionsConfirmed: true` when findings existed.

`noninteractive` is only for headless invocations with no further chat possible
(`copilot -p`, `claude --print`, `codex exec`). There the publish request authorizes
supplied/default settings and the native-package warning; unresolved secrets still block.
Urgency, "just publish it", or a demo never authorize headless mode in live chat.

## Errors and retries

- **Routing failure:** use host tool search only; never probe MCP resources or the environment.
- **Source errors:** relay it; never substitute a session or synthetic history.
- **`CURRENT_SESSION_EVIDENCE_REQUIRED` / `CURRENT_SESSION_NOT_VERIFIED`:**
  retry with the newest complete turns. If still unverified, report it; never
  invent turns, reuse historical IDs/paths, or redirect to a native publisher.
- **`MISSING_DEPENDENCY`:** use `dependencyMappings` only for owner-supplied
  relocated files; never search or substitute.
- **`UNSUPPORTED_DEPENDENCY`:** report the decode error; never treat it as file authorization.
- **Security findings:** collect explicit owner decisions and regenerate metadata
  only from approved content. Never suppress scan failures.
- **Unmatched owner redactions:** check the applied-redaction count; they do not block publication.
- **`confirmation-timeout`:** report expired form; no upload. Retry only
  if the owner asks, after recollecting approvals. Never auto-answer or switch to noninteractive.
- **`PUBLISH FAILED`:** while `automaticRetry` is true, wait `retryAfterSeconds` and
  call `structuredContent.nextCall` with the unchanged `retryRequest`. Otherwise
  relay `ownerMessage` and stop. If `structuredContent` is missing, use adjacent
  JSON. Refresh only `currentSession` evidence when required; never redo forms.
  On an owner-requested retry of a result with `resume`, call `save_session`
  with its `captureId`, `resume: true`, same harness/interactionMode.
- **Transport timeout without a server `retryRequest`:** stop; the handler may
  still run, so report the outcome as unknown.
- **`PUBLISH_STATE_UNKNOWN`:** use any server `retryRequest` unchanged; refresh
  `currentSession` only if needed. Without one, stop. Never recapture; claim
  success only with the full share URL.

## Share output

Relay the server-authored publication receipt unchanged; copy its raw API `shareUrl` exactly.
Never reconstruct, normalize, shorten, substitute, rehost, or omit it. Don't
republish or fetch a card to verify. The server controls its MCP result, not the final
assistant response; host rendering is not guaranteed.
