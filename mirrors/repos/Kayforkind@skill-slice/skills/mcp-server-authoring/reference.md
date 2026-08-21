# MCP Protocol Reference for Server Authors

Companion to `SKILL.md`. Everything here is host-agnostic protocol knowledge; SDK-specific code lives in the two template files.

## 1. Architecture and lifecycle

```
Host application (Cursor / Claude Desktop / Claude Code / custom agent)
 └── MCP Client (1 per server connection; host may run many)
      └── Transport (stdio pipe | Streamable HTTP)
           └── Your MCP Server
```

- Wire format: **JSON-RPC 2.0** — requests (`id` + `method` + `params`), responses (`result` XOR `error`), and notifications (no `id`, never answered). As of revision 2025-06-18, JSON-RPC **batching is removed** — send one message per frame.
- **Lifecycle**:
  1. Client → `initialize` with `protocolVersion`, `capabilities`, `clientInfo`.
  2. Server responds with the version it will speak, its `capabilities`, `serverInfo`, optional `instructions` (a string the host may inject as system-prompt context — keep it short and imperative; this is prime real estate).
  3. Client → `notifications/initialized`. Only now is normal traffic legal.
  4. Shutdown: stdio = close stdin / process exit; HTTP = session `DELETE` or expiry.
- **Version negotiation**: client proposes a revision (`2025-06-18`, `2025-03-26`, `2024-11-05` are the ones in the wild); server answers with that version if supported, else its latest. Mismatch → client disconnects. On Streamable HTTP, subsequent requests carry `MCP-Protocol-Version` header (2025-06-18+). SDKs handle all of this — your job is only to keep the SDK current.
- **Capabilities you declare** (only declare what you implement): `tools` (+`listChanged`), `resources` (+`subscribe`, `listChanged`), `prompts` (+`listChanged`), `logging`, `completions`. **Capabilities the client may declare**: `sampling`, `roots`, `elicitation` — feature-gate any use of these on what arrived in `initialize`.

## 2. Tools (deep dive)

### 2.1 Descriptor anatomy

```jsonc
{
  "name": "search_orders",                  // ^[a-zA-Z0-9_-]{1,64}$ — required
  "title": "Search orders",                 // human-facing display name (2025-03-26+)
  "description": "Search orders by customer, status, or date range. Returns at most 20 matches per page (use cursor to page). Use get_order for full line-item detail. Read-only.",
  "inputSchema": {                          // JSON Schema, draft 2020-12, type MUST be "object"
    "type": "object",
    "properties": {
      "query":  { "type": "string", "description": "Free-text match on customer name or order id." },
      "status": { "type": "string", "enum": ["open", "shipped", "cancelled"], "description": "Filter by lifecycle status." },
      "cursor": { "type": "string", "description": "Opaque pagination cursor from a previous call." }
    },
    "required": ["query"],
    "additionalProperties": false
  },
  "outputSchema": { /* optional; enables structuredContent validation (2025-06-18) */ },
  "annotations": {
    "readOnlyHint": true,       // does not modify environment
    "destructiveHint": false,   // meaningful only when readOnlyHint=false; default true
    "idempotentHint": true,     // repeat call with same args = no additional effect
    "openWorldHint": false      // touches external world (web) vs closed domain (local db)
  }
}
```

Annotation rules: they are **hints, not security** — hosts use them for confirmation UX (Cursor may auto-run read-only tools but prompt on destructive ones). Lying (e.g. `readOnlyHint: true` on a deleter) gets your server uninstalled and is a safety bug. When unsure, leave defaults (which are conservative: not read-only, destructive).

### 2.2 Call results

```jsonc
{
  "content": [
    { "type": "text", "text": "Found 3 orders…" },
    { "type": "image", "data": "<base64>", "mimeType": "image/png" },
    { "type": "audio", "data": "<base64>", "mimeType": "audio/wav" },
    { "type": "resource_link", "uri": "orders://ORD-1042", "name": "ORD-1042",
      "description": "Full order record", "mimeType": "application/json" },
    { "type": "resource", "resource": { "uri": "file:///tmp/report.md", "mimeType": "text/markdown", "text": "…" } }
  ],
  "structuredContent": { "matches": [ … ] },   // must validate against outputSchema if declared
  "isError": false
}
```

