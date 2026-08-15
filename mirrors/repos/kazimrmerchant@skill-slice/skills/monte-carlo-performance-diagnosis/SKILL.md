---
name: monte-carlo-performance-diagnosis
description: "Diagnoses data-pipeline slowness with Monte Carlo observability across Airflow, dbt, Databricks, and warehouse engines (slow jobs, costly queries, compute regressions). Use when the user asks why a pipeline is slow or what burns compute. Not for data-quality incidents (monte-carlo-analyze-root-cause), storage-cost analysis, or creating monitors."
version: 1.0.1
risk: unknown
source: https://github.com/monte-carlo-data/mc-agent-toolkit/tree/main/skills/performance-diagnosis
source_repo: monte-carlo-data/mc-agent-toolkit
source_type: community
date_added: 2026-07-01
license: Apache-2.0
license_source: https://github.com/monte-carlo-data/mc-agent-toolkit/blob/main/LICENSE
---

# Monte Carlo Performance Diagnosis Skill

Diagnose data pipeline performance issues using Monte Carlo's cross-platform observability data. This skill works across Airflow, dbt, Databricks, and warehouse query engines to find bottlenecks, detect regressions, and identify root causes using a tiered investigation approach: discover problems → bridge to affected tables → drill into root causes.

> **Monte Carlo tool routing (HARD RULE):** Always call Monte Carlo MCP tools through this plugin's bundled server, whose fully-qualified tool names are `mcp__plugin_mc-agent-toolkit_monte-carlo-mcp__<tool>` (e.g. `mcp__plugin_mc-agent-toolkit_monte-carlo-mcp__get_alerts`). Bare tool names used in this skill (`get_alerts`, `search`, `get_table`, …) refer to that bundled server. If the session also has a separately-configured `monte-carlo-mcp` server, do **not** route to it — it may point at a different endpoint or credentials.

Tiered methodology lives **in this SKILL.md** (Steps 1–4). Use the Read tool on this file (not MCP resources).

## When to Use

Activate when the user:

- Asks about slow pipelines, jobs, or queries
- Wants to find expensive or costly queries
- Mentions performance regressions or degradation
- Asks "why is this pipeline slow?" or "what's using the most compute?"
- Wants to compare performance over time or find bottleneck tasks
- Asks about failed or futile query patterns

**Do NOT activate** when the user is:

- Investigating data quality issues → use the `prevent` skill
- Looking at storage costs → use the `storage-cost-analysis` skill
- Creating monitors → use the `monitoring-advisor` skill
- Just querying data or exploring table contents

## Prerequisites

The following MCP tools must be available via the bundled Monte Carlo MCP server (`mcp__plugin_mc-agent-toolkit_monte-carlo-mcp__*`):

**Discovery tools (Tier 1):**

| Tool | Purpose |
|------|---------|
| `get_jobs_performance` | Find slow/failing jobs across Airflow, dbt, Databricks |
| `get_top_slow_queries` | Find slowest query groups by total runtime |

**Bridge tool:**

| Tool | Purpose |
|------|---------|
| `get_tables_for_job` | Convert job MCONs to table MCONs |

**Diagnosis tools (Tier 2):**

| Tool | Purpose |
|------|---------|
| `get_tasks_performance` | Drill into a job's individual tasks |
| `get_change_timeline` | Unified timeline of query changes, volume shifts, Airflow/dbt failures |
| `get_query_rca` | Root cause analysis for failed/futile queries |
| `get_query_latency_distribution` | Latency trend over time |
| `get_asset_lineage` | Trace upstream/downstream impact |

**Supporting tools:**

| Tool | Purpose |
|------|---------|
| `get_warehouses` | List available warehouses |

## Procedure

### Step 1 — Identify the scope

Determine what the user wants to investigate:

- **Specific job/pipeline** — User mentions a job name or pipeline.
- **Specific table** — User mentions a table that's slow to update.
- **General discovery** — User wants to find what's slow.

Call `get_warehouses` to list available warehouses. Match the user's context to a warehouse.

> **Tier 1 start:** job/pipeline named → `get_jobs_performance`; expensive/slow queries → `get_top_slow_queries`; hour-level regression → `get_query_latency_distribution` with `bucket="1h"`; otherwise run both discovery tools, then present top findings before drilling.

### Step 2 — Tier 1: Discovery

If you don't have specific MCONs to investigate, start with discovery:

1. **Find slow jobs** — Call `get_jobs_performance` with optional `integration_type` filter (`AIRFLOW`, `DATABRICKS`, `DBT`) if the user specifies a platform.
   - Results include: job name, average duration, trend (7-day), run count, failure rate.
   - Look for: high `avgDuration`, negative `runDurationTrend7d`, high failure rates.

2. **Find expensive queries** — Call `get_top_slow_queries` with optional `warehouse_id` and `query_type` (`"read"` for SELECTs, `"write"` for INSERT/CREATE/MERGE).
   - Results include: query hash, total runtime, average runtime, run count.
   - Look for: queries with high total runtime or high individual execution time.

Present the top findings to the user before drilling deeper. A typical investigation needs only **3–7 tool calls**.

**If both discovery tools return no results:** Tell the user no performance issues were found in the current time window. Suggest broadening the scope (different warehouse, longer time range, or a different platform filter).

