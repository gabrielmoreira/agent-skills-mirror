# Agent environments from recorded captures

Use `rea environment-serve` to serve an environment manifest as an agent
environment: an MCP server whose tools answer from what one retained web
network capture observed, plus the environment card the agentenv framework
reads to discover it. By default the server derives the
[state the capture observed](#the-state-a-capture-observed) at startup and
answers read tools from it, and the write tools whose effect the capture
confirmed by changing it; `--replay-only` replays the capture's records
instead. Nothing is fetched from the recorded application; every answer comes
from retained Evidence. `rea environment-export` writes the same pair as a
bundle folder `agent-env run` builds and runs; see
[Export a bundle](#export-a-bundle).

```sh
rea inspect-web-network-capture /absolute/session.har har --format json > capture.json
rea inspect-analysis-view view.json --format json > manifest.json
rea environment-serve manifest.json --evidence capture.json --port 8765
```

The first command inspects the capture; the second projects the
[environment manifest](web-network-captures.md#environment-manifest) view from
it, where `view.json` wraps the capture Evidence as the inline source:

```json
{
  "source": { "kind": "inline", "evidence": { "evidence_id": "ev_…" } },
  "view": {
    "kind": "environment-manifest",
    "template_rules": ["after-uid-literal", "opaque-token", "sibling-variance"]
  }
}
```

The third command serves that manifest from the state it derives from the
capture; see [Serve from the state](#serve-from-the-state). Both served files
are complete REA Evidence JSON as the commands write it with `--format json`;
the `evidence` member of `view.json` is the whole of `capture.json`.

## From a browser scenario

The capture can also come from REA itself: a
[browser scenario](browser-scenario-contract.md) records a scripted session
in a browser REA launches, and its Evidence is a manifest parent like a HAR
inspection. Select the `network` event family and response bodies. A replayed
reply carries up to 256 KiB of a recorded body, but the scenario keeps at most
`max_network_body_bytes` of each body (64 KiB by default), and only within its
allocation budgets: base64 is charged about 11 bytes per body byte, and
redaction more the shorter a declared secret is (about 35 bytes per body byte
for a 12-character `admin_password`). A body over
`max_network_body_allocation_bytes` (1 MiB by default) is kept as `unavailable`
with that reason; one over `max_event_allocation_bytes` (4 MiB) or
`max_total_event_allocation_bytes` (16 MiB) loses its whole content event,
headers included, which the capture lists among its omissions. Either way its
tool replays no body. The example raises all four so that 256 KiB bodies are
kept when the declared secret has at least 12 characters:

```json
{
  "browser": { "mode": "launch", "executable_path": "/usr/bin/chromium" },
  "start_url": { "url": "http://127.0.0.1:5230/auth", "query": [] },
  "secrets": [
    { "secret_id": "admin_password", "environment_variable": "APP_PASSWORD" }
  ],
  "actions": [
    {
      "step_id": "user",
      "action": "fill",
      "locator": { "kind": "css", "selector": "input[name=username]" },
      "value": { "source": "literal", "value": "admin" }
    },
    {
      "step_id": "password",
      "action": "fill",
      "locator": { "kind": "css", "selector": "input[type=password]" },
      "value": { "source": "secret", "secret_id": "admin_password" }
    },
    {
      "step_id": "sign-in",
      "action": "press",
      "locator": { "kind": "css", "selector": "input[type=password]" },
      "key": "Enter"
    },
    {
      "step_id": "first-memo",
      "action": "goto",
      "destination": { "url": "http://127.0.0.1:5230/m/1", "query": [] },
      "wait_until": "load"
    }
  ],
  "capture": {
    "events": ["network"],
    "network": {
      "request_body": true,
      "response_body": true,
      "header_values": false
    },
    "limits": {
      "max_network_body_bytes": 262144,
      "max_network_body_allocation_bytes": 12582912,
      "max_event_allocation_bytes": 12582912,
      "max_total_event_allocation_bytes": 67108864
    }
  }
}
```

```sh
APP_PASSWORD=… rea capture-browser-scenario scenario.json --format json > capture.json
rea inspect-analysis-view view.json --format json > manifest.json   # view.json wraps capture.json as before
rea environment-serve manifest.json --evidence capture.json --port 8765
```

Each network transaction becomes one record, in request order, and the
record's ordinal is its zero-based position; a transaction whose URL carried a
redacted secret is left unrepresented rather than templated, and one the
capture cannot attribute to a single request and response is left
unrepresented too. Tools are chosen by response media type, so a scenario that
selected neither response bodies nor header values is refused; one that
selected header values but no response bodies yields a manifest but no state,
so it is served by replay. The browser
scenario redacts credential headers and the secrets it declares; values the
application returns in response bodies, such as session tokens, are kept, and
the replayed body is the bytes the browser exposes for each response, with any
declared secret replaced by its redaction marker (a body that redaction had to
empty replays no body).

## What a manifest is

An environment manifest is a projection of one application's recorded request
lines into a tool surface: one tool per method and path template on the
primary origin, with inferred path parameters, observed query parameter
names, value-free body shapes and pointers to the parent records each tool
cites. It carries no bodies and no headers. The manifest's
`parent_evidence_id` names the capture Evidence it was projected from; the
serve command refuses a manifest whose parent is not the supplied `--evidence`
file with an `invalid_request` error naming both identifiers, so a manifest can
never be served from records it did not cite.

The MCP catalog and environment card use a 1 KiB UTF-8 budget for each
captured display sample. Observation, body-key and cited-record lists show
whole values with omission counts; long method, path and query-name displays
show a marked prefix. Complete values remain in manifest Evidence. Argument
names longer than 64 characters use collision-safe `path_<n>` or `query_<n>` aliases; replay maps
those aliases to the complete captured names.

Discovery is admitted as a complete catalog under a 1 MiB serialization
reservation before the listener binds. Reservation charges up to six bytes per
UTF-16 code unit for JSON escaping/UTF-8 expansion, plus schema overhead;
a catalog may therefore be refused even when its compact JSON is smaller.
This was calibrated with 1500 query fields and eight concurrent SDK discovery
requests (183,798-byte card, 507.27 MiB sampled process-family RSS). Over-capacity
catalogs return `resource_constraint`, retain complete input Evidence, and require
a smaller capture or manifest. Fields and tools are never silently omitted.
Served from the state, each description is longer and the card declares the
data plane, so a catalog replay admits can exceed the reservation; the state
is then unavailable and the server serves replay instead (see
[Serve from the state](#serve-from-the-state)).

## What replay means and does not mean

Replay answers every tool with `--replay-only` or when the state is unavailable,
and, served from the state, each read tool whose view the state does not back.
Each such MCP tool call selects one of the records its manifest tool cites and
returns that record's recorded response. Selection compares the supplied path
parameters against the record's path segments at the parameter indexes, then
the supplied query values against the record's query string, and keeps the
record with the most matches; ties keep manifest order. The result reports
where the answer came from:

```json
{
  "status": 200,
  "content_type": "application/json",
  "body": { "id": 2, "login": "probe" },
  "replay": {
    "record_ordinal": 5,
    "evidence_id": "ev_…",
    "exact_match": true,
    "recorded_path": "/api/users/2",
    "recorded_query": null,
    "recorded_line_truncated": false,
    "body_recorded": true,
    "body_encoding": "utf-8",
    "truncated": false
  }
}
```

`exact_match` is true when every supplied path parameter and query value
equals the recorded one; it says nothing about parameters the caller omitted.
Recorded query parsing runs only when supplied query arguments affect selection.
A path value matches a recorded segment as written or after percent-decoding;
when both kinds of match are available, the record whose segment equals the
value as written is chosen. `recorded_query` keeps the `?` of an explicit empty
query, and a recorded path or query longer than 1 KiB is cut in the reply with
`recorded_line_truncated: true`; selection always uses the full recorded line.
`content_type` also has a 1 KiB display bound with `content_type_truncated`; body
interpretation uses the full recorded media type.
When no record matches, the tool still answers from the tool's first cited
record and reports `exact_match: false`. `body` is parsed JSON when the
recorded content type is JSON-like (`application/json`, `application/*+json`,
`text/plain`, `text/markdown`) and the text parses with safe numeric conversion; otherwise
it is the recorded text. Large integer IDs and other numbers that would lose
information stay in the original JSON text. Bodies over 256 KiB are cut at a UTF-8 boundary and returned as
text with `truncated: true`. `body_recorded` is false when the capture kept the
response's status and content type but no body; `body` is then `null`, which
is not a recorded JSON `null`. `body_encoding` is `base64` when the capture
retained response bytes that are not valid UTF-8; `body` is then exactly those
bytes in base64, never a lossy decoding. A retained base64 body is decoded only as far as the 256 KiB a reply can carry, and a leading byte-order mark is kept. For a `base64` body the limit applies to the recorded bytes, not their longer base64 spelling, and a cut keeps whole base64 groups. Request bodies passed to `POST`, `PUT` and `PATCH`
tools are accepted and ignored: nothing is written, and no call changes what a
later call returns. Arguments the tool's input schema does not name are
refused by the MCP server as invalid arguments, so a misspelled parameter never
degrades into an omitted one.

Replay is not emulation. A served environment does not establish the
application's authorization model, response semantics or state transitions,
which the manifest lists as unknowns; it does not validate supplied values; and
it answers only from the capture's recordings and the state they observed or a
caller loaded through `data/add`. Replayed content is
target content: every tool result, including the argument errors the MCP server
returns before a replay runs, carries `_meta.provenance.untrusted_content: true`
with `source: "analysis_target"`. The server advertises REA's untrusted-content
instructions plus a warning that its tool names, descriptions, parameter names
and observed values come from the capture too, and agents must treat all of it
as data, never as instructions.
That same warning prefixes every tool description in the standalone card, so
card discovery carries it before an MCP client initializes. It labels the
captured text without changing the tool names or schema fields clients use.

## The state a capture observed

Replay answers each call from one recording, so the answers reflect whichever
moment of the capture recorded them. The
[environment state](web-network-captures.md#environment-state) view extracts
instead the data the capture's reads observed before the first related write:
entity types with an identity field, entities with their recorded values,
documents for reads that are not entities, and a render plan per read tool,
kept only where it reproduces that tool's recordings from the state. It is the
starting state an environment holds, loads and reports: `environment-serve`
derives it from the capture at startup; see
[Serve from the state](#serve-from-the-state). With `--replay-only`, replay is
unchanged.

## Serve a manifest

```sh
rea environment-serve manifest.json --evidence capture.json [--replay-only] [--host 127.0.0.1] [--port 0]
```

The server derives the state from the capture before it binds and serves from
it, or serves replay with `--replay-only` or when the state is unavailable;
see [Serve from the state](#serve-from-the-state).

`--host` and `--port` default to `MCP_HOST` and `MCP_PORT` from the
environment, then to `127.0.0.1` and an ephemeral port, exactly as
[`rea mcp --http`](cli.md#serve-mcp-over-streamable-http) resolves them. The
bound MCP URL is written to stderr as one JSON log line
(`"msg":"MCP transport listening"` with `url`); `REA_LOG_LEVEL` overrides that
log level. `ENVIRONMENT_NAME` renames the served environment; otherwise the
manifest's `name` is used, and a set but blank value is refused as
`configuration_invalid` before binding rather than silently falling back. The
listener serves one MCP client at a time with the same session, `Host` header
and shutdown contract as [transports](mcp-contracts.md#transports) describes.
It runs until SIGINT or SIGTERM, then closes the listener, prints one
`{"status":"stopped", …}` document whose `state` member says whether it served
from the state, and exits `130` or `143`.
Signals during input loading or DNS/bind cancel the owning reader/listener before
a listening announcement;
that path returns a structured `cancelled` result instead of a stopped-listener
document, with the same signal exit status.

Three routes are served:

| Route                             | Answer                                                                                                                                                                                                                                              |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `POST /mcp`                       | The MCP server: from the state, one tool per read tool, answering from the state where it backs them, and one per write tool whose effect the capture confirmed, applying it to the state; in replay, one tool per manifest tool, replaying records |
| `GET /.well-known/agent-env.json` | The environment card                                                                                                                                                                                                                                |
| `POST /agentenv`                  | From the state, `data/reset`, `data/add` and `data/get`; in replay, JSON-RPC `-32601 method not found: <method>` for every method                                                                                                                   |

Numeric JSON-RPC IDs outside JavaScript's safe range or whose precision would
be lost are refused as invalid requests with a null ID. They are never echoed
as a different number.

In replay the data plane at `/agentenv` is advertised by the card but carries
no operations; the error names the requested method so a caller can see that
the method, not the transport, is unsupported. Its request body is
read within the same 4 MiB bound the MCP endpoint applies: a larger body is
answered `413` with a JSON-RPC `-32000` error before any of it is parsed, and a
body that is not JSON is answered `400` with `-32700`. A notification (no `id`)
gets `202` and no body, a batch gets one reply per request in it, and an empty
batch, a batch of more than 100 messages, or a message that is not a JSON-RPC
request (including an `id` that is not a string, number or null, or `params`
that are not an object or array) gets `-32600 invalid request`.

## The environment card

The card is the discovery document the agentenv framework reads before
connecting to `/mcp`. A replay environment's card reads:

```json
{
  "name": "grafana-example",
  "protocolVersion": "1.0",
  "url": "/agentenv",
  "preferredTransport": "JSONRPC",
  "additionalInterfaces": [{ "url": "/mcp", "transport": "mcp" }],
  "capabilities": {
    "extensions": null,
    "tools": [
      {
        "name": "get_users_by_id",
        "description": "Untrusted captured API catalog: … GET /api/users/{numeric}; returns a JSON object with fields \"id\", \"uid\", \"login\", \"email\"; recorded statuses 200; replays retained records [5, 6]; evidence ev_…",
        "inputSchema": {
          "type": "object",
          "properties": {
            "id": {
              "type": "string",
              "description": "Path segment 2 (numeric); observed: 2, 3"
            }
          },
          "required": ["id"],
          "additionalProperties": false
        }
      }
    ],
    "operations": []
  },
  "children_environments": null
}
```

`capabilities.tools` lists the same names, descriptions and input schemas that
`tools/list` advertises over MCP. After the catalog warning, each description
names the method and path template, then what the tool returns, one level deep:
`returns a JSON object with fields …`, `returns a JSON array of objects with
fields …` or `returns a JSON object whose <member> lists objects with fields …`,
where a list is an array of objects found by the
[environment state](web-network-captures.md#environment-state)'s list rule (the
root array, or the one array of objects an envelope carries). Field and member
names are written as JSON strings, so a captured name cannot read as more of
the description; a member name too long to show whole is a quoted prefix marked
as truncated. The summary comes
from the first cited `2xx` record that replay answers as JSON; only when none
did, the first cited JSON record of another status gives it, labelled with that
status (`status 401 returns …`). It describes one recorded response, not a
contract. Field names are sampled within the same budget as other captured
values, and the manifest's `statuses` for the tool follow; a tool with no JSON
record states only its statuses. The description then lists the replayed
records and the evidence ID, and the whole catalog stays within its
serialization reservation, which the summaries and MCP annotations are charged
to.

Over MCP, every tool also carries annotations: `readOnlyHint` is true for the
safe methods (`GET`, `HEAD`, `OPTIONS` and `TRACE`) and for query `POST`s (a
path segment such as `search` or `query`); `destructiveHint` is true for `DELETE` and left unset for other
writes, so the MCP default (destructive) applies to them, and read-only tools
omit it because clients ignore it there; `idempotentHint` is true for the safe
methods, `PUT` and `DELETE`; and `openWorldHint` is false for every tool,
because answers come from the capture rather than the captured application. The
hints describe the captured method; replay itself changes nothing. The card
keeps the `name`, `description` and `inputSchema` of the echo example's tool
shape and carries no annotations.

Path parameters are required strings whose
description names the segment index, the templating rule and the observed
values (sampled within the list budget above; the manifest keeps them all);
query parameter names are optional strings; write methods accept an
optional `body` object described by the recorded top-level key types. Each
input keeps its own argument: a query name equal to a path parameter's name is
advertised as `query_<name>`, a query name longer than 64 characters as
`query_<n>` (its position) with the captured name sampled in its description,
and the write body as `request_body` when a query parameter is named `body`. Every
schema closes with `additionalProperties: false`, a key the echo example's
schema does not carry.
In replay, `extensions`, `operations` and `children_environments` are fixed to
`null`, `[]` and `null`: a replay environment declares no extensions, no
data-plane operations and no children. Served
[from the state](#serve-from-the-state), the card declares the three data-plane
operations and one intake extension instead, and the catalog holds the read
tools and only the write tools whose effect the capture confirmed: a read tool
is described as answering from the state where the state backs it, and a
served write tool by the effect it applies to the state and the quoted body members it
accepts.

## Serve from the state

```sh
rea environment-serve manifest.json --evidence capture.json
```

Before it binds, the server derives the
[environment state](web-network-captures.md#environment-state) the capture
observed: it runs the `environment-state` view on the capture in-process with
the manifest's `template_rules` in the same order, exactly as
`inspect-analysis-view` projects it from the same capture, so the state
Evidence id it reports is the one that projection produces. The view's own
budget and refusals apply, and the result is checked like the view's Evidence
for this manifest: extracted from the served capture, with the manifest's
rules, naming only manifest tools. The server keeps one live state, shared by
every MCP session and the data plane, starting from the derived state.

A state that is unavailable does not stop the server: it logs a warning naming
the error `code` and message before it binds, then serves replay. The state is
unavailable when it cannot be derived, such as from a
`capture_browser_scenario` capture that selected header values but no response
bodies or over the view's budget, when `data/get` would write it past the 32 MiB
`data/add` intake limit, and when its catalog under the served name
exceeds the [discovery reservation](#what-a-manifest-is). That check runs
first, so no state is derived for it, and replay is then admitted exactly as
with `--replay-only`. `--replay-only`
serves replay without deriving anything; the card, tools and `/agentenv`
answers are then exactly those of replay. The stopped document's `state`
member reports which applied:

- `{"served": true, "evidence_id": "ev_…"}`: served from the derived state.
- `{"served": false, "reason": "replay-only"}`: `--replay-only` was given.
- `{"served": false, "reason": "unavailable", "code": "unsupported_target", "message": "…"}`:
  the state is unavailable; `code` and `message` are those of the refusal
  (`resource_constraint` for a catalog over the reservation), as the warning
  logged them.

Each read tool answers according to its view in the state:

| View       | Answer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `item`     | The entity the path arguments name, rendered into the recorded envelope of `envelope_ordinal`. Arguments match as replay matches them: each collection segment equals the held collection's segment as written or after percent-decoding, and the identity is the last argument percent-decoded, then as written; values are never re-split on `/`. Any entity the state holds answers, including one `data/add` loaded; query arguments only decide `replay.exact_match`. An entity the state does not hold answers the tool's latest recorded 400, 404 or 410 response with `state.view` `missing`, or is a tool error when none was recorded; one lacking a field every recording carried is a tool error, unless a read showed the application leaves that field out; a body is never invented.                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `list`     | When the arguments name one of the lines the view checked exactly (its latest recordings before the first related write; every path and query value equal to the recording's, and every recorded query parameter supplied), that recorded envelope with its array rendered from the state: every entity of the collection in state order for `membership: "all"` or a line `all_record_ordinals` names, or the recorded members still held. A call with no query argument answers from such a line of the collection its path arguments name that only pages its list, with `replay.exact_match` false. On a line the view's `query` answers, and for a call whose every query argument has a role there (an argument-less call aside), the answer is the query evaluated over the state: filtered, searched, sorted and paged, with counters at the number listed and `query.totals` at the number matched, and `state.membership: "query"`; such a call answers on a query or whole line of its collection with `replay.exact_match` false. A value an `inert` parameter never recorded, or a parameter without a role, replays its recording. A member lacking a field every recording carried makes the call a tool error rather than a partial list. |
| `document` | When the arguments name the document's checked line exactly, the state's value for it; a tool error when the state holds none.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `recorded` | The recording, as replay answers it.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |

An item or list view that always spells a clock field otherwise than the
entity's stored value names that spelling in `clock_formats`, and a value it
never recorded, such as a created entity's clock, is rendered in it: a list that
writes `+00:00` where item reads write `Z` lists a new entity the same way.

A list or document call that names no checked line, including a line recorded
after a write or with other query values, answers from the recording. Every
answer has the replay shape plus `state`: `{"source": "state", "view": …}`
naming the entity, collection or document path, or `{"source": "recording",
"reason": …}` with the view's reason, `no-view`, `unrecorded-request`, `page-exceeded` (a call naming a page of a whole list that the collection has outgrown) or `projection` (a call to an item tool whose recordings asked for some fields only, naming such a parameter for an entity the state holds; the answer is a recording, so it does not show served writes). A
state answer carries the base record's status, content type and `replay`
provenance with `truncated: false`; one whose JSON would exceed 256 KiB is
refused as a `resource_constraint` tool error rather than cut. Extraction does
not state-back a document whose rendered JSON exceeds 256 KiB; that read stays
recorded (`rendered-oversize`) and replays the captured body. Query `POST`s
stay served and answer from their recordings with the reason `query-body`.

A line establishes whole-collection membership only from the beginning:
`offset`, `start`, `_start` and `page` must be zero when present. Positive or
malformed positions do not by themselves establish whole membership. A separate
query model may describe supported paging; an empty later page cannot start
returning earlier entities merely because it was empty in the capture.

`POST`, `PUT`, `PATCH` and `DELETE` tools are served only when the state's
[write plan](web-network-captures.md#environment-state) for them is served:
the capture's later reads confirmed the effect the plan models. Other write
tools are not served, so no call claims a change it does not make; each one's
plan states why in its `reason`. A served write changes the live state, which
every MCP session and `data/get` then see:

| Effect     | Call                                                                                                                                                                                                                                 |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `create`   | Adds an entity to the collection the path names, built from the observed entity with each ruled field taken from the call or generated, at the plan's `insert` position. A plan tied to its exemplar's collection writes only there. |
| `update`   | Sets the sent members on the entity the path names, constants for members accepted only with their recorded value, and the clock, increment, slug, unique and renewed changes the plan models.                                       |
| `delete`   | Removes the entity the path names.                                                                                                                                                                                                   |
| `document` | Merges the body into the plan's document object, or replaces it for `PUT`.                                                                                                                                                           |

Its answer has the status and content type of the plan's recorded response,
with the written entity or its identity rendered in, no body, or the recorded
body. A call whose body is not an object, sends a member the capture did not
show stored, sends a fixed member with another value or a member of another
JSON type, or lacks a required member is a tool error naming the accepted
members; so is a rendered answer missing a field the recorded response
carried, and an update or delete of an entity the state does not hold answers
the recorded 400, 404 or 410 of the tool or of an item view of the type, if
any. A refused call leaves the state unchanged. Values a write generates are
deterministic: the clock starts at `write_clock` and advances one second per
served write, sequences take one past both the largest held value and the
largest they generated, and UUIDs and tokens derive from the state Evidence
id, tool, field and write count, skipping held values. `data/reset` and
`data/add` restart the clock, counter and sequences, so the same calls after a
reset give the same state. Answers carry `state: {"source": "state", "view":
"create" | "update" | "delete", …}` or `"document-write"`.

The data plane serves three JSON-RPC methods:

| Method       | Result                                                                                                    |
| ------------ | --------------------------------------------------------------------------------------------------------- |
| `data/reset` | `{}` after restoring the state the Evidence holds                                                         |
| `data/add`   | `{}` after replacing the whole state with one valid `rea-state/v1` document                               |
| `data/get`   | `{"parts": [{"kind": "data", "data": <rea-state/v1 document>}]}` with `state_evidence_id` and the `types` |

Calls run one at a time in arrival order across requests. Every message of a
batch is queued when the batch arrives, so another request's call never lands
between them and each message sees the changes of those before it; a reset
sent while a download is loading applies after that load. `data/add`
takes exactly one part: a `data` part whose `data` is the document, or a
`file` part whose `file` carries `bytes` (base64 of UTF-8 JSON) or a `uri`,
either a `file://` URL of a local regular file, whose host is empty or
`localhost`, or an `https://` URL fetched without following redirects and
within 30 seconds, including reading the body; `mimeType`, when given, is
`application/json`. A `file://` URL naming another host, or a UNC path such as
`file:////server/share/state.json`, is refused before anything is opened, so a
load never reaches a network share. A loaded document is at most 32
MiB, and so is the state as `data/get` writes it back with the members a
document may omit (`types`, `state_evidence_id`, record citations), so a
reported state always loads again; an inline part also stays within the 4 MiB
request body bound, so larger states arrive by `uri`. Anything else, including `{"parts": []}`, is `-32602
invalid params`; a download that fails or answers a non-2xx status is
`-32000`. Errors never echo the uri or the content; a file or download failure
names its category in `error.data.reason`: `not-found`, `permission`,
`not-regular-file`, `changed` or `read-failed` for files, `timeout`,
`http-status` or `network` (connection, TLS or a refused redirect) for
downloads, and `cancelled` for a download the server's stop or its caller's
departure ended.

Served creates also bound additional collection history since the last reset
or `data/add` to 1 MiB of deterministic accounting: UTF-8 bytes for each new
collection spelling and its possible sequence keys, plus a 64-byte allowance
per collection and potential sequence-key record. The score bounds identifier
payload and a fixed record allowance; it is not a measurement or guarantee of
process memory. Collections
already present in the Evidence or loaded state are part of the state itself;
the store indexes their unique spellings so they remain known after deletion,
but they do not consume this additional-history budget. A create that would
exceed the budget is refused before the state changes. `data/reset` or `data/add`
clears generated history; if the same calls would hit the limit again, use
fewer distinct collection paths. The 1 MiB score ceiling is 1/32 of the
separate 32 MiB state-intake ceiling, reserving a small, explicit allowance
for identifiers retained beyond the loaded state. A loaded-state path that is
later deleted and then introduced again may consume the additional-history
budget when the store must retain it beyond the source entity.

Stopping the server cancels every pending call, and a caller that leaves before
its reply cancels its own: a download in progress ends, and calls not yet run
are answered `-32000` with `error.data.reason` `cancelled` without running. A
cancelled call leaves the state unchanged, and shutdown never waits for a
download.

One `/agentenv` response carries at most 64 MiB of replies, twice the 32 MiB
a loaded document may hold: room for a `data/get` of a loaded state, while a
batch of reads cannot multiply a large state into one body. Replies are
measured in order as they are produced, in bounded parts and before they are
assembled, and room is kept for every later reply's budget error and the
batch's brackets and commas, so one that would take the response past the
budget is never built whole and is answered instead with `-32000` whose `error.data` gives
`max_response_bytes` and the `reply_bytes` it would have taken. That call still
ran, so repeat such a read in another request. A reply no larger than that
error, such as a write's `{}`, is always kept.

```json
{
  "rea_state": {
    "version": 1,
    "entities": [
      {
        "type": "/api/users",
        "collection": "/api/users",
        "id": "2",
        "fields": { "id": 2, "login": "probe" }
      }
    ],
    "documents": []
  }
}
```

Each entity's `type` is a state type's `collection_template`, its `collection`
matches that template segment by segment (a template parameter matches any one
segment), its identity field's value is its `id`, and its type, collection and
id are unique; `view_fields` is optional and names item or list views of its
type. Views render their values over the entity's fields, so a view's values
must not set the type's identity field to a value whose text differs from the
entity's `id`. Spell a collection as requests spell it, as `data/get` reports it: list
calls find entities under the checked line's recorded path. Each document
names a `document` view once, at its initial document's `path`. The `version`,
and the `state_evidence_id` and `types` that `data/get` reports, must match
the served state, so a `data/get` result loads back unchanged. A number without
an exact native value, or whose serialized spelling would not be read as exact
(an integer from 2^53 below 1e21, such as `1e20`, in any spelling), or a
`__proto__` member is refused rather than altered.
An invalid document is `-32602` naming the first problem by JSON pointer, as in
`/rea_state/entities/3/collection` (also in `error.data.path`); a problem
inside caller data (`fields`, `value`, `types`) is located at that member, so
the pointer never names the caller's keys. A refused document changes nothing;
a valid one replaces the whole state at once. The order of `entities` is the
state order lists use.

Record citations stay Evidence provenance. An entity's `record_ordinals` may
be omitted or empty and a document's `record_ordinal` omitted; otherwise they
must be the served Evidence's citations for that entity or document, or the
document is refused. After loading, an entity or document whose values equal the Evidence's cites
the Evidence's records, and one whose values were edited or added cites none
(`record_ordinals: []`, no `record_ordinal`), so `data/get` never presents a
loaded value as recorded.

The card declares the operations and what `data/add` accepts:

```json
{
  "extensions": [
    {
      "uri": "urn:agentenv:intake/v1",
      "description": "data/add replaces the whole environment state with one rea-state/v1 document; data/get returns the current state in the same format.",
      "params": {
        "add": [
          { "part": "data", "format": "rea-state/v1", "load": "replace" },
          {
            "part": "file",
            "format": "rea-state/v1",
            "mimeTypes": ["application/json"],
            "load": "replace"
          }
        ],
        "get": [{ "part": "data", "format": "rea-state/v1" }]
      }
    }
  ],
  "operations": ["data/reset", "data/add", "data/get"]
}
```

The state starts as a projection of recorded reads and changes only through
served write tools and the data plane. List and document calls answer from the
state only for the lines their views checked, and every recorded view answers
from recordings; item calls answer for any held entity but render only the
envelope one recording carried. Values copied outside entity objects, derived
values and counters other than those that count a list stay as recorded, and a
served write changes only the one entity or document it writes: side effects
on counters, relations and copies of entities in other collections, reordering
after an update and referential rules on delete are not modelled. An exported
bundle carries no state file: its server derives the state at startup, as the
export does to predict what it serves.

## Export a bundle

`rea environment-export` writes the same pair as a bundle folder the agentenv
framework runs directly, shaped like its own echo example:

```sh
rea environment-export manifest.json --evidence capture.json ./grafana-example --json
agent-env run ./grafana-example
```

```text
grafana-example/
  README.md                                 provenance, what it serves, run command, rights note
  envs/grafana-example/Dockerfile           pinned image: node:24.18.0-bookworm-slim + rea-agents@<this version>
  envs/grafana-example/env.toml             environment_name = "grafana-example"
  envs/grafana-example/manifest.json        byte-exact copy of manifest.json
  envs/grafana-example/evidence.json        byte-exact copy of capture.json
  artifacts/check_grafana-example/verify.py the verifier
  tasks/smoke.json                          deploy_env (local sandbox), then env_outcome_verifier
```

The command reads each file once, after checking that reading and parsing the
whole file, including sealing traversal, fits the process's live heap headroom (a file that does not is
refused as a `resource_constraint` before it is read), then authenticates and cross-checks the
pair as `environment-serve` does, so a manifest projected from another capture
is refused with the same `invalid_request` before anything is written, and the
bytes it copies are the bytes it authenticated. The bundle directory must be
absent or empty; an occupied directory is refused and nothing in it changes.
After checking the bundle name, the export prepares the state from the capture
exactly as the bundle's server will at startup under that name, to predict what
the bundle serves; an unavailable state, including one whose catalog exceeds
the discovery reservation, does not stop the export, and the bundle then
serves replay. The complete tool catalog the bundle serves must also fit the
server's advertised catalog budget before any files are written. Privately parsed JSON is sealed once so authentication
and replay share immutable response trees rather than copying the capture repeatedly.
`--name` replaces the manifest's portable kebab-case name as the env folder and env id
(Windows device names such as `con` and `lpt1` are refused);
`--package-tarball <path>` copies a packed `rea-agents` tarball into the env
folder and makes the Dockerfile install it instead of the registry package and
remove it in the same layer, which is how a checkout rather than a release is
run. The command prints the
written files with their sizes, the pinned package source, the number of tools
the bundle serves as `tool_count`, and in `state` whether it serves from the
state, in the shape of the serve command's stopped document.

Export uses the shared output-tree owner to check directory identities around
exclusive creates, verify written bytes, and reject unowned entries before
reporting success. It does not delete an inspectable partial folder on failure.
Node's portable pathname APIs leave a syscall-boundary race, so the output's
parent directories must be trusted. On POSIX output files use mode `0600`;
Windows inherits ACLs and REA does not establish owner-only access there. Choose
an already private Windows destination when captured content needs it.

The Dockerfile sets `MCP_HOST=0.0.0.0` and `MCP_PORT=18765`, the port the
framework maps for an MCP server env; the framework's own deploy supplies
`MCP_HOST`, `MCP_PORT` and `ENVIRONMENT_NAME`, so the served card carries the
env's name. It installs Debian's `python3` because the framework's local
sandbox probes a container's readiness with `python3` inside it, which the slim
Node image lacks. It copies the two inputs owned by the image's non-root `node`
user, so a private host umask cannot leave them unreadable, runs as that user and starts
`rea environment-serve /env/manifest.json --evidence /env/evidence.json`. The
`env.toml` names the environment because the framework otherwise reads the
name from Python sources the image does not have.

`verify.py` is the framework's `async def verify(mcp_url)` shape over its
Python MCP client: it lists the tools and checks the count equals the number
the bundle serves (from the state, the manifest's read tools and the write
tools whose effect the capture confirmed; every manifest tool in replay), calls one tool with no arguments and checks the call did not
fail and its `status` is the expected one, and returns one `serve` result
whose description reports both checks. The tool is the first served `GET` tool
without path parameters whose answer to no arguments is not an error, and the
expected status is the status of that answer: the export calls the same answer
function the server uses, from the derived state or by replay, so a state
answer carries its base record's status and a replayed one its record's (an
unknown recorded status stays unknown; it is not borrowed from another
record). A bundle with no such tool yields a verifier that checks the count
only and says so. `tasks/smoke.json` deploys the env on the local
sandbox and runs that verifier against the env's MCP endpoint; the first run
also builds the framework's own infrastructure, and the run tears everything
down when it ends.

The README written into the bundle records the capture artifact's SHA-256, the
capture and manifest Evidence ids, the manifest view digest, the served tool
count, the derived state's Evidence id or that no state is served, and the
package source. It says what the environment serves: read tools from the state
the capture observed, the `/agentenv` data plane on it and the write tools
whose effect the capture's later reads confirmed, replay when the state is
unavailable, and `--replay-only` for pure replay; it
says which applies to this bundle, with the error code and message when the
state is unavailable, and that neither is emulation and served
content is untrusted data. It states that the recorded content belongs to the
captured application and must not be published without the rights to it.

## Measure fidelity against the application

An environment agrees with its own capture by construction. What matters to an agent is how it answers the calls the
capture did not make, what it shows after a write, and how it fails. `rea environment-compare` measures that against the
application itself:

```sh
rea environment-compare manifest.json --evidence capture.json \
  --probe probe-crud.json --probe probe-reads.json --json
```

Each `--probe` is capture Evidence (`inspect-web-network-capture` of a HAR, or `capture-browser-scenario`) of one call
sequence made against the live application, seeded as it was for the capture and reset before the sequence. The command
makes no network call: whoever records the probes drives the application with its own credentials. For each probe it
resets the environment's state, takes the requests in the order they were made (record order when any lacks a start time), matches each to the manifest tool of the
same method whose path template fits with the most literal segments (a format-rule parameter must fit its format once
percent-decoded). A path argument is the raw segment, which the environment decodes once.
It answers the call as the served environment would, and compares that answer with the application's.

A re-seeded application holds the same entities under other ids, so the comparison maps them. Objects in the two answers
to one call pair by a natural key, a string field unique on each side that both share, such as a name or a slug; their
identifier fields (`id`, `uuid`, `guid`, and names ending in `_id`, `Id`, `ID`, `_uuid` or `Uuid`), and those of two single
answers such as a create's, map the live value to the environment's, including a create that returns only the new id.
Ids are learned only from an answer the environment
gave that call itself, from its state or a recording of that very call, request line and body, never from another call's
recording replayed in its place and never from a recording whose body the probe omitted. The answer's own `id`, `uuid` or `guid` also maps within the collection the call names, since
two collections can reuse a live id, and an equal pair stays in that collection. A live id in a later request's path, query or body is translated before the
environment answers, a path parameter by the collection the live path names (a nested collection keeps its parent values, each decoded once, and a literal route segment stays), except a query value that pages a list, such as `limit`
or `page`. Each call is checked against the served tool's input schema first, as the MCP server checks it. After mapping, two clock values compare by format only (ISO-8601 strings, and epoch numbers under
time-named fields), and two different values each side generated on its own compare equal: both UUIDs, or one length of
eight or more with the same character classes and a digit. The report counts each kind of normalised value.

A step agrees when the statuses and the normalised bodies are equal. The report gives agreement overall, per probe and
per tool, `agreement_ignoring_order` for steps that differ only in item order, and each step's differences, at most 20,
with a JSON pointer and both values cut short:

| Category        | Meaning                                                                                                      |
| --------------- | ------------------------------------------------------------------------------------------------------------ |
| `status`        | The statuses differ                                                                                          |
| `missing-field` | The application's object has a member the environment's lacks                                                |
| `extra-field`   | The environment's object has a member the application's lacks                                                |
| `value`         | Values differ, or one is an object or array and the other is not                                             |
| `length`        | Arrays differ in length, or not every item pairs                                                             |
| `order`         | Paired items come in a different order                                                                       |
| `clock-format`  | Both are clocks, in different formats                                                                        |
| `refused`       | The environment refused the call                                                                             |
| `not-served`    | The request's tool is one the environment does not offer, such as a withheld write                           |
| `no-tool`       | No manifest tool matches the request                                                                         |
| `unmapped-id`   | The application answered with success and the environment did not, for a path id the comparison never mapped |

What a probe did not observe is not counted as the application's behaviour. A record without a usable request line,
such as a redacted URL or a transaction the capture cannot attribute, is not replayed, nor is a request to another
origin than the application's (`other-origin`: the probe's origin with the most JSON-like records, as the manifest
chooses its own), and a request with no recorded
answer is made, since it may have changed the application, but not compared: each probe lists them under `unobserved` with the reason, and the summary counts them. A live
body the probe did not record compares by status only and is counted as `unobserved_bodies`, unless the answer never
carries one (204, 205, 304, `HEAD`). A browser probe captured without `capture.network.response_body` is refused, as
is one that makes POST, PUT or PATCH calls without `capture.network.request_body`.

Agreement covers only the calls the probes make, after the mapping the answers allow. Values compared by form, clocks
and generated values, can still differ in content, and an equal answer after a write shows the state matched for that
read, not that the write had no other effect.

## Compatibility verification

`npm run verify:agentenv:environment` is the hosted `real-agentenv` lane
described in [testing](testing.md#exported-environment-bundles). It projects
the Grafana-shaped source-owned capture through the built CLI, packs the
checkout, exports a bundle with `--package-tarball`, runs it with the pinned
`agentenv-framework` release on the runner's Docker and requires the smoke task
to pass with no container left behind other than the framework's own
image-registry helper, which the receipt reports. It proves that one exported bundle runs
on one framework release; it does not claim any hosted platform or other
framework versions.

## Resource and lifecycle boundaries

The Evidence files are read once at startup through the bounded JSON input
reader and authenticated as Evidence before the listener binds; a file that is
not Evidence, a manifest of another view kind, a capture of another format, or
a manifest projected from a different capture is refused before any port is
opened. The state is derived once, in-process and before binding, from the
already authenticated capture: it is projected as retained Evidence, so the
capture's strings are not charged again as inline view input, and the view's
96 MiB budget bounds the derivation. Because authentication covers the capture's records, a manifest whose
parent check passes cites only records the capture retains. The server keeps
only the cited records' request lines and response text in memory, plus the
live state when it serves from one: the derived initial state, or one
validated document whose JSON was at most 32 MiB. Data-plane calls run one at a time, so
at most one loaded document is being read and parsed at once; `data/get`
serializes the held state whole. No process is launched and nothing is
written to disk. No outbound network request is made unless a `data/add` call names an
`https://` uri, which is fetched once within the limits above; a `file://` uri
is read once. A listener that fails after binding is logged and ends the command with
a `resource_constraint` error and exit `1` instead of serving nothing.
