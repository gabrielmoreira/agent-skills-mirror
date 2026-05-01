# OneLake Capacity Unit Consumption Optimization

Guide for understanding, monitoring, and reducing OneLake CU consumption across read,
write, and iterative operations.

## Table of Contents

- [OneLake Billing Model](#onelake-billing-model)
- [Transaction CU Rates](#transaction-cu-rates)
- [High-Cost Operations to Watch](#high-cost-operations-to-watch)
- [Cost Reduction Strategies](#cost-reduction-strategies)
- [Monitoring CU Consumption](#monitoring-cu-consumption)
- [BCDR Cost Impact](#bcdr-cost-impact)
- [Diagnostics Overhead](#diagnostics-overhead)

---

## OneLake Billing Model

OneLake has two billing dimensions:

1. **Storage**: Pay-as-you-go per GB, does NOT consume Fabric CUs.
   Soft-deleted data is billed at the same rate as active data.
2. **Transactions**: Consume Fabric Capacity Units (CUs) based on operation type
   and volume.

### Access Paths: Proxy vs Redirect

OneLake supports two access paths. Both now share identical CU rates:

- **Redirect**: Application is redirected to storage directly (lower load on OneLake service)
- **Proxy**: Request proxied through OneLake service

The access path is determined by the workload and network conditions — not user-configurable.

---

## Transaction CU Rates

### Standard Operations (No BCDR)

| Operation | Unit of Measure | CU Seconds |
|-----------|----------------|------------|
| Read | Every 4 MB, per 10,000 | 104 |
| Write | Every 4 MB, per 10,000 | 1,626 |
| Other Operations | Per 10,000 | 104 |
| Iterative Read | Per 10,000 | 1,626 |
| Iterative Write | Per 100 | 1,300 |

### Key Insight: Write and Iterative Operations Are Expensive

- **Writes cost ~15.6x more** than reads per transaction
- **Iterative writes cost 13,000 CU seconds per 10,000 operations** (compared to
  104 for reads) — that's 125x more expensive
- **Iterative reads** (list operations) are 15.6x more expensive than standard reads

### How File Size Affects Transactions

For files larger than 4 MB, OneLake counts one transaction per 4 MB block.

**Example**: 10,000 read operations where each file is 16 MB:
- Each read = 4 transactions (16 MB / 4 MB blocks)
- Total: 40,000 transactions = 416 CU seconds

For files smaller than 4 MB, a full transaction is still counted per file, making
small file reads proportionally more expensive.

---

## High-Cost Operations to Watch

### 1. Iterative Write Operations

At 1,300 CU seconds per 100 operations, iterative writes are the most expensive
OneLake operation. These occur during:

- Directory creation/restructuring
- Metadata updates across many files
- Batch file moves or renames

**Mitigation**: Batch directory operations, minimize file-level metadata writes.

### 2. Standard Write Operations

At 1,626 CU seconds per 10,000, writes dominate CU consumption for ETL pipelines.

**Mitigation**:
- Write larger, fewer files (enable Optimized Write)
- Reduce write frequency with micro-batching
- Use `coalesce()` before writing to reduce output file count

### 3. Iterative Read (List) Operations

Directory listing operations at 1,626 CU seconds per 10,000. These add up when:

- Scanning directories with many small files
- Delta log reads on tables with many transactions
- Discovery scans across deeply nested folder structures

**Mitigation**:
- VACUUM tables to reduce Delta log entries
- Compact files to reduce directory entry counts
- Use specific file paths instead of directory scans where possible

### 4. Small File Reads

Each file under 4 MB counts as one full transaction. Reading 10,000 x 100 KB files
costs the same as reading 10,000 x 4 MB files.

**Mitigation**: Compact small files with OPTIMIZE.

---

## Cost Reduction Strategies

### Strategy 1: Optimize File Sizes

Target ~1 GB files for analytical workloads. This maximizes data per transaction.

```python
# Enable Optimized Write to auto-merge small partitions
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")
```

### Strategy 2: Reduce Write Frequency

Replace frequent small writes with less frequent larger batch writes:

```python
# Use trigger intervals for streaming to batch events
rawData.writeStream \
    .format("delta") \
    .trigger(processingTime="5 minutes") \
    .option("checkpointLocation", "Files/checkpoint") \
    .toTable("my_table")
```

### Strategy 3: Minimize Iterative Operations

```python
# BAD: Reading files one at a time (10,000 iterative reads)
for file in file_list:
    df = spark.read.parquet(file)

# GOOD: Read entire directory (1 read operation for metadata + bulk data reads)
df = spark.read.parquet("Files/my_data/")
```

### Strategy 4: Use Shortcuts Strategically

When shortcut targets are external (ADLS Gen2, S3), OneLake does NOT charge CUs for
the external request — the external service bills directly. This can be cost-effective
for read-heavy workloads over external data.

### Strategy 5: Schedule Heavy Operations Off-Peak

CU consumption is smoothed over time in the Fabric capacity model. Scheduling
write-heavy ETL jobs during off-peak hours reduces the risk of capacity throttling
during business hours.

---

## Monitoring CU Consumption

### Fabric Capacity Metrics App

Navigate to the **Compute** tab to see OneLake operations broken down by type:

- OneLake Read via Redirect/Proxy
- OneLake Write via Redirect/Proxy
- OneLake Iterative Read/Write
- OneLake Other Operations

Look for:
- **Spikes in write operations** correlating with ETL schedules
- **Sustained iterative read** patterns indicating directory scan issues
- **Write:Read ratio** — high ratios suggest optimization opportunity

### OneLake Diagnostics

Enable OneLake diagnostics at the workspace level to get granular event-level data
including operation types, callers, timestamps, and resources accessed.

See [OneLake Diagnostics Guide](./onelake-diagnostics-guide.md) for setup instructions.

### PowerShell: Quick CU Estimation

```powershell
# Estimate CU impact of a batch operation
function Get-OneLakeCUEstimate {
    param(
        [int]$ReadCount,
        [int]$WriteCount,
        [int]$AvgFileSizeMB = 4,
        [switch]$BCDR
    )
    $blocksPerFile = [math]::Max(1, [math]::Ceiling($AvgFileSizeMB / 4))
    $readTx = $ReadCount * $blocksPerFile
    $writeTx = $WriteCount * $blocksPerFile

    $readRate = 104     # CU seconds per 10,000
    $writeRate = if ($BCDR) { 3056 } else { 1626 }

    $readCU = ($readTx / 10000) * $readRate
    $writeCU = ($writeTx / 10000) * $writeRate

    [PSCustomObject]@{
        ReadTransactions  = $readTx
        WriteTransactions = $writeTx
        ReadCUSeconds     = [math]::Round($readCU, 2)
        WriteCUSeconds    = [math]::Round($writeCU, 2)
        TotalCUSeconds    = [math]::Round($readCU + $writeCU, 2)
        TotalCUMinutes    = [math]::Round(($readCU + $writeCU) / 60, 2)
    }
}

# Example: 50,000 reads and 10,000 writes of 8 MB files
Get-OneLakeCUEstimate -ReadCount 50000 -WriteCount 10000 -AvgFileSizeMB 8
```

---

## BCDR Cost Impact

When Business Continuity and Disaster Recovery is enabled, write operations nearly double
in CU cost:

| Operation | Standard CU | BCDR CU | Increase |
|-----------|------------|---------|----------|
| Write (per 10K) | 1,626 | 3,056 | +88% |
| Iterative Write (per 100) | 1,300 | 2,730 | +110% |
| Read (per 10K) | 104 | 104 | No change |

**Recommendation**: If BCDR is enabled, optimizing write patterns becomes even more
critical. Prioritize file compaction and batch writes to minimize transaction count.

---

## Diagnostics Overhead

OneLake diagnostics itself consumes CUs:

| Operation | Unit | CU Cost |
|-----------|------|---------|
| Diagnostics Event Write | Every 4 MB, per 10,000 | 1,626 CU seconds |
| BCDR Diagnostics Event Write | Every 4 MB, per 10,000 | 3,056 CU seconds |
| Diagnostics Data Transfer | Per GB | 1.389 CU Hours |

For high-traffic workspaces, diagnostics overhead can be meaningful. Enable diagnostics
selectively on workspaces that need monitoring rather than blanket-enabling across all
workspaces.