- When you declare `outputSchema`, return `structuredContent` **and** mirror it as serialized JSON in a `text` block for backward compatibility (SDKs do this automatically).
- `resource_link` is the correct answer to "the result is huge": return a link; the model reads it via `resources/read` only if needed.

### 2.3 Two error channels — never confuse them

| Channel | When | Shape | Model sees it? |
|---|---|---|---|
| **JSON-RPC error** | Protocol problems: unknown tool (`-32602`), malformed request (`-32600`), parse failure (`-32700`), method not found (`-32601`), internal transport fault (`-32603`) | `error: { code, message, data? }` | Usually surfaced as a hard failure |
| **Tool execution error** | Your logic failed: API 404, file missing, validation beyond schema, upstream timeout | Normal result with `isError: true` and a `text` block | Yes — and it can recover |

Execution-error text must be **actionable**: state what failed, why, and what to do (`"GitHub API rate limit exceeded; retry after 2026-07-15T10:30:00Z or reduce per_page"`). Never leak stack traces, absolute internal paths, or secrets in either channel.

### 2.4 Dynamic tool lists

If tools appear/disappear at runtime (feature flags, auth state), declare `tools.listChanged` and emit `notifications/tools/list_changed`. Hosts re-fetch lazily; don't thrash it. Prefer a static list when possible — dynamic lists complicate host caching and user trust.

### 2.5 Pagination

List operations (`tools/list`, `resources/list`, `prompts/list`) and your own listing tools should use **opaque cursor** pagination: result carries `nextCursor`; caller passes it back as `cursor`. Never expose raw offsets you'll regret; treat cursors as opaque tokens (base64 of position + query hash is fine). Cap page sizes server-side regardless of what the caller asks for.

## 3. Resources and prompts

- **Resources** = nouns the *application/user* attaches to context (files, configs, records). URI-addressed; `resources/read` returns text or base64 blob contents with `mimeType`. Direct resources for fixed URIs; **resource templates** (`file:///{path}`, `orders://{id}`) for parameterized families — templates can back `completion/complete` for argument autocompletion.
- `resources.subscribe` capability + `notifications/resources/updated` lets clients watch a URI. Only declare if you truly push updates.
- **Prompts** = user-invoked templates (`prompts/get` with args → a list of role+content messages). In Cursor-like hosts they surface as slash commands. Use for repeatable workflows ("review this diff against our style guide"), not as a substitute for tool descriptions.
- Practical hierarchy: **tools carry 90% of the value in coding hosts today**; add resources when there's genuinely browsable data; add prompts when a canned workflow exists. Don't ship empty capability stubs.

## 4. Transports

### 4.1 stdio (default for local)

- Framing: **newline-delimited JSON-RPC over stdin/stdout**, UTF-8, no embedded literal newlines inside a frame.
- Server MUST NOT write anything non-protocol to stdout (see SKILL.md fatal rule). stderr is yours for logging — hosts typically capture it into their log UI.
- Host owns the process lifecycle: spawned on connect, killed on host exit. Design for **fast startup** (<1s to `initialize` response; lazy-init heavy clients on first tool call) and **statelessness across restarts** (persist anything that matters to disk).
- Environment: hosts pass a *minimal* env plus whatever `env` block the user configured. Never assume your interactive shell's PATH, HOME-derived config, or proxy vars are present.

### 4.2 Streamable HTTP (default for remote)

- Single endpoint (e.g. `/mcp`) accepting:
  - `POST` with JSON-RPC message(s) → response is either `application/json` (single response) or `text/event-stream` (server streams the response plus interleaved notifications/requests).
  - `GET` with `Accept: text/event-stream` → optional server→client channel for unsolicited notifications.
  - `DELETE` → session termination.
- **Sessions**: server may return `mcp-session-id` header on the `initialize` response; client echoes it on every later request. IDs must be cryptographically random and visible-ASCII. Session ≠ authentication — authenticate every request independently.
- **Resumability**: SSE events may carry `id`; client reconnects with `Last-Event-ID` to replay missed messages. SDKs implement via an event-store hook.
- **Security hard requirements**: validate `Origin` (DNS-rebinding defense), bind `127.0.0.1` not `0.0.0.0` for local servers, TLS for anything non-localhost, OAuth 2.1 resource-server behavior for real deployments (validate tokens *addressed to you*; **never pass through** an inbound token to upstream APIs).
- **Deprecated HTTP+SSE** (2024-11-05, separate `/sse` + `/messages` endpoints): don't author new servers against it; SDKs can expose a compat endpoint if an old host demands it.

