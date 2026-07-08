# Query Cost Attribution

Step-by-step workflow for investigating what is driving DQL query scan costs.
Covers BUE billable totals, per-source attribution, per-detector breakdown
(ALERTING pool), and QEE drill-down.

## Contents

- [Common Principles](#common-principles)
- [Overview](#overview)
- [BUE Query Attribution Fields](#bue-query-attribution-fields)
- [Step 1 — Top Sources by Billable Scan (BUE)](#step-1--top-sources-by-billable-scan-bue)
  - [Step 1a — Coverage Check](#step-1a--coverage-check)
  - [Step 1b — Combined Attribution](#step-1b--combined-attribution)
- [Step 2 — Identify Source Type](#step-2--identify-source-type)
  - [Step 2b — Drill Down by Bucket](#step-2b--drill-down-by-bucket)
- [Step 3 — Drill Into QEE for Details](#step-3--drill-into-qee-for-details)
  - [Step 3b — Cross-Validate Execution Count](#step-3b--cross-validate-execution-count)
- [Step 4 — Per-Detector Scan & Name Resolution (ALERTING pool)](#step-4--per-detector-scan--name-resolution-alerting-pool)
- [Step 5 — Rank by Cost Weight](#step-5--rank-by-cost-weight)
- [Best Practices](#best-practices)
- [Investigating QEE↔BUE Mismatches](#investigating-qeebue-mismatches)

## Common Principles

1. **BUE is billable truth, QEE is diagnostic** — BUE Query events reflect
   actual billed scan volumes; QEE provides per-query execution details
   (`client.client_context`, query text, duration). Always start cost
   investigations with BUE, then drill into QEE for attribution detail.

2. **Sample first** — Before building any attribution query, run
   `| limit 3` (without `| fields`) on the target event type to discover
   available fields. `client.source`, `client.function_context`, and
   `client.workflow_context` vary by pool; confirm they are populated.

3. **Dedup billing events** — Use `| dedup {event.id, event.type}` for
   multi-type queries. See
   [Billing Event Deduplication](billing-capabilities.md#billing-event-deduplication).

4. **Always verify coverage before attributing** — Run the
   [Step 1a coverage check](#step-1a--coverage-check) before filtering on any
   `client.*` field.

5. **Rolling windows are acceptable here** — Investigation queries use
   `from: -7d` or `from: -30d` for diagnostic analysis. For billing totals
   that must match the Account Management Portal, use explicit UTC midnight
   boundaries per [billing-capabilities.md § Billing Timeframe Boundaries](billing-capabilities.md#billing-timeframe-boundaries).

## Overview

Query cost attribution requires **all 5 steps**. BUE (Step 1) shows billable
totals but lacks per-detector breakdown. Steps 2-4 resolve that using QEE
and `ANALYZER_EXECUTION_EVENT`. Stopping at Step 1 leaves most costs
unattributed.

**BUE vs QEE:** BUE Query events are billable truth. QEE's `scanned_bytes` is diagnostic,
not billable. Start with BUE for totals, drill into QEE for breakdown.

## BUE Query Attribution Fields

Coverage of all `client.*` attribution fields depends on your tenant's query pool
distribution, not on BUE event type. Always run the coverage check in Step 1a
before building attribution queries.

| Field | Description | Populated on |
|-------|-------------|--------------|
| `client.source` | Named source (dashboard URL, detector ID) | ALERTING, DASHBOARDS, APPLICATION, OPERATIONAL, BILLING; variable on INTERNAL_APPLICATION |
| `client.application_context` | App ID (e.g., `dynatrace.automations`) | AUTOMATION, DASHBOARDS, APPLICATION, INTERNAL_APPLICATION |
| `client.function_context` | Function within the app — drill down after attributing | AUTOMATION reliably; partial on INTERNAL_APPLICATION |
| `client.client_context` | Structured JSON with app, function, and version details | ALERTING and AUTOMATION reliably; variable on API and APPLICATION |
| `client.internal_service_context` | Internal Dynatrace service name | ALERTING, OPERATIONAL, BILLING |
| `client.workflow_context` | Workflow ID | AUTOMATION only |
| `user.id` / `user.email` | User or service account | Most pools |

Use `coalesce(client.source, client.application_context, client.internal_service_context, client.workflow_context, client.function_context, client.client_context, "unknown")` for
attribution. For app-level results, drill into `client.function_context`.

## Step 1 — Top Sources by Billable Scan (BUE)

Start with BUE — billable truth. First run a **coverage check** to see which
attribution field to use, then run the attribution query.

### Step 1a — Coverage Check

Verify which attribution fields are populated before building the attribution
query:

```dql
fetch dt.system.events, from: -7d
| filter event.kind == "BILLING_USAGE_EVENT"
| filter in(event.type,
    "Log Management & Analytics - Query",
    "Events - Query",
    "Traces - Query",
    "Files - Query")
| dedup {event.id, event.type}
| fieldsAdd has_source = isNotNull(client.source)
| fieldsAdd has_app_ctx = isNotNull(client.application_context)
| summarize
    total_gib = sum(toDouble(billed_bytes) / 1073741824),
    with_source_gib = sum(if(has_source, toDouble(billed_bytes) / 1073741824, else: 0)),
    with_app_ctx_gib = sum(if(has_app_ctx, toDouble(billed_bytes) / 1073741824, else: 0)),
    by: {event.type}
| fieldsAdd source_coverage_pct = round(with_source_gib / total_gib * 100, decimals: 1)
| fieldsAdd app_ctx_coverage_pct = round(with_app_ctx_gib / total_gib * 100, decimals: 1)
| sort event.type asc
```

### Step 1b — Combined Attribution

Use `coalesce()` across all six `client.*` attribution fields to capture the first
non-null value regardless of which query pool generated the event:

```dql
fetch dt.system.events, from: -30d
| filter event.kind == "BILLING_USAGE_EVENT"
| filter in(event.type,
    "Log Management & Analytics - Query",
    "Events - Query",
    "Traces - Query",
    "Files - Query")
| dedup {event.id, event.type}
| fieldsAdd attribution = coalesce(client.source, client.application_context, client.internal_service_context, client.workflow_context, client.function_context, client.client_context, "unknown")
| summarize total_billed_gib = sum(toDouble(billed_bytes) / 1073741824),
    by: {attribution, event.type}
| sort total_billed_gib desc
| limit 20
```

## Step 2 — Identify Source Type

The meaning of `attribution` depends on which query pool generated the cost.

| `attribution` pattern | Source type | Next step |
|------------------------|-------------|-----------|
| `https://.../document/...` | Dashboard (DASHBOARDS pool) | Filter Step 1b by `matchesPhrase(client.source, "/ui/dashboard/")` to rank dashboards |
| Encoded settings UID / opaque ID | Detector settings `objectId` (ALERTING pool) | Step 4 — resolved in combined query |
| `builtin:davis.anomaly-detectors/...` | Detector type name (ALERTING pool) | Step 4 — parse `client.client_context` |
| `dynatrace.automations:...` | Automation function (AUTOMATION pool) | Cross-ref with `WORKFLOW_EVENT` |
| `dynatrace.<appname>` | Platform app (from `client.application_context`) | Drill into `client.function_context` |
| `dt.*` service name | Internal platform service | Review with platform team |

### Step 2b — Drill Down by Bucket

Identify which Grail storage buckets drive scan volume. High scan on a specific
bucket may indicate queries without time filters, over-broad aggregations, or
detectors running against large-retention data:

```dql
fetch dt.system.events, from: -7d
| filter event.kind == "BILLING_USAGE_EVENT"
| filter in(event.type,
    "Log Management & Analytics - Query",
    "Events - Query",
    "Traces - Query",
    "Files - Query")
| dedup {event.id, event.type}
| summarize total_gib = sum(toDouble(billed_bytes) / 1073741824),
    query_count = count(),
    by: {usage.bucket, event.type}
| sort total_gib desc
| limit 20
```

> To join BUE with QEE for per-query details, use `query_id` (present on both).
> **Cardinality:** one DQL statement (`query_id`) → **multiple QEE records and
> multiple BUE events, one each per `usage.bucket` touched.** So `count()` on
> either event kind counts bucket-touches, not DQL statements — use
> `countDistinct(query_id)` for the statement count (see
> [Step 3](#step-3--drill-into-qee-for-details)). When aggregating `billed_bytes`
> from joined results, group by `event.id` (not `query_id`) to avoid inflating
> totals.

Join BUE with QEE for per-query details (group by `event.id` when summing
`billed_bytes` to avoid inflation from the bucket fan-out):

```dql
fetch dt.system.events, from: -7d
| filter event.kind == "BILLING_USAGE_EVENT"
| filter in(event.type,
    "Log Management & Analytics - Query",
    "Events - Query",
    "Traces - Query",
    "Files - Query")
| dedup {event.id, event.type}
| lookup [
    fetch dt.system.events, from: -7d
    | filter event.kind == "QUERY_EXECUTION_EVENT"
    | fields query_id, query_string, execution_duration_ms, user.email, table
  ], sourceField: query_id, lookupField: query_id,
     fields: {query_string, execution_duration_ms, query_user = user.email, table}
```

## Step 3 — Drill Into QEE for Details

QEE provides per-query execution details not available on BUE: `query_string`,
`scanned_bytes`, and `execution_duration_ms`.

> **Sample a BUE Query event with `| limit 1` before joining to QEE** to
> confirm available fields — notably `query_id`, the correct join key.

> **Filter must match the attribution field from Step 1b.** If the top
> `attribution` value came from `client.source`, filter on `client.source`.
> If it came from `client.application_context`, filter on that instead. Use
> `coalesce` to cover both:

> ### ⛔ What QEE `count()` actually counts — do NOT mislabel it
>
> A `QUERY_EXECUTION_EVENT` is emitted **once per bucket touched per DQL
> statement** — NOT once per DQL statement, and NOT once per workflow/detector
> run. A single `fetch logs` that scans 3 buckets produces **3 QEE records**
> (all sharing one `query_id`). Therefore:
>
> | Quantity | How to count it | What it means |
> |----------|-----------------|---------------|
> | `qee_events = count()` | raw QEE row count | bucket-touches — **diagnostic only** |
> | `dql_statements = countDistinct(query_id)` | distinct `query_id` | actual DQL queries executed |
> | workflow / detector **runs** | a **separate** `WORKFLOW_EVENT` / `ANALYZER_EXECUTION_EVENT` query — see [Step 3b](#step-3b--cross-validate-execution-count) | how many times something actually ran |
>
> **Never** alias the QEE row count as `queries`, and **never** phrase it as
> "ran N times" or compute a frequency (per-second / per-minute) from it. The
> inflation factor is workflow-dependent — it ranges from a few× (one DQL
> statement touching a handful of buckets) to 50×+ (many statements per run,
> each touching many buckets). Even a modest 2–3× gap turns a real run count
> into a wrong one, so the size of the gap is never a reason to trust the QEE
> count. Always count distinct `query_id` for query volume, and cross-validate
> run counts with the source event
> ([Step 3b](#step-3b--cross-validate-execution-count)) before reporting any
> "how often did this run" conclusion.

```dql-template
fetch dt.system.events, from: -7d
| filter event.kind == "QUERY_EXECUTION_EVENT"
| filter coalesce(client.source, client.application_context, client.internal_service_context, client.workflow_context, client.function_context, client.client_context) == "<top attribution from step 1b>"
| summarize qee_events = count(),
    dql_statements = countDistinct(query_id),
    total_scanned_gib = sum(scanned_bytes) / 1073741824,
    avg_duration_ms = avg(execution_duration_ms),
    by: {table, status}
| sort total_scanned_gib desc
```

> The `qee_events` and `dql_statements` columns will differ whenever queries
> touch more than one bucket. Report `dql_statements` (or scan volume) — not
> `qee_events` — when describing how much querying a source did.

### Step 3b — Cross-Validate Execution Count

**Required whenever you report how often a source ran** (e.g. "this workflow
runs N times/day", "this detector fires every X"). QEE counts can never answer
this — the run count lives on the originating event:

| Attribution pool | Run-count event | Filter | True run count |
|------------------|-----------------|--------|----------------|
| `dynatrace.automations` (AUTOMATION) | `WORKFLOW_EVENT` | `event.type == "WORKFLOW_EXECUTION"` + workflow id | `countDistinct(dt.automation_engine.workflow_execution.id)` |
| ALERTING (detectors) | `ANALYZER_EXECUTION_EVENT` | `dt.task.id` | sample first — `count()` may fan out; prefer `countDistinct` on the analyzer execution/run id |

> ### ⛔ `WORKFLOW_EXECUTION` `count()` is NOT the run count either
>
> `WORKFLOW_EVENT` / `WORKFLOW_EXECUTION` is a **state-change** event: one row
> per `dt.automation_engine.state` transition, where state ∈
> `{RUNNING, SUCCESS, ERROR, CANCELLED}` (`dt.automation_engine.state.is_final`
> is `true` for the terminal states). A run emits a `RUNNING` row
> (`duration` ≈ `0,00 ns`, no end timestamp) and one terminal row (real
> `duration` + end timestamp), **both sharing the same**
> `dt.automation_engine.workflow_execution.id`. A completed run is 2 rows; an
> in-flight run is 1. So `count()` overstates runs by ≈2× and the exact factor
> drifts (validated on a live tenant: 2,879 rows vs 1,440 distinct executions
> for the same workflow over 24h). **Always use
> `countDistinct(dt.automation_engine.workflow_execution.id)` for the run
> count** — never bare `count()`. Same lesson as QEE: confirm an event is
> one-row-per-thing before counting it.

For workflows, count distinct executions and compare against the QEE figure:

```dql-template
fetch dt.system.events, from: -7d
| filter event.kind == "WORKFLOW_EVENT"
| filter event.provider == "AUTOMATION_ENGINE"
| filter event.type == "WORKFLOW_EXECUTION"
| filter in(dt.automation_engine.workflow.id, "<workflow-uuid-1>", "<workflow-uuid-2>")
| summarize
    workflow_runs = countDistinct(dt.automation_engine.workflow_execution.id),
    workflow_title = takeFirst(dt.automation_engine.workflow.title),
    by: {workflow_id = dt.automation_engine.workflow.id}
| sort workflow_runs desc
```

> - **Exclude editor test runs:** add `| filter dt.automation_engine.is_draft == false`
>   to count only production executions (drafts are runs from the workflow
>   editor).
> - **Explain a high run rate:** check
>   `dt.automation_engine.workflow_execution.trigger.type`
>   (`Schedule` = cron cadence, `Event` = event-driven, `Manual`, `Workflow` =
>   triggered by another workflow). A `Schedule` trigger firing every 30–60s is
>   the usual reason for thousands of runs/day.
> - **Hitting the cap:** `event.type == "WORKFLOW_THROTTLED"` rows mean the
>   workflow exceeded its executions-per-hour limit
>   (`dt.automation_engine.throttle.limit`) — a strong signal in a cost or
>   runaway-automation investigation.

> **Worked example (validated, 24h, one scheduled workflow):** 1,440 distinct
> runs (≈1/min) → 2,879 `WORKFLOW_EXECUTION` rows (≈2× — start + completion) →
> 2,867 DQL statements (≈2 per run) → 7,195 QEE events (≈5× runs — bucket
> fan-out). Reading the QEE `count()` as a run count overstates by 5×; reading
> the `WORKFLOW_EXECUTION` `count()` as a run count overstates by 2×. Derive any
> frequency **only** from `workflow_runs` (distinct executions) ÷ timespan. A
> large gap between any `count()` and the distinct-execution count is expected
> fan-out, not a spike.

## Step 4 — Per-Detector Scan & Name Resolution (ALERTING pool)

For ALERTING sources, parse `client.client_context` from QEE to get per-detector
scan volume, then resolve detector names from `ANALYZER_EXECUTION_EVENT` via
`join`.

**`dt.task.id` is the full encoded settings UID** (base64-encoded, e.g.,
`vu9U3hXa3q0AAAAB...vu9U3hXa3q0`) — not a plain UUID. This same encoded UID
appears in QEE `client.client_context` → `dt.task.id`, AEE `dt.task.id`, and
partially in QEE `client.source`.

```dql
fetch dt.system.events, from: -7d
| filter event.kind == "QUERY_EXECUTION_EVENT"
| filter query_pool == "ALERTING"
| parse client.client_context, "JSON:ctx"
| summarize qee_events = count(),
    dql_statements = countDistinct(query_id),
    total_scanned_gib = sum(scanned_bytes) / 1073741824,
    by: {task_id = ctx[`dt.task.id`], task_group = ctx[`dt.task.group`]}
| sort total_scanned_gib desc
| limit 20
| join [
    fetch dt.system.events, from: -7d
    | filter event.kind == "ANALYZER_EXECUTION_EVENT"
    | fieldsAdd task_id = dt.task.id, detector_name = dt.task.name
    | summarize detector_name = takeFirst(detector_name), by: {task_id}
  ], on: {task_id}, fields: {detector_name}, kind: leftOuter
```

> **Dotted JSON keys:** `ctx[\`dt.task.id\`]` — without backticks, DQL
> interprets dots as nested field access and fails silently.
>
> **`user.id` is NOT detector-specific.** All anomaly detectors share a service
> account. Use `dt.task.id` / `client.client_context` instead.

## Step 5 — Rank by Cost Weight

Apply normalization weights from [cost-estimations.md](cost-estimations.md) → [Cost Normalization Weights](cost-estimations.md#cost-normalization-weights).

## Best Practices

1. **Use BUE `client.source` for ALERTING attribution** — covers a subset of
   detector queries; use `client.client_context` parse on QEE for the full
   per-detector breakdown.
2. **`user.id` is never detector-specific** — all anomaly detectors share the
   same service account; use `dt.task.id` / `client.client_context` instead.
3. **Sample first, then extend to 30d** — verify field availability on a 7-day
   slice before running expensive 30-day queries.
4. **Dedup every BUE aggregation** — Use `| dedup {event.id, event.type}` for
   multi-type queries. See
   [Billing Event Deduplication](billing-capabilities.md#billing-event-deduplication).

## Investigating QEE↔BUE Mismatches

When QEE `scanned_bytes` significantly exceeds BUE `billed_bytes` for the same
source:

1. **Join on `query_id`** to identify which QEE records have no matching BUE
2. **Check for zero-rating** — certain queries may be zero-rated based on
   execution context (user, apps, queried data). These produce QEE
   records but no corresponding BUE. The gap is zero-rated usage, not a
   pipeline issue.
3. Only after ruling out zero-rating, investigate attribution coverage gaps
