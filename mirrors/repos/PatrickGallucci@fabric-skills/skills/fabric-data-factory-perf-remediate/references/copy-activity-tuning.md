# Copy Activity Tuning Guide

Detailed guidance for optimizing Microsoft Fabric Data Factory copy activity performance, covering Intelligent Throughput Optimization (ITO), parallelism, partitioning strategies, and staging.

## Table of Contents

- [Understanding Copy Activity Execution Stages](#understanding-copy-activity-execution-stages)
- [Intelligent Throughput Optimization (ITO)](#intelligent-throughput-optimization-ito)
- [Degree of Copy Parallelism](#degree-of-copy-parallelism)
- [Partition Options for SQL Sources](#partition-options-for-sql-sources)
- [Staging Configuration](#staging-configuration)
- [Performance Benchmarks](#performance-benchmarks)
- [Step-by-Step Tuning Process](#step-by-step-tuning-process)

## Understanding Copy Activity Execution Stages

Every copy activity run includes multiple stages. The Duration Breakdown in the Monitoring Hub shows:

| Stage | Description | Optimization Target |
|-------|-------------|---------------------|
| Queue | Time waiting for compute resources | Reduce concurrent activities or upgrade SKU |
| Pre-copy script | Script execution before data transfer | Optimize or remove pre-copy scripts |
| Transfer | Actual data movement | ITO, parallelism, partitioning |
| Post-copy script | Script execution after data transfer | Optimize or remove post-copy scripts |

Access the Duration Breakdown by selecting the run details icon (glasses) in the Monitoring Hub.

## Intelligent Throughput Optimization (ITO)

ITO controls the maximum CPU, memory, and network resource allocation for a copy activity.

### ITO Settings

| Setting | Max Value | Use Case |
|---------|-----------|----------|
| Auto | Service-determined | Default; good starting point |
| Standard | 64 | Cost-conscious workloads |
| Balanced | 128 | Balance between cost and speed |
| Maximum | 256 | Fastest possible throughput |
| Custom | 4-256 | Fine-grained control |

### Recommendations

- Start with **Auto** and review the `usedDataIntegrationUnits` in the copy activity output
- If throughput is insufficient, step up to **Balanced** or **Maximum**
- For cost optimization, set a custom value just above the observed `usedDataIntegrationUnits`
- Higher ITO values do not guarantee proportional throughput increases; bottlenecks may be elsewhere

### Checking Actual ITO Used

After a copy activity run completes, check the output JSON for:

```json
{
  "usedDataIntegrationUnits": 16,
  "effectiveIntegrationRuntime": "AutoResolveIntegrationRuntime"
}
```

If the actual value is significantly lower than your setting, the service auto-optimized based on the workload.

## Degree of Copy Parallelism

Controls the maximum number of threads reading from source or writing to destination.

### Default Behavior

The service dynamically determines optimal parallelism based on source-sink pair and data pattern.

### When to Override

- Source database is under-utilized (CPU < 30%)
- Destination can handle more concurrent writes
- Default parallelism is too aggressive (causing source throttling)

### Recommended Values by Scenario

| Scenario | Recommended Parallelism |
|----------|------------------------|
| SQL to Fabric Warehouse | Start with Auto; cap at 32 (Warehouse limit) |
| SQL to Fabric Lakehouse | Auto; increase if source can handle it |
| File store to Lakehouse | Auto; parallelism is per-file |
| Large SQL table (partitioned) | Match to partition count or cap at 50-85 |

### Critical Constraint: Fabric Warehouse Sink

Fabric Warehouse can execute a maximum of **32 concurrent queries**. Setting parallelism too high causes throttling. Use:

```
Degree of copy parallelism <= 32
```

## Partition Options for SQL Sources

Partitioning dramatically improves throughput for large SQL tables by enabling parallel reads.

### Option 1: None (Default)

Single-threaded read from source. Suitable for small tables only.

### Option 2: Physical Partitions of Table

Uses existing table partitions. Best when table has well-distributed partitions.

| Physical Partitions | Auto Parallel Copies | Typical Duration Improvement |
|--------------------|--------------------|------------------------------|
| 8 | 8 | ~5x faster than None |
| 85 | 85 | ~17x faster than None |

### Option 3: Dynamic Range

Service generates parallel queries against a numeric column. Best for large tables without physical partitions or with skewed partition distributions.

#### Configuration

| Parameter | Required | Description |
|-----------|----------|-------------|
| Partition Column | Yes | Integer or date column for range splitting |
| Partition Upper Bound | Optional (recommended) | Max value of partition column |
| Partition Lower Bound | Optional (recommended) | Min value of partition column |

#### Pre-calculate Bounds (Recommended)

Pre-calculating bounds avoids an extra query to determine ranges:

```sql
SELECT MIN(Id) AS LowerBound, MAX(Id) AS UpperBound
FROM MySourceTable
```

#### Heap vs Clustered Index Performance

| Table Type | Dynamic Range + Auto Parallel | Dynamic Range + Parallel 50 |
|-----------|-------------------------------|----------------------------|
| Heap | Slower (many parallel copies) | Faster (controlled parallelism) |
| Clustered Index | Fast (efficient range scans) | Fast (efficient range scans) |

For heap tables, set **Degree of copy parallelism** to 50 to avoid excessive concurrent queries.

### Isolation Level Impact

| Isolation Level | Duration | Capacity Units | Recommendation |
|----------------|----------|---------------|----------------|
| None (default) | Baseline | Baseline | Good default |
| Read Uncommitted | ~4% faster | ~5% less | Best for non-critical reads |
| Read Committed | ~78% slower | ~4% more | Avoid unless required |

## Staging Configuration

Staging is **required** when the copy activity sink is Fabric Warehouse. Data flows through an interim storage before loading.

### Workspace Staging (Recommended)

Uses built-in Fabric workspace staging storage. Ensure the last modified user for the pipeline has at least **Contributor** role.

### External Staging

Uses an external storage account. Requires connection configuration and enableCompression setting.

### Staging Best Practices

- Enable compression for staging to reduce transfer time
- Use workspace staging unless compliance requires external storage
- Monitor staging storage for cleanup (temporary files)

## Performance Benchmarks

Reference benchmarks for 1.5 billion records from Azure SQL Database:

### To Fabric Warehouse

| Partition | Parallelism | Used Copies | Duration | Capacity Units |
|-----------|------------|-------------|----------|---------------|
| None | Auto | 1 | 02:23:21 | 51,839 |
| Physical (8) | Auto | 8 | 00:26:29 | 49,320 |
| Physical (85) | Auto | 85 | 00:08:31 | 108,000 |
| Dynamic Range (Heap) | Auto | 242 | 00:39:03 | 282,600 |
| Dynamic Range (Heap) | 50 | 50 | 00:13:05 | 92,159 |
| Dynamic Range (Clustered) | Auto | 251 | 00:09:02 | 64,080 |
| Dynamic Range (Clustered) | 50 | 50 | 00:08:38 | 55,440 |

### Key Takeaways

1. Partitioning provides 5x-17x improvement over default
2. Clustered index tables perform best with Dynamic Range
3. For heap tables, capping parallelism at 50 gives best balance of speed and cost
4. Physical partitions with 85+ partitions match Dynamic Range performance

## Step-by-Step Tuning Process

1. **Establish baseline**: Run copy with default settings, record duration and CU consumption
2. **Check Duration Breakdown**: Identify if bottleneck is queue, transfer, or script execution
3. **Set ITO to Maximum**: Re-run and compare throughput
4. **Enable partitioning**: For SQL sources, try Physical partitions first, then Dynamic Range
5. **Pre-calculate bounds**: For Dynamic Range, query min/max before running
6. **Adjust parallelism**: If source is being overwhelmed, cap at 50; if under-utilized, increase
7. **Enable staging**: Required for Warehouse sink; optional but helpful for large Lakehouse loads
8. **Validate consistency**: Enable `validateDataConsistency` for critical loads (impacts performance)
9. **Iterate**: Compare each run's metrics and find the optimal configuration
10. **Document**: Record the optimal settings for each pipeline in a runbook