### 4.3 Choosing (expanded)

stdio wins when: the server needs local filesystem/process access; per-user credentials live in local env; you want zero ops. HTTP wins when: shared state/caches, centralized secrets, non-local clients, horizontal scaling, or the host can't spawn processes (web-based hosts). If both audiences exist, keep server logic transport-free and ship two thin entry points.

## 5. Long-running work, progress, cancellation, timeouts

- **Progress**: if the request's `_meta.progressToken` is present, emit `notifications/progress` (`progress`, optional `total`, optional `message`). Emit at meaningful milestones, not per-row spam.
- **Cancellation**: client may send `notifications/cancelled` with the request id. SDKs surface an abort signal / cancellation scope — check it in loops and pass it to downstream HTTP calls. After cancellation, the response is discarded; stop burning resources.
- **Timeouts**: hosts time out tool calls (commonly 30–120s, sometimes reset by progress). Design accordingly: either finish fast, or convert to a **job pattern** — `start_x` returns a job id immediately; `get_x_status(job_id)` polls; result delivered as resource link. Never hold a tool call open for many minutes even with progress.
- Concurrency: hosts may issue overlapping `tools/call` requests. Handlers must be re-entrant; guard shared state (single-writer queues, per-resource locks).

## 6. Logging

Two sinks, different purposes:

1. **stderr** — operator-facing diagnostics; always available in stdio; structured (JSON lines or `level ts msg` prefix) beats freeform.
2. **MCP logging** — declare `logging` capability; client sets threshold via `logging/setLevel`; you emit `notifications/message` with RFC-5424 levels (`debug`, `info`, `notice`, `warning`, `error`, `critical`, `alert`, `emergency`), a `logger` name, and JSON-serializable `data`. This reaches the *host's* UI and helps users debug your server without terminal access.

Redact secrets and PII at the logging call site, not in a hoped-for downstream filter. Rate-limit your own log emission — a log-per-row loop can flood the transport.

## 7. Versioning and evolution

- **Server version**: semver in `serverInfo` and your package manifest. Bump **major** when: removing/renaming a tool, adding a new `required` param, tightening a type, changing result semantics. **Minor**: new tools, new *optional* params, richer results. **Patch**: fixes.
- **Schema evolution safe moves**: add optional property with `default`; widen an enum; add fields to result objects (models tolerate extra fields; strict `outputSchema` consumers may not — extend the schema in the same release). **Unsafe**: everything else — instead, ship `tool_v2` (or a new name) alongside, mark the old description "Deprecated: use X", remove next major.
- **Protocol version**: don't chase revisions manually; upgrade the SDK, re-run Inspector + host smoke tests, read the SDK changelog for behavioral flags.
- Keep a `CHANGELOG.md`; hosts and users have no other way to know a tool's meaning shifted.

## 8. Validating descriptors before shipping

Checklist (automate in CI where possible):

1. Names match `^[a-zA-Z0-9_-]{1,64}$`; no two tools differ only by synonym.
2. Every `inputSchema` is `type: "object"`, draft-2020-12-valid (run a meta-schema validator), every property has `description`, `required` is accurate, `additionalProperties: false` unless you truly accept extras.
3. Descriptions state purpose + when-to-use + limits + read/write nature; under ~1500 chars each (host context budgets).
4. Annotations truthful; every mutating tool reviewed for `destructiveHint`/`idempotentHint`.
5. `outputSchema` (if any) matches what handlers actually return — assert in tests.
6. Total descriptor payload sane: hosts inject *all* tool descriptors into model context; 40 tools × 2KB descriptions = you just spent 80KB of every prompt. Trim or split servers.
7. Inspector run: list tools; call each with valid, invalid, and boundary inputs; verify error shape (`isError` vs protocol error).

## 9. Windows-specific issues (author + install side)

