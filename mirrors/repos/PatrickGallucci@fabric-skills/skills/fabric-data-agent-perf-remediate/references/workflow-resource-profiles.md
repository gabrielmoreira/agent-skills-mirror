# Workflow: Resource Profile Optimization

## Table of Contents

- [Profile Selection Guide](#profile-selection-guide)
- [Configuration Methods](#configuration-methods)
- [Default Profile Behavior](#default-profile-behavior)
- [Profile Configuration Details](#profile-configuration-details)
- [Autotune Integration](#autotune-integration)
- [Native Execution Engine](#native-execution-engine)

## Profile Selection Guide

Match your Data Agent workload pattern to the correct resource profile:

| Agent Workload | Recommended Profile | Reason |
|----------------|-------------------|--------|
| Read-heavy analytics queries | `readHeavyForSpark` | OptimizeWrite enabled, 128MB bins |
| Power BI dashboard serving | `readHeavyForPBI` | VOrder enabled, 1GB bins |
| ETL ingestion pipelines | `writeHeavy` | VOrder disabled, stats collection off |
| Mixed read/write | `custom` | Tune individually per workload |

## Configuration Methods

### Method 1: Environment-Level (Recommended for Agents)

1. Navigate to **Workspace** > **Environments**.
2. Edit or create a new environment.
3. Under **Spark Configurations**, set:
   ```
   spark.fabric.resourceProfile = readHeavyForSpark
   ```
4. Publish the environment.
5. Attach the environment to all agent-related notebooks and Spark Job Definitions.

### Method 2: Runtime Override

```python
# Override at runtime inside a notebook cell
spark.conf.set("spark.fabric.resourceProfile", "readHeavyForSpark")
```

**Note:** Runtime settings take precedence over environment settings.

### Method 3: Custom Profile

```python
# Create a fully custom profile
spark.conf.set("spark.fabric.resourceProfile", "agentOptimized")
spark.conf.set("spark.sql.parquet.vorder.default", "true")
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
spark.conf.set("spark.databricks.delta.optimizeWrite.binSize", "256")
spark.conf.set("spark.sql.adaptive.enabled", "true")
```

## Default Profile Behavior

All new Fabric workspaces default to `writeHeavy`:

```json
{
  "spark.sql.parquet.vorder.default": "false",
  "spark.databricks.delta.optimizeWrite.enabled": "false",
  "spark.databricks.delta.optimizeWrite.binSize": "128",
  "spark.databricks.delta.optimizeWrite.partitioned.enabled": "true",
  "spark.databricks.delta.stats.collect": "false"
}
```

**Impact on Data Agents:** If your agent primarily runs read queries (which most Data Agents
do), the default `writeHeavy` profile is suboptimal. Switch to `readHeavyForSpark` or
`readHeavyForPBI` depending on whether consumers are Spark notebooks or Power BI.

## Profile Configuration Details

### writeHeavy
- VOrder: **Disabled** — no read optimization overhead during writes
- OptimizeWrite: **Disabled** — maximum write throughput
- Stats Collection: **Disabled** — reduced write latency

### readHeavyForPBI
- VOrder: **Enabled** — Parquet layout optimized for Power BI and Data Warehouse reads
- OptimizeWrite: **Enabled** with 1GB bin size — larger files, fewer reads
- Best for: Serving Power BI dashboards from Delta tables

### readHeavyForSpark
- VOrder: **Disabled** — Spark reads don't benefit from VOrder as much
- OptimizeWrite: **Enabled** with 128MB bin size — balanced file sizes for Spark
- Partitioned OptimizeWrite: **Enabled** — better for partitioned tables
- Best for: Interactive Spark queries and Data Agent SQL generation

## Autotune Integration

Autotune learns optimal Spark configurations from workload patterns over 20-25 iterations.

**Enable autotune:**
```
spark.ms.autotune.enabled = true
```

**Compatibility requirements:**
- Fabric Runtime 1.1 or 1.2 only (not higher)
- High Concurrency mode must be disabled
- Private endpoints must be disabled
- Works with autoscaling regardless of configuration

**Note:** Autotune deactivates automatically if a query processes unusually large data volumes.

## Native Execution Engine

The Native Execution Engine provides additional performance improvements for Spark
workloads. When available, it optimizes common ETL patterns automatically.

**Recommendation for Data Agents:** Enable both resource profiles AND autotune for the
best combined performance. Resource profiles set the baseline; autotune refines from there.
