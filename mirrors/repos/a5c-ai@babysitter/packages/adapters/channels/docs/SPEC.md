# mcp-channels — Specification (authoritative contract)

> **Migration note (2026-06).** This is the original `mcp-channels` design record,
> preserved as-is. The package has since been **ported to TypeScript and published
> as [`@a5c-ai/channels-adapter`](../README.md)** inside the babysitter monorepo at
> `packages/adapters/channels`. Where this document says `mcp-channels`, read
> `@a5c-ai/channels-adapter`; the `src/*.js` modules referenced below are now
> `src/*.ts` compiled to `dist/` (the CLI ships as the `adapters-channels` bin, with
> `mcp-channels` kept as an alias). The framework also gained an additive built-in
> **`webhook`** backend (built on `@a5c-ai/triggers-adapter`'s `normalizeEvent`) —
> see the README. The acceptance criteria below remain the contract.

> This file is the single source of truth. Tests are authored from it; the
> convergence verifier compares artifacts against it verbatim. Keep acceptance
> criteria (AC-*) testable and stable.

## 1. Purpose & scope

`mcp-channels` is a Node.js (ESM, no build step) **MCP-server mini-framework**
that turns external systems (GitHub, Jira, …) into a Claude Code **channel**
via a declarative YAML config. It:

- runs as a stdio MCP server that declares the `claude/channel` capability,
- **polls** pluggable backends on a per-source schedule,
- computes **what changed since the last check** (cursor) and **dedupes** so a
  given external event triggers **at most once**,
- **filters** events declaratively (assignee, label, project, substring/regex on
  payload, boolean combinations),
- pushes each surviving event into the session as a `notifications/claude/channel`
  event, and
- **relays Claude's replies back to the origin** (e.g. a comment on the GitHub
  issue/PR or Jira issue that triggered the event) via a `reply` MCP tool.

Backends are **JavaScript hook points**: a small documented interface
(`poll`, `reply`, optional `validateConfig`/`init`) that anyone can implement to
add a new system without touching the core.

### Non-goals / scope boundaries
- Running a **live** Claude Code research-preview session is out of scope for the
  automated tests (channels require the `claude` CLI + Anthropic allowlist + a dev
  flag). Integration is verified with an **in-memory/stdio MCP transport** that
  captures notifications and tool calls, plus **mocked GitHub/Jira HTTP**. A
  README walkthrough documents wiring to a real session.
- Backends other than GitHub/Jira are out of scope to ship, but the interface and
  registry MUST make them addable as plain JS modules.

## 2. Channel contract the server MUST implement (from channels-reference)

- **Capability**: construct the MCP `Server` with
  `capabilities.experimental['claude/channel'] = {}`. Two-way adds
  `capabilities.tools = {}`. Optional permission relay adds
  `capabilities.experimental['claude/channel/permission'] = {}`.
- **Outbound event**: `mcp.notification({ method: 'notifications/claude/channel',
  params: { content: string, meta: Record<string,string> } })`. Arrives to Claude
  as `<channel source="<server name>" k="v" ...>content</channel>`.
  - `meta` keys MUST be identifiers (`[A-Za-z0-9_]+`); keys with hyphens/other
    characters are silently dropped. The framework MUST sanitize/validate meta
    keys so routing never depends on a dropped key.
  - `source` is set by Claude Code from the server name; the framework MUST NOT
    put it in `meta`.
- **Reply tool**: register via `ListToolsRequestSchema` + `CallToolRequestSchema`.
  Returns `{ content: [{ type:'text', text }] }`; on failure
  `{ content:[...], isError:true }`.
- **Permission relay (optional)**: handle
  `notifications/claude/channel/permission_request` (params: `request_id`,
  `tool_name`, `description`, `input_preview`) and emit
  `notifications/claude/channel/permission` (params: `request_id`,
  `behavior: 'allow'|'deny'`).
- **Sender gating**: untrusted inbound text is a prompt-injection vector; gating
  is on the **sender identity**, not room/channel.

## 3. Architecture (modules under `src/`)

