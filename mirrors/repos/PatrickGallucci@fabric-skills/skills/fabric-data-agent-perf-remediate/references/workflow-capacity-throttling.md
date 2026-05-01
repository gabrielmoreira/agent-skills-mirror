# Workflow: Capacity Throttling (HTTP 430)

## Table of Contents

- [Diagnosis](#diagnosis)
- [SKU Capacity Reference](#sku-capacity-reference)
- [Resolution Steps](#resolution-steps)
- [Autoscale Billing Option](#autoscale-billing-option)
- [Monitoring Active Jobs](#monitoring-active-jobs)

## Diagnosis

When the Fabric capacity reaches maximum VCore utilization, new Spark jobs receive:

```
HTTP 430: This Spark job can't be run because you have hit a Spark compute or API
rate limit. To run this Spark job, cancel an active Spark job through the Monitoring
hub, or choose a larger capacity SKU or try again later.
```

**Queueing behavior:** Jobs triggered from pipelines, job scheduler, and Spark Job
Definitions are automatically queued (FIFO) and retried. Interactive notebook runs are NOT
queued and fail immediately.

**Trial capacities:** Queueing is NOT supported on Fabric Trial capacities.

## SKU Capacity Reference

| Fabric SKU | Equivalent PBI SKU | Spark VCores | Queue Limit |
|------------|-------------------|-------------|-------------|
| F2 | — | 4 | 4 |
| F4 | — | 8 | 4 |
| F8 | — | 16 | 8 |
| F16 | — | 32 | 16 |
| F32 | — | 64 | 32 |
| F64 | P1 | 128 | 64 |
| F128 | P2 | 256 | 128 |
| F256 | P3 | 512 | 256 |
| F512 | P4 | 1024 | 512 |
| F1024 | — | 2048 | 1024 |
| F2048 | — | 4096 | 2048 |

**Formula:** 1 Capacity Unit = 2 Spark VCores

## Resolution Steps

### Step 1: Check Active Jobs in Monitoring Hub

1. Open **Fabric Portal** > **Monitoring Hub**.
2. Filter by **Spark** activity type.
3. Identify long-running or stalled jobs consuming VCores.
4. Cancel unnecessary jobs to free capacity.

### Step 2: Evaluate Capacity Utilization

```powershell
# List active Spark sessions for a workspace
$workspaceId = "<your-workspace-id>"
$token = (Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com").Token
$headers = @{ Authorization = "Bearer $token" }

# Check workspace items to understand workload mix
$items = Invoke-RestMethod `
    -Uri "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/items" `
    -Headers $headers -Method Get

$sparkItems = $items.value | Where-Object {
    $_.type -in @('Notebook', 'SparkJobDefinition', 'Lakehouse')
}
Write-Host "Spark-related items: $($sparkItems.Count)"
```

### Step 3: Consider SKU Upgrade

If throttling is consistent during business hours, the current SKU is undersized.
Only Azure administrators can resize SKUs via the Azure portal.

### Step 4: Redistribute Workloads

- Move non-critical Spark jobs to off-peak hours.
- Separate heavy ETL workloads from interactive Data Agent workspaces.
- Use different capacities for production vs. development.

## Autoscale Billing Option

Autoscale Billing for Spark moves Spark workloads to dedicated serverless resources, freeing
shared capacity for other Fabric workloads.

**Requirements:**
- F-SKU only (F2 and above), not P-SKU or Trial
- Fabric Capacity Administrator role

**Configuration:**
1. Navigate to **Admin Portal** > **Capacity Settings** > **Fabric Capacity** tab.
2. Select your capacity.
3. Scroll to **Autoscale Billing for Fabric Spark**.
4. Enable the toggle.
5. Set **Maximum Capacity Units (CU)** via slider.
6. Click **Save**.

**Warning:** Enabling, disabling, or reducing max CU cancels all active Spark jobs.

## Monitoring Active Jobs

Use the **Monitoring Hub** to track:
- Active Spark sessions and their VCore consumption
- Queued jobs waiting for capacity
- Failed jobs due to throttling

Use **Azure Cost Analysis** to track Autoscale Billing spend:
1. Azure Portal > Subscription > Cost Analysis
2. Filter by Fabric capacity resource
3. Use meter: `Autoscale for Spark Capacity Usage CU`
