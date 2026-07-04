# Metrics Ingest Cost Optimization

Actionable strategies to reduce Metrics — Ingest & Process costs. Metrics
ingest is typically the leading cost driver among the three metrics billing
capabilities (Ingest & Process, Retain, Query), because retention is included
at no cost for the first 15 months and queries are included at no cost.

Based on [Dynatrace docs: Best practices for optimizing metrics cost](https://docs.dynatrace.com/docs/analyze-explore-automate/metrics/best-practices-metrics).

Use this reference **after** identifying metrics ingest as a top cost driver
via [cost-estimations.md](cost-estimations.md) or
[entity-cost-drilldown.md](entity-cost-drilldown.md).

## Contents

- [Core Concepts](#core-concepts)
- [Billable vs Non-Billable Metrics](#billable-vs-non-billable-metrics)
- [Analyze Metrics Ingest](#analyze-metrics-ingest)
  - [Step 1 — Break Down by Source, Cost Center, and Cost Product](#step-1--break-down-by-source-cost-center-and-cost-product)
  - [Step 2 — Drill Down into Metric Keys](#step-2--drill-down-into-metric-keys)
- [OTel Collector Self-Monitoring Metrics](#otel-collector-self-monitoring-metrics)
  - [Debug Exporter](#debug-exporter)
- [Optimization Strategies](#optimization-strategies)
- [Ongoing Cost Management](#ongoing-cost-management)
- [Best Practices](#best-practices)

## Core Concepts

| Term | Definition |
|------|------------|
| Metric | A named numerical measurement observed over time |
| Dimension | A key-value pair used to filter, split, or group metrics |
| Metric data point | A single recorded value at a specific point in time |
| Timeseries | A unique combination of a metric and its dimension values |
| Cardinality | The number of unique timeseries a metric produces |

Ingested data points depend on three factors: **number of metrics**,
**collection intervals**, and **cardinality**. Any increase in these factors
raises consumption.

## Billable vs Non-Billable Metrics

Not all ingested metrics are billed. NEVER include non-billable metrics in cost
rankings or cost estimates — they inflate numbers and mislead users.

### Billable Rules

| Rule | Billable? |
|------|-----------|
| `dt.*` keys (default) | **No** — most `dt.*` built-in metrics are zero-rated |
| `dt.cloud.aws.*` (except `dt.cloud.aws.az.running`) | **Yes** |
| `dt.cloud.azure.*` (except 6 VM count metrics¹) | **Yes** |
| `dt.osservice.*` | **Yes** |
| `dt.service.*` | **Yes** (charged as Metrics Ingest unless originating from Full-Stack hosts²) |
| `dt.synthetic.multi_protocol.*` (8 NAM metrics³) | **Yes** |
| Non-`dt.*` keys (custom, extension, OTel) | **Yes** |
| Any key in bucket `dt_system_metrics` | **No** |
| Metrics with `dt.system.monitoring_source` = `mainframe` or `legacy` | **No** |

¹ Non-billable Azure VM metrics: `dt.cloud.azure.region.vms.initializing`,
`.running`, `.stopped`, `dt.cloud.azure.vm_scale_set.vms.initializing`,
`.running`, `.stopped`

² `dt.service.*` from Full-Stack hosts consume included volume, not Metrics
Ingest. From other sources, they are charged as Metrics Ingest.

³ NAM metrics: `dt.synthetic.multi_protocol.request.availability`,
`.request.executions`, `.icmp.success_rate`, `.icmp.packets_sent`,
`.icmp.packets_received`, `.icmp.round_trip_time`, `.tcp.connection_time`,
`.dns.resolution_time`

Also non-billable: `legacy.containers.*`, `legacy.dotnet.perform.*`,
`legacy.tomcat.*`

Source: [Dynatrace docs: Billable and non-billable metrics](https://docs.dynatrace.com/docs/license/capabilities/metrics/dps-metrics-ingest#billable-and-non-billable-metrics)

### Billable Metrics Filter

Use this filter in `metrics` queries to restrict results to billable metrics
only. Apply it in Steps 1 and 2 whenever presenting cardinality rankings for
cost optimization. In `dql-template` blocks below, replace
`<Billable Metrics Filter>` with the full filter block shown here.

**MUST copy this filter verbatim — NEVER abbreviate or omit clauses.** Dropping
clauses produces incorrect rankings in environments with Azure, NAM, or other
`dt.*` billable metrics.

```dql-template
// Billable metrics filter — append after `metrics` command
| filter (
    NOT startsWith(metric.key, "dt.")
    OR (startsWith(metric.key, "dt.cloud.aws") AND metric.key != "dt.cloud.aws.az.running")
    OR (startsWith(metric.key, "dt.cloud.azure")
        AND NOT in(metric.key, {
          "dt.cloud.azure.region.vms.initializing",
          "dt.cloud.azure.region.vms.running",
          "dt.cloud.azure.region.vms.stopped",
          "dt.cloud.azure.vm_scale_set.vms.initializing",
          "dt.cloud.azure.vm_scale_set.vms.running",
          "dt.cloud.azure.vm_scale_set.vms.stopped"}))
    OR startsWith(metric.key, "dt.osservice")
    OR startsWith(metric.key, "dt.service")
    OR in(metric.key, {
          "dt.synthetic.multi_protocol.request.availability",
          "dt.synthetic.multi_protocol.request.executions",
          "dt.synthetic.multi_protocol.icmp.success_rate",
          "dt.synthetic.multi_protocol.icmp.packets_sent",
          "dt.synthetic.multi_protocol.icmp.packets_received",
          "dt.synthetic.multi_protocol.icmp.round_trip_time",
          "dt.synthetic.multi_protocol.tcp.connection_time",
          "dt.synthetic.multi_protocol.dns.resolution_time"})
  )
  AND dt.system.bucket != "dt_system_metrics"
  AND (isNull(dt.system.monitoring_source) OR NOT in(dt.system.monitoring_source, {"mainframe", "legacy"}))
```

> **When to omit this filter:** If the user explicitly asks about *all* ingested
> metrics (including non-billable), run without the filter but clearly label
> results as "total cardinality (including non-billable metrics)".

## Analyze Metrics Ingest

Before optimizing, identify which metrics and sources drive the most ingest.
Follow the two-step workflow below **in order** — each step narrows scope and
increases detail.

> **NEVER expose internal workflow steps to the user.** Do not say "Step 1",
> "Step 2", "proceed to the next step", or reference this skill's internal
> structure. Describe actions in natural language: "Let me break down your
> metrics by source, cost center, and product", "Now I'll drill into the top
> metric keys for that source". The workflow steps are for agent execution
> order — the user should experience a natural conversation, not a numbered
> checklist.

> **NEVER recommend specific metrics or dimensions to drop, reduce, or change.** Users
> configure metrics intentionally — the agent lacks context on whether a
> high-cardinality metric or dimension serves critical downstream analysis, alerting, or
> business reporting. Present data and explain optimization levers. Wait for the
> user to decide what to optimize. See
> [Agent Behavior — User-Driven Optimization](#agent-behavior--user-driven-optimization)
> for the full rule.

> **Critical: Cardinality ≠ Data Points.** The `metrics` command returns
> **timeseries count** (cardinality), NOT actual data point volume. There is
> currently no reliable way to determine actual data point volume from DQL.
> Cardinality shows **relative cost contribution** (which metrics are expensive
> compared to others) but NEVER extrapolate to exact data point counts or
> absolute cost per metric key. Use cardinality rankings for identifying
> optimization candidates, not for precise volume claims.

### Step 1 — Break Down by Source, Cost Center, and Cost Product

**MUST run all three breakdown queries in the first pass.** Do NOT ask the user
to choose a breakdown axis — present all three results together so the
highest-cardinality areas are immediately visible.

Append the [Billable Metrics Filter](#billable-metrics-filter) after the
`metrics` command in each query to exclude non-billable metrics from rankings.

**Query 1a — by metric source:**

```dql-template
metrics
<Billable Metrics Filter>
| summarize count = count(), by: {dt.metrics.source}
| sort count desc
```

**Query 1b — by cost center:**

```dql-template
metrics
<Billable Metrics Filter>
| summarize count = count(), by: {dt.cost.costcenter}
| sort count desc
```

**Query 1c — by cost product:**

```dql-template
metrics
<Billable Metrics Filter>
| summarize count = count(), by: {dt.cost.product}
| sort count desc
```

Present all three results together. Identify the highest-cardinality values
across all breakdowns to guide the drill-down in Step 2.

> **Scan limit check:** The `metrics` command scans a maximum of **100,000
> series**. If the sum of the `count` column in any breakdown query approaches
> 90,000, warn the user that results may be truncated and suggest filtering by
> `dt.metrics.source` or `dt.cost.costcenter` for accurate numbers.

If cost center/product queries return only null values, Cost Allocation for
metrics has not been configured. Note this to the user and rely on the
`dt.metrics.source` breakdown. See [cost-allocation.md](cost-allocation.md)
and [Dynatrace docs: Allocate your DPS costs](https://docs.dynatrace.com/docs/license/cost-allocation).

### Step 2 — Drill Down into Metric Keys

Based on Step 1 results, drill into the highest-cardinality source, cost
center, or cost product. Continue applying the
[Billable Metrics Filter](#billable-metrics-filter) to exclude non-billable
keys from rankings.

```dql-template
metrics
| filter dt.metrics.source == "<metric_source_name>"
<Billable Metrics Filter>
| summarize count = count(), by: {metric.key}
| sort count desc
```

```dql-template
metrics
| filter dt.cost.costcenter == "<cost_center_name>"
<Billable Metrics Filter>
| summarize count = count(), by: {metric.key}
| sort count desc
```

```dql-template
metrics
| filter dt.cost.product == "<cost_product_name>"
<Billable Metrics Filter>
| summarize count = count(), by: {metric.key}
| sort count desc
```

Present results as **cardinality rankings** — these show relative cost
contribution across metric keys.

#### Optional: Dimension-Level Drill-Down

To identify which dimensions drive cardinality for a specific metric key:

```dql-template
metrics
| filter metric.key == "<metric_key>"
| summarize count = count(), by: {<dimension_name>}
| sort count desc
| limit 20
```

Run for each dimension of interest. Dimensions whose top values contribute
disproportionately many timeseries are optimization candidates.

#### Optional: Single-Key Cardinality Check

To check overall cardinality of a single metric key:

```dql-template
timeseries count(<metric.key>, scalar: true)
```

This returns the count of distinct timeseries that produced data in the
selected timeframe. Unlike the `metrics` command, `timeseries` is not subject
to the 100K series scan limit, making it the accurate way to verify cardinality
for a single key. Note: the count grows with wider timeframes as ephemeral
series (short-lived processes, scaling events) accumulate.

## OTel Collector Self-Monitoring Metrics

If ingesting metrics via the OTel Collector, use these built-in metrics to
validate ingest volume and confirm optimization effects:

| Metric | Description |
|--------|-------------|
| `dt.sfm.active_gate.metrics.ingest.otlp.datapoints.received.total` | Incoming OTLP data points |
| `dt.sfm.active_gate.metrics.ingest.otlp.datapoints.accepted` | Accepted data points |
| `dt.sfm.active_gate.metrics.ingest.otlp.datapoints.rejected` | Rejected data points (split by `reason`) |
| `dt.sfm.active_gate.rest.request_count` (filter by operation `POST /otlp/v1/metrics`) | OTLP request count |

OTel Collector internal telemetry (requires Collector self-monitoring
configuration):

| Metric | Description |
|--------|-------------|
| `otelcol_receiver_accepted_metric_points` | Data points received by Collector |
| `otelcol_exporter_sent_metric_points` | Data points exported by Collector |

### Debug Exporter

To inspect individual metrics and their attributes, use the Collector's debug
exporter. Prints metrics to the Collector console — useful for troubleshooting
and validating filter/transform processors.

```yaml
exporters:
  debug:
    verbosity: detailed

service:
  pipelines:
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [debug, otlp_http/dynatrace]
```

## Optimization Strategies

After presenting the analysis from Steps 1–2, **NEVER jump to recommendations
or suggest specific metrics or dimensions to drop, reduce, or change.** Users configure
metrics intentionally — the agent lacks context on whether a high-cardinality
metric or dimension serves critical downstream analysis, alerting, or business reporting.

### Agent Behavior — User-Driven Optimization

1. **Present data, not judgments** — Show cardinality rankings from the analysis
   steps. Do NOT label metrics or dimensions as "wasteful", "unnecessary", or
   "candidates for removal".
2. **Explain the three optimization levers** — Briefly describe what each
   strategy does (see table below) so the user understands their options.
3. **Ask the user what they want to optimize** — Wait for the user to identify
   which metric, dimension, or interval they want to change. The user knows
   their intent; the agent does not.
4. **Provide guidance only after the user decides** — Once the user names a
   specific metric/dimension/action, provide the detailed how-to from the
   matching strategy section below.

> **Why:** Suggesting drops or reductions for metrics or dimensions the user purposely
> configured (e.g., spanmetrics, self-monitoring, custom business metrics)
> erodes trust. The agent's role is to surface data and execute the user's
> chosen optimization — not to decide what should be optimized.

### Strategy Overview

Present this table when explaining optimization options to the user:

| Strategy | Cost Factor | What It Does |
|----------|-------------|--------------|
| [Drop metric](#strategy-1--drop-metric) | Number of metrics | Eliminates all timeseries for a metric key |
| [Reduce cardinality](#strategy-2--reduce-cardinality) | Cardinality (dimensions) | Removes a dimension to reduce timeseries count |
| [Change ingest interval](#strategy-3--change-ingest-interval) | Collection frequency | Reduces data points per timeseries |

### Strategy 1 — Drop Metric

Eliminates an entire metric key from ingestion. Use when a metric is unused in
dashboards, notebooks, alerts, or SLOs.

> ⚠ **Dropped records are never persisted and are not recoverable.** Verify the
> metric is not referenced before proceeding.

#### Option A — OpenPipeline (recommended)

1. Go to **Settings → Process and contextualize → OpenPipeline → Metrics**
2. Route the metric key to a pipeline
3. In the **Processing** stage, add a **Drop record** processor
4. Set the matching condition:

```dql-snippet
metric.key == "<metric_key>"
```

To scope the drop (e.g., drop only dev traffic):

```dql-snippet
matchesValue(environment, "dev") AND matchesValue(metric.key, "<metric_key>")
```

#### Option B — OTel Collector filter processor

Use when `dt.metrics.source == "opentelemetry"`. Prevents the metric from
reaching Dynatrace.

```yaml
processors:
  filter/drop-unwanted:
    error_mode: ignore
    metrics:
      metric:
        - 'IsMatch(name, "<metric_key>")'
      datapoint:
        # Drop only matching datapoints (optional scoping)
        - attributes["environment"] == "dev" and metric.name == "<metric_key>"
```

**Only present OTel Collector options when the metric source is
`opentelemetry`.** For other sources, show only the OpenPipeline option.

#### Option C — OTel SDK Views

When instrumenting with OTel SDKs directly, use **Views** to drop metrics at
the SDK level before export. This is the earliest and cheapest drop point.
Always consider metric cardinality when creating custom metrics and avoid
volatile dimensions (timestamps, request IDs, or other rapidly-changing
attributes). See [OpenTelemetry SDK Views documentation](https://opentelemetry.io/docs/specs/otel/metrics/sdk/#view).

### Strategy 2 — Reduce Cardinality

Removes a high-cardinality dimension from a metric key to reduce timeseries
count. Target dimensions flagged in Step 2 with unusually high unique-value
counts.

#### Identify high-cardinality dimensions

Before applying this strategy, identify which dimensions drive cardinality for
a specific metric key:

```dql-template
metrics
| filter metric.key == "<metric_key>"
| summarize count = count(), by: {<dimension_name>}
| sort count desc
| limit 20
```

Run this for each dimension of the metric. Dimensions whose top values
contribute disproportionately many timeseries are optimization candidates.

#### Option A — DQL processor in OpenPipeline

1. Go to **Settings → Process and contextualize → OpenPipeline → Metrics**
2. Route the metric key to a pipeline
3. In the **Processing** stage, add a **DQL processor**
4. Matching condition:

```dql-snippet
metric.key == "<metric_key>"
```

5. DQL processor definition:

```dql-snippet
fieldsRemove <dimension_name>
```

#### Option B — Remove fields processor in OpenPipeline

1. Go to **Settings → Process and contextualize → OpenPipeline → Metrics**
2. In the **Processing** stage, add a **Remove fields** processor
3. Matching condition: `metric.key == "<metric_key>"`
4. Remove fields: enter `<dimension_name>` → select **Add**

Multiple fields can be removed in one processor. Removing a field preserves
metric-level rollups and rollups by remaining dimensions.

#### Option C — OTel Collector transform processor

Use when `dt.metrics.source == "opentelemetry"`. Removes the dimension before
it reaches Dynatrace.

```yaml
processors:
  transform:
    metric_statements:
      - context: datapoint
        statements:
          - delete_key(attributes, "<dimension_name>")
```

**Only present OTel Collector options when the metric source is
`opentelemetry`.**

### Strategy 3 — Change Ingest Interval

Reduces collection frequency to produce fewer data points per timeseries.

> **Minimum billable resolution:** Dynatrace aggregates measurements into fixed
> 1-minute buckets. Intervals below 1 minute do **not** reduce ingest cost. To
> save cost, set the interval to **1 minute or longer**.

**Best candidates:** slowly-changing metrics (disk usage, memory pools),
less-critical operational metrics, metrics used only for long-term trend
analysis.

#### OneAgent metrics (`dt.*` keys)

Adjust monitoring frequency in **Settings → Monitoring → Monitored
technologies**, or work with the Dynatrace administrator to modify the
collection policy.

#### OTel Collector — Prometheus receiver

```yaml
receivers:
  prometheus:
    config:
      scrape_configs:
        - job_name: "your-service"
          scrape_interval: 5m  # Increase from default 30s or 1m
          static_configs:
            - targets: ["your-target:port"]
```

#### OTel SDK — PeriodicExportingMetricReader

```text
const reader = new PeriodicExportingMetricReader({
  exporter: new OTLPMetricExporter(),
  exportIntervalMillis: 300_000, // 5 minutes
});
```

#### Prometheus — scrape_interval

```yaml
# prometheus.yml
scrape_configs:
  - job_name: "your-job"
    scrape_interval: 5m  # Increase from default 1m or 30s
    static_configs:
      - targets: ["your-target:port"]
```

> ⚠ **Alerting impact:** Longer intervals introduce gaps at 1-minute
> resolution. Validate that existing alert configurations can tolerate the new
> interval before applying changes.

## Ongoing Cost Management

1. **Continuous validation** — Integrate cardinality and ingest interval checks
   into CI/CD using Site Reliability Guardian (SRG). Detect instrumentation
   changes that increase cardinality before they reach production. See
   [Dynatrace docs: Site Reliability Guardian](https://docs.dynatrace.com/docs/deliver/site-reliability-guardian).

2. **Cost allocation** — Enrich metrics with `dt.cost.costcenter` or
   `dt.cost.product` attributes to enable per-team chargeback. See
   [cost-allocation.md](cost-allocation.md).

3. **Business value validation** — Periodically review whether each ingested
   metric supports a defined use case. Drop metrics that no longer serve
   monitoring, alerting, or reporting needs.

## Best Practices

1. **Follow the 2-step workflow** — Break down all three axes upfront → drill
   into keys. Each step narrows scope.
2. **Cardinality for relative ranking only** — Use cardinality rankings
   (Steps 1–2) to identify which metrics contribute most to cost. Do NOT
   extrapolate cardinality to exact data point counts or per-key cost estimates.
3. **NEVER estimate per-metric-key costs** — Billing totals reflect included
   volume deductions, aggregation rules, and billable/non-billable
   classification that cannot be reproduced at individual metric level. For
   cost data, use [billing-capabilities.md](billing-capabilities.md).
4. **Never recommend unprompted** — Present data and explain options. Wait for
   the user to choose what to optimize. Do not suggest dropping or reducing
   specific metrics — the user knows their intent.
5. **Validate after changes** — Use
   [OTel self-monitoring metrics](#otel-collector-self-monitoring-metrics) and
   billing usage queries from
   [billing-capabilities.md](billing-capabilities.md) to confirm ingest
   reduction.
6. **Document decisions** — Record why metrics were dropped or dimensions
   removed to prevent re-introduction.
7. **Filter non-billable metrics** — Most `dt.*` keys are zero-rated. Always
   apply the [Billable Metrics Filter](#billable-metrics-filter) when ranking
   metrics by cost impact. Including non-billable metrics inflates cardinality
   numbers and misleads optimization efforts.