| Module | Responsibility |
|--------|----------------|
| `server.js` (`ChannelServer`) | Wrap MCP `Server`; declare channel caps; register the `reply` tool; expose `emit(event)` → `notifications/claude/channel`; route `reply` tool calls to the right backend; optional permission relay. Transport-injectable for tests. |
| `runtime.js` | Bootstrap: load config → build backends via registry → start `Poller` → connect stdio transport. Exposes `createRuntime(configPath, deps)` returning `{ server, poller, start, stop }`. |
| `config.js` | Load + validate YAML; `${ENV}` interpolation; defaults; produce a typed, normalized config object; collect actionable validation errors. |
| `poller.js` (`Poller`) | Per-source interval scheduling; for each tick: load state → `backend.poll` → apply filter → dedup → persist state → `server.emit`. Injectable clock/timer for tests; `tick(sourceId)` for deterministic testing. |
| `state.js` (`StateStore`) | Persist `{ cursor, seen[] }` per source as JSON (atomic write). Default dir `~/.claude/channels/<server>/state`; overridable. Pluggable interface (`get`, `set`). `seen` is bounded (max N, FIFO prune). |
| `filter.js` | Declarative matcher engine over a dot-path payload. Ops: `eq, ne, in, nin, includes, contains, regex, exists, gt, gte, lt, lte`. Combinators: `all`, `any`, `not`. `contains`/`regex` support `ignoreCase`. Unknown op / bad path → no match (never throws). |
| `dedup.js` | Helpers: `deriveNew(items, { idOf, seen })` and cursor advance. Encapsulates the "no changed-since semantics → seen-set" fallback so backends share it. |
| `registry.js` | Map backend `type` → backend module. Built-ins `github`, `jira`. `register(type, backend)` and `load(path)` for custom JS backends referenced from YAML (`backend: ./my-backend.js`). |
| `relay.js` | Encode/decode an opaque `reply_to` routing token (so Claude just echoes one attribute) and dispatch `reply({ routing, text })` to the owning backend. |
| `backends/github.js` | GitHub backend (below). |
| `backends/jira.js` | Jira backend (below). |
| `backend.js` | JSDoc typedefs for the hook interface + shared helpers. |
| `index.js` | Public exports: `ChannelServer`, `createRuntime`, `defineBackend`, `registry`, filter/state, types. |

`types.d.ts` mirrors the JSDoc typedefs for editor support.

## 4. Backend hook interface (the extension points)

```js
/** @typedef {{ id:string, content:string, meta:Object<string,string>,
 *             payload:object, routing:object }} ChannelEvent */
/** @typedef {{ source:object, state:object, http:Function, log:Function,
 *             now:Date }} PollContext */
/** @typedef {{ events:ChannelEvent[], state:object }} PollResult */
/** @typedef {{
 *   type: string,
 *   validateConfig?: (source:object) => string[],
 *   init?: (source:object) => void|Promise<void>,
 *   poll: (ctx:PollContext) => Promise<PollResult>,
 *   reply: (a:{routing:object, text:string, source:object, http:Function})
 *            => Promise<{ ok:boolean, ref?:string }>
 * }} Backend */
```

- `poll` MUST be **pure w.r.t. side effects** except HTTP via the injected
  `http` (so tests inject a fake). It returns new events + the next state. It MUST
  use `state.cursor` to request only changes since last check where the API
  supports it, and MUST set `routing` on every event so a reply can reach origin.
- `reply` posts back to origin using `routing` + `source.auth`.
- The **core** (not the backend) is the authoritative filter + dedup gate; a
  backend MAY pre-filter at the API for efficiency but MUST NOT rely on it for
  correctness.

### 4.1 GitHub backend (`backends/github.js`)
- Auth: `source.auth.token` (PAT). Base `https://api.github.com` (overridable for
  GHE).
- `config.repo: "owner/name"`, `config.events: [issue_comment | issue_opened | pr_opened]`.
- **issue_comment**: `GET /repos/{o}/{r}/issues/comments?sort=updated&direction=asc&since=<cursor>`.
  Cursor = max `updated_at`. Dedup id = `gh:comment:<id>:<updated_at>` (so an edit
  can re-trigger only if configured; default: dedup on `<id>` only → no re-trigger
  on edit). Each event resolves the parent issue/PR number from `issue_url`.
- **issue_opened**: `GET /repos/{o}/{r}/issues?state=open&sort=created&direction=asc&since=<cursor>`
  filtering to items whose `created_at > cursor`; dedup id = `gh:issue:<id>`.
