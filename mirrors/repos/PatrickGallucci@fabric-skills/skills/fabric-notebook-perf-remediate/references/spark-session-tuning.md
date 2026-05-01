# Spark Session Tuning Reference

Detailed guidance for configuring Spark sessions in Microsoft Fabric notebooks for optimal performance.

## Table of Contents

- [Native Execution Engine (NEE)](#native-execution-engine-nee)
- [Autotune](#autotune)
- [Session-Level Spark Configurations](#session-level-spark-configurations)
- [Read Optimization](#read-optimization)
- [Shuffle Optimization](#shuffle-optimization)
- [Write Optimization](#write-optimization)
- [Task Parallelism](#task-parallelism)
- [Session Timeout Management](#session-timeout-management)
- [High Concurrency Sessions](#high-concurrency-sessions)
- [Resource Profiles](#resource-profiles)

## Native Execution Engine (NEE)

NEE is the single highest-impact optimization available. It replaces the JVM-based execution with native code and delivers 2x–5x performance improvements in most workloads.

**Enable at session level:**

```python
# PySpark
spark.conf.set("spark.native.enabled", "true")
```

```sql
%%sql
SET spark.native.enabled = True
```

**Enable at environment level:**

Set the Spark property `spark.native.enabled = true` in the environment's Spark Properties configuration. This applies to all notebooks and jobs using that environment.

> If you are not using NEE and operating on the traditional Spark JVM engine, you are missing significant performance gains.

## Autotune

Autotune uses a feedback loop to gradually optimize Spark configurations based on your actual query patterns. It requires 20–25 iterations to learn optimal settings.

**Enable in session:**

```python
spark.conf.set("spark.ms.autotune.enabled", "true")
```

```sql
%%sql
SET spark.ms.autotune.enabled=TRUE
```

**Enable in environment:**

Set `spark.ms.autotune.enabled = true` in the environment Spark properties.

**Compatibility notes:**

- Compatible with Fabric Runtime 1.1 and 1.2
- Cannot be enabled on runtimes higher than 1.2
- Does not function with high concurrency mode or private endpoints
- Integrates with autoscaling regardless of configuration
- Automatically deactivates if a query processes unusually large data

## Session-Level Spark Configurations

Set these in the first cell of your notebook before any data operations:

```python
# Performance fundamentals
spark.conf.set("spark.native.enabled", "true")
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")

# Shuffle tuning (adjust based on data volume)
spark.conf.set("spark.sql.shuffle.partitions", "100")

# Read tuning
spark.conf.set("spark.sql.files.maxPartitionBytes", "128m")
```

## Read Optimization

Spark determines partition count based on input file sizes. The `maxPartitionBytes` setting controls maximum partition size.

```python
# Default is 128 MB — increase for fewer, larger partitions
spark.conf.set("spark.sql.files.maxPartitionBytes", "256m")

# Decrease for more parallelism on smaller files
spark.conf.set("spark.sql.files.maxPartitionBytes", "64m")
```

**Best practices for reads:**

- Prefer Delta/Parquet formats over CSV/JSON for columnar pruning
- Provide explicit schemas for JSON/XML instead of relying on inference
- Use `.option("samplingRatio", 0.1)` if schema inference is necessary
- Apply column pruning (`select()`) and row filtering (`filter()`) before joins

## Shuffle Optimization

Shuffles are the most expensive Spark operation. The default `spark.sql.shuffle.partitions = 200` is rarely optimal.

**Tuning guidelines:**

| Data Volume | Recommended Partitions |
|-------------|----------------------|
| < 1 GB | 10–20 |
| 1–10 GB | 50–100 |
| 10–100 GB | 200 (default) |
| > 100 GB | 400–2000 |

```python
spark.conf.set("spark.sql.shuffle.partitions", "100")
```

With AQE enabled, Spark dynamically coalesces shuffle partitions, reducing the need for manual tuning.

## Write Optimization

**Auto Compaction** for ingestion pipelines with frequent small writes:

```python
spark.conf.set("spark.databricks.delta.autoCompact.enabled", "true")
```

This replaces the need for scheduling separate OPTIMIZE jobs for compaction on new tables.

**Optimize Write** reduces the number of output files:

```python
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")
```

## Task Parallelism

`spark.task.cpus` controls CPU cores allocated per Spark task (default: 1).

| Scenario | Setting | Effect |
|----------|---------|--------|
| CPU-bound tasks, no memory pressure | `0.5` | More tasks run in parallel |
| Memory-intensive tasks causing OOM | `2` | More memory per task |
| Default / general workloads | `1` | Balanced allocation |

```python
spark.conf.set("spark.task.cpus", "2")  # For memory-heavy tasks
```

## Session Timeout Management

Default session timeout is 20 minutes of inactivity.

**Change at notebook level:**

1. Open notebook and start a session.
2. Click the **Session Ready** indicator in the lower-left corner.
3. Update the timeout duration in the dialog.

**Change at workspace level:**

1. Go to Workspace Settings → Data Engineering/Science → Spark Settings.
2. Under the Jobs tab, adjust the session timeout duration.

> Active idle sessions consume CU capacity. Always stop sessions when not in use.

## High Concurrency Sessions

Run multiple notebooks in a single Spark session to optimize resource usage. Compute resources are shared across child notebooks.

```python
# Run notebooks in parallel
mssparkutils.notebook.runMultiple(["NotebookA", "NotebookB"])
```

**Concurrency limit:** The number of concurrent notebooks is constrained by driver cores. A Medium node driver with 8 cores supports up to 8 concurrent notebooks (each REPL consumes one driver core).

## Resource Profiles

Predefined profiles auto-configure Spark for specific workload patterns.

| Profile | Key Configurations |
|---------|--------------------|
| `Default` | General-purpose balance |
| `readHeavyforSpark` | Enables V-Order, optimized for queries |
| `ReadHeavy` | Same as above, alias |
| Write-heavy (default for new workspaces) | V-Order disabled for faster ingestion |

Switch profiles via environment configuration or session-level properties.
