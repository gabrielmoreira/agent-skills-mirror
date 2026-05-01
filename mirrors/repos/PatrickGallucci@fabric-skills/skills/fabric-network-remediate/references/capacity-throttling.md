# Capacity Throttling and Queue Limits

## Table of Contents

- [How Fabric Capacity Maps to Spark VCores](#how-fabric-capacity-maps-to-spark-vcores)
- [Queue Limits by SKU](#queue-limits-by-sku)
- [Throttling Behavior](#throttling-behavior)
- [Monitoring and Resolution](#monitoring-and-resolution)
- [Resource Profiles](#resource-profiles)

## How Fabric Capacity Maps to Spark VCores

**Formula**: 1 Capacity Unit = 2 Spark VCores

When a Fabric capacity is created on Azure, users choose a capacity size. The Spark VCores associated with that capacity are shared among all Spark-based items (notebooks, Spark Job Definitions, lakehouses) across all workspaces assigned to the capacity.

## Queue Limits by SKU

| Fabric SKU | Power BI Equivalent | Queue Limit |
|------------|-------------------|-------------|
| F2 | — | 4 |
| F4 | — | 4 |
| F8 | — | 8 |
| F16 | — | 16 |
| F32 | — | 32 |
| F64 | P1 | 64 |
| F128 | P2 | 128 |
| F256 | P3 | 256 |
| F512 | P4 | 512 |
| F1024 | — | 1024 |
| F2048 | — | 2048 |
| Trial | P1 | N/A (no queueing) |

**Note**: Queueing is **not supported** for Fabric trial capacities. Users must switch to a paid F or P SKU to enable queueing.

## Throttling Behavior

When all Spark VCores for a capacity are consumed and the queue limit is reached, new job submissions receive:

```
HTTP Response code 430: This Spark job can't be run because you have hit a Spark
compute or API rate limit. To run this Spark job, cancel an active Spark job
through the Monitoring hub, or choose a larger capacity SKU or try again later.
```

Error code: `TooManyRequestsForCapacity`

### What Gets Queued

With queueing enabled, the following job types are automatically queued and retried when capacity becomes available:

- Notebook jobs triggered from **pipelines**
- Notebook jobs triggered from **job scheduler**
- **Spark Job Definitions**

### What Does NOT Get Queued

- Interactive notebook sessions started manually
- Lakehouse operations (Load to Table) — these fail immediately
- Jobs on Trial capacities

## Monitoring and Resolution

### Step 1: Check Current Utilization

1. Open the **Monitoring Hub** in the Fabric portal
2. Filter by **Spark** activities
3. Review active, queued, and recently completed jobs
4. Identify jobs consuming disproportionate resources

### Step 2: Immediate Relief

```powershell
# List active Spark sessions via Fabric REST API
$token = (Get-AzAccessToken -ResourceUrl 'https://api.fabric.microsoft.com').Token
$headers = @{ Authorization = "Bearer $token" }

# Cancel a specific Spark session (if API available)
# Use the Monitoring Hub UI to cancel active sessions
```

From the Monitoring Hub:
1. Select the active Spark job
2. Click **Cancel** to free up VCores
3. Re-submit throttled jobs after capacity is freed

### Step 3: Structural Solutions

| Solution | Impact | Effort |
|----------|--------|--------|
| Cancel idle Spark sessions | Immediate | Low |
| Upgrade capacity SKU | Immediate (after provisioning) | Medium |
| Stagger job schedules | Reduces peak contention | Low |
| Optimize Spark configs (resource profiles) | Reduces per-job VCore usage | Medium |
| Split workloads across multiple capacities | Isolates workloads | High |

### Step 4: Capacity Metrics App

Install the **Fabric Capacity Metrics** app for detailed consumption analysis:
1. Navigate to AppSource or the Fabric admin portal
2. Install the Capacity Metrics app
3. Connect to your capacity
4. Review Spark utilization trends and peak patterns

## Resource Profiles

Fabric supports predefined resource profiles to optimize Spark configurations. New workspaces default to `writeHeavy`.

| Profile | Optimized For | VOrder Default |
|---------|---------------|----------------|
| `writeHeavy` | Ingestion, ETL, streaming | Disabled |
| `readHeavyForSpark` | Interactive Spark queries | Enabled |
| `readHeavyForPBI` | Power BI dashboards, Direct Lake | Enabled |

### Impact on Capacity Usage

- **writeHeavy**: Better throughput for batch/streaming, lower per-job overhead
- **readHeavy**: Better query performance but may consume more VCores per session
- Choose the profile matching your dominant workload pattern to optimize capacity utilization

### Changing the Profile

Set the resource profile at the Environment level or override dynamically:

```python
# In a Fabric Notebook
spark.conf.set("spark.fabric.resourceProfile", "readHeavyForSpark")
```

Or configure in the Environment settings under **Spark properties**.
