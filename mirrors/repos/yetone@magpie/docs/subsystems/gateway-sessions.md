# Gateway Session Aggregation

The Sessions API combines file-backed native sessions with a read-only
projection of gateway usage records. A gateway session identity is exactly
`AgentOf(record.Agent) + record.Session`, where the session is the one the
client sent (`X-Magpie-Session`, or its own session header), whatever it starts
with. The response returns that id in `X-Magpie-Session`; listed browser
origins can read this header through CORS. magpie never makes up an id for a
request without one, so such a request has no session and its text is not
recorded: text kept under an id nothing lists couldn't be opened. Prompt text,
caller keys and network addresses are never used to guess conversation ownership.
So the configs magpie writes have each agent name its session: Pi's provider
block sets `compat.sendSessionAffinityHeaders` (`x-session-affinity` on Chat and
Messages; Responses sends `session_id` anyway), and omp 16.0.6 and later gets
`compat.promptCacheSessionHeader: x-session-affinity`. A user's own
`sendSessionAffinityHeaders` is kept (`piBlockKept`). Verification:
`TestPiNamesItsSessionToTheGateway`, `TestOmpNamesItsSessionToTheGateway`.
Older ledger records without `Session` remain excluded. The projection is
computed from the usage ledger and is not persisted. Window projections and
routing summaries reuse versioned log snapshots; appends and rewrites invalidate
them, and price/provider changes also invalidate priced projections. Single-session
lookups use the cached identity index. Native exclusions are applied per caller.

When the same identity is present in a native session, the native session wins
and the gateway projection is omitted. Gateway projections have no path,
resume command or terminal action: the agent's own files of them are not on
this computer. Their rows carry `gateway: true`; the Sessions page groups them
under "Seen through the gateway" rather than "No folder", and their size is the
text magpie recorded of them (`sessions.GatewaySizes`), shown only when there
is some. Their
models, token totals, start/last timestamps and effective prices come from the
same usage records used by Usage and stats endpoints.

A gateway projection can be deleted (lc on Discord). `sessions.DeleteGateway`
moves its recorded text folders (`gateway-conversations/<date>/<identity hash>`)
into magpie's session trash under `trash/sessions/gateway/`, with a note
marked `gateway`, and adds `{agent, id, last}` to
`gateway-sessions-hidden.json` in the config directory. `/api/sessions` and
`/api/sessions/manage` leave out a hidden session up to that last request; a
newer request lists it again. The usage ledger is not changed, so Usage,
`/api/sessions/one` and the stats endpoints keep what it spent. A session with
a request in the last minute is refused as active. Restore moves the text back
(items that expired or were cleared meanwhile are skipped; a session recorded
again on the same day is refused rather than overwritten) and unhides it; it
accepts only items that are that session's identity folders in the store.
Delete forever keeps it hidden. The recording's promises hold in the trash:
the hourly cleanup erases trashed gateway text past the seven days, "Delete
saved conversations…" erases it too (the notes stay, so Restore can still
list the session), and `HasGatewayConversations` counts it.
Implementation: [`internal/sessions/gateway_delete.go`](../../internal/sessions/gateway_delete.go),
`Restore` in [`internal/sessions/manage.go`](../../internal/sessions/manage.go), and
[`internal/gui/sessions_manage.go`](../../internal/gui/sessions_manage.go).
All-time statistics include gateway history older than native files. Calendar
activity and output totals use each session's actual request dates, including
intermediate dates; extending the range rebases existing native calendar indices.

Implementation: [`internal/usage/gateway_sessions.go`](../../internal/usage/gateway_sessions.go),
[`internal/sessions/external.go`](../../internal/sessions/external.go), and
[`internal/gui/sessions.go`](../../internal/gui/sessions.go).

## Local Gateway Conversation Recording

