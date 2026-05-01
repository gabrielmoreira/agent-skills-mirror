# Dataflow Gen2 Performance Optimization Guide

Deep-dive reference for optimizing Microsoft Fabric Dataflow Gen2 execution time, throughput, and resource consumption across all common scenarios.

## Table of Contents

- [Fast Copy Deep Dive](#fast-copy-deep-dive)
- [Query Folding Analysis](#query-folding-analysis)
- [Staging Architecture Patterns](#staging-architecture-patterns)
- [Gen1 vs Gen2 Runtime Differences](#gen1-vs-gen2-runtime)
- [Destination Optimization](#destination-optimization)
- [Gateway Optimization Patterns](#gateway-optimization-patterns)
- [Partitioned Compute](#partitioned-compute)
- [Incremental Refresh Patterns](#incremental-refresh-patterns)
- [Capacity Cost Optimization](#capacity-cost-optimization)
- [Monitoring and Trend Analysis](#monitoring-and-trend-analysis)

---

## Fast Copy Deep Dive

### Performance Benchmark

Fast Copy can provide up to approximately 9x faster ingestion for supported workloads. Real-world benchmark from NYC Taxi dataset (year-wise merged Parquet files):

| Mode | Execution Time |
|------|---------------|
| Without Fast Copy | 01:09:21 |
| With Fast Copy | 00:07:43 |

### Supported File Formats

- CSV
- Parquet

### Supported Connectors

ADLS Gen2, Azure Blob Storage, Azure SQL DB, Lakehouse, PostgreSQL, On-premises SQL Server, Warehouse, Oracle, Snowflake, SQL Database in Fabric.

### Row Limits

- Azure SQL Database: Up to 1M rows per table per run via Fast Copy

### Transformation Compatibility (File Sources)

Only these transformations are supported with Fast Copy on file sources:

1. Combine files
2. Select columns
3. Change data types
4. Rename a column
5. Remove a column

For SQL sources, any transformation that is part of the native query (query folding) works with Fast Copy.

### Step-by-Step Query Splitting

When the Fast Copy indicator shows red on later steps:

1. **Identify the boundary**: Note which step first shows a red indicator
2. **Remove red steps**: Delete transformations showing red icons and the destination from the original query
3. **Verify green indicators**: Confirm all remaining steps show green
4. **Enable staging**: Right-click the query > Enable staging (query turns blue)
5. **Create reference**: Right-click the query > Reference
6. **Add transforms back**: In the new referenced query, add the Group By, joins, aggregations, and destination
7. **Publish and refresh**: First query uses CopyActivity engine; second uses SQL DW compute

### Requiring Fast Copy

Right-click query > **Require Fast Copy** forces Fast Copy usage regardless of data size thresholds. Warning: if the query is incompatible with Fast Copy, the dataflow will fail rather than falling back to default data movement.

### Fast Copy Output Destinations

Fast Copy currently only supports Lakehouse as a direct output destination. For other destinations, stage the data first with Fast Copy, then use a referenced query to write to your preferred destination.

### Known Limitations

- Gateway version must be 3000.214.2 or newer
- Fixed schema is not supported
- Schema-based destination is not supported

---

## Query Folding Analysis

Query folding pushes transformations to the source system, reducing data transfer and processing time.

### How to Check Folding Status

In the Dataflow Gen2 editor, the folding indicators appear next to each step:

- **Folded** (green checkmark): Step is pushed to source
- **Not folded** (warning): Step runs in Mashup engine locally

### Common Non-Foldable Operations

- Custom M functions
- Complex aggregations not supported by source SQL dialect
- Cross-source joins
- Operations after a non-foldable step (folding breaks downstream)

### Optimization Strategies

1. **Reorder steps**: Place foldable operations before non-foldable ones
2. **Use native queries**: Write SQL directly when complex folding fails
3. **Enable allowNativeQueries**: Set to `true` in dataflow metadata for sources that support it
4. **Stage then transform**: For non-foldable work, stage data first and use SQL DW compute

### Impact Assessment

Folded queries: Source system handles compute and only sends result set.
Non-folded queries: All data transfers to Mashup engine, consuming Dataflow Standard Compute CUs.

---

## Staging Architecture Patterns

### Pattern 1: Lakehouse Destination Without Staging (Simple ETL)

```
Source → Mashup Engine → Lakehouse
```

Best for: Small datasets, simple transforms that fold to source.

### Pattern 2: Warehouse Destination With Staging (Required)

```
Source → Staging Lakehouse → SQL DW Compute → Warehouse
```

Staging is mandatory for Warehouse destinations. Provides best performance for complex transforms.

### Pattern 3: Lakehouse Destination With Staging (Complex Transforms)

```
Source → Staging Lakehouse → SQL DW Compute → Staging Warehouse → Lakehouse
```

Warning: Extra data hop from Staging Warehouse to Lakehouse can be a bottleneck. Consider switching to Warehouse destination or disabling staging.

### Pattern 4: Fast Copy + Referenced Query (Optimal for Large Data)

```
Query 1: Source → [Fast Copy] → Staging Lakehouse
Query 2: Staging Lakehouse → [SQL DW] → Destination
```

Best for: Large datasets where ingestion speed matters and complex transforms needed.

### Decision Matrix

| Data Volume | Transform Complexity | Destination | Recommendation |
|------------|---------------------|-------------|----------------|
| Small (<100K rows) | Simple (foldable) | Lakehouse | Disable staging |
| Small (<100K rows) | Complex | Warehouse | Enable staging |
| Large (>1M rows) | Minimal (EL only) | Lakehouse | Fast Copy, no staging |
| Large (>1M rows) | Complex | Warehouse | Fast Copy + referenced query |
| Large (>1M rows) | Complex | Lakehouse | Fast Copy + referenced query (disable staging on final) |

---

## Gen1 vs Gen2 Runtime

### Why Gen2 May Appear Slower

Dataflow Gen2 outputs data in **Delta Parquet format** when using staging or Lakehouse destinations. Dataflow Gen1 used CSV output. While Delta Parquet may result in longer initial ETL runtimes, it enables powerful downstream capabilities:

- **Direct Lake** mode for Power BI (no data import needed)
- **Lakehouse** and **Warehouse** SQL analytics
- **Time travel** and **ACID transactions** on output tables

### Mitigation Strategies

1. Compare total end-to-end time including downstream processing (Gen2 often wins overall)
2. Use Fast Copy for data movement phase
3. Disable staging when transforms fold to source
4. Consider using Warehouse destination for complex scenarios (single-hop staging)

---

## Destination Optimization

### Use Data Destinations Over Dataflow Connectors

Data destinations (Lakehouses, Warehouses) are more efficient for downstream consumption than dataflow connectors. They support generic connection methods like SQL endpoint and Direct Lake, which improve performance and reduce resource consumption.

### Warehouse Destination Benefits

- Staging + write happen in same SQL DW compute engine
- Single data hop (no Lakehouse intermediary)
- Best for complex transformation workloads

### Lakehouse Destination Tips

- Disable staging for simple foldable queries
- Use Fast Copy for large volume ingestion
- Consider schema support (preview) for organizing output tables

---

## Gateway Optimization Patterns

### Problem

When a gateway runs the entire dataflow, all transformations execute on the gateway host machine. This creates a bottleneck for complex dataflows.

### Solution: Two-Dataflow Architecture

**Dataflow 1 (Data Movement)**:
- Gateway scope: Only data extraction and transfer
- Enable Fast Copy for supported connectors
- Destination: Lakehouse or Warehouse staging
- Minimal transforms (only what folds to source)

**Dataflow 2 (Transformation)**:
- No gateway needed (reads from cloud staging)
- Apply complex transformations via SQL DW compute
- Write to final destination

### Gateway Requirements

- Version 3000.214.2+ for Fast Copy support
- Keep within last 6 supported versions
- Detailed logs not available for on-premises gateways (use cloud/VNet gateways when possible)

---

## Partitioned Compute

Partitioned compute (Preview) offers an alternative to Fast Copy for file-based sources where transformations don't fold.

### When to Use

- File sources that don't support query folding
- Need per-file transformations via Combine Files experience
- Want parallel processing across partitions

### Recommendations

- Load directly to staging or Fabric Warehouse for best performance
- Only latest partition run is stored in staging Lakehouse
- Use data destinations to retain data across partitioned runs
- Use the Sample transform file from Combine Files to define per-file transformations
- Billing is based on CU consumption

---

## Incremental Refresh Patterns

### When Incremental Refresh Helps

- Large transactional datasets updated frequently
- Only new/changed records need processing
- Want to reduce CU consumption per refresh

### When Incremental Refresh Hurts

- Small datasets where full refresh is already fast
- Too many small buckets creating partition management overhead
- Overhead of change detection exceeds savings from reduced data

### Tuning Parameters

| Parameter | Impact | Recommendation |
|-----------|--------|----------------|
| Bucket size | Larger = fewer buckets, less overhead | Start large, reduce if needed |
| Bucket count | More = finer granularity, more overhead | Minimize for best performance |
| Concurrency | Max parallel requests to source | Reduce if source can't handle load |
| Refresh window | Time range for incremental detection | Match to actual data change patterns |

### Incremental Amassing Pattern

For scenarios where you want to incrementally collect data over time without reprocessing historical data. See Microsoft Learn tutorial for setup guidance.

---

## Capacity Cost Optimization

### Compute Pricing Tiers

**Standard Compute** (Mashup Engine):
```
First 600 seconds: 12 CU per second
Beyond 600 seconds: 1.5 CU per second
```

**High Scale Compute** (SQL DW):
- Based on Lakehouse staging storage + Warehouse compute duration
- More efficient for large transformations

**Fast Copy**:
- Based on copy job duration
- Most efficient for high-volume EL workloads

### Optimization Priorities

1. **Enable Fast Copy** for supported connectors (up to 9x faster = less CU time)
2. **Maximize query folding** to reduce Mashup engine processing
3. **Use staging + SQL DW** for complex transforms (more efficient than Mashup for large data)
4. **Right-size refresh frequency** to match actual data update patterns
5. **Monitor via Fabric Capacity Metrics app** to track CU consumption trends

---

## Monitoring and Trend Analysis

### Monitoring Hub Dashboard

The Monitoring Hub provides:
- Refresh status across all dataflows
- Start time and duration per refresh
- Submitter and capacity information
- Average refresh duration trends
- Refresh count per day

### Refresh History Deep Dive

Available data per refresh:
- Overall status, type, duration
- Request ID, Session ID, Dataflow ID
- Per-table: entity-level timing and row/byte statistics
- Per-activity: destination write performance and volume metrics
- Detailed logs (downloadable zip with Mashup engine logs)
- CSV export for trend analysis

### Retention

- UI shows up to 50 refresh histories or 6 months (whichever comes first)
- OneLake stores up to 250 refresh histories or 6 months

### Workspace Status Column

Quick health check: the Status column in workspace view shows last refresh status and last saved/validated status. Red exclamation marks indicate failures—hover for details.

### Automated Monitoring

Use the [Get-DataflowHealthReport.ps1](../scripts/Get-DataflowHealthReport.ps1) script to programmatically collect refresh history and configuration data across all dataflows in a workspace. Use the [Watch-DataflowRefresh.ps1](../scripts/Watch-DataflowRefresh.ps1) script for real-time refresh tracking.
