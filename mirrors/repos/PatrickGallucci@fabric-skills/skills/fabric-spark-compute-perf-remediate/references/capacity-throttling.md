# Capacity Throttling & SKU Sizing

## Table of Contents

- [Understanding HTTP 430 Errors](#understanding-http-430-errors)
- [Queue Limits by SKU](#queue-limits-by-sku)
- [Diagnosing Throttling](#diagnosing-throttling)
- [Resolution Strategies](#resolution-strategies)
- [SKU Sizing Guidelines](#sku-sizing-guidelines)

## Understanding HTTP 430 Errors

When the maximum queue limit for a Fabric capacity is reached, new Spark jobs are
rejected with:

```
[TooManyRequestsForCapacity] This spark job can't be run because you have hit a
spark compute or API rate limit. To run this spark job, cancel an active Spark job
through the Monitoring hub, choose a larger capacity SKU, or try again later.
HTTP status code: 430
```

This is a hard limit — no retry will succeed until active jobs complete or are canceled.

## Queue Limits by SKU

| Fabric SKU | Equivalent Power BI SKU | Spark VCores | Queue Limit |
|-----------|------------------------|-------------|-------------|
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
| Trial | P1 | 128 | No queueing |

**Trial Capacity**: Queueing is not supported. Users must switch to a paid F or P SKU
to use queueing for Spark jobs.

## Diagnosing Throttling

### Step 1: Check Monitoring Hub

Navigate to: **Monitoring Hub** in the Fabric portal.

Look for active Spark sessions and jobs. Each interactive notebook session, running
Spark job definition, and pipeline Spark activity counts toward the queue limit.

### Step 2: Identify Long-Running Sessions

Idle notebook sessions hold capacity. Users who opened a notebook but haven't run
code in hours still consume a queue slot until the session times out.

### Step 3: Check for Pipeline Fan-Out

Fabric pipelines with ForEach loops that launch parallel Spark activities can rapidly
exhaust queue limits. A ForEach with 50 items on an F8 SKU (queue limit 8) will
throttle immediately.

## Resolution Strategies

### Immediate Relief

1. **Cancel idle sessions** via Monitoring Hub
2. **Kill stuck jobs** that are no longer needed
3. **Reduce pipeline parallelism** (lower ForEach batch count)

### Short-Term Optimization

1. **Stagger scheduled jobs** — spread across time windows
2. **Set session timeouts** — configure `spark.fabric.session.idle.timeout` to auto-stop idle sessions
3. **Consolidate notebooks** — run multiple tasks in one session instead of launching separate sessions
4. **Use high concurrency mode** — share a single Spark session across multiple users/notebooks

### Long-Term Capacity Planning

1. **Right-size the SKU** — use the sizing guidelines below
2. **Separate workloads** — use different workspaces on different capacities for dev/test vs. production
3. **Optimize job duration** — faster jobs free slots sooner (see [general-tuning.md](./general-tuning.md))

## SKU Sizing Guidelines

### Estimate Required Queue Slots

Count your peak concurrent Spark workloads:

| Workload Type | Queue Slots Used |
|--------------|-----------------|
| Interactive notebook session | 1 per user |
| Spark Job Definition | 1 per running job |
| Pipeline Spark activity | 1 per concurrent activity |
| Scheduled notebook | 1 per running instance |
| Streaming job (always-on) | 1 per stream |

**Formula**: Required SKU queue limit >= (interactive users) + (peak scheduled jobs) +
(streaming jobs) + (buffer of 20–30%)

### Cost-Performance Trade-offs

- **F8 (8 queue slots)**: Small teams, limited concurrent jobs
- **F32 (32 queue slots)**: Medium teams with scheduled pipelines
- **F64 (64 queue slots)**: Large teams with multiple concurrent workloads
- **F128+ (128+ slots)**: Enterprise with heavy pipeline orchestration

### Capacity Smoothing

If you hit throttling only during brief peaks, consider Fabric's capacity smoothing
(24-hour smoothing window) which averages consumption over time. This can allow
burst workloads that would otherwise exceed instantaneous limits.