1. **JSON path escaping**: `mcp.json` needs `"C:\\Users\\user\\srv\\dist\\index.js"` (or forward slashes — Node and Python accept `C:/Users/...`, which sidesteps escaping bugs).
2. **npx/uvx spawn failures**: GUI hosts spawn without a shell; `.cmd` shims (`npx.cmd`, `uvx.cmd`) may not resolve. Fix: `"command": "cmd", "args": ["/c", "npx", "-y", "pkg"]` — or better, avoid runtime download entirely: install globally / build locally and point `command` at the absolute `node.exe`/script path.
3. **PATH**: GUI-launched hosts get the *login* env, not your terminal's (nvm-windows, conda, venv activation don't apply). Use absolute interpreter paths in config.
4. **Encoding**: set `"env": { "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8" }` for Python servers — cp1252 stdout will mangle JSON with non-ASCII content. In Node, don't set `stdout` encodings that transcode.
5. **Line endings**: protocol frames end in `\n`; SDKs handle it — but if you post-process stdout in a wrapper script (don't), CRLF injection breaks framing. Keep `.gitattributes` from converting any fixture files used in framing tests.
6. **Long paths** (>260 chars) in deep `node_modules`: enable `LongPathsEnabled` or keep the server shallow (`C:\mcp\<name>`).
7. **Spaces in paths**: rely on args arrays (never a single concatenated command string); spaces are then safe without quoting games.
8. **Firewall prompts**: an HTTP-transport server binding a port triggers Windows Defender dialogs — bind `127.0.0.1` explicitly to minimize them and document the first-run prompt.
9. **Process cleanup**: hosts kill the direct child; a `cmd /c` wrapper can orphan the grandchild. Another reason to spawn the runtime directly. Handle stdin-close as shutdown in your server (SDK default) so orphans exit.

## 10. Anti-pattern catalogue

| # | Anti-pattern | Why it fails | Fix |
|---|---|---|---|
| 1 | **Endpoint mirroring** (tool per REST route) | 40 tools bloat context; model picks wrong ones; multi-call choreography pushed onto the model | Design 3–10 outcome-shaped tools that internally orchestrate the API |
| 2 | **Huge blobs** in results | Blows context window; host truncates arbitrarily; model summarizes garbage | Paginate; summarize; `resource_link` for full data; hard caps (e.g. 50KB/result) with explicit truncation notice |
| 3 | **Blocking tools** | Host timeout kills the call; user sees spinner→failure | Progress notifications; job pattern (`start`/`status`); internal deadline < host timeout with partial results |
| 4 | **stdout pollution** (stdio) | Corrupts JSON-RPC framing; "server disconnected" mysteries | All logging to stderr / MCP logging; smoke-test stdout cleanliness incl. dependency imports |
| 5 | **Vague descriptors** ("Manages data") | Model can't route; tool unused or misused | Purpose + when-to-use + when-NOT + limits, written like a prompt |
| 6 | **Kitchen-sink params** (12 optional args, `options: object` with no schema) | Model hallucinates arg combos; validation gaps | Split tools; enumerate; `additionalProperties: false` |
| 7 | **Secrets in descriptors/results/logs** | Descriptors go to every client and telemetry | Env/keychain only; redact at boundaries (see security-checklist) |
| 8 | **Trusting external content** | Fetched page says "ignore previous instructions" → prompt injection through your result | Label untrusted content, strip/neutralize instructions, length-cap (security-checklist §output) |
| 9 | **Stateful assumptions in stdio** | Host restarts server whenever; in-memory state vanishes | Persist to disk; make tools self-contained per call |
| 10 | **Hand-rolled protocol** | Framing/lifecycle/version-negotiation bugs that only appear in some hosts | Use official SDKs; write only handlers |
| 11 | **Dynamic list thrash** | `list_changed` storms make hosts re-fetch and users distrust | Static list; batch changes |
| 12 | **Token passthrough** (HTTP) | Reusing inbound bearer token upstream = confused deputy | Exchange/mint your own upstream credentials; validate audience |
| 13 | **Error swallowing** (`catch { return "error" }`) | Model retries blindly, user sees nothing useful | `isError: true` + cause + remedy; log details to stderr |
| 14 | **Startup heavy-lifting** | 10s DB warmup → host initialize timeout | Lazy-init on first call; cache connections after |
