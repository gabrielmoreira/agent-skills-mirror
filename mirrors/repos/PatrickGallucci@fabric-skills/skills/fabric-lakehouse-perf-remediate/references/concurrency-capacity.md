# Concurrency and Capacity Reference

## Table of Contents

- [Overview](#overview)
- [Capacity SKUs and Spark VCores](#capacity-skus-and-spark-vcores)
- [Job Admission Models](#job-admission-models)
- [Burst Capacity](#burst-capacity)
- [Autoscale Billing](#autoscale-billing)
- [Diagnosing Throttling](#diagnosing-throttling)
- [Optimization Strategies](#optimization-strategies)

## Overview

Spark workloads in Fabric consume capacity VCores. Understanding how jobs are admitted, throttled, and how burst capacity works is essential for diagnosing performance issues that stem from resource contention rather than query or table problems.

## Capacity SKUs and Spark VCores

Each Fabric capacity SKU provides a fixed number of VCores. Spark VCores are allocated from this pool. The burst factor of 3x applies to concurrent max cores.

Formula: `Available Spark VCores = Capacity CUs x 2 (1 CU = 2 Spark VCores)`

With burst: `Max Spark VCores = Available Spark VCores x 3`

Example: F64 capacity = 128 base Spark VCores = 384 max burst VCores.

## Job Admission Models

### Without Optimistic Job Admission (Legacy)

Each job reserves its maximum node configuration upfront. With F32 capacity (192 total cores) and Medium starter pool (64 cores max per job), only 3 concurrent jobs are admitted. Job 4 is throttled.

### With Optimistic Job Admission (Default)

Jobs are admitted using minimum node configuration (1 node). With F32 capacity and Medium starter pool (8 VCores minimum per job), up to 24 concurrent jobs can run. Scale-up requests are approved or rejected based on available cores.

Key behaviors:
- Jobs admitted with 1 node and scale up
- Scale up approved/rejected based on available cores
- New job admission or scale-up exceeding available cores is queued or throttled
- Batch jobs are queued and executed once cores become available

## Burst Capacity

Admins can configure Spark pools to use maximum Spark VCores including the 3x burst factor.

Example: F64 with Starter Pool max nodes = 48 (Medium = 8 VCores each) = 384 Spark VCores.

### Job-Level Bursting Control

Navigate to Admin Portal > Capacity Settings > Data Engineering/Science tab.

"Disable Job-Level Bursting" switch prevents a single Spark job from consuming all available burst capacity. Useful for multi-tenant environments.

| Setting | Effect |
|---------|--------|
| Bursting enabled (default) | Single large job can consume all 384 VCores on F64 |
| Bursting disabled | No single job can use all capacity; better concurrency and fairness |

## Autoscale Billing

Autoscale Billing for Spark provides pay-as-you-go billing independent of capacity.

| Feature | Capacity Model | Autoscale Billing |
|---------|---------------|-------------------|
| Billing | Fixed cost per capacity tier | Pay-as-you-go per Spark job |
| Scaling | Shared across workloads | Spark scales independently |
| Resource contention | Possible between workloads | Dedicated compute for Spark |
| Best use case | Predictable workloads | Dynamic or bursty Spark jobs |

Strategy: Run stable recurring jobs on capacity; offload ad-hoc or compute-heavy Spark workloads to Autoscale Billing.

## Diagnosing Throttling

### Symptoms

- Spark notebooks take a long time to start
- Jobs show "Queued" status in Monitoring Hub
- Error messages about insufficient capacity or cores
- Intermittent slowness during peak usage hours

### Diagnostic Steps

1. **Check Monitoring Hub** — Look for queued or throttled jobs
2. **Review capacity metrics** — Admin Portal > Capacity Settings > Metrics
3. **Count concurrent jobs** — Check how many notebooks/jobs run simultaneously
4. **Assess job sizes** — Are jobs requesting large node configurations?
5. **Check burst settings** — Is job-level bursting enabled or disabled?

### PowerShell: Check Capacity Utilization

```powershell
# Use Fabric REST API to list running job instances
$token = (Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com").Token
$headers = @{ "Authorization" = "Bearer $token" }

$uri = "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/items/$lakehouseId/jobs/instances"
$response = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get

$response.value | Where-Object { $_.status -eq 'InProgress' } |
    Select-Object id, jobType, status, startTimeUtc |
    Format-Table -AutoSize
```

## Optimization Strategies

### Reduce Capacity Pressure

1. **Schedule maintenance off-peak** — Run OPTIMIZE/VACUUM during low-usage windows
2. **Stagger notebook executions** — Avoid launching many concurrent notebooks at the same time
3. **Right-size Spark pools** — Use smaller node sizes when full capacity is not needed
4. **Enable optimistic admission** — Allows more concurrent jobs with smaller initial footprint
5. **Disable job-level bursting** — In multi-tenant environments to ensure fair sharing

### Scale Capacity

1. **Upgrade SKU** — Move to a higher capacity tier for more VCores
2. **Enable Autoscale Billing** — Offload bursty workloads to pay-as-you-go compute
3. **Use Custom Pools** — Configure larger nodes for compute-intensive jobs

### Workload Isolation

1. **Separate workspaces** — Dedicate capacity to critical workloads
2. **Multiple environments** — Different Spark configurations per workload type
3. **Pipeline scheduling** — Orchestrate jobs to minimize overlap