### Step 3 — Bridge: Job to Tables

After Tier 1 identifies problematic jobs, convert to table MCONs:

Call `get_tables_for_job(job_mcon=..., integration_type=...)` using the `integration_type` from the job performance results.

This gives you the table MCONs needed for Tier 2 investigation.

### Step 4 — Tier 2: Diagnosis

Drill into root causes using the MCONs from discovery or the bridge:

1. **Task bottleneck** — Call `get_tasks_performance` to find which specific task in a job is the bottleneck.

2. **What changed?** — Call `get_change_timeline`. This is your most powerful tool. It returns a unified timeline of:
   - Query text changes (schema modifications, new JOINs, filter changes)
   - Volume shifts (row count spikes/drops)
   - Airflow task failures
   - dbt model failures

   All in one call. Look for correlations: "query changed on day X, runtime doubled on day X+1."

3. **Why are queries failing?** — Call `get_query_rca` to get root cause analysis:
   - **Failed** queries: errors, timeouts, permission issues.
   - **Futile** queries: queries that run but produce no useful output.
   - Patterns are pre-computed — the tool groups failures by cause.

4. **Is latency degrading?** — Call `get_query_latency_distribution` to see the trend:
   - Compare p50 vs p95 — if p95 >> p50 (>5×), the problem is outlier queries.
   - Look for step-changes in latency (sudden increase = regression).
   - **For step-change / regression-time-localization use cases, pass `bucket="1h"`.** The default downsamples to daily on windows ≥ 3 days, which hides hour-level steps.

5. **Trace impact** — Call `get_asset_lineage` with `direction="DOWNSTREAM"` to see what's affected by a slow table, or `direction="UPSTREAM"` to find what feeds it.

### Step 5 — Present findings

Structure your response as:

1. **Problem summary** — What's slow and by how much (with exact numbers from tools).
2. **Root cause** — What changed or what's causing the issue.
3. **Impact** — What downstream systems are affected.
4. **Recommendations** — Specific actions to fix the issue.

## Hard Rules

These rules are non-negotiable and must be followed on every invocation:

1. **Quote tool numbers exactly.** If a tool returns "1282 runs, avg 22.5s", say exactly that. Never round, estimate, or fabricate numbers.
2. **Always compare to baselines.** Use 7-day trend data (`runDurationTrend7d`) to distinguish regressions from normal variance. Flag if trend data has less than 0.1 confidence.
3. **Stop when you have a root cause.** 3–7 tool calls is typical. More than 10 means you're over-investigating.
4. **Read vs write queries — never mix them.** When the user asks about "reads" or "read queries", filter with `query_type="read"`. When they ask about "writes", use `query_type="write"`.
5. **Never expose MCONs, UUIDs, or internal identifiers** to the user. Use human-readable names.
6. **Cross-platform awareness.** This skill works across Airflow, dbt, and Databricks. Note which platform each finding comes from.
7. **Tool routing.** Always use the bundled server prefix `mcp__plugin_mc-agent-toolkit_monte-carlo-mcp__<tool>`. Never route to a separately-configured `monte-carlo-mcp` server.

## Pitfalls

- **Default latency bucketing hides hour-level steps.** `get_query_latency_distribution` downsamples to daily on windows ≥ 3 days. If you're hunting for a regression that happened at a specific hour, always pass `bucket="1h"`.
- **Over-investigation.** Calling more than 10 tools usually means you haven't formed a hypothesis. Stop, summarize what you know, and present findings.
- **Mixing read and write query types.** Passing no `query_type` or mixing them produces misleading "top slow" results because write queries (INSERT/MERGE) have fundamentally different runtime profiles than reads.
- **Ignoring trend confidence.** A negative `runDurationTrend7d` with confidence < 0.1 is noise, not a regression. Always check confidence before flagging.
- **Exposing internal IDs.** MCONs and UUIDs are implementation details. Users should see job names, table names, and query descriptions — never raw identifiers.
- **Both discovery tools return empty.** This doesn't mean "no data" — it means no performance issues in the current window. Suggest broadening scope before concluding nothing is wrong.
- **Assuming platform homogeneity.** A single investigation may span Airflow orchestration, dbt models, and Databricks compute. Always track which platform each finding originates from.

## Verification

After completing the investigation, verify your findings are actionable:

1. **Numbers check** — Every metric in your summary (durations, run counts, failure rates, latency percentiles) must trace back to a specific tool call's output. No fabricated or rounded values.
2. **Root cause linkage** — Your stated root cause must reference a specific event from `get_change_timeline` or a specific pattern from `get_query_rca`. If you can't point to one, you don't have a root cause yet.
3. **Impact trace** — If you claim downstream impact, it must come from `get_asset_lineage` with `direction="DOWNSTREAM"`. If you claim upstream dependency, it must come from `direction="UPSTREAM"`.
4. **Baseline comparison** — Every "slow" or "degraded" claim must include the baseline (7-day trend or p50 vs p95 comparison). A single data point is not a regression.
5. **Tool call budget** — Confirm you used ≤ 10 tool calls. If you exceeded this, prune the investigation and present what you have.

## Related Skills

- **`prevent`** — Data quality issue investigation
- **`storage-cost-analysis`** — Storage cost analysis
- **`monitoring-advisor`** — Monitor creation and alerting configuration
