# @a5c-ai/channels-adapter

> An MCP-server mini-framework that turns external systems (GitHub, Jira, inbound
> webhooks, …) into a Claude Code **channel** via a declarative YAML config — with
> pluggable backends, per-source polling + change detection + dedup, declarative
> filtering, a `reply` tool that relays Claude's replies back to the origin, and an
> optional per-event session spawner backed by `@a5c-ai/adapters`.

`@a5c-ai/channels-adapter` is a TypeScript (ESM) stdio MCP server. It:

- declares the experimental `claude/channel` capability,
- **polls** pluggable backends on a per-source schedule,
- computes **what changed since the last check** (a per-source *cursor*) and
  **dedupes** so each external event triggers Claude **at most once**,
- **filters** events declaratively (assignee, label, project, substring/regex,
  boolean `all`/`any`/`not`),
- pushes each surviving event into the session as a `notifications/claude/channel`
  event (Claude sees `<channel source="…" …>content</channel>`),
- **relays Claude's replies back to origin** (a comment on the GitHub issue/PR or
  Jira issue that triggered the event) through a single `reply` MCP tool, and
- optionally **spawns a fresh agent session per event** via
  [`@a5c-ai/adapters`](https://www.npmjs.com/package/@a5c-ai/adapters), handing the
  spawned session the same `reply_to` token so it can answer the same origin.

Backends are **hook points** — a tiny documented interface (`poll`, `reply`,
optional `validateConfig`/`init`) anyone can implement to add a new system without
touching the core. Three built-ins ship: `github`, `jira`, and `webhook`.

> Design & spec: see [docs/DESIGN.md](docs/DESIGN.md), [docs/SPEC.md](docs/SPEC.md).

---

## Table of contents

- [Install](#install)
- [Quick start](#quick-start)
- [YAML configuration schema](#yaml-configuration-schema)
- [Built-in backends](#built-in-backends)
- [The Backend hook interface](#the-backend-hook-interface)
- [Writing a custom backend](#writing-a-custom-backend)
- [How polling, change-detection & dedup work](#how-polling-change-detection--dedup-work)
- [The opaque `reply_to` token](#the-opaque-reply_to-token)
- [Event-triggered session spawning](#event-triggered-session-spawning)
- [Wiring to a real Claude Code session](#wiring-to-a-real-claude-code-session)
- [Programmatic API](#programmatic-api)
- [Testing](#testing)
- [License](#license)

---

## Install

Requires **Node.js ≥ 20.9** (developed/tested on Node 22).

```bash
npm i @a5c-ai/channels-adapter
```

The package is published with a build step (TypeScript → `dist/`); installing from
npm gives you the compiled `dist/`. It exposes two equivalent bin names:

- **`adapters-channels`** — the canonical bin (matches the in-repo adapters family).
- **`mcp-channels`** — a back-compat alias for the original framework name.

Both run the same stdio MCP server.

---

## Quick start

1. Write a config (see [the schema](#yaml-configuration-schema)). A ready example
   lives at [`examples/channels.yml`](examples/channels.yml).

2. Export the env vars your config interpolates:

   ```bash
   export GITHUB_TOKEN=ghp_xxx
   export JIRA_EMAIL=you@example.com
   export JIRA_TOKEN=xxx
   ```

3. Run the stdio server:

   ```bash
   npx -p @a5c-ai/channels-adapter adapters-channels examples/channels.yml
   # or, with the alias:  npx -p @a5c-ai/channels-adapter mcp-channels examples/channels.yml
   # or, against a checkout:  node dist/cli.js examples/channels.yml
   ```

The process speaks MCP over stdio. To actually attach it to Claude Code, see
[Wiring to a real Claude Code session](#wiring-to-a-real-claude-code-session).

---

## YAML configuration schema

```yaml
server:
  name: mcp-channels            # MCP server name → <channel source="mcp-channels">
  instructions: "...optional override..."   # else a sane default is used
  permissionRelay: false        # opt-in claude/channel/permission relay
  replySecret: "${MCP_CHANNELS_REPLY_SECRET}"  # optional; stable HMAC secret (see spawning)

state:
  dir: ./.mcp-channels-state    # optional; default ~/.claude/channels/<name>/state
  maxSeenPerSource: 1000        # FIFO-bounded per-source dedup seen-set

defaults:
  pollIntervalSeconds: 60       # per-source override falls back to this

sources:
  - id: gh-comments-by-alice    # unique id; also the state-file key
    backend: github             # a built-in type (github|jira|webhook) OR ./relative/custom.js
    pollIntervalSeconds: 30
    auth: { token: "${GITHUB_TOKEN}" }
    config: { repo: "octo/app", events: [issue_comment] }
    filter:
      all:
        - { field: "issue.assignee.login", op: eq, value: "alice" }
    routing: { reply: comment } # default reply mode per backend

  - id: jira-crash-bugs
    backend: jira
    auth:
      baseUrl: "https://x.atlassian.net"
      email: "${JIRA_EMAIL}"
      token: "${JIRA_TOKEN}"
    config: { project: "BUG", events: [issue_created] }
    filter:
      all:
        - { field: "fields.labels",  op: includes, value: "needs-triage" }
        - { field: "fields.summary", op: contains, value: "crash", ignoreCase: true }
```

### `${ENV}` interpolation

`${NAME}` placeholders are read from `process.env` at load time. A **missing**
required variable is a **validation error** — never a crash at poll time.

### Validation

`loadConfig()` never throws: malformed YAML, an unresolved `${ENV}`, an unknown
backend type, a malformed filter, or a backend's own `validateConfig()` failure
are all collected into an `errors: string[]` array. `createRuntime()` throws once,
up front, with all the aggregated messages if the config is invalid — including
errors from the **built-in** github/jira/webhook backends (e.g. a github
`config.repo` that is not `"owner/name"`, a jira source missing `auth.token`, or a
webhook source with an unrecognized `config.backend`). Custom-path backends are
imported and validated **at startup**, so a broken custom backend (missing
`poll`/`reply`) fails `createRuntime`, not the first tick.

### The filter engine

A filter is either a **leaf** clause `{ field, op, value, ignoreCase? }` over a
**dot-path** into the event payload, or a **combinator** `{ all: [...] }`,
`{ any: [...] }`, or `{ not: clause }`.

| op | meaning |
|----|---------|
| `eq` / `ne` | strict equal / not-equal |
| `in` / `nin` | field value is / is not in a list |
| `includes` | the field is an **array** containing `value` |
| `contains` | the field is a **string** containing substring `value` |
| `regex` | the field is a **string** matching the `value` pattern |
| `exists` | path is present (`value:true`) / absent (`value:false`) |
| `gt` `gte` `lt` `lte` | numeric comparisons |

`contains` and `regex` honor `ignoreCase: true`. An **unknown op, a bad/missing
dot-path, or a malformed regex yields no match and never throws** — a
misconfigured filter can't crash a poll. An empty/missing filter matches
everything.

---

## Built-in backends

### `github`

- **Auth:** `auth.token` (a PAT). Base `https://api.github.com` (override with
  `config.baseUrl` for GitHub Enterprise).
- **Config:** `repo: "owner/name"`, `events: [issue_comment | issue_opened | pr_opened]`.
- **`issue_comment`:** `GET /repos/{o}/{r}/issues/comments?sort=updated&direction=asc&since=<cursor>`.
  The cursor is the max `updated_at`. Each comment resolves its parent issue/PR
  (one cached GET) so filters like `issue.assignee.login` work. Dedup id is
  `gh:comment:<id>` (an edit does **not** re-trigger; set
  `config.retriggerOnEdit: true` to make `<id>:<updated_at>` the id).
- **`issue_opened`:** `GET /repos/{o}/{r}/issues?state=open&sort=created&direction=asc&since=<cursor>`,
  post-filtered to `created_at >= cursor` (+ seen-set dedup, so equal-timestamp
  creations aren't dropped). Dedup id `gh:issue:<id>`.
- **Pagination:** follows the `Link: rel="next"` header and accumulates **all**
  pages before advancing the cursor.
- **Failure handling:** a non-2xx list response advances **nothing** (cursor and
  seen are kept) so the window is retried; a failed parent-issue fetch holds the
  comment for the next poll instead of dropping it.
- **meta:** `{ repo, issue_number, kind, author, reply_to }`.
- **reply:** `POST /repos/{o}/{r}/issues/{issue_number}/comments { body: text }`.

### `jira`

- **Auth:** `auth.baseUrl`, `auth.email`, `auth.token` (HTTP Basic).
- **Config:** `project` (`[A-Za-z0-9_]+`), `events: [issue_created | issue_updated]`,
  optional `config.jql` extra clause.
- **Poll:** `POST /rest/api/3/search` with JQL
  `project = "<P>" AND created >= "<cursor-minute>" ORDER BY created ASC`
  (`updated` for `issue_updated`). The cursor is stored at full precision but the
  JQL literal is the minute-granular `"yyyy-MM-dd HH:mm"` Jira accepts.
- **Pagination:** loops `startAt` until `startAt + len >= total`, accumulating all
  pages before advancing the cursor.
- **Dedup:** because JQL datetime comparisons are minute-granular, the cursor is
  combined with a seen-set keyed by `jira:<key>:<created>` (full timestamp) so a
  same-minute issue re-returned next poll is recognized and dropped.
- **Security:** `config.project` is validated against `[A-Za-z0-9_]+` and any
  `config.jql` is stripped of quote/backslash/semicolon so neither can inject into
  the JQL string.
- **meta:** `{ project, issue_key, kind, reply_to }`.
- **reply:** `POST /rest/api/3/issue/{key}/comment` with an ADF body.

### `webhook` (optional, additive)

An **additive** built-in backend (it does not replace or alter `github`/`jira`)
that turns **inbound webhook payloads** (GitHub / GitLab / Bitbucket / generic)
into channel events by delegating the parsing to
[`@a5c-ai/triggers-adapter`](https://www.npmjs.com/package/@a5c-ai/triggers-adapter)'s
`normalizeEvent(backend, eventName, payload)` — the same normalizer the
triggers-adapter uses for CI/action triggers — so the channels framework reuses
that battle-tested webhook-shape knowledge instead of re-deriving it.

Channels is **poll-based**, so this backend reads a **queue of already-captured
webhook payloads** and normalizes each on every poll (live HTTP receipt — a bound
listener / tunnel — is intentionally out of scope, mirroring how live agent launch
is out of offline-test scope):

- **Auth:** none (webhooks are inbound; nothing is posted back).
- **Config:**
  - `backend: github | gitlab | bitbucket | generic-webhook` — which webhook shape
    `normalizeEvent` should parse (unrecognized values are a validation error).
  - `payloads: [...]` — an inline array of captured webhook entries (the injection
    seam: each entry is `{ eventName, payload, id? }`, or a bare payload object
    whose `eventName` falls back to `config.eventName`).
  - `dir: "./captured"` — a directory of captured `*.json` payload files (read
    through an injectable `config.fs`, defaulting to `node:fs/promises`; files are
    sorted by name for stable emit order; an unparseable file is skipped with a log
    line, not a poll failure).
  - `eventName: "..."` — optional fallback event name for bare-payload entries.
  - At least one of `payloads` / `dir` is **required**.
- **Dedup id:** the entry's explicit `id` (e.g. a GitHub `X-GitHub-Delivery`) when
  present, else a deterministic id derived from the normalized shape
  (`webhook:<backend>:<event>:<action>:<sha|url|repo#ref>`).
- **meta:** `{ backend, event, action?, repo?, author?, ref?, sha?, source_branch?,
  target_branch?, url? }` (empties dropped; values stringified).
- **payload:** the raw upstream payload (so declarative dot-path filters match).
- **reply:** **unsupported** — a webhook is a one-way inbound notification with no
  generic callback channel, so `reply()` throws a clear, actionable error rather
  than silently no-op'ing. To reply, route through the concrete `github`/`jira`
  backend the payload originated from.

---

## The Backend hook interface

A backend is a module that default-exports an object implementing the `Backend`
interface (TypeScript types ship in `dist/index.d.ts`):

```ts
interface ChannelEvent {
  id: string;
  content: string;
  meta: Record<string, string>;
  payload: object;
  routing: object;
}
interface PollContext { source: object; state: object; http: Function; log: Function; now: Date }
interface PollResult  { events: ChannelEvent[]; state: object }
interface Backend {
  type: string;
  validateConfig?(source: object): string[];
  init?(source: object): void | Promise<void>;
  poll(ctx: PollContext): Promise<PollResult>;
  reply(a: { routing: object; text: string; source: object; http: Function }):
    Promise<{ ok: boolean; ref?: string }>;
}
```

- **`type`** — stable identifier (used in logs and as the registry key).
- **`validateConfig(source) → string[]`** *(optional)* — runs at config-load time;
  return human-readable problems (empty == valid). This is how misconfiguration
  becomes a validation error instead of a poll-time crash.
- **`init(source)`** *(optional)* — runs once before the first poll of a source.
- **`poll(ctx) → { events, state }`** — the heart of a backend. It MUST be pure
  w.r.t. side effects **except HTTP via the injected `ctx.http`** (so tests inject
  a fake), MUST use `ctx.state.cursor` to request only changes since last check
  where the API supports it, and MUST set `routing` on **every** event so a reply
  can reach origin. It returns the new events **and** the next state to persist.
- **`reply({ routing, text, source, http }) → { ok, ref? }`** — posts `text` back
  to the origin identified by `routing`, using `source.auth` and the injected
  `http`. A falsy `ok` or a thrown error becomes a tool result with `isError:true`.

> The **core** (not the backend) is the authoritative filter + dedup gate. A
> backend MAY pre-filter at the API for efficiency but MUST NOT rely on it for
> correctness.

`defineBackend(obj)` is an identity helper that gives editors the `Backend` type
and asserts the required `poll`/`reply` hooks are present.

---

## Writing a custom backend

Reference a custom module from YAML by **relative path** instead of a built-in
type. The path resolves relative to the config file:

```yaml
sources:
  - id: my-thing
    backend: ./examples/custom-backend.js   # resolved by registry.load()
    pollIntervalSeconds: 30
    auth:   { token: "${MY_TOKEN}" }
    config: { endpoint: "https://example.test/api/events" }
    filter:
      all:
        - { field: "kind", op: eq, value: "mention" }
```

A minimal backend (importing the authoring helper from the package):

```js
import { defineBackend } from '@a5c-ai/channels-adapter';

export default defineBackend({
  type: 'example-custom',

  validateConfig(source) {
    const errors = [];
    if (!source?.config?.endpoint) errors.push('config.endpoint is required');
    if (!source?.auth?.token) errors.push('auth.token is required');
    return errors;
  },

  async poll(ctx) {
    const { source, state, http } = ctx;
    const cursor = state?.cursor ?? null;
    const seen = state?.seen ?? [];

    const url = new URL(source.config.endpoint);
    if (cursor) url.searchParams.set('since', cursor); // ask for "since last time"

    const res = await http(url.toString(), {
      headers: { authorization: `Bearer ${source.auth.token}` }
    });
    const items = Array.isArray(res?.body?.items) ? res.body.items : [];

    const seenSet = new Set(seen);
    const fresh = items.filter((it) => !seenSet.has(String(it.id)));

    const events = fresh.map((it) => ({
      id: `example:${it.id}`,                 // stable dedup id
      content: it.text ?? '',
      meta: { kind: String(it.kind), author: String(it.author) },
      payload: it,                            // raw object for dot-path filters
      routing: { endpoint: source.config.endpoint, itemId: it.id } // reply needs this
    }));

    const nextCursor = fresh.reduce((a, it) => (it.updatedAt > a ? it.updatedAt : a), cursor ?? '');
    return { events, state: { cursor: nextCursor, seen: [...seen, ...fresh.map((it) => String(it.id))] } };
  },

  async reply({ routing, text, source, http }) {
    const res = await http(`${routing.endpoint}/${routing.itemId}/replies`, {
      method: 'POST',
      headers: { authorization: `Bearer ${source.auth.token}`, 'content-type': 'application/json' },
      body: JSON.stringify({ text })
    });
    return { ok: res?.status >= 200 && res?.status < 300, ref: res?.body?.id };
  }
});
```

A complete, commented version lives at
[`examples/custom-backend.js`](examples/custom-backend.js). You can also register
a backend programmatically: `registry.register('my-type', backend)`.

---

## How polling, change-detection & dedup work

State per source is `{ cursor, seen[] }`, persisted as JSON (atomic write) under
`state.dir` (default `~/.claude/channels/<name>/state`). `seen` is **bounded**
(`maxSeenPerSource`, FIFO).

On each tick for a source (`Poller.tick(id)`):

1. **load state** → `{ cursor, seen }`.
2. **poll the backend** with `{ source, state, http, log, now }`. The backend
   queries the upstream API narrowed by `cursor`, paginating to fetch the whole
   window, and returns new events + the next state.
3. **filter** (core): keep events whose `payload` satisfies `source.filter`.
4. **dedup** (core): drop events whose id is already in `seen`. This is the
   authoritative *at-most-once* gate, even when polling windows overlap (an
   inclusive `since`, a minute-granular JQL `>=`, …).
5. **mint `reply_to`** and attach it to each survivor's `meta`.
6. **persist state**: the cursor advances; `seen` grows (boundary-safe FIFO).
7. **dispatch** each survivor per the source's `onEvent` mode (`emit` / `spawn` /
   `both`, default `emit`) — `emit` sends one `notifications/claude/channel`.

Two correctness details worth knowing:

- **Boundary-safe pruning.** The FIFO bound never evicts an id whose timestamp is
  still inside the cursor window (the "boundary bucket"). A naive count-based FIFO
  could drop such an id and then re-emit it on the next overlapping poll; the
  bound is *soft* and retains the boundary bucket so that can't happen.
- **Serialized ticks.** Ticks for the **same** source are serialized — a second
  tick that arrives while the first is running is queued behind it, so two
  overlapping ticks can't read the same prior state and clobber each other's
  cursor/seen. Ticks for **different** sources run concurrently.

---

## The opaque `reply_to` token

A reply must reach the **exact** origin, but Claude only echoes one small
attribute back, and inbound channel text is an untrusted prompt-injection surface.
So the framework mints a single **opaque, tamper-evident** routing token per event
and exposes it as `meta.reply_to`. Claude treats it as a black box and passes it
verbatim to the `reply` tool.

- The token is `<base64url(JSON)>.<base64url(HMAC-SHA256)>`, URL-safe and a valid
  channel attribute value.
- By default it is signed with a **per-process random secret** generated at
  startup, so a forged or tampered token (even a single flipped character, or a
  hand-rolled `base64url(JSON)` without the signature) fails verification.
- It carries **no upstream credentials** — auth lives only in the loaded config,
  keyed by source id. The HMAC exists so the runtime never POSTs under real
  credentials to a routing target it didn't itself mint.

Decoding a bad/garbled/forged token returns `null` (never throws), and the `reply`
tool surfaces that as `{ isError: true }`. For cross-process replies (spawned
sessions), configure a stable `server.replySecret` — see below.

---

## Event-triggered session spawning

By default a surviving event is **emitted** into the current session. A source can
instead (or additionally) **spawn a brand-new agent session** to handle the event,
via [`@a5c-ai/adapters`](https://www.npmjs.com/package/@a5c-ai/adapters) — which is
a regular **dependency** of this package. The spawned session is
**self-associated**: it is re-launched with *this* MCP server over stdio (the same
config path) and handed the event context plus the same `reply_to` token, so the
new session can post back to the **same origin** by calling the `reply` tool —
exactly like the in-session path.

### `onEvent`: choosing emit / spawn / both

Each source has an `onEvent` mode (default `emit`, so existing configs are
unchanged and never spawn):

| `onEvent` | behavior |
|-----------|----------|
| `emit` *(default)* | push a `notifications/claude/channel` event into the current session only. |
| `spawn` | launch a fresh agent session for the event; do **not** emit. |
| `both` | emit **and** spawn (both carry the same minted `reply_to`). |

```yaml
sources:
  - id: gh-triage
    backend: github
    auth: { token: "${GITHUB_TOKEN}" }
    config: { repo: "octo/app", events: [issue_opened] }
    onEvent: spawn            # emit | spawn | both   (default emit)
```

### The `spawn` block (global defaults + per-source overrides)

A top-level `spawn:` block sets global defaults; a per-source `spawn:` block is
**merged over** it (per-source keys win; `env` is deep-merged):

```yaml
spawn:                        # global defaults
  agent: claude               # adapters agent key (see below)
  mode: headless              # headless | interactive   (default headless)
  approvalMode: yolo          # yolo | prompt | deny      (default yolo, autonomous reply)
  selfMcpName: mcp-channels   # name of the self-association MCP entry (must match ^[A-Za-z0-9_-]{1,64}$)
  maxConcurrent: 4            # bound on in-flight session launches

sources:
  - id: gh-triage
    backend: github
    auth: { token: "${GITHUB_TOKEN}" }
    config: { repo: "octo/app", events: [issue_opened] }
    onEvent: spawn
    spawn:                    # per-source overrides
      model: claude-opus-4-8  # optional adapter model
      cwd: "."                # working dir (resolved absolute against the config dir)
      systemPrompt: "..."     # optional system prompt passthrough
      env: { FOO: bar }       # optional env passthrough
      promptTemplate: "..."   # optional; overrides the default prompt (placeholders below)
```

**The `agent` key.** The default — and the canonical
[`@a5c-ai/adapters`](https://www.npmjs.com/package/@a5c-ai/adapters) registry id
for Claude Code — is **`claude`**. The friendly alias **`claude-code`** is also
accepted and is normalized to `claude` before launch, so either spelling resolves.

### Prompt template placeholders

If you omit `promptTemplate`, a sensible default prompt is built containing the
event content, the routing-relevant meta, the `reply_to` token, and an instruction
to respond via the `reply` tool. To customize it, set `promptTemplate` with any of
these `{{…}}` placeholders (a single literal pass — untrusted event text can never
inject a *new* placeholder; an unknown key expands to the empty string):

| placeholder | expands to |
|-------------|-----------|
| `{{content}}` | the event body |
| `{{reply_to}}` | the opaque reply token (pass verbatim to the `reply` tool) |
| `{{source_id}}` | the source's `id` |
| `{{meta.KEY}}` | `event.meta.KEY` (e.g. `{{meta.repo}}`, `{{meta.issue_number}}`, `{{meta.issue_key}}`) |

```yaml
    spawn:
      promptTemplate: |
        New issue on {{meta.repo}}#{{meta.issue_number}} ({{source_id}}):
        {{content}}

        When done, call the `reply` tool with reply_to={{reply_to}}.
```

### Cross-process replies — `server.replySecret`

A spawned session is a **separate process**, so for its `reply` to decode a token
minted by the parent, both processes must derive the **same** HMAC key. Set a
stable shared secret via `server.replySecret` (typically from the environment); the
parent passes it to the spawned self-MCP entry as `MCP_CHANNELS_REPLY_SECRET`:

```yaml
server:
  name: mcp-channels
  replySecret: "${MCP_CHANNELS_REPLY_SECRET}"   # stable HMAC secret for cross-process replies
```

The runtime also reads `MCP_CHANNELS_REPLY_SECRET` from the environment as a
fallback when `server.replySecret` is unset. **When no secret is configured**, the
token is signed with a per-process random key (the default) — single-process
replies still work, but a token minted by one process won't verify in another, so
configure a shared secret whenever you use `onEvent: spawn`/`both`.

### Live-spawn prerequisites

Spawning a **live** session is out of scope for the offline test suite (the suite
always injects a fake client). A real launch additionally requires:

- the **agent CLI** for your chosen `agent` on `PATH` — for the default `claude`
  agent that is the **`claude` CLI** (Claude Code),
- valid **agent auth** for that CLI (e.g. an Anthropic login/allowlist).

`@a5c-ai/adapters` is a regular dependency, so the launch path is always available;
when a source is configured to spawn but no adapters client can be obtained and
none is injected, this surfaces as a **clear startup error** from `createRuntime()`
— never a silent no-op at event time.

---

## Wiring to a real Claude Code session

> Channels are a **research preview**. Running a live Claude Code session requires
> the `claude` CLI, an Anthropic allowlist, and a development flag. The automated
> test suite verifies the whole pipeline **offline** with an in-memory MCP
> transport and mocked HTTP — this section is the manual wiring guide.

1. **Register the server** with Claude Code via an `.mcp.json` at your project
   root:

   ```json
   {
     "mcpServers": {
       "mcp-channels": {
         "command": "adapters-channels",
         "args": ["examples/channels.yml"]
       }
     }
   }
   ```

   The `mcpServers` key (here `mcp-channels`) becomes the `source` attribute Claude
   shows on each `<channel source="mcp-channels" …>` — so name it after the
   channel, not the transport.

2. **Export the env vars** your config interpolates (`GITHUB_TOKEN`, `JIRA_EMAIL`,
   `JIRA_TOKEN`, …) in the shell that launches Claude Code.

3. **Launch Claude Code with development channels enabled.** Channels are gated
   behind a development flag; start the CLI with:

   ```bash
   claude --dangerously-load-development-channels
   ```

   Claude Code reads `.mcp.json`, spawns the channels stdio server, and sees its
   `claude/channel` capability. From then on, every event that survives your
   filters arrives in the session as:

   ```
   <channel source="mcp-channels" repo="octo/app" issue_number="42" kind="issue_comment" author="bob" reply_to="…opaque…">
   …the comment text…
   </channel>
   ```

4. **Reply to origin.** To respond, Claude calls the `reply` tool with the event's
   exact `reply_to` value and the text to post. The framework decodes the token,
   routes to the owning backend, and posts the comment back to the originating
   GitHub issue/PR or Jira issue. (This guidance is also baked into the server's
   default `instructions`.)

### Optional: permission relay

Set `server.permissionRelay: true` to opt into the `claude/channel/permission`
capability. The runtime answers each inbound `permission_request` with exactly one
`permission` decision. The default policy is **deny** (untrusted inbound text is a
prompt-injection surface); supply a `permissionHandler(req) => 'allow' | 'deny'`
via `createRuntime`'s `deps` to implement sender-gating.

---

## Programmatic API

The package's main entry (`@a5c-ai/channels-adapter`) re-exports the framework
surface for embedding apps:

- `createRuntime(configPath, deps?)` — bootstrap a runtime (`{ server, poller,
  start, stop }`); `deps` can inject a fake transport / clock / http / adapters
  client for tests.
- `ChannelServer`, `DEFAULT_INSTRUCTIONS`, `Poller`.
- `defineBackend`, `registry`, `Registry`.
- `webhookBackend` (the built-in webhook backend module), plus the re-exported
  `NormalizedTriggerEvent` / `TriggerBackend` types from `@a5c-ai/triggers-adapter`.
- `loadConfig`, `compileFilter`, `filterMatch`.
- `StateStore`, `MemoryStateStore`, `deriveNew`, `boundSeen`.
- `encodeReplyTo`, `decodeReplyTo`, `dispatchReply`, `createRelay`.
- `SessionSpawner`, `buildSpawnRunOptions`.

---

## Testing

The whole suite is offline (vitest): mocked GitHub/Jira HTTP, an in-memory MCP
transport, an injected fake adapters client for the spawner, and inline/injected-fs
queues for the webhook backend.

```bash
npm test                 # vitest run
npm run test:coverage    # vitest run --coverage  (≥90% lines on src/ enforced)
```

Coverage is measured on `src/**` only (`src/cli.ts` and the environment-gated
`@a5c-ai/adapters` real-launch branch are excluded as trivial / not offline-testable).

---

## License

[MIT](LICENSE).
