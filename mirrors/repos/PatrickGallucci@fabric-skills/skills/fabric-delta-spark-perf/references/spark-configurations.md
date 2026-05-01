# Spark Configurations Guide for Microsoft Fabric

Comprehensive reference for Spark configuration tuning in Fabric, including resource profiles, Adaptive Query Execution, autotune, pool sizing, and capacity limits.

## Table of Contents

- [Resource Profiles](#resource-profiles)
- [Adaptive Query Execution (AQE)](#adaptive-query-execution-aqe)
- [Autotune](#autotune)
- [Pool Sizing and Compute](#pool-sizing-and-compute)
- [Capacity Limits](#capacity-limits)
- [Native Execution Engine](#native-execution-engine)
- [Key Spark Properties Reference](#key-spark-properties-reference)

---

## Resource Profiles

Microsoft Fabric supports predefined Spark resource profiles that apply workload-optimized settings. All new workspaces default to `writeHeavy`.

### Available Profiles

| Profile | Use Case | V-Order | Optimized Write | Stats Collection |
|---------|----------|---------|-----------------|------------------|
| `writeHeavy` | High-frequency ingestion, ETL, streaming | Off | Off | Off |
| `readHeavyForSpark` | Spark SQL queries, interactive analytics | Default | On (128MB bin) | Default |
| `readHeavyForPBI` | Power BI Direct Lake dashboards | On | On (1GB bin) | Default |
| `custom` | Fully user-defined settings | User choice | User choice | User choice |

### Profile Configuration Details

**writeHeavy** (default for new workspaces):
```json
{
    "spark.sql.parquet.vorder.default": "false",
    "spark.databricks.delta.optimizeWrite.enabled": "false",
    "spark.databricks.delta.optimizeWrite.binSize": "128",
    "spark.databricks.delta.optimizeWrite.partitioned.enabled": "true",
    "spark.databricks.delta.stats.collect": "false"
}
```

**readHeavyForPBI**:
```json
{
    "spark.sql.parquet.vorder.default": "true",
    "spark.databricks.delta.optimizeWrite.enabled": "true",
    "spark.databricks.delta.optimizeWrite.binSize": "1g"
}
```

**readHeavyForSpark**:
```json
{
    "spark.databricks.delta.optimizeWrite.enabled": "true",
    "spark.databricks.delta.optimizeWrite.partitioned.enabled": "true",
    "spark.databricks.delta.optimizeWrite.binSize": "128"
}
```

### How to Set Resource Profiles

**Method 1: Environment level** (applies to all jobs in the environment):

1. Navigate to Fabric workspace > Edit environment
2. Under Spark Configurations, set:
   ```
   spark.fabric.resourceProfile = readHeavyForSpark
   ```

**Method 2: Runtime override** (per notebook or job):

```python
spark.conf.set("spark.fabric.resourceProfile", "readHeavyForSpark")
```

> **Note:** Runtime settings take precedence over environment settings.

**Method 3: Custom profile:**

```python
# Create a meaningful custom profile name
spark.conf.set("spark.fabric.resourceProfile", "fastIngestProfile")
spark.conf.set("spark.sql.shuffle.partitions", "800")
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
```

### How to Choose a Profile

| Workload Pattern | Recommended Profile | Reasoning |
|-----------------|---------------------|-----------|
| Batch ETL ingestion (hourly/daily) | `writeHeavy` | Maximize write throughput, skip V-Order overhead |
| Streaming ingestion | `writeHeavy` | Minimize per-write latency |
| Interactive Spark SQL queries | `readHeavyForSpark` | Optimized Write produces better file layout |
| Power BI Direct Lake reports | `readHeavyForPBI` | V-Order enables faster VertiScan, 1GB target for Direct Lake |
| Mixed read/write | `readHeavyForSpark` | Balanced default, override per job if needed |

---

## Adaptive Query Execution (AQE)

AQE dynamically re-optimizes queries at runtime based on actual data statistics collected after shuffle and broadcast exchanges. It is enabled by default in Fabric.

### Capabilities

1. **Dynamic broadcast join conversion** — Converts sort-merge joins to broadcast hash joins when a table is small enough after filtering
2. **Dynamic partition coalescing** — Combines small post-shuffle partitions into larger ones
3. **Dynamic skew join handling** — Splits skewed partitions into smaller sub-partitions
4. **Empty relation propagation** — Short-circuits processing of empty intermediate results

### Key AQE Configuration Properties

```python
# Enable/disable AQE (enabled by default)
spark.conf.set("spark.databricks.optimizer.adaptive.enabled", "true")

# Auto-optimized shuffle partitions
spark.conf.set("spark.sql.shuffle.partitions", "auto")

# Dynamic broadcast threshold (default 30MB)
spark.conf.set("spark.databricks.adaptive.autoBroadcastJoinThreshold", "30m")

# Partition coalescing (default enabled)
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes", "64m")
spark.conf.set("spark.sql.adaptive.coalescePartitions.minPartitionSize", "1m")

# Skew join detection thresholds
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256m")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
```

### When AQE Does Not Help

- Streaming queries (AQE only applies to non-streaming)
- Queries with no exchanges (no joins, aggregations, or window functions)
- When the AQE-evaluated plan matches the static plan (no improvement possible)

---

## Autotune

Autotune automatically adjusts Spark configurations using historical execution data. It tunes three properties per query:

| Property | Default | What It Controls |
|----------|---------|-----------------|
| `spark.sql.shuffle.partitions` | 200 | Partition count for shuffles during joins/aggregations |
| `spark.sql.autoBroadcastJoinThreshold` | 10MB | Max table size to broadcast in joins |
| `spark.sql.files.maxPartitionBytes` | 128MB | Max bytes per partition when reading files |

### Enabling Autotune

**Via environment:**

Set `spark.ms.autotune.enabled = true` in Environment > Spark properties.

**Via notebook session:**

```python
spark.conf.set("spark.ms.autotune.enabled", "true")
```

> **Note:** Autotune is in preview. It learns from historical runs, so it improves over time for recurring workloads.

---

## Pool Sizing and Compute

### SKU to Compute Mapping

| SKU | Capacity Units | Spark VCores | Node Size | Default Max Nodes | Max Nodes |
|-----|---------------|-------------|-----------|-------------------|-----------|
| F2 | 2 | 4 | Medium | 1 | 1 |
| F4 | 4 | 8 | Medium | 1 | 1 |
| F8 | 8 | 16 | Medium | 2 | 2 |
| F16 | 16 | 32 | Medium | 3 | 4 |
| F32 | 32 | 64 | Medium | 8 | 8 |
| F64 | 64 | 128 | Medium | 10 | 16 |

### Custom Pool Configuration

- Set minimum nodes to 1 (Fabric provides restorable availability for single-node clusters)
- Enable autoscaling for variable workloads
- Enable dynamic executor allocation for efficient resource use
- Driver core options: 4, 8, 16, 32, 64
- Driver/executor memory options: 28g, 56g, 112g, 224g, 400g

### Session-Level Compute Customization

```python
# Override executor configuration for a specific session
# (Workspace admin must enable "Customize compute configurations for items")
spark.conf.set("spark.executor.cores", "8")
spark.conf.set("spark.executor.memory", "56g")
```

---

## Capacity Limits

### Queue Limits by SKU

| SKU | Queue Limit |
|-----|-------------|
| F2, F4 | 4 |
| F8 | 8 |
| F16 | 16 |
| F32 | 32 |
| F64 (P1) | 64 |
| F128 (P2) | 128 |
| F256 (P3) | 256 |
| F512 (P4) | 512 |

When the queue limit is reached, new jobs receive HTTP 430 error:

> *TooManyRequestsForCapacity — This spark job can't be run because you have hit a spark compute or API rate limit.*

**Mitigation:**

- Cancel idle or stuck Spark jobs via Monitoring Hub
- Upgrade to a larger capacity SKU
- Use Autoscale Billing for Spark (pay-as-you-go) for bursty workloads
- Stagger job schedules to avoid concurrent peaks

### Autoscale Billing for Spark

For dynamic or bursty workloads, Autoscale Billing provides independent Spark compute that does not consume Fabric capacity:

| Feature | Capacity Model | Autoscale Billing |
|---------|---------------|-------------------|
| Billing | Fixed per capacity tier | Pay-as-you-go per job |
| Scaling | Shared across workloads | Independent Spark scaling |
| Resource contention | Possible | Dedicated compute |
| Best for | Predictable workloads | Dynamic/bursty jobs |

---

## Native Execution Engine

The Native Execution Engine provides accelerated query execution for compatible Spark workloads.

**Enable via Environment:**

Set `enable_native_execution_engine = true` in the environment Spark compute settings.

**Enable via API:**

```json
{
    "enable_native_execution_engine": true
}
```

> **Note:** Not all operations are supported by the Native Execution Engine. Unsupported operations fall back to standard Spark execution automatically.

---

## Key Spark Properties Reference

Quick reference for the most impactful Spark configuration properties in Fabric:

| Property | Default | Purpose | Tune When |
|----------|---------|---------|-----------|
| `spark.fabric.resourceProfile` | `writeHeavy` | Workload preset | Changing workload type |
| `spark.sql.parquet.vorder.default` | `false` | V-Order on writes | Enabling read optimization |
| `spark.microsoft.delta.optimizeWrite.enabled` | varies | Merge partitions on write | Small file prevention |
| `spark.databricks.delta.optimizeWrite.binSize` | `128` | Target file size (MB) | File size tuning |
| `spark.sql.shuffle.partitions` | `200` | Shuffle parallelism | Large data shuffles |
| `spark.sql.autoBroadcastJoinThreshold` | `10m` | Broadcast join max size | Small table joins |
| `spark.sql.files.maxPartitionBytes` | `128m` | Read partition size | File scan parallelism |
| `spark.databricks.optimizer.adaptive.enabled` | `true` | AQE master switch | Never disable |
| `spark.sql.adaptive.skewJoin.enabled` | `true` | Skew join handling | Data skew issues |
| `spark.ms.autotune.enabled` | `false` | Automatic tuning | Recurring workloads |
| `spark.memory.fraction` | `0.6` | Execution+storage memory | OOM errors |
| `spark.memory.storageFraction` | `0.5` | Storage vs execution split | Cache-heavy workloads |
| `spark.databricks.delta.retentionDurationCheck.enabled` | `true` | VACUUM safety check | Emergency cleanup only |