- `payload` is the raw GitHub object (so filters like `issue.assignee.login`,
  `user.login`, `body`, `labels[].name` work). For comments the framework
  attaches the parent `issue` object to `payload.issue` (one extra GET, cached).
- `meta`: `{ repo, issue_number, kind, author, reply_to }`.
- `reply`: `POST /repos/{o}/{r}/issues/{issue_number}/comments {body:text}`.

### 4.2 Jira backend (`backends/jira.js`)
- Auth: `source.auth.baseUrl`, `email`, `token` (Basic). 
- `config.project`, `config.events: [issue_created | issue_updated]`, optional
  `config.jql` extra clause.
- Poll: `POST /rest/api/3/search` with JQL
  `project = "<P>" AND created >= "<cursor>" ORDER BY created ASC` (or `updated`).
  Cursor = max created/updated (Jira minute-granularity → combine with seen-set
  dedup by `<key>:<created>` to avoid double-trigger within the same minute).
- `payload` = the raw issue (`fields.labels`, `fields.summary`,
  `fields.project.key`, `fields.assignee.emailAddress`, …).
- `meta`: `{ project, issue_key, kind, reply_to }`.
- `reply`: `POST /rest/api/3/issue/{key}/comment` with ADF body.

## 5. Configuration (YAML) schema

```yaml
server:
  name: mcp-channels            # MCP server name (becomes <channel source=...>)
  instructions: "...optional override..."
  permissionRelay: false        # opt-in claude/channel/permission
state:
  dir: ./.mcp-channels-state    # optional; default ~/.claude/channels/<name>
  maxSeenPerSource: 1000
defaults:
  pollIntervalSeconds: 60
sources:
  - id: gh-comments-by-alice
    backend: github             # built-in type OR ./relative/custom.js
    pollIntervalSeconds: 30
    auth: { token: "${GITHUB_TOKEN}" }
    config: { repo: "octo/app", events: [issue_comment] }
    filter:
      all:
        - { field: "issue.assignee.login", op: eq, value: "alice" }
    routing: { reply: comment } # default per backend
  - id: jira-crash-bugs
    backend: jira
    auth: { baseUrl: "https://x.atlassian.net", email: "${JIRA_EMAIL}", token: "${JIRA_TOKEN}" }
    config: { project: "BUG", events: [issue_created] }
    filter:
      all:
        - { field: "fields.labels", op: includes, value: "needs-triage" }
        - { field: "fields.summary", op: contains, value: "crash", ignoreCase: true }
```

`${ENV}` interpolation reads `process.env`. Missing required env → validation
error (not a crash at poll time).

## 6. Functional requirements → acceptance criteria

- **R1 MCP channel server.** AC-1: `ChannelServer` constructs an MCP `Server` whose
  capabilities include `experimental['claude/channel']={}`; with two-way it adds
  `tools={}`; with `permissionRelay` it adds `experimental['claude/channel/permission']={}`.
  AC-2: `emit({content,meta})` sends exactly one `notifications/claude/channel`
  with sanitized meta (identifier keys only) and never sets `source` in meta.
- **R2 Pluggable JS backends.** AC-3: `registry.register(type, backend)` and YAML
  `backend: ./file.js` both resolve; an invalid backend (missing `poll`/`reply`)
  fails config validation with a clear message. AC-4: a custom backend authored in
  `examples/custom-backend.js` works end-to-end in a test.
- **R3 GitHub + Jira backends.** AC-5: GitHub `issue_comment` poll against mocked
  HTTP emits an event with correct `content`, `meta.repo/issue_number/reply_to`,
  and `payload.issue.assignee.login`. AC-6: Jira `issue_created` poll against
  mocked HTTP emits an event with `meta.issue_key` and `payload.fields.labels`.
- **R4 YAML-driven triggers + filtering.** AC-7: "GitHub issue comment on an issue
  assigned to `alice`" only emits when `issue.assignee.login == alice`. AC-8: "Jira
  issue opened in project `BUG` with label `needs-triage`" only emits on match.
  AC-9: substring/regex match on payload (e.g. `fields.summary contains "crash"`)
  gates emission. AC-10: `all`/`any`/`not` combinators behave per boolean logic.
