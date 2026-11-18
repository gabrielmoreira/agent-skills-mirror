# OpenMotion tracking

An explicit-event package shared by the standalone MCP runtime and Motion Studio.
It has no runtime dependencies. The application consumes its TypeScript sources;
`npm run build:tracking` emits JavaScript and declarations for a local `npm pack`
from this directory. The package remains private; this change does not publish it.

For new events, start with the [integration guide and agent task template](INTEGRATION.md).

## Reporting and user control

Reporting is **on by default in every application environment and version**, including
stable releases, test/prerelease packages and local builds, into the existing
OpenDesign project (420348). Application version and environment remain event
properties; they do not disable collection. DEV packages retain their separate
installation/data directories and template routing.
OM events carry `product=openmotion`; OM reports must filter by that property,
and shared-project reports must distinguish OM from other products. The project's
public, write-only token and ingestion host are distributed in
`shared/tracking-config.json`; it contains no read/admin credentials and is never
included in the browser bundle. Users do not need to supply a key or opt-in flag.

Users can turn collection off in Studio's **Privacy settings → Share usage data**.
This preference is persisted under the installation's data directory and applies
to both MCP and Studio, including already-running processes and future restarts.
Disabling clears pending queues and aborts in-flight delivery; accepted events
cannot be recalled. A filesystem watcher propagates preference changes, and each
enqueue/flush also checks the saved preference. Corrupt preference files fail closed.
Re-enabling resumes collection of new events in MCP and Studio
without restarting. Events discarded while disabled are not buffered or replayed.

`OPENMOTION_TELEMETRY=0` (also `false`/`off`) or `DO_NOT_TRACK=1` forces all collection
off and locks the Studio switch. Restart services after changing launch environment
variables. Browser Do Not Track suppresses browser collection. The environment
override takes priority over the saved preference.

For another collector, supply both `OPENMOTION_POSTHOG_HOST` and
`OPENMOTION_POSTHOG_KEY`. Partial or invalid configuration fails closed. Custom
collectors default to zero-IP mode; `OPENMOTION_GEOIP=1` requires that collector to
discard IP after enrichment. Never supply a personal `phx_` API key.

Keep the OM-only receiver transformation active while geo-enabled clients report
to this shared project. Before removing it, stop OM collection or switch those
clients to zero-IP mode. Do not revoke the shared OpenDesign token as an OM rollback.

Use `OPENMOTION_TRACKING_ENV=test` and a UUID in
`OPENMOTION_TRACKING_TEST_RUN_ID` for isolated ingestion checks; filter these records
out of product dashboards. Normal environments are `production` and `development`.
Node/Vitest tests suppress collection unless explicitly given a test run ID; CI
also forces collection off. No test should silently report into production funnels.
Marked live-ingestion checks use `env=test` with any application version.
Deterministic checks use fake senders and extracted stable/test/local packages
without external requests.

Studio retrieves only an enabled flag and submits semantic events to the same-origin
`/motion-api/tracking` endpoint. The server validates the complete batch, rejects
identity/source/credential overrides, and adds trusted common fields before posting
to PostHog `/batch/`. Browser Do Not Track suppresses browser collection. Network
reporting is asynchronous, with a bounded timeout; local business results never wait
for PostHog. A collector receipt confirms acceptance, not queryable ingestion.

