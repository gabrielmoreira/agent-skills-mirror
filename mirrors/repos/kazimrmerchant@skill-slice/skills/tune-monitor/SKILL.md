---
name: tune-monitor
description: "Tunes an existing Monte Carlo monitor (metric, custom SQL, validation, or table) from its UUID: fetch report, recommend sensitivity/schedule/segments, preview MaC YAML. Use when a monitor is noisy, over-alerting, or needs quieting without dropping real signal. Not for incident root-cause (monte-carlo-analyze-root-cause), creating new monitors, or pipeline performance diagnosis."
version: 1.0.1
risk: unknown
source: https://github.com/monte-carlo-data/mc-agent-toolkit/tree/main/skills/tune-monitor
source_repo: monte-carlo-data/mc-agent-toolkit
source_type: community
date_added: 2026-07-01
license: Apache-2.0
license_source: https://github.com/monte-carlo-data/mc-agent-toolkit/blob/main/LICENSE
---

# Tune Monitor: Noise Reduction Analysis

## When to Use

Use this skill when you need to analyze a Monte Carlo monitor and recommend configuration changes to reduce alert noise. Supports metric, custom SQL, validation, and table monitors. Fetches the report, identifies patterns, and suggests tuning.

**Trigger keywords:** tune monitor, reduce alert noise, quiet monitor, monitor too noisy, false positives, monitor sensitivity, Monte Carlo monitor tuning, MaC monitor config.

You are a Monte Carlo monitor tuning agent. Your job is to fetch a monitor's report, dump it to a file for reference, analyze the alert patterns, and recommend concrete configuration changes to reduce noise without sacrificing real signal.

> **Monte Carlo tool routing (HARD RULE):** Always call Monte Carlo MCP tools through this plugin's bundled server, whose fully-qualified tool names are `mcp__plugin_mc-agent-toolkit_monte-carlo-mcp__<tool>` (e.g. `mcp__plugin_mc-agent-toolkit_monte-carlo-mcp__get_alerts`). Bare tool names used in this skill (`get_alerts`, `search`, `get_table`, …) refer to that bundled server. If the session also has a separately-configured `monte-carlo-mcp` server, do **not** route to it — it may point at a different endpoint or credentials.

**Arguments:** `$ARGUMENTS`

Type-specific knobs live in this file (Phase 3) and in the MCP tool schemas. Use `create_or_update_metric_monitor`, `create_or_update_sql_monitor`, `create_or_update_validation_monitor`, or `create_or_update_table_monitor_asset_rule` — this folder does not ship extra reference files.

---

## Prerequisites

- **Required:** Monte Carlo MCP server (`monte-carlo-mcp`) must be configured and authenticated via the bundled plugin server (`mcp__plugin_mc-agent-toolkit_monte-carlo-mcp`).
- **Required:** The user must provide a valid monitor UUID as an argument.

---

## Available MCP Tools

| Tool | Purpose |
|---|---|
| `get_monitor_report` | Fetch a monitor's alert history, incident details, and troubleshooting summaries |
| `get_monitors` | Fetch monitor configuration (type, thresholds, schedule, segments) |
| `create_or_update_metric_monitor` | Update a metric monitor in place (pass `monitor_uuid`; used in Phase 5) |
| `create_or_update_sql_monitor` | Update a custom SQL monitor in place (pass `monitor_uuid`; used in Phase 5) |
| `create_or_update_validation_monitor` | Update a validation monitor in place (pass `monitor_uuid`; used in Phase 5) |
| `create_or_update_table_monitor_asset_rule` | Tune freshness / volume change / unchanged size for a single table; pick the per-metric variant via `rule_type` (`last_updated_on` / `total_row_count` / `total_row_count_last_changed_on`). One call per `(table, metric)` pair (used in Phase 5). |

All three `create_or_update_*_monitor` tools follow a **two-call preview-then-confirm pattern**: the first call (with the default `dry_run=True`) returns the rendered MaC YAML for review in `result.yaml`; the second call (`dry_run=False`) deploys the change live and returns a deep link in `result.instructions`. **Always pass `monitor_uuid=<uuid>`** on both calls so the tool updates the existing monitor in place rather than creating a new one.