- **R5 Polling / cursor / changed-since / dedup.** AC-11: poller calls `backend.poll`
  on the configured interval (verified with injected timer/clock). AC-12: the cursor
  persists across runs and is passed to the next poll (`since`/JQL uses it). AC-13:
  re-polling an unchanged or overlapping window emits **no duplicate** events (seen-set
  fallback), even when the API lacks precise changed-since. AC-14: editing an item does
  not re-trigger unless configured to.
- **R6 Reply relayed to origin.** AC-15: the server exposes a `reply` tool; calling it
  with the event's `reply_to` posts a comment to the **originating** GitHub issue/PR
  (`POST …/issues/{n}/comments`) or Jira issue (`POST …/issue/{key}/comment`),
  verified against mocked HTTP. AC-16: an unknown/garbled `reply_to` returns
  `isError:true` without throwing.
- **R7 Test coverage.** AC-17: `npm test` runs a vitest suite covering config, filter,
  state, dedup, poller, both backends, relay, server, and an end-to-end integration
  (config → mocked poll → captured notification → reply tool → mocked origin POST).
  AC-18: line coverage ≥ 90% for `src/` (vitest --coverage), enforced in CI config.

## 7. Test plan (vitest, all offline)

- Unit: `config.test.js`, `filter.test.js`, `state.test.js`, `dedup.test.js`,
  `relay.test.js`, `server.test.js` (capture transport).
- Backend: `github.test.js`, `jira.test.js` with an injected `http` fake returning
  fixture payloads; assert request URLs/params (cursor/since/JQL), emitted events,
  dedup across two polls, and reply POST shape.
- Poller: `poller.test.js` with fake timers + in-memory state; assert interval calls,
  cursor advance, no double-trigger.
- Integration: `integration.test.js` boots `createRuntime` with a capturing transport
  and fake HTTP; drives a tick; asserts the `<channel>`-bound notification params; then
  invokes the `reply` tool and asserts the origin POST.
- Coverage gate: `vitest run --coverage` with ≥90% lines on `src/`.

## 8. Deliverable layout

```
package.json  (type:module, bin: mcp-channels, scripts: test, test:coverage, start)
src/…         (modules above)   types.d.ts
backends/     (github.js, jira.js)   # under src/backends
examples/channels.yml  examples/custom-backend.js
test/…        (vitest)
.mcp.json     (example registration)   README.md   LICENSE
```

## 9. Definition of done
All AC-1..AC-18 demonstrably pass; `vitest run --coverage` is green with ≥90% lines;
convergence score ≥ 95/100; README documents config, the backend hook interface, and
the live Claude Code wiring guide.

---

## 10. Extension: event-triggered session spawner (R8) + shared reply secret + CI

This extends the framework so a matching event can **spawn a new agent session**
(via `@a5c-ai/adapters`) instead of (or in addition to) emitting into the current
session. The spawned session is **self-associated** (wired with this MCP server) and
receives the **event context + `reply_to`** in its prompt, so it can reply to the
**same origin** (the triggering PR/issue/Jira issue).

### 10.1 New modules / surface
- `src/spawner.js` (`SessionSpawner`): given a resolved source + a `ChannelEvent`,
  launches a session via an injected adapters-like client and returns a handle/result.
  The adapters client is **injected** (a fake in tests); `@a5c-ai/adapters` is an
  **optional dependency**, lazy-loaded only for real launches via
  `createClient()` + `registerBuiltInAdapters()`.
- `src/index.js` additionally exports `SessionSpawner` and `buildSpawnRunOptions`.

### 10.2 Adapters launch contract (from `@a5c-ai/adapters`)
- `createClient(opts?)` → client with `run(options): RunHandle`.
- `RunOptions` used: `{ agent, prompt, mcpServers, nonInteractive?, interactive?, cwd?, model?, approvalMode?, env? }`.
- `McpServerConfig` = `{ name, transport:'stdio', command, args?, env?, url?, headers? }`
  (name must match `^[a-zA-Z0-9_-]{1,64}$`).

