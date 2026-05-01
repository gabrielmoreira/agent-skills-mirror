# Monitoring and Diagnostics Reference

## Table of Contents

- [Monitoring Hub Navigation](#monitoring-hub-navigation)
- [Spark UI Deep Dive](#spark-ui-deep-dive)
- [Notebook Contextual Monitoring](#notebook-contextual-monitoring)
- [Spark Advisor Interpretation](#spark-advisor-interpretation)
- [Resource Utilization Analysis](#resource-utilization-analysis)
- [Run Series and Anomaly Detection](#run-series-and-anomaly-detection)
- [Spark Monitoring APIs](#spark-monitoring-apis)
- [Log Analysis](#log-analysis)
- [Capacity Metrics App](#capacity-metrics-app)

---

## Monitoring Hub Navigation

The Monitoring Hub is the central portal for all Spark activities across a workspace.

### Accessing the Monitoring Hub

1. From the Fabric portal navigation pane, select **Monitor**.
2. Use filters to narrow by item type (Notebook, Spark Job Definition, Lakehouse).
3. Filter by status: In Progress, Completed, Failed, Cancelled.

### Key Actions from Monitoring Hub

- **View active sessions**: See all running Spark applications and their VCore consumption.
- **Cancel jobs**: Free up capacity by cancelling unnecessary or stuck jobs.
- **Drill down**: Click any Spark application to open its detail monitoring page.
- **Historical view**: Switch to historical tab to see past runs and access run series.

---

## Spark UI Deep Dive

Access Spark UI from any notebook cell's context menu or from the Spark application detail page.

### Jobs Tab

Displays all Spark jobs within the application. Each notebook cell that triggers a Spark action creates one or more jobs.

**What to look for**:

- Jobs with unusually long duration relative to data size
- Jobs with many failed or killed tasks (indicates OOM or skew)
- Job descriptions map back to your code operations

### Stages Tab

Each job is broken into stages separated by shuffle boundaries.

**Key metrics per stage**:

| Metric | Healthy Range | Problem Indicator |
|--------|--------------|-------------------|
| Task count | Matches partition count | Exactly 200 = default partitions |
| Duration (median vs max) | Max < 2x median | Max > 10x median = data skew |
| Shuffle Read | Proportional to data | >> input data = cartesian/explode |
| Shuffle Write | Proportional to output | Unexpected large = wide transforms |
| Spill (Memory/Disk) | 0 | Any spill = insufficient memory per partition |

### SQL Tab

Shows the physical execution plan for Spark SQL queries. Critical for understanding join strategies and scan operations.

**Look for**:

- `BroadcastHashJoin` vs `SortMergeJoin` — broadcast is faster for small tables
- `FileScan` with `PushedFilters` — confirms predicate pushdown is working
- `Exchange` nodes — each represents a shuffle stage
- Autotune status indicators (when autotune is enabled)

### Storage Tab

Shows cached RDDs and DataFrames.

**Look for**:

- Fraction cached < 100% — indicates memory pressure
- Large cached datasets that are no longer needed — call `unpersist()`

### Environment Tab

Shows all Spark configuration properties for the current session.

**Useful for verifying**:

- `spark.sql.shuffle.partitions` actual value
- `spark.sql.autoBroadcastJoinThreshold` actual value
- `spark.ms.autotune.enabled` status
- Resource profile settings
- Memory allocation per executor

---

## Notebook Contextual Monitoring

### Cell-Level Progress Bar

Each notebook cell shows a real-time progress bar with:

- Number of jobs and stages
- Task completion count
- Duration per stage

### Resource Usage per Cell

Click the **Resources** tab below a cell (Runtime 3.4+) to see executor allocation and usage for that specific cell's execution.

### Real-Time Logs

Access Spark logs directly below the cell output:

1. Click the log icon below the cell
2. Filter by log level: Error, Warning, Info
3. Search for specific exception patterns

---

## Spark Advisor Interpretation

The built-in Spark Advisor analyzes notebook execution and provides three types of advice:

### Info (Blue)

Informational insights about execution characteristics. Examples:

- Query execution statistics
- Partition information
- Cache utilization notes

### Warning (Yellow)

Performance concerns that should be addressed. Examples:

- **Data Skew Detected**: A partition has significantly more data than others
- **Too Many Small Files**: Delta table has accumulated fragmented files
- **Unused Cache**: Cached data is not being reused

### Error (Red)

Critical issues requiring immediate attention. Examples:

- **Out of Memory**: Executor or driver ran out of memory
- **Task Failures**: Tasks failed and were retried
- **Serialization Errors**: Data type or serialization problems

### Responding to Skew Detection

When the Spark Advisor shows skew detection:

1. Note the skewed key values and their counts.
2. Review the affected join or aggregation operation.
3. Apply one of the skew resolution strategies from the [configuration tuning guide](./spark-configuration-tuning.md#data-skew-resolution).
4. Re-run and verify the advisor no longer flags skew.

---

## Resource Utilization Analysis

### Executor Usage Graph

Access from Spark application detail page → Resources tab. Four line graphs:

| Line | Description | Healthy Pattern |
|------|-------------|-----------------|
| Running | Cores actively executing tasks | Should be close to Allocated |
| Idled | Cores allocated but not running tasks | Should be minimal during active stages |
| Allocated | Total cores currently assigned | Should scale with autoscale |
| Maximum | Max cores available per pool config | Upper bound for scaling |

### Identifying Resource Problems

**Underutilization** (Running << Allocated):

- Too many partitions relative to data size
- Barriers or synchronization points in the DAG
- Driver-side bottleneck (collect, toPandas)

**Over-subscription** (tasks > cores):

- Normal when tasks complete quickly and queue for execution
- Problem if task queue grows continuously

**Flat Maximum line with throttled jobs**:

- Capacity is fully consumed
- Need to upgrade SKU or reduce concurrent workloads

---

## Run Series and Anomaly Detection

### Accessing Run Series

1. Monitoring Hub → Historical View → select a Spark application
2. More Options → Monitor Run Series

Or from notebook/Spark Job Definition:

1. Item Context Menu → Recent Runs
2. Select an application → More Options → Monitor Run Series

### Interpreting the Run Series Chart

The chart shows duration trend with data I/O overlay:

- **Duration spikes**: Indicate regression, often caused by data growth or config changes
- **Data input increase without duration increase**: Good scalability
- **Duration increase without data change**: Configuration or infrastructure issue

### Anomaly Detection

Fabric automatically flags anomalous runs. When flagged:

1. Click the anomalous data point to view its Spark application detail.
2. Compare the Spark UI stages with a normal run.
3. Look for: new shuffle stages, missing broadcast joins, increased partition count.

---

## Spark Monitoring APIs

### Workspace-Level APIs

List all Spark applications in a workspace:

```
GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/spark/livySessions
```

### Item-Level APIs

List Spark applications for a specific notebook:

```
GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/notebooks/{notebookId}/livySessions
```

### Single Application Diagnostics

Get detailed metrics for a specific Spark application:

```
GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/notebooks/{notebookId}/livySessions/{sessionId}
```

### Available Deep-Dive APIs

| API | Purpose |
|-----|---------|
| Spark Open-source metrics APIs | Spark History Server compatible metrics |
| Livy Log API | Session-level diagnostic logs |
| Driver Log API | Driver process logs for application errors |
| Executor Log API | Executor logs for distributed execution issues |
| Resource Usage APIs | Core and memory utilization data |

---

## Log Analysis

### Common Log Patterns to Search

| Pattern | Indicates |
|---------|-----------|
| `java.lang.OutOfMemoryError` | Executor or driver memory exhausted |
| `SparkException: Job aborted` | Task failures exceeded retry limit |
| `ShuffleMapTask` + `FetchFailedException` | Shuffle service issues or OOM during shuffle |
| `FileNotFoundException` on Delta path | Concurrent write conflict or vacuum too aggressive |
| `TooManyRequestsForCapacity` | Capacity throttling (HTTP 430) |
| `WARN TaskSetManager: Lost task` | Task failure, check subsequent lines for cause |

### Accessing Logs

**From notebook**: Click the log icon below the cell output.

**From Monitoring Hub**: Click the Spark application → Logs tab.

**Via API**: Use the Driver Log or Executor Log APIs for programmatic access.

---

## Capacity Metrics App

### Installation and Access

1. Install the Microsoft Fabric Capacity Metrics app from AppSource.
2. Select item types: Notebook, Lakehouse, Spark Job Definition.
3. Adjust the time range to analyze specific periods.

### Key Metrics for Spark

| Metric | What It Tells You |
|--------|-------------------|
| CU consumption per item | Which notebooks/jobs consume the most capacity |
| Duration trends | Whether jobs are getting slower over time |
| Concurrent utilization | Peak concurrency and throttling frequency |

### Capacity Billing Formula

For any Spark job:

```
CU Hours = Total Spark VCores / 2 * Duration in Hours
```

One CU = 2 Spark VCores. For autoscale billing, you pay only for compute used during job execution with no idle costs.