The Sessions page offers an explicit, default-off recording switch. Confirmation
discloses that prompts, replies and tool results can contain private files and
code. The switch is a card above the session list that says what is kept and
where (this computer only, up to 7 days and 256 MiB). It shows only where it
applies: on an agent whose list has gateway sessions (`gateway` on a
`/api/sessions/manage` row), in gateway mode, or while recording is on or text
is kept. Its "Delete saved conversations…" shows while
`/api/sessions/manage`'s `recorded` says some text is kept
(`sessions.HasGatewayConversations`, true when the folder can't be read), and
asks in magpie's own dialog first. `Settings.GatewayConversations` is machine-local consent:
`settings.SetGatewayConversations` updates it under the settings file lock.
Other Settings saves retain the latest stored consent under that lock, so an
older snapshot cannot re-enable recording after it is stopped. `KeepOwn`
also prevents sync/restore from enabling it.
`POST /api/sessions/recording` changes this switch; `clear: true` disables it and
erases only locally recorded gateway content (the store and deleted sessions'
text in the trash), leaving usage and native files.
The existing browser-mode authentication guard protects these APIs; this is an
administrator view, not per-caller-key access control.

[`recordConversation`](../../internal/gateway/conversations.go) wraps
`serveAgent` outside protocol translation and gateway middleware. It records
one client-facing exchange, not each retry, only under the session the client
named, using the same `usage.AgentOf` identity as the usage projection, so
every recorded conversation has a Sessions row that opens it. Codex's direct `/backend-api/codex/responses` relay is captured too.
Internal helper calls, token counting, embeddings, model listings, and compaction
paths that do not pass through these entry points are not recorded.
Recording adds no header and changes none, so routing and prompt-cache
affinity see the request as the client sent it. The existing protocol
readers handle Chat, Anthropic, Responses and Gemini; streaming replies use the
existing decoders, with completed Responses items retaining custom tool calls.
Only content actually sent through the gateway is available. Images are shown
as placeholders; hidden reasoning, client-only operations and unsupported wire
items cannot be reconstructed. This is not a raw request archive or remote
session synchronization, and existing S3 archives are not imported.

[`SaveGatewayTurn`](../../internal/sessions/gateway.go) stores normalized,
scrubbed exchanges in one append-only `turns.jsonl` per
`gateway-conversations/<UTC date>/<identity hash>/` under
the Magpie config directory, using 0700 directories and 0600 files. Each line is
one bounded turn; legacy per-turn JSON files remain readable until they expire.
An incomplete final append is omitted from reads (marked truncated) and removed
before the next append; complete earlier lines remain available. No headers are
stored. Known secrets and secret-named JSON
fields are scrubbed, but arbitrary sensitive text is not guaranteed removable.
Response capture uses an 8 MiB temporary spool; input is bounded to 8 MiB too.
Normalized turns are bounded to 1 MiB on disk, individual parts to 64 KiB,
and each daily session file to 256 MiB. A full daily session file rejects further
recording that day. Hourly background cleanup removes expired buckets and the
oldest files above 256 MiB; this is a soft store limit between cleanup passes.
Saving a turn does not rescan the whole store, and background traversal and
sorting do not hold the save lock.
Capture, parsing or persistence failure does not change the model response;
filesystem failures are logged without conversation bodies.

Content older than seven days is excluded from reads. The serving gateway
cleans up expired UTC-day buckets at startup and hourly, including with recording
off; the daily layout means physical cleanup can lag the read cutoff by one day.
Disable-and-clear and writes share a lock and recheck the consent generation,
preventing an in-flight request from refilling a cleared store even if recording
is enabled again before that request completes.

`GET /api/sessions/transcript` still prefers a matching native session. Otherwise
it reads a known gateway session's last 128 retained exchanges. A full exact
previous-history prefix is omitted from the next request, while repeated new
messages are preserved. System/tool-definition context is separately collapsed
when unchanged. Compacted, edited or incremental contexts may repeat material;
they are never guessed into a single canonical history. The existing transcript
display bounds apply and truncation is marked. Empty/expired/missing content
has an explicit empty state and all gateway transcripts identify their source.
The page invalidates pending transcript reads on reload or clear. A completed
read updates the current open transcript after redraw, and an older response
cannot replace content fetched after clearing the store.

`GET /api/sessions/markdown` and `POST /api/sessions/export` take the same
choice: a native session is written from its file (`sessions.WriteMarkdown`),
and otherwise a known gateway session from what its transcript reads
(`sessions.WriteGatewayMarkdown`, "Recorded by: magpie's gateway", with a note
when turns or a part's end weren't kept). A magpie that others reach as a
remote magpie has no file of their agents' sessions, so this is the only way
it can export them. Verification: `TestGatewaySessionExportsMarkdown`.

Verification: `TestGatewayConversation*` (`TestGatewayConversationNeedsTheClientsSession`
and `TestGatewayConversationClientRequestPrefixedSession` for the two rules above), `TestGatewaySessionHistoryAndCalendar`,
`TestGatewaySessionsNativeWinsBeforeLimits`,
`TestGatewayStatsRebaseNativeCalendar`, `TestCORSKeyThroughTheServer`,
`TestSessionsDeleteGatewaySession`, `TestGatewayDeleteTrashExpires`, `TestGatewayPurgeKeepsItHidden`, `TestGatewayDeleteNothingRecorded` and
`TestGatewayRestoreRefusesForeignItems`; browser
`gateway-conversations.test.cjs`, `sessions-talk.test.cjs`,
`sessions-gateway-delete.test.cjs`, and locale checks.

## Usage over the gateway, and subagents

`GET /v1/magpie/usage` and `GET /v1/magpie/usage/requests`
([`internal/gateway/usage_api.go`](../../internal/gateway/usage_api.go)) serve
the Usage page's summary and request ledger from the same builders as the
window's `/api/usage` and `/api/usage/requests`
([`internal/usageapi`](../../internal/usageapi/usageapi.go)), read-only and
without conversation text. They follow `/v1/magpie/quotas`' guard: this
machine, or another with an enabled gateway key, behind the same Host check.
A key that is held (`heldKey`: a budget, models or accounts) is refused the
summary and gets the ledger filtered to its own `CallerKey`, with its filter
lists cut to its own rows (`usageapi.OwnPage`): the ledger's facets are drawn
from every call in the period, so without the cut they would name other keys.
`TestUsageOverGateway` covers both, and a red when either cut is removed.

A usage record's `Session` stays the conversation. A Claude Code subagent's
record adds `Subagent` and `ParentAgent`. Through the gateway they come from
the `x-claude-code-agent-id` and `x-claude-code-parent-agent-id` headers
Claude Code sends for a subagent's requests (`subagentOf`, read in
`appendUsage`); the main thread sends neither. A row read from the agent's own
files gets `Subagent` from the file's name, `<session>/subagents/agent-<id>.jsonl`
or `<session>/subagents/workflows/<run>/agent-<id>.jsonl`
(`sessions.SubagentOf`), so no cache version changes, and `ParentAgent` from
the `parentAgentId` of the `agent-<id>.meta.json` beside it, which Claude Code
writes for a subagent a subagent started (`sessions.SubagentParent`, read once
a file; a meta file not read is unknown and read again). A gateway row matched
to a file row keeps the gateway's own. Both were checked against Claude Code
2.1.296 spawning a subagent from a subagent.
Codex sub-agents are told apart by `Kind` (`x-openai-subagent`) only: no
spawned Codex thread was found on disk to take a parent's shape from.
