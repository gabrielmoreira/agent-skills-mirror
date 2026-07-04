# Workflow Total Cost

Composite cost attribution for automation workflows. Workflows generate costs
across **three separate billing signals** — missing any one gives an incomplete
picture.

## Contents

- [Common Principles](#common-principles)
- [Three-Signal Checklist](#three-signal-checklist)
- [Cross-Event Field Reference](#cross-event-field-reference)
- [Step 1 — Query Scan Cost (QEE)](#step-1--query-scan-cost-qee)
- [Step 2 — AppEngine Function Cost (BUE)](#step-2--appengine-function-cost-bue)
- [Step 3 — Automation Workflow BUE Cost](#step-3--automation-workflow-bue-cost)
- [Per-Workflow Deep Dive](#per-workflow-deep-dive)
- [How Often Did the Workflow Run](#how-often-did-the-workflow-run)
- [Owner Identification](#owner-identification)
- [Best Practices](#best-practices)

## Common Principles

1. **BUE is billable truth, QEE is diagnostic** — BUE Query events reflect
   actual billed scan volumes; QEE provides per-query execution details
   (`client.client_context`, query text, duration). Always start cost
   investigations with BUE, then drill into QEE for attribution detail.

2. **Sample first** — Before building any attribution query, run
   `| limit 3` (without `| fields`) on the target event type to discover
   available fields. When a field returns no results, sample raw events first.

3. **Dedup billing events** — Use `| dedup event.id` for single-type queries
   (all templates below filter to one `event.type`). See
   [Billing Event Deduplication](billing-capabilities.md#billing-event-deduplication).

4. **Rolling windows are acceptable here** — Investigation queries use
   `from: -7d` or `from: -30d` for diagnostic analysis. For billing totals
   that must match the Account Management Portal, use explicit UTC midnight
   boundaries per [billing-capabilities.md § Billing Timeframe Boundaries](billing-capabilities.md#billing-timeframe-boundaries).

## Three-Signal Checklist

| # | Signal | BUE `event.type` | What it measures |
|---|--------|------------------|-----------------|
| 1 | Query Execution | `Events - Query`, `Log Management & Analytics - Query`, `Traces - Query`, `Files - Query` | DQL scans run inside workflow scripts |
| 2 | AppEngine Functions | `AppEngine Functions - Small` | JS/Python function invocations |
| 3 | Automation Workflow | `Automation Workflow` | Workflow execution time (workflow-hours) |

Always check all three before concluding what a workflow costs.

## Cross-Event Field Reference

Field names differ across event kinds **and** across BUE event types. BUE Query
events lack workflow attribution fields — use QEE AUTOMATION pool instead.

| Concept | QEE (AUTOMATION pool) | `WORKFLOW_EVENT` | BUE `Automation Workflow` | BUE `AppEngine Functions` | BUE Query types |
|---------|----------------------|------------------|--------------------------|--------------------------|----------------|
| Workflow ID | `client.workflow_context` | `dt.automation_engine.workflow.id` | `workflow.id` | `workflow.id` | ❌ not available |
| Workflow name | — | `dt.automation_engine.workflow.title` | `workflow.title` | — | ❌ not available |
| Function/action | `client.function_context` | `dt.automation_engine.action.name` | — | `function.id` | `client.function_context` |
| User ID | `user.id` | `dt.automation_engine.workflow_execution.actor` | `workflow.actor` | `user.id` | `user.id` |
| Trigger type | — | `dt.automation_engine.workflow_execution.trigger.type` | `workflow.trigger_type` | — | — |

> **Critical:** BUE Query events (`Events - Query`, etc.) have NO `workflow.id`
> or `client.workflow_context` field. To attribute query scan costs to a workflow,
> use QEE AUTOMATION pool with `client.workflow_context`.
>
> **Tip:** When a field returns no results, sample raw events first:
> `| limit 3` (without `fields`) to see all available fields on the event.

## Step 1 — Query Scan Cost (QEE)

BUE Query events lack workflow attribution fields. Use QEE AUTOMATION pool
(`client.workflow_context`) to attribute query scan volume to a workflow:

```dql-template
fetch dt.system.events, from: -30d
| filter event.kind == "QUERY_EXECUTION_EVENT"
| filter query_pool == "AUTOMATION"
| filter client.workflow_context == "<workflow-uuid>"
| summarize total_scanned_gib = sum(scanned_bytes) / 1073741824,
    qee_events = count(),
    dql_statements = countDistinct(query_id),
    by: {table}
| sort total_scanned_gib desc
```

> **Note:** QEE `scanned_bytes` is diagnostic, not billable. For billable totals,
> sum BUE Query events by `client.source` pattern matching (see
> [query-cost-attribution.md](query-cost-attribution.md)), then correlate with
> QEE for per-workflow breakdown.

> **⛔ QEE count ≠ workflow run count.** `count()` on QEE counts bucket-touches
> (one row per bucket per DQL statement), `countDistinct(query_id)` counts DQL
> statements. **Neither is the number of times the workflow ran** — one run
> fires multiple DQL statements, each touching multiple buckets. To get actual
> run count and frequency, use the
> [WORKFLOW_EXECUTION query](#how-often-did-the-workflow-run) below. Never write
> "ran N times" or compute a per-second/per-minute rate from a QEE count.

## Step 2 — AppEngine Function Cost (BUE)

```dql-template
fetch dt.system.events, from: -30d
| filter event.kind == "BILLING_USAGE_EVENT"
| filter event.type == "AppEngine Functions - Small"
| dedup event.id
| filter workflow.id == "<workflow-uuid>"
| summarize total_invocations = sum(billed_invocations)
```

## Step 3 — Automation Workflow BUE Cost

Workflow-hours = distinct `workflow.id` per hour. Bin by hour first, then sum:

```dql-template
fetch dt.system.events, from: -30d
| filter event.kind == "BILLING_USAGE_EVENT"
| filter event.type == "Automation Workflow"
| dedup event.id
| filter workflow.id == "<workflow-uuid>"
| fieldsAdd hour = bin(timestamp, 1h)
| summarize hourly_wf = countDistinct(workflow.id), by: {hour}
| summarize total_workflow_hours = sum(hourly_wf)
```

> **Note:** Each distinct `workflow.id` appearing within a given hour contributes
> 1 workflow-hour. The standard `coalesce()` pattern cannot capture this; query
> it separately.

> **Output rule:** Present `total_invocations` and `total_workflow_hours` in
> native units. Apply **SKILL.md § Cost Ranking Rules** for any cross-capability
> cost comparison — do not compute or display dollar estimates from these values.

## Per-Workflow Deep Dive

First, identify top workflows by query scan volume using QEE AUTOMATION pool
(BUE Query events lack workflow attribution):

```dql
fetch dt.system.events, from: -30d
| filter event.kind == "QUERY_EXECUTION_EVENT"
| filter query_pool == "AUTOMATION"
| filter isNotNull(client.workflow_context)
| summarize total_scanned_gib = sum(scanned_bytes) / 1073741824,
    qee_events = count(),
    dql_statements = countDistinct(query_id),
    by: {client.workflow_context}
| sort total_scanned_gib desc
| limit 20
```

> Rank workflows by `total_scanned_gib`, not by `qee_events`. A workflow whose
> queries touch many buckets will have a large `qee_events` count without
> necessarily running often or scanning the most — see
> [How Often Did the Workflow Run](#how-often-did-the-workflow-run).

Then resolve the workflow name from `WORKFLOW_EVENT`:

```dql-template
fetch dt.system.events, from: -30d
| filter event.kind == "WORKFLOW_EVENT"
| filter dt.automation_engine.workflow.id == "<uuid from above>"
| fields dt.automation_engine.workflow.id, dt.automation_engine.workflow.title
| limit 1
```

> **Deleted workflows:** Workflows that have been deleted may still appear in
> QEE events for queries that were already in-flight. If a workflow ID doesn't
> resolve via `WORKFLOW_EVENT`, BUE `Automation Workflow`, or `dtctl get workflow`,
> it was likely deleted. Check whether it still appears in recent billing events
> or only in historical data.

## How Often Did the Workflow Run

**The number of times a workflow ran lives on `WORKFLOW_EVENT`** with
`event.type == "WORKFLOW_EXECUTION"` — but count it with
`countDistinct(dt.automation_engine.workflow_execution.id)`, **not** bare
`count()`.

> ### ⛔ Two layers of `count()` fan-out
>
> 1. **QEE** (`QUERY_EXECUTION_EVENT`) `count()` = bucket-touches (one row per
>    bucket per DQL statement); `countDistinct(query_id)` = DQL statements.
>    Neither is a run count.
> 2. **`WORKFLOW_EXECUTION` `count()` is also not a run count** — it is a
>    **state-change** event: one row per `dt.automation_engine.state` transition
>    (`RUNNING` with `duration` ≈ `0,00 ns`, then a terminal
>    `SUCCESS`/`ERROR`/`CANCELLED` row with real `duration` + end timestamp),
>    **both sharing the same** `dt.automation_engine.workflow_execution.id`. A
>    completed run is 2 rows, an in-flight run is 1, so the factor drifts around
>    2×. Use `countDistinct(dt.automation_engine.workflow_execution.id)`.
>
> Validated on a live tenant for one scheduled workflow (24h): **1,440 distinct
> runs** (≈1/min) → 2,879 `WORKFLOW_EXECUTION` rows (≈2×) → 2,867 DQL statements
> (≈2 per run) → 7,195 QEE events (≈5×). Reading the QEE `count()` as runs
> overstates 5×; reading the `WORKFLOW_EXECUTION` `count()` as runs overstates
> 2×. Frequency comes **only** from distinct executions ÷ timespan.

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

> - **Exclude editor test runs:** add `| filter dt.automation_engine.is_draft == false`.
> - **Why so often:** `dt.automation_engine.workflow_execution.trigger.type`
>   (`Schedule`/`Event`/`Manual`/`Workflow`) — a `Schedule` trigger is the usual
>   cause of thousands of runs/day.
> - **Hit the cap:** `event.type == "WORKFLOW_THROTTLED"` rows mean the workflow
>   exceeded its per-hour execution limit (`dt.automation_engine.throttle.limit`).
> - **Reporting both signals:** when QEE or row volume looks alarming, anchor it
>   with the distinct-execution count, e.g. "≈1,440 runs/day (≈1/min), generating
>   ≈7.2K QEE bucket-events/day (≈5 per run)". A large gap between any `count()`
>   and the distinct-execution count is expected fan-out, not a spike.

## Owner Identification

Use this priority order to identify who owns an expensive workflow:

| Priority | Field | Event Kind / BUE Type | Notes |
|----------|-------|----------------------|-------|
| 1 | `workflow.owner` | BUE `Automation Workflow` | Most reliable — set at creation |
| 2 | `dt.automation_engine.workflow_execution.actor` | `WORKFLOW_EVENT` | UUID, not email — resolve via user API |
| 3 | `user.email` | BUE Query types | Available when query ran under a user context |
| 4 | `user.id` | BUE / QEE | UUID — resolve via user API if needed |

Quick owner lookup (uses BUE `Automation Workflow` which has `workflow.owner`):

```dql-template
fetch dt.system.events, from: -7d
| filter event.kind == "BILLING_USAGE_EVENT"
| filter event.type == "Automation Workflow"
| dedup event.id
| filter workflow.id == "<workflow-uuid>"
| filter isNotNull(workflow.owner)
| fields workflow.id, workflow.title, workflow.owner
| limit 1
```

## Best Practices

1. **Always check all three billing signals** for workflows — a query scan spike
   may be just one of multiple cost contributors.
2. **Sample first, then extend to 30d** — verify field availability on a 7-day
   slice before running expensive 30-day queries.
3. **Dedup every BUE aggregation** — `| dedup event.id` is safe here
   (single-type queries). See
   [Billing Event Deduplication](billing-capabilities.md#billing-event-deduplication).