### 10.3 Configuration (additions)
```yaml
server:
  replySecret: "${MCP_CHANNELS_REPLY_SECRET}"   # optional; stable HMAC secret
spawn:                                           # optional global defaults
  agent: claude-code
  mode: headless                                 # headless | interactive  (default headless)
  approvalMode: yolo                             # yolo | prompt | deny (default yolo for autonomous reply)
  selfMcpName: mcp-channels
  maxConcurrent: 4
sources:
  - id: gh-triage
    backend: github
    auth: { token: "${GITHUB_TOKEN}" }
    config: { repo: "octo/app", events: [issue_opened] }
    onEvent: spawn                               # emit | spawn | both  (default emit)
    spawn:                                       # per-source overrides (merged over global)
      agent: claude-code
      mode: headless
      model: claude-opus-4-8
      cwd: "."
      promptTemplate: "..."                      # optional; overrides default prompt
```

### 10.4 Acceptance criteria
- **AC-19 spawn invocation.** When a source's effective `onEvent` includes `spawn` and an
  event survives filter+dedup, `SessionSpawner.spawn(source, event)` calls the injected
  client's `run(...)` **exactly once** with `agent` = effective spawn agent, a `prompt`
  containing the event content + key meta + the `reply_to` token, and `mcpServers`
  including the self entry. `mode: headless` → `nonInteractive:true`;
  `mode: interactive` → `interactive:true`.
- **AC-20 self-association.** The self `McpServerConfig` has `name` (default `mcp-channels`,
  identifier-valid), `transport:'stdio'`, a `command`/`args` that re-launch this framework
  with the **same config path**, and `env` carrying the shared reply secret **when set**
  (`MCP_CHANNELS_REPLY_SECRET`).
- **AC-21 reply_to portability.** With `server.replySecret` (or `MCP_CHANNELS_REPLY_SECRET`)
  set, `encodeReplyTo`/`decodeReplyTo` derive the HMAC key from it, so a **second process**
  constructed with the same secret decodes a token minted by the first (cross-process reply
  works). Unset ⇒ per-process random key (a token from another process fails verification →
  `decodeReplyTo` returns `null`, reply tool `isError`). Existing single-process behavior is
  unchanged (backward compatible).
- **AC-22 action routing.** `onEvent: emit` ⇒ only `server.emit`, never spawns;
  `spawn` ⇒ only spawns, never emits; `both` ⇒ emits AND spawns; default `emit`.
- **AC-23 prompt content.** The default spawned prompt includes the event `content`, the
  routing-relevant meta (e.g. repo + issue_number, or project + issue_key), the `reply_to`
  token, and an instruction to respond by calling the `reply` tool with that `reply_to`.
  A per-source `promptTemplate` (with documented placeholders) overrides the default.
- **AC-24 concurrency + isolation.** Concurrent spawns are bounded by `maxConcurrent`
  (default 4); a spawn error is caught and logged and does **not** crash the poller, block
  other events, or advance/rollback dedup incorrectly (an event is still recorded as seen
  once dispatched).
- **AC-25 optional-dep safety.** If a source is configured to spawn but no client is injected
  and `@a5c-ai/adapters` cannot be loaded, this surfaces as a **config-validation / startup
  error with a clear message**, not a crash at event time.
- **AC-26 CI.** `.github/workflows/ci.yml` runs `npm ci` + `npm run test:coverage` on push and
  PR to `main` (Node 20 + 22).

### 10.5 Tests (offline)
- `spawner.test.js`: AC-19/20/22/23/24/25 with an injected fake client (records `run` calls);
  assert agent, prompt (contains reply_to + content + meta), mcpServers self entry (name,
  stdio, command/args, env secret), mode mapping, action routing, bounded concurrency,
  error isolation, and the missing-client error.
- `relay.test.js` (extend): AC-21 cross-process portability — two relay instances with the
  same configured secret round-trip a token; different/random secrets do not.
- `config.test.js` / `poller.test.js` (extend): `onEvent` + `spawn` parsing/merge and that the
  poller dispatches emit/spawn/both per source.
- Coverage gate stays ≥90% lines on `src/`.

### 10.6 Definition of done (extension)
AC-19..AC-26 pass; full suite green at ≥90% lines; convergence ≥95/100; README documents the
`onEvent`/`spawn` config, the shared reply secret, and the live spawning prerequisites
(`claude-code` CLI + `@a5c-ai/adapters` installed + auth).