Event `producers` and closed property schemas live together in `events.ts`.
Studio's typed API and the service's browser-admission registry are derived from
that definition; server-side validation remains mandatory. Studio configuration
loading retries transient failures with bounded backoff, stays disabled until
confirmed, and never treats a valid opt-out as a retryable failure. Callers can
inspect local queue/configuration statuses and a content-free status snapshot;
see [diagnostics and retry semantics](INTEGRATION.md#diagnose-without-logging-event-contents).

## North-star evidence and task ledger

The runtime now records a local export task ledger before returning an accepted
export request. Each export keeps its task ID, project, optional work-round ID,
acceptance time, explicit deadline, terminal time and observed outcome. A worker
terminal result updates the same ledger and emits `task_terminal`; unknown or
cancelled results remain separate from success. An export whose worker vanished or
whose deadline passed is reconciled once with outcome `unknown`, so its accepted
entry also gets a terminal time and the same event; whichever caller closes the task
(the worker tick or a status read) states that evidence. A tick never
reconciles an export this process is still rendering, and a worker whose job was
closed that way does not restate its terminal outcome. The ledger is
installation-local, atomic and does not contain prompts, source content or
credentials.

Host run boundaries use the existing work-round ID returned by
`openmotion_open_preview(action=begin)`. The MCP boundary emits
`host_run_started` and `host_state_changed`; a host-reported visible preview with
verified content emits `host_preview_observed` and `host_run_delivered`. A verified
technical export can also close the same run with `host_run_delivered`. A failed or
cancelled export emits the corresponding host terminal event. These events do not
claim a run boundary when the host did not provide a work-round ID.

Quality evidence is explicit. Technical export, preview visibility and recorded
content review each emit `check_required` and `check_completed` with a version,
checklist, checker type and bounded evidence reference. A technical export check
does not assert visual or human acceptance. Queue workers emit `queue_snapshot` at
most once per minute and `worker_heartbeat` with bounded counts. Confirmed
correctness incidents and recovery evidence use `incident_confirmed` and
`recovery_recorded`; ordinary task failures are not incidents.

## Identity, properties and privacy

`account_sign_in_result` reports each finished OpenDesign connector attempt with
`source_product=openmotion`, `source_detail=openmotion_editor_login`, and an
`entry_id` / `entry_occurred_at` pair created when the editor starts sign-in.
Attempts replaced within that sign-in retain the entry pair while their
`attempt_id` changes. A new explicit sign-in creates a new entry pair. Success
is reported only after the connector completes credential acceptance and the
local account setup finishes; browser opening or approval alone is not success.
Successful completion also reports the confirmed account ID as `amr_user_id`,
so account counts can deduplicate across installations and join AMR account facts.
Failures and cancellations omit that ID. The existing collection controls apply;
`distinct_id` remains the installation ID, without identify/alias or person merging.
Email, names, activation URLs, authorization codes and credentials are omitted.
These fields describe the local OM result; AMR handoff attribution is separate.

The account and subscription settings' **Manage subscription** link carries
`od_origin=openmotion`, `od_entry_source=openmotion_manage_subscription`, and a
fresh `od_entry_id` / UTC `od_entry_at` for each primary or middle click. The link
retains `billing=plan` and contains no account, installation or credential data.
AMR must accept the OpenMotion origin and entry source in its attribution
validation before these parameters can reach its subscription/payment events.

One random `installation_id` UUID is persisted atomically in `tracking/identity.json`
under each owned data directory, outside projects and versioned application caches.
Different data directories remain separate installations.

Device-level analytics uses an OS-provided stable identifier: IOPlatformUUID on macOS,
the 64-bit MachineGuid registry value on Windows, and machine-id on Linux. A bounded,
lazy read runs only when enabled tracking sends a batch. The identifier is never
persisted, logged or transmitted: HMAC-SHA256 uses it as the key with the fixed
OpenMotion-specific `openmotion:device:v1` namespace and platform. Only the resulting
`omd_` hash is sent as `device_id`, with `device_id_source=platform`. It is independent
of project, data directory, app version and host. MCP, Studio and worker events on
one OS device share this device hash. PostHog `distinct_id` continues to use the
persisted `installation_id`, preserving each installation's historical analytics
identity across upgrade. Different data directories remain separate analytics
identities even when their device hash is the same. No identify/alias or person-profile
migration is performed.

Unreadable, invalid or unsupported platform identifiers produce `device_id=unknown`
and `device_id_source=unavailable`, never an installation UUID presented as a device.
Device counts must filter `device_id_source=platform` and count distinct `device_id`,
not `distinct_id` or person IDs. Unknown events are a separate coverage measure,
not one device. Historical events without this marker used directory UUIDs in the
device field; this change does not backfill them as measured devices.

Native PostHog unique-user charts and person-based funnels/retention continue to
measure installations. Filtering by device source alone does not turn them into
device-level analyses; those need explicit aggregation by `device_id`. For example:

```sql
SELECT uniqExact(properties.device_id) AS active_devices
FROM events
WHERE timestamp >= now() - INTERVAL 2 DAY
  AND properties.product = 'openmotion'
  AND properties.device_id_source = 'platform'
```

This measures OS-device identities, not people or immutable physical hardware. Shared
machines count once, a person on two machines counts twice, cloned OS identifiers can
collide, and an OS reinstall can change Windows/Linux identifiers. Device context contains
no account identity, MAC address, raw platform identifier or probabilistic fingerprint. The package can
initialize an identity with a validated source label; existing identities retain
their first source. Landing-page attribution and installer `--source` plumbing are
a separate change. Unknown source remains null.

Common fields include schema/product/app version, environment, entrypoint/runtime,
platform/architecture, OS/version, runtime locale, device IANA timezone and UTC offset
(east of UTC is positive). After OpenDesign's existing GeoIP transformation, the
[OM-only transformation](./posthog-geoip.hog) matches `product=openmotion`, derives
country/first-level region/geographic timezone and removes raw IP, precise GeoIP
and person-location updates before storage. The transformation has both an event
filter and a source-code guard; non-OM events pass through unchanged. Existing
OpenDesign transformations and the project's global IP setting are unchanged.
Lookup failures leave geographic fields unknown. GeoIP describes the observable
network egress; VPNs/proxies can change it. Device timezone is a separate setting.
Network intermediaries still see the connection address. Operators must keep the
OM transformation enabled after GeoIP; it is a receiver requirement, not a guarantee
enforced by a public capture token. The earlier standalone OM project's test data
is retained and is not migrated or deleted. Custom zero-IP mode retains the fixed address
`0.0.0.0`, because a null property is replaced with the request IP. OM requests no
person profiles and emits no autocapture or session replay; other OpenDesign
producers retain their own settings. Upstream engine telemetry stays disabled.

Runtime and TypeScript event contracts whitelist required fields, enums, UUIDs and
bounded counts. No prompts, messages, source files, URLs, local paths, titles, raw
exceptions or credentials are accepted. Safe error categories are explicitly mapped.
The sole bounded free-text exception is the settled template-search keyword,
described below; it does not enable text on other event fields.
All retries retain the original event UUID/timestamp and PostHog `$insert_id`.
Bounded numeric rules also preserve fractional timings, playback rates and signed
audio/geometry measurements; non-finite or out-of-range values are rejected.

### Host Agent attribution

Every event has `host_agent` and `host_agent_source`. Known declared clients map
to `codex`, `deepseek` (DeepSeek Harness/DSH), `claude`, `cursor`, `opencode`,
`gemini`, `workbuddy` or `chatgpt`; another declared client maps to `other`.
Missing evidence is `unknown`, never inferred from an installed executable,
model provider, browser user agent or the last caller of a shared backend.
`mcp_client_name` is included only for a bounded implementation identifier;
`mcp_client_version` is the client's declared numeric version, not a verified
host-application version. DSH currently declares its MCP adapter version.

The stdio runtime captures `initialize.params.clientInfo` per connection and also
recognizes standard per-request `io.modelcontextprotocol/clientInfo` metadata.
An absent declaration can fall back to `OPENMOTION_HOST_AGENT`, `CODEX_THREAD_ID`
or `CLAUDECODE=1` in that MCP process, labeled `launch_environment`. Environment
values and thread IDs themselves are never reported. Client metadata is
self-declared analytics context, not authenticated identity or an entitlement.

The calling context follows domain operations and is persisted on export jobs
for the worker. Editor handoffs receive an opaque `tracking_context` query token;
the local service associates it with that opener for at most 24 hours and 256
live contexts, in memory only. The browser submits the token to its same-origin
collector and cannot supply host properties in an event. Repeated handoffs retain
their connection's token, project navigation preserves it, and another client
cannot replace an existing association. A manually opened, expired, evicted or
restarted page context reports `unknown`. No global last-used-host attribution is
used. These tokens are metadata references, not authorization credentials.

The research sources are the [supported MCP lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle),
[Codex's MCP client](https://github.com/openai/codex/blob/main/codex-rs/rmcp-client/src/utils.rs)
and [DSH's client declaration](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/mcp/mcp-client/src/connection.ts).

## Implemented signals and limits

- All registered phase-one stdio tools: accepted start and observed finish, including
  early-return catalog tools, input rejection, partial import and idempotent replay.
- All nineteen page WebMCP tools: `webmcp_tool_started` and
  `webmcp_tool_finished`, correlated by a fresh `call_id` per invocation, with
  the public `tool_name`, `transport=webmcp`, observed `outcome` and bounded
  `duration_ms`. These are browser-call measurements, separate from stdio MCP
  events and committed business results; a replayed call is still a call.
  Structured error replies and thrown failures count as failed calls, even when
  their applied effect is uncertain. Explicit aborts count as `cancelled`; missing
  or malformed replies count as `unknown`. A late abort does not turn a successful
  reply into a cancelled operation. Arguments, results, handles, paths and raw errors are
  excluded. Host Agent fields retain their existing page-handoff meaning; the
  transport marker does not identify the calling browser agent.
- Asset call action: `mcp_tool_started/finished` and
  `webmcp_tool_started/finished` include an optional closed `action` category for
  asset tools: `list`, `get`, `import`, `update`, `generate`, `jobs`, `status`,
  `cancel`, `import_to_project`, `read`. The shared extractor ignores other tools,
  missing/malformed actions and unknown values; no raw arguments or media are sent.
  The action is captured once at invocation start and retained on finish, including
  failure and input rejection. Stdio keeps `tool_name=motion_assets` for both public
  asset names; WebMCP keeps their public names. Historical events without action
  remain valid and cannot be backfilled. Registration has no action.
  To measure `read`, filter `product=openmotion`, exclude `env=test`, select the
  appropriate `*_tool_finished` event and `action=read`: count distinct `call_id`
  for observed calls, divide successful calls (`outcome=success`) by all observed
  calls for success rate, and aggregate `duration_ms` (e.g. median/p95) for latency.
  Stdio rejected inputs have `accepted=false` and no start event; use finished
  events for the denominator, or filter `accepted=true` explicitly when measuring
  accepted executions only. Each invocation, including replay, is a new call.
  Browser and stdio are separate transports; do not sum starts and finishes or add
  domain-result events to call counts. This measures observed call outcomes, not
  paid generation completion, human media acceptance or guaranteed billing usage.
- WebMCP registration: `webmcp_registration_result` records one result per
  attempted tool registration (`success`, `failure` or `cancelled`), including
  validation/duplicate refusals and teardown cancellation. Use this event for
  registration counts; existing native/polyfill and registration-error events
  remain diagnostic signals. A disabled tool preference or absent modelContext
  makes no tool-registration attempt. The existing consent, Do Not Track,
  configuration retry and best-effort delivery policies apply to all three events.
- Domain results: create/open/edit/import/restore and export request/cancel. Replayed
  operations do not manufacture additional domain completions. Preview returned by
  a tool does not imply the host opened it.
- Worker export terminal state, after render and available technical verification;
  it is distinct from queue acceptance and does not assert human content acceptance.
- Studio project readiness and load outcome, plus project-sidebar creation/switching.
- Motion editor exports started from the Studio UI: one `studio_export_request_result`
  per start attempt (accepted or rejected with a safe code) and one
  `studio_export_result` per accepted render when that tab observes its terminal
  state, joined by a browser-minted `export_id`. These renders run in the editor's
  own pipeline and never reach the worker `export_result`, which stays MCP-only.
- Motion editor manual edits: one `studio_edit_result` per committed history entry,
  emitted where Studio claims the entry, with a closed `edit_kind` and the `surface`
  the gesture started on. Coalesced claims of one entry report once. Writes
  dispatched by an in-page Agent tool are skipped; MCP edits never reach this path.
  Project rename and asset rename/delete report from their own commit points, and
  save failures report `outcome=failure` with a status class only.
- Undo/redo outcomes, UI asset imports (counts, entry point, safe category),
  notices actually shown (missing FFmpeg, external file conflict, unreachable
  project) and editor intent clicks through `ui_click` with `page_name=studio`;
  theme, language and privacy-settings choices made in the settings center use area `settings`.
  `ui_click.option` carries the chosen value of a control with a small fixed set.
- UI export events carry `video_duration_bucket` for the composition being rendered;
  the request event and `studio_load_result` carry `clip_count_bucket`,
  `asset_count_bucket` and `composition_count_bucket`. They are read from what the
  editor already holds in memory at that moment and report `unknown` otherwise:
  at load the timeline and file tree have usually not arrived, so the load values
  are mostly `unknown` and the export request is the reliable reading. No raw
  duration, count or file size is sent.
- The template gallery shared with the website (`web/template-gallery.ts`, shown in the
  connection dialog):
  copy click and the actual copy result, preview open, use, category change and
  one search per query, through `ui_click` area `templates` and
  `template_instruction_copy_result`. `template_id` is the catalogue id and is
  accepted only as a `slug`; a non-matching id is omitted and the event still
  sent. Titles, authors and URLs are never fields. When the workspace catalogue
  records the template a project was created from, the same id is added to
  `studio_load_result` and both UI export events.
- Editor events carry `project_scope`; `project_id` is sent only when the Studio
  project id is a UUID. The built-in local project (id `project`) reports
  `project_scope=default` and no id; names and titles are never sent.
- All 78 retained Studio event names are registered in
  [studio-events.ts](studio-events.ts) and included in the same derived browser
  admission registry: startup/preview/render/performance, editor interaction,
  feedback/desktop, save/error/transaction, SDK, WebMCP status and audio FX.
  Existing `trackEvent` and `trackStudioEvent` callers use the OpenMotion transport.
  Their [adapter](studio-properties.ts) removes private fields before queueing;
  upstream tokens, transports and automatic experiment enrollment remain disabled.
  Feature visibility and SDK gates do not change: hidden feedback, desktop and
  audio-FX features emit only when their existing producer actually runs.
- Manual import/export recovery uses `studio_io_action` and `studio_io_result`,
  joined by one random `attempt_id` per intentional action. The Studio-only
  `beginStudioIo` helper reports at most one result; automatic reads and background
  render updates do not create actions. Import counts cover only the files selected
  in that attempt, and a subsequent listing failure does not turn confirmed imports
  into failed imports. A successful render recheck means the query succeeded, even
  when `state_after=failed`. An inaccessible file is `failure/unavailable`; a network
  result that cannot confirm availability is `unknown/unknown`. Opening a new window
  is `success` with `delivery_status=opened`; a blocked popup is `failure` with
  `delivery_status=popup_blocked`. Passing a download to the browser reports
  `outcome=unknown`, `file_status=available` and
  `delivery_status=browser_save_requested`; it does not confirm a saved file.
  Only fixed actions, outcomes, statuses and aggregate counts are allowed: no
  project/task identity, file names, paths, content or full error messages.
- The editor's template library reports with the names of the shared OpenMotion
  tracking sheet, so its funnel lines up with the website's: `surface_view` for
  the library, a gallery card, a template's detail and the instruction to copy;
  `ui_click` areas `template_card`, `template_detail`, `template_instruction` and
  `template_discovery`; `template_search_result`, `template_filter_result` and
  `resource_download_result`. A template is identified by `template_id` only
  (a bounded slug); titles, authors and URLs are never fields. `placement` says
  how a detail was reached: `catalog`, `related`, `random` (Surprise me) or
  `navigation` (previous/next). `detail_view_id`, `copy_attempt_id`,
  `download_attempt_id` and `search_id` are random UUIDs that tie a click to its
  result. Recreate and Recreate-and-submit report `start_use` with
  `template_action` and copy that same instruction; the instruction panel has no
  Copy control of its own, so no separate copy click is reported. Every copy
  reports `template_instruction_copy_result`, and only `clipboard_written` is a
  successful copy. `host_product` names the instruction variant that was copied
  (the library builds the Codex one), not the client the user later pastes it
  into. A category or filter option is sent
  as a lowercase slug of the stable catalogue value and omitted when it cannot be
  reduced to one. `template_search_result.search_keyword` is the one free-text
  field in the registry: the settled search-box value, trimmed and capped at 100
  characters, sent once per keyword 500 ms after typing stops and never per
  keystroke. A card impression (`template_card` / `card`) is reported once the
  card has been at least half visible for one unbroken second and is not covered
  by the detail, once per search, filter and sort combination, so click-through
  per card can be read. Hover, scroll depth, autoplay and video progress are not
  reported. These events carry no project fields yet.
  Library exposure records the actual dialog opening, including pending or failed
  catalog loads; it omits `result_count` because that count is not known at opening.
  Loading retries and locale changes do not create another opening. Instruction
  exposure waits until at least 1% of its text enters the viewport in a visible tab, once per
  detail view. Recreate and Recreate-and-submit carry the same `copy_attempt_id`
  on their `start_use` click and copy result; Open-and-edit has no copy attempt.

The adapter preserves fixed actions, counts, booleans and safe catalog/control
identifiers. It drops messages/stacks, file paths, selectors, composition/block
names, free-text feedback, breadcrumb text and arbitrary error names. Feedback
retains `has_comment`, rating and fixed question/answer categories; resolver
mismatches become per-kind counts, and attempt rollups retain total attempts and
distinct-operation counts without raw JSON keys. Audio parameter numbers are
bounded; string parameters retain only a fixed engine-catalog `value_category` and
`value_kind=category`. Custom effect/preset/parameter identifiers become `other`.
Unknown event names are ignored. Invalid required fields prevent the event from
being queued; optional invalid fields are omitted. The server still rejects
unknown fields and forged common properties rather than applying this adapter.

Coverage follows the existing producers; it does not invent new product actions.
Installer/integration/resource-read events, actual WebMCP tool-execution outcomes,
every successful editor save/import gesture and human review/adoption results
still need their own confirmed completion semantics. WebMCP status signals and
save-failure/blocked signals are not those missing success/result events.
Worker origin is `worker`; its caller's host context is persisted, while a full
request-to-worker operation context is not. Pending cancellation has a cancel
result but no worker completion because no worker claimed it.
Editor UI coverage has known gaps: a render whose tab reloads before it finishes, or
whose cancel the server never confirmed, has a request result but no terminal result;
caption and beat undo stacks, keyboard playback, frame stepping and source-editor saves
are not reported; `edit_kind` is derived from Studio's fixed history labels, so an
unmapped label reports `other`. Turning sharing off is itself not reported, because
the preference applies before the event could be sent.

The compatibility adapter bounds initialization-waiting calls at 64. The queue is
process-local: 64 events, batches of 16, one in-flight request, a one-day
TTL and retry backoff capped at one minute. Disabling aborts and drops pending data;
shutdown drains for at most two seconds. Crashes, queue overflow, page termination
or permanent collector rejection may lose events. Add durable delivery if product
decisions require guaranteed counts. Public ingest tokens are not read/admin keys,
but forged events and quota abuse still require collector-side rate limiting and
monitoring; this package is not an anti-fraud boundary.

## AI asset generation

The shared model gateway owns three worker events for Studio and MCP. Each carries
`modality` (`image`, `video`, or `audio`); speech and music both use `audio`.

| Event | Emission point | Additional fields |
| --- | --- | --- |
| `media_generation_requested` | A generation submission reaches the gateway with a recognized modality, before validation and routing. | None |
| `media_generation_submitted` | The gateway persists a new queued job. Replaying its idempotency key returns the original job. | `job_id` |
| `media_generation_result` | The gateway persists a completed, failed, cancelled or interrupted job. Interrupted workers produce a failed result. | `job_id`, `job_state`, `asset_count` |

Count distinct anonymous installations per modality and window, and distinct
submitted jobs. Attribute results to the original submission date. A job succeeds
when it completes with at least one saved asset. The success rate divides those
jobs by all submitted jobs, including cancelled, failed and unresolved jobs at
the report cutoff. Inspect, list and status calls do not enter this cohort.
A local save retry can update the terminal result for the same job. Use the latest result per job at the report cutoff. It does not add a model request or submission. Count outputs saved to the workspace library or project once per output.
Generation uses the existing telemetry preference and installation identity.

Studio recovery keeps request acknowledgement separate from execution outcome. An uncertain export receipt reports `studio_export_request_result.outcome=unknown`; a later identity-matched lookup can report one terminal result with the same browser `export_id`. Progress loss, cancelling and an inactive unknown record never produce a failed or cancelled terminal event. `studio_asset_import_result` retains its entry-point categories and reports confirmed failure, unknown and pending counts separately; unknown/pending items are not counted as failed. The manual `reload_editor` recovery action records only an unknown handoff outcome, not confirmed recovery.