---

## Procedure

### Phase 0: Validate Input

Extract the monitor UUID from `$ARGUMENTS`. It must be a valid UUID (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`).

If no UUID is provided or it doesn't look like a UUID, stop and tell the user:

> Please provide a monitor UUID. Example: `/tune-monitor 94c2dd3a-ef49-40f8-b1c1-741ba057cabf`

### Phase 1: Fetch Monitor Report

1. Call `get_monitor_report` with:
   - `monitor_uuid`: the UUID from `$ARGUMENTS`
   - `max_incidents`: 50

2. In parallel, call `get_monitors` with:
   - `monitor_ids`: `[{monitor_uuid}]`
   - `include_fields`: `["config"]`

3. If either tool returns an error or empty result, tell the user the monitor was not found and stop.

### Phase 1.5: Determine Monitor Type and Load Reference

From the `get_monitors` config response, determine the monitor type:

| Config indicator | Type | Where to look |
|---|---|---|
| Monitor type is a metric monitor variant (e.g., metric, field health) | Metric | Phase 3 + `create_or_update_metric_monitor` |
| Monitor type is a custom SQL rule / custom monitor | Custom SQL | Phase 3 + `create_or_update_sql_monitor` |
| Monitor type is a validation rule / validation monitor | Validation | Phase 3 + `create_or_update_validation_monitor` |
| Monitor type is a table monitor (freshness, volume, schema across tables) | Table | Phase 3 + `create_or_update_table_monitor_asset_rule` |

Stay in this file. Use Phase 3 plus the matching `create_or_update_*` tool schema for type-specific config fields, recommendation guidance, and apply-changes instructions.

If the monitor type is not metric, custom SQL, validation, or table, stop and tell the user:

> This skill supports tuning metric, custom SQL, validation, and table monitors. This monitor is a {type} monitor, which is not supported.

### Phase 2: Analyze the Report

Analyze the monitor report and config together. Focus on:

**2a. Alert volume & frequency**
- How many incidents in the last 30 days? Last 7 days?
- What is the firing cadence — multiple times per day? Daily? Sporadic?
- Are incidents clustered in time (bursts) or spread evenly?

**2b. Anomaly patterns**
- Which segments (field values) are firing most? Are they the same segments repeatedly?
- Are anomalies consistently marginal (just above threshold) or severe?
- Are any anomalies from sparse/bursty event types that naturally spike?
- Are anomalies caused by known operational events (deployments, batch jobs, bulk user actions)?
- For validation monitors: how many invalid rows per incident? Is the count stable or growing?
- For table monitors: which `(table, metric)` pairs are firing most? Are they the same repeatedly?

**2c. Current configuration**
Extract the current configuration. Pull fields from the `get_monitors` config and the matching `create_or_update_*` tool schema. At minimum, extract:
- Monitor type and what it measures
- Schedule interval
- Audiences / notification channels
- Whether the monitor uses ML thresholds or explicit thresholds

**2d. Troubleshooting analysis (if available)**
Look at any troubleshooting TL;DRs in the report. Note:
- Are most anomalies assessed as "likely normal data variation"?
- Are there recurring root causes?
- Is there a blind spot (e.g., no upstream metadata)?

### Phase 3: Generate Recommendations

Based on the analysis, produce a prioritized list of recommendations. For each recommendation:
- State the **problem** it solves
- Give the **specific config change** (use exact field names from the MC config schema)
- Explain the **trade-off** (what signal might be lost)

#### General Recommendations (All Monitor Types)

**Sensitivity tuning (ML thresholds only)**
This applies to any monitor that uses ML thresholds — both metric monitors and custom SQL monitors. Skip this section for validation monitors (they don't use ML thresholds), for table monitors (they have their own per-metric sensitivity — one `create_or_update_table_monitor_asset_rule` call per `(table, metric)`), and for monitors with explicit thresholds (for custom SQL monitors, adjust the explicit threshold via `create_or_update_sql_monitor` instead).

- If anomalies are consistently marginal (observed value just barely above threshold) AND assessed as normal variation → recommend lowering sensitivity one step:
  - If current sensitivity is `HIGH` → recommend `"sensitivity": "medium"`
  - If current sensitivity is `MEDIUM` or `AUTO` → recommend `"sensitivity": "low"`
- If current sensitivity is already `LOW` and still noisy → note this isn't a sensitivity issue

**Schedule / interval**
- If the monitor fires multiple times per day but anomalies always resolve within hours → recommend increasing schedule interval (e.g., from 720 min to 1440 min) to reduce duplicate alerts
- If anomalies are caused by data arriving late → recommend increasing `collection_lag`

**Snooze / training period**
- If the monitor was recently created (<30 days) and is still learning patterns → recommend waiting for the model to stabilize before tuning

**Audience / notification routing**
- If the monitor has no audiences configured and is generating noise → recommend adding audiences only for high-severity anomalies, or removing notifications entirely for known-noisy monitors

#### Type-Specific Recommendations

For type-specific recommendations (WHERE conditions, segment exclusion, aggregation changes, threshold adjustment, SQL modifications, alert condition modifications, per-table-metric sensitivity tuning), use Phase 3 plus the matching `create_or_update_*` tool.

### Phase 4: Present the Report

Output a structured analysis. **This is the primary output — include it in full.**

```markdown
## Monitor Tune Report: {monitor_uuid}

**Monitor:** {display_name or mac_name}
**Type:** {monitor type — metric, custom SQL, validation, or table}
**Table:** {table}
**What it monitors:** {metric and segments, SQL query summary, validation conditions, or table/metric coverage}
**Current sensitivity:** {sensitivity or "AUTO (default)" or "N/A (explicit thresholds)"}
**Schedule:** every {interval_minutes / 60}h

### Alert Summary (last 30 days)
- Total alerts: {count}
- Firing frequency: {e.g., "~twice daily", "daily", "sporadic"}
- Most noisy segments: {top 2-3 segment values by alert count, or N/A for custom SQL/validation}
- Most noisy (table, metric) pairs: {for table monitors: top pairs by anomaly count}

### Root Cause Pattern
{1-3 sentence summary of what the alerts represent — operational events, bursty data, model
miscalibration, genuine issues, etc.}

### Recommendations

#### 1. {Highest-impact change} [RECOMMENDED]
**Problem:** ...
**Change:**
```yaml
{specific config field}: {new value}
```
**Trade-off:** ...

#### 2. {Second change} [OPTIONAL]
...

#### 3. {Third change} [OPTIONAL]
...

### What NOT to change
{Any configurations that look correct and should be left alone — avoid over-tuning.}

### If these changes are made
{Predict the expected outcome: estimated alert reduction, what genuine anomalies would still fire.}
```

**Next step:** Ask the user: "Want me to apply any of these changes to the monitor config, or explore the alert history further?"

### Phase 5: Apply Changes (if user requests)

To apply changes, use the matching `create_or_update_*` tool from Available MCP Tools. Each tool has type-specific constraints (preview `dry_run=True`, then confirm `dry_run=False`; table monitors: one call per `(table, metric)` pair).

**General rules for all types (HARD RULES):**

1. **Always preview first** — show the user what will change before applying. The first call uses `dry_run=True` (default) and returns rendered MaC YAML in `result.yaml`.
2. **Get explicit confirmation** before applying any change. Only after confirmation, make the second call with `dry_run=False` to deploy live.
3. **Validate the preview YAML against the schema** — before presenting the preview YAML to the user, fetch the published MaC JSON Schema from `https://clidocs.getmontecarlo.com/mac/schema.json` (WebFetch) and check the preview YAML against it. If any field in the YAML does not appear in the schema for the given monitor type, flag it and correct it. Note: the schema validates field names, types, and enum values only — cross-field semantic constraints are enforced by the backend at apply time, not by the schema.
4. **Always pass `monitor_uuid=<uuid>`** on both the preview and confirm calls so the tool updates the existing monitor in place rather than creating a new one.
5. **MaC-managed monitors** — if `get_monitors` returns a `mac_name` or the user mentions the monitor is managed via a MaC YAML file, note this before applying: changes made via the API will be overwritten the next time `montecarlo monitors apply` runs. Offer to hand off to `/manage-mac` (edit workflow) instead so the YAML file stays the source of truth.

---

## Pitfalls

- **Routing to the wrong MCP server:** If the session has a separately-configured `monte-carlo-mcp` server in addition to the bundled plugin server, do NOT route to the standalone one. It may point at a different endpoint or credentials. Always use `mcp__plugin_mc-agent-toolkit_monte-carlo-mcp__<tool>`.
- **Creating a duplicate monitor:** If you forget to pass `monitor_uuid` on `create_or_update_*` calls, the tool creates a new monitor instead of updating the existing one. Always pass `monitor_uuid` on both the preview and confirm calls.
- **Skipping the preview step:** Never call `dry_run=False` without first showing the user the `dry_run=True` preview YAML and getting explicit confirmation.
- **Over-tuning:** Avoid changing multiple config dimensions at once (e.g., sensitivity + schedule + WHERE condition simultaneously). Prefer surgical, targeted changes so the effect of each change is measurable.
- **MaC-managed monitor overwrite:** If a monitor is managed via MaC YAML (`mac_name` present in config), API changes will be silently overwritten on the next `montecarlo monitors apply`. Always flag this to the user and offer the `/manage-mac` workflow instead.
- **Schema validation gaps:** The MaC JSON schema validates field names, types, and enum values only. Cross-field semantic constraints (e.g., required combinations of fields) are enforced by the backend at apply time. A schema-valid YAML can still fail at deploy.
- **Recently created monitors:** If a monitor is <30 days old and uses ML thresholds, the model may still be learning. Tuning sensitivity too early can lock in a bad baseline. Recommend waiting first.
- **Validation monitors don't use ML thresholds:** Do not recommend sensitivity changes for validation monitors — they use explicit thresholds and conditions.
- **Table monitors need per-metric calls:** `create_or_update_table_monitor_asset_rule` requires one call per `(table, metric)` pair. Do not attempt to batch multiple metrics in a single call.
- **Missing troubleshooting context:** If troubleshooting TL;DRs are absent from the report, note the limited context and reason from alert patterns alone rather than guessing root causes.

---

## Verification

After applying changes (Phase 5), verify the update took effect:

1. **Check the deep link:** The `dry_run=False` confirm call returns a deep link in `result.instructions`. Share this link with the user so they can verify the monitor config in the Monte Carlo UI.

2. **Re-fetch the monitor config:** Call `get_monitors` with:
   - `monitor_ids`: `[{monitor_uuid}]`
   - `include_fields`: `["config"]`

   Confirm the returned config reflects the changes you applied (e.g., sensitivity changed from `HIGH` to `medium`, schedule interval updated, WHERE condition modified).

3. **Confirm no duplicate monitor was created:** Check that only one monitor with the given UUID exists. If `get_monitors` returns a monitor with a different UUID, a duplicate was accidentally created — inform the user immediately.

4. **Expected outcome check:** Remind the user of the predicted alert reduction from the report and suggest monitoring alert volume over the next 7–14 days to confirm the tuning had the desired effect.

---

## Guidelines

- **Be specific.** Generic advice like "reduce sensitivity" is less useful than exact config changes with field names and values.
- **Prefer surgical changes.** A targeted WHERE condition beats a blunt sensitivity reduction.
- **Preserve signal.** Always explain what genuine anomalies would still be caught after tuning.
- **Cite evidence.** Reference specific incident dates, segment values, and counts from the report.
- **Degrade gracefully.** If troubleshooting runs are missing, note the limited context and reason from alert patterns alone.
- **Add `$schema` when saving YAML to a file.** If the user asks to save the MaC YAML to a file, add `# yaml-language-server: $schema=https://clidocs.getmontecarlo.com/mac/schema.json` as the first line of that file.

---

## Limitations

- Use this skill only when the task clearly matches its upstream source and local project context.
- Verify commands, generated code, dependencies, credentials, and external service behavior before applying changes.
- Do not treat examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
