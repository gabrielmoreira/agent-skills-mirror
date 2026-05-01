# Ingestion remediate Guide

## Table of Contents

1. [Ingestion Architecture Overview](#ingestion-architecture-overview)
2. [Eventstream Performance Diagnostics](#eventstream-performance-diagnostics)
3. [Eventhouse Ingestion Modes](#eventhouse-ingestion-modes)
4. [Throughput Settings and Limits](#throughput-settings-and-limits)
5. [Common Ingestion Failures](#common-ingestion-failures)
6. [Lakehouse Destination Tuning](#lakehouse-destination-tuning)
7. [Streaming Ingestion](#streaming-ingestion)
8. [Diagnostic Checklist](#diagnostic-checklist)

---

## Ingestion Architecture Overview

Fabric Real-Time Intelligence supports multiple ingestion paths:

- **Eventstream → Eventhouse**: Primary real-time path (direct ingestion or event processing mode)
- **Eventstream → Lakehouse**: For batch-oriented streaming destinations
- **Direct ingestion APIs**: Queued (batched) or managed (streaming with fallback)
- **External tools**: Telegraf, Azure Data Factory, custom SDK clients

Each path has distinct latency characteristics, throughput limits, and failure modes.

---

## Eventstream Performance Diagnostics

### Key Metrics to Monitor

Access via the Eventstream editor → select a node → **Data insights** tab:

| Metric | What It Tells You |
|--------|-------------------|
| IncomingMessages / OutgoingMessages | Event flow rate through the stream |
| IncomingBytes / OutgoingBytes | Data volume throughput |
| BackloggedInputEvents | Events queued but not yet processed — rising values indicate bottleneck |
| WatermarkDelay (seconds) | Maximum processing lag across partitions — key latency indicator |
| RuntimeErrors | Total processing errors in the engine |
| DataConversionErrors | Schema mismatch between source and destination |
| DeserializationErrors | Malformed events that cannot be parsed |

### Interpreting Watermark Delay

- **< 10 seconds**: Healthy, near real-time processing
- **10–60 seconds**: Mild lag, check throughput settings and destination capacity
- **> 60 seconds**: Significant bottleneck, investigate destination throttling, schema errors, or insufficient throughput tier

### Runtime Logs

Access via the node → **Runtime logs** tab. Filter by severity (Warning, Error, Information) and search with keywords. Common error patterns:

- `SchemaConversionFailure` — incoming schema does not match destination table
- `ThrottlingException` — destination cannot accept data at current rate
- `SerializationError` — malformed JSON or unsupported data type

---

## Eventhouse Ingestion Modes

### Direct Ingestion

Events flow directly from Eventstream into the KQL database with no intermediate processing. Best for simple append scenarios.

### Event Processing Before Ingestion

Events pass through the Eventstream processing engine before reaching the KQL database. Enables transformations, filtering, and routing but adds processing latency.

### Throughput comparison (approximate, per Microsoft testing)

| Destination Mode | Low | Medium | High |
|-----------------|-----|--------|------|
| Eventhouse (Direct) | 10 MB/s | 50 MB/s | 100 MB/s |
| Eventhouse (Event Processing) | 20 MB/s | 100 MB/s | 200 MB/s |
| Lakehouse | 40 MB/s | 120 MB/s | 200 MB/s |
| Custom Endpoint | 100 MB/s | 150 MB/s | 200 MB/s |

Testing conditions: same data center, 1 KB JSON events batched in groups of 100, one source → one stream → one destination, no processing operators.

---

## Throughput Settings and Limits

Eventstream throughput is configurable per source. Access via source node → **Settings** → **Event throughput**.

Three tiers: **Low**, **Medium**, **High**. Select based on expected data volume. If BackloggedInputEvents grows consistently, increase the throughput tier.

### Capacity-level throttling

If your Fabric capacity is fully consumed, ingestion may be throttled at the capacity level. Symptoms:

- HTTP 430 errors in ingestion logs
- Sudden ingestion drop with no source-side issues
- Eventstream runtime logs showing throttling exceptions

Resolution: check the Fabric Capacity Metrics app for CU saturation and consider SKU upgrade or workload redistribution.

---

## Common Ingestion Failures

| Failure Type | Cause | Resolution |
|-------------|-------|------------|
| Schema mismatch | Source schema changed; new columns not in target table | Use `.create-merge table` to add new columns, or configure schema mapping |
| Deserialization error | Malformed JSON, unexpected encoding | Validate source event format; check for BOM or non-UTF-8 characters |
| Partial ingestion | Some rows succeed, some fail | Check ingestion result logs for per-row error details |
| Batching timeout | Events arrive too slowly to fill a batch | Reduce minimum rows or maximum duration in destination settings |
| Duplicate events | At-least-once delivery without dedup | Use `arg_max` materialized view to deduplicate on a unique key |
| CDC schema drift | Database CDC source adds/removes columns mid-stream | Lakehouse destinations are not recommended for CDC; use Eventhouse with flexible schema |

---

## Lakehouse Destination Tuning

When using Lakehouse as an Eventstream destination, two parameters control batching:

- **Minimum rows**: 1 to 2,000,000 per file. Lower values create more small files (impacts downstream read performance).
- **Maximum duration**: 1 minute to 2 hours. Longer durations produce larger, fewer files.

For optimal streaming performance, Microsoft recommends streaming to Eventhouse first, enabling OneLake availability, and then accessing the data from Lakehouse via shortcut.

---

## Streaming Ingestion

For lowest latency (sub-second), enable streaming ingestion on the Eventhouse:

```kql
-- Check if streaming ingestion is enabled
.show database MyDB policy streamingingestion
```

When using Telegraf or SDK clients, select **managed ingestion** mode which attempts streaming first and falls back to batched ingestion if streaming is not enabled.

Streaming ingestion is best for low-volume, low-latency scenarios (< 4 GB/hr per table). For high-volume scenarios, queued (batched) ingestion provides better throughput and reliability.

---

## Diagnostic Checklist

Use this checklist when investigating ingestion problems:

- [ ] Check Eventstream → Data insights for BackloggedInputEvents trend
- [ ] Check WatermarkDelay — is it increasing or stable?
- [ ] Review Runtime logs for errors on source and destination nodes
- [ ] Verify source event schema matches destination table schema
- [ ] Check Fabric Capacity Metrics app for CU saturation
- [ ] Verify Eventhouse is not in suspended state (check Always-On setting)
- [ ] Review ingestion results logs via workspace monitoring
- [ ] Check throughput tier setting on Eventstream source
- [ ] For Lakehouse destinations, verify minimum rows and maximum duration settings
- [ ] If using streaming ingestion, confirm policy is enabled on the database
