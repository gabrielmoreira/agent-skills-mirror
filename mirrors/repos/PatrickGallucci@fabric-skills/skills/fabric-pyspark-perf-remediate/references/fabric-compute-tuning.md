# Fabric Compute Tuning

## Table of Contents

- [Capacity and CU Mapping](#capacity-and-cu-mapping)
- [Starter Pools vs Custom Pools](#starter-pools-vs-custom-pools)
- [Resource Profile Selection](#resource-profile-selection)
- [Autotune Configuration](#autotune-configuration)
- [Native Execution Engine](#native-execution-engine)
- [Concurrency and Throttling](#concurrency-and-throttling)
- [Autoscale Billing for Spark](#autoscale-billing-for-spark)
- [Environment Configuration](#environment-configuration)

## Capacity and CU Mapping

Every Fabric CU (Capacity Unit) translates to 2 Apache Spark VCores.

| SKU | Capacity Units | Spark VCores | Max Concurrent Spark Jobs |
|-----|---------------|-------------|--------------------------|
| F2 | 2 | 4 | 1 |
| F4 | 4 | 8 | 1 |
| F8 | 8 | 16 | 1 |
| F16 | 16 | 32 | 2 |
| F32 | 32 | 64 | 4 |
| F64 | 64 | 128 | 8 |
| F128 | 128 | 256 | 16 |
| F256 | 256 | 512 | 32 |
| F512 | 512 | 1024 | 64 |

**Throttling**: When capacity utilization exceeds available CUs, additional Spark jobs are queued. Check the Monitoring Hub for queued jobs.

## Starter Pools vs Custom Pools

### Starter Pools

- Pre-warmed clusters, session start in 5-10 seconds
- Medium-sized nodes by default
- Autoscaling based on workload
- Best for: interactive development, ad-hoc queries, prototyping

### Custom Pools

- Configurable node size (Small to XX-Large)
- Configurable min/max node count
- Longer cold-start time
- Best for: production workloads with known resource requirements

### Choosing Pool Type

| Scenario | Recommended Pool |
|----------|-----------------|
| Notebook development | Starter Pool |
| Scheduled ETL pipeline | Custom Pool (sized for workload) |
| Interactive data exploration | Starter Pool |
| Large-scale data processing | Custom Pool (Large/X-Large nodes) |
| Memory-intensive ML training | Custom Pool (X-Large/XX-Large nodes) |

## Resource Profile Selection

Resource profiles apply predefined Spark configurations optimized for specific workload patterns. Set at the workspace level in Data Engineering/Science > Spark Settings.

### writeHeavy (Default for New Workspaces)

```
Optimized for:
- ETL pipelines
- Batch and streaming ingestion
- Data transformation at scale

Key settings:
- VOrder: DISABLED
- Optimized for write throughput
- Better data ingestion performance
```

### readHeavyForSpark

```
Optimized for:
- Interactive Spark SQL queries
- Exploratory data analysis
- Read-heavy analytics workloads

Key settings:
- VOrder: ENABLED
- Optimized for Spark read operations
```

### readHeavyForPBI

```
Optimized for:
- Power BI DirectQuery
- SQL analytics endpoint queries
- Dashboard and report serving

Key settings:
- VOrder: ENABLED
- Optimized for downstream BI consumption
```

### Overriding at Environment Level

If your workspace uses `writeHeavy` but a specific notebook needs read optimization:

```python
# Override VOrder for this session only
spark.conf.set("spark.sql.parquet.vorder.default", "true")
```

## Autotune Configuration

Autotune uses ML to iteratively optimize three Spark settings per query.

### Enabling Autotune

**Via Environment**:
Navigate to Environment > Spark Properties > Add:
```
spark.ms.autotune.enabled = true
```

**Via Notebook Session**:
```python
spark.conf.set("spark.ms.autotune.enabled", "true")
```

### What Autotune Optimizes

| Configuration | Default | Autotune Range |
|--------------|---------|---------------|
| `spark.sql.shuffle.partitions` | 200 | Adjusted per query |
| `spark.sql.autoBroadcastJoinThreshold` | 10 MB | Adjusted per query |
| `spark.sql.files.maxPartitionBytes` | 128 MB | Adjusted per query |

### Requirements and Limitations

- Compatible with Fabric Runtime 1.1 and 1.2 only
- NOT compatible with Runtime versions higher than 1.2
- NOT compatible with high concurrency mode
- NOT compatible with private endpoints
- Works with autoscaling
- Needs 20-25 iterations to learn optimal settings
- Only effective for queries running >15 seconds
- Targets Spark SQL API queries (not RDD API)

### Monitoring Autotune

Check driver logs for entries starting with `[Autotune]`:

| Status | Meaning |
|--------|---------|
| `AUTOTUNE_DISABLED` | Autotune is off, enable it |
| `QUERY_TUNING_DISABLED` | Query tuning specifically disabled |
| `QUERY_PATTERN_NOT_MATCH` | Query structure not suitable (e.g., write-only) |
| `QUERY_DURATION_TOO_SHORT` | Query runs <15 seconds, too fast to optimize |
| `QUERY_TUNING_SUCCEED` | Optimization applied successfully |

## Native Execution Engine

The Native Execution Engine compiles Spark operations into native code for faster execution, bypassing the JVM for supported operations.

### Enabling

```python
spark.conf.set("spark.native.enabled", "true")
```

Or via Environment Spark Properties:
```
spark.native.enabled = true
```

### Supported Operations

The native engine accelerates common operations including scans, filters, projections, aggregations, and joins on supported data types. Unsupported operations automatically fall back to standard Spark execution.

### When to Enable

- Compute-intensive workloads with heavy aggregations
- Large scan operations on Parquet/Delta
- Workloads dominated by filter + aggregate patterns
- Not beneficial for workloads dominated by Python UDFs or I/O-bound operations

## Concurrency and Throttling

### Understanding Throttling

When total Spark compute demand exceeds capacity, Fabric queues additional jobs. Signs of throttling:

- Jobs show "Pending" status in Monitoring Hub for extended periods
- "Session not available" errors when starting notebooks
- Pipeline activities waiting for Spark session

### Mitigation Strategies

1. **Stagger scheduled jobs**: Avoid running all ETL pipelines at the same time
2. **Right-size compute**: Use smaller node sizes for light workloads
3. **Use autoscale billing**: Offload bursty workloads to pay-as-you-go compute
4. **Monitor capacity**: Track CU utilization trends in Microsoft Fabric Capacity Metrics app

## Autoscale Billing for Spark

Autoscale Billing provides pay-as-you-go compute separate from Fabric capacity.

### When to Use

| Use Case | Capacity Model | Autoscale Billing |
|----------|---------------|-------------------|
| Predictable daily ETL | Recommended | Possible |
| Ad-hoc heavy analytics | Possible | Recommended |
| Bursty workloads | Not ideal | Recommended |
| Cost-sensitive steady state | Recommended | Not ideal |

### Key Characteristics

- Spark jobs run on dedicated serverless resources (not capacity)
- Billed per Spark job runtime (0.5 CU Hour per job)
- No idle compute costs
- Set maximum CU limit to control budget
- Integrates with Azure Quota Management

## Environment Configuration

### Creating an Optimized Environment

```yaml
# SparkCompute.yml structure
enable_native_execution_engine: true
driver_cores: 8
driver_memory: "56g"
executor_cores: 8
executor_memory: "56g"
dynamic_executor_allocation:
  enabled: true
  min_executors: 1
  max_executors: 10
runtime_version: "1.3"
spark_conf:
  spark.ms.autotune.enabled: "true"
  spark.microsoft.delta.optimizeWrite.enabled: "true"
  spark.sql.adaptive.enabled: "true"
```

### Environment Spark Properties for Performance

Set these in Environment > Spark Properties:

```
spark.sql.adaptive.enabled = true
spark.sql.adaptive.coalescePartitions.enabled = true
spark.sql.adaptive.skewJoin.enabled = true
spark.microsoft.delta.optimizeWrite.enabled = true
spark.sql.parquet.vorder.default = false  (or true for read-heavy)
spark.native.enabled = true
```
