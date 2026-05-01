# Spark UI Interpretation Guide for Microsoft Fabric

## Table of Contents

- [Accessing Spark UI in Fabric](#accessing-spark-ui-in-fabric)
- [Jobs Tab](#jobs-tab)
- [Stages Tab](#stages-tab)
- [Task Metrics Deep Dive](#task-metrics-deep-dive)
- [Storage Tab](#storage-tab)
- [SQL Tab](#sql-tab)
- [Executors Tab](#executors-tab)
- [Environment Tab](#environment-tab)
- [Common Patterns and What They Mean](#common-patterns-and-what-they-mean)

## Accessing Spark UI in Fabric

### From a Notebook

1. While a notebook session is active, click the Spark session indicator at the bottom of the notebook
2. Select "Open Spark UI" or navigate to Monitoring Hub
3. The Spark UI opens showing the application details

### From Monitoring Hub

1. Navigate to Monitoring Hub in your Fabric workspace
2. Find the Spark application (notebook run, Spark job definition)
3. Click on the application name to open details
4. Select "View Spark UI"

## Jobs Tab

The Jobs tab shows all Spark jobs triggered by actions (e.g., `count()`, `write()`, `show()`).

### Key Columns

- **Job Id**: Sequential identifier for each action
- **Description**: The action that triggered the job (e.g., `save at NativeMethodAccessorImpl.java`)
- **Duration**: Wall-clock time for the entire job
- **Stages**: Shows succeeded/total stages (e.g., `3/3`)

### What to Look For

- **Long-running jobs**: Click to drill into stages
- **Failed jobs**: Red indicators, click for error details
- **Skipped stages**: Stages that reused cached or shuffle data (normal, efficient)

## Stages Tab

The Stages tab provides the most actionable performance data. Each stage represents a set of tasks that can execute in parallel.

### Stage Detail Metrics

Click on a stage to see:

- **Summary Metrics**: Aggregated min, 25th, median, 75th, max for all task metrics
- **Task List**: Individual task execution details
- **DAG Visualization**: Visual representation of the stage's operations

### Critical Metrics to Check

**Duration Distribution**:
```
Min: 2s | 25th: 3s | Median: 4s | 75th: 5s | Max: 180s
                                                 ^^^^
If max >> median (e.g., 40x), you have data skew.
```

**Shuffle Read/Write**:
```
Shuffle Read: 45.2 GB total across 200 tasks
Shuffle Write: 12.1 GB total across 200 tasks

If shuffle is large relative to input data, consider broadcast joins
or reducing shuffle partitions.
```

**GC Time**:
```
If GC Time > 10% of task duration, memory is under pressure.
Example: Task duration 60s, GC time 15s = 25% (problematic)
```

**Spill Metrics**:
```
Spill (Memory): Data serialized to free execution memory
Spill (Disk): Data written to disk when memory exhausted

Any disk spill > 1 GB per task warrants investigation.
```

## Task Metrics Deep Dive

### Reading the Task Table

Each row represents one task (one partition of work). Sort by Duration (descending) to find stragglers.

| Metric | What It Tells You |
|--------|-------------------|
| Duration | Total task time including compute, I/O, GC |
| GC Time | Time spent in garbage collection |
| Input Size | Bytes read from source (file scan) |
| Output Size | Bytes written by this stage |
| Shuffle Read | Bytes pulled from other executors |
| Shuffle Write | Bytes written for next stage to read |
| Spill (Memory) | Bytes spilled from execution memory |
| Spill (Disk) | Bytes written to local disk (overflow) |

### Skew Detection Pattern

```
Task 0:   Duration 3s,   Input 50 MB
Task 1:   Duration 4s,   Input 55 MB
Task 2:   Duration 3s,   Input 48 MB
...
Task 150: Duration 300s,  Input 15 GB   ← SKEWED TASK
Task 151: Duration 3s,   Input 52 MB

Diagnosis: Partition 150 has 300x more data than average.
Fix: See data-skew-resolution.md
```

### Spill Detection Pattern

```
Task 0:   Duration 5s,   Spill(Disk) 0 B
Task 1:   Duration 45s,  Spill(Disk) 2.5 GB   ← SPILLING
Task 2:   Duration 5s,   Spill(Disk) 0 B

Diagnosis: Task 1 exceeded memory and spilled to disk.
Fix: Increase partitions, increase executor memory, or fix skew.
```

## Storage Tab

Shows cached DataFrames and their memory/disk usage.

### Key Information

- **RDD Name**: The cached DataFrame identifier
- **Storage Level**: Memory only, memory+disk, etc.
- **Fraction Cached**: Percentage of partitions actually in memory
- **Size in Memory**: Memory consumed by cached data
- **Size on Disk**: Data spilled to disk (for MEMORY_AND_DISK level)

### Warning Signs

- **Fraction Cached < 100%**: Not all partitions fit in memory; some evicted
- **Large Size in Memory**: Cached data consuming most of storage memory
- **Many cached RDDs**: May be consuming too much memory

## SQL Tab

Shows DataFrame operations as SQL-like execution plans with metrics.

### Reading the SQL Plan

Click on a completed SQL query to see the physical plan with runtime metrics:

- **Scan**: File reads (check rows output and bytes read)
- **Filter**: Row filtering (check rows input vs output for pushdown effectiveness)
- **Exchange**: Shuffle operations (check data size)
- **BroadcastExchange**: Broadcast operations (check time and data size)
- **HashAggregate**: Aggregation (check rows processed)
- **SortMergeJoin**: Large table join (check both sides' row counts)

### Identifying Bottleneck Operators

The plan shows cumulative time for each operator. Look for:
- **Exchange** with large data sizes (shuffle bottleneck)
- **Scan** with many files (small file problem)
- **SortMergeJoin** that could be BroadcastHashJoin (missed broadcast opportunity)

## Executors Tab

Shows resource utilization across all executors and the driver.

### Key Columns

- **Address**: Executor hostname and port
- **Status**: Active or Dead
- **Storage Memory**: Used / Total
- **Disk Used**: Local disk consumption
- **Cores**: Allocated cores
- **Active Tasks**: Currently running tasks
- **Failed Tasks**: Tasks that failed on this executor
- **Input Size**: Total bytes read
- **Shuffle Read/Write**: Total shuffle I/O

### Warning Signs

- **Dead executors**: Executor lost (likely OOM)
- **Storage Memory near 100%**: Cache pressure
- **High Shuffle Read on few executors**: Data skew
- **Failed Tasks > 0**: Check logs for error details

## Environment Tab

Shows all Spark configuration values for the session.

### Important Settings to Verify

```
spark.sql.adaptive.enabled = true
spark.sql.shuffle.partitions = 200 (or auto)
spark.sql.autoBroadcastJoinThreshold = 10485760 (10 MB)
spark.sql.files.maxPartitionBytes = 134217728 (128 MB)
spark.executor.memory = (check matches your environment config)
spark.driver.memory = (check matches your environment config)
spark.microsoft.delta.optimizeWrite.enabled = (true/false)
spark.ms.autotune.enabled = (true/false)
spark.native.enabled = (true/false)
```

## Common Patterns and What They Mean

### Pattern: One Very Slow Stage

Likely cause: Shuffle or join on skewed data. Open the stage, check task duration distribution.

### Pattern: All Stages Slow

Likely cause: Undersized compute (too few/small nodes), capacity throttling, or reading from non-optimized tables. Check executor count and node size.

### Pattern: Lots of Small Stages

Likely cause: Many small file reads or overly fragmented query plan. Check if OPTIMIZE has been run on source tables.

### Pattern: Executor Deaths Mid-Job

Likely cause: OOM. Check executor memory settings, look for skewed tasks or large collect operations. See memory-and-spill-tuning.md.

### Pattern: High GC Across All Executors

Likely cause: Memory pressure from too many cached DataFrames, large shuffle buffers, or undersized executors. Unpersist unneeded caches, increase partitions, or scale up nodes.
