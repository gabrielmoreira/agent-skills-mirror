# Throttling and Concurrency Guide

## Table of Contents

- [Capacity SKU Limits Table](#capacity-sku-limits-table)
- [Understanding HTTP 430 Errors](#understanding-http-430-errors)
- [Job Queueing](#job-queueing)
- [Burst Factor and Job-Level Bursting](#burst-factor-and-job-level-bursting)
- [Concurrency Optimization Strategies](#concurrency-optimization-strategies)

---

## Capacity SKU Limits Table

Each Fabric capacity SKU maps to Spark VCores and queue limits:

| Fabric SKU | Power BI Equiv | Base VCores | Max VCores (3x Burst) | Queue Limit |
|------------|---------------|-------------|----------------------|-------------|
| F2 | - | 4 | 20 | 4 |
| F4 | - | 8 | 24 | 4 |
| F8 | - | 16 | 48 | 8 |
| F16 | - | 32 | 96 | 16 |
| F32 | - | 64 | 192 | 32 |
| F64 | P1 | 128 | 384 | 64 |
| F128 | P2 | 256 | 768 | 128 |
| F256 | P3 | 512 | 1536 | 256 |
| F512 | P4 | 1024 | 3072 | 512 |
| F1024 | - | 2048 | 6144 | 1024 |
| F2048 | - | 4096 | 12288 | 2048 |
| Trial | P1 | 128 | 384 | N/A |

**Key formula**: `1 Capacity Unit = 2 Spark VCores`. Burst factor provides 3x the base VCores.

**Trial capacity**: Queueing is NOT supported. Switch to a paid F or P SKU to enable queueing.

---

## Understanding HTTP 430 Errors

### Error Message

```text
HTTP Response code 430: This Spark job can't be run because you have hit a Spark
compute or API rate limit. To run this Spark job, cancel an active Spark job
through the Monitoring hub, or choose a larger capacity SKU or try again later.
```

Also appears as: `[TooManyRequestsForCapacity]`

### Root Cause

All Spark VCores for the capacity are consumed by running jobs. The throttling is purely cores-based — there are no arbitrary job-count limits.

### Diagnostic Steps

1. Open the **Monitoring Hub** in your Fabric workspace
2. Filter by **Spark** activity type and **In Progress** status
3. Sum the VCores consumed by all active sessions
4. Compare against your SKU's max VCores (see table above)
5. Check if any sessions are idle but not yet expired (default session timeout: 20 minutes)

### Resolution Actions

| Action | When to Use | Impact |
|--------|------------|--------|
| Cancel idle Spark sessions via Monitoring Hub | Immediate relief needed | Frees VCores instantly |
| Wait for session auto-expiry (20 min default) | Sessions are finishing soon | No intervention needed |
| Upgrade Fabric capacity SKU | Chronic throttling | Higher cost, more VCores |
| Enable job queueing (pipeline/scheduler jobs) | Batch workloads can wait | Jobs auto-retry from queue |
| Reduce pool max nodes per job | Jobs consuming too many cores | Better concurrency, slower individual jobs |
| Disable job-level bursting | One job monopolizing burst capacity | Fairer distribution across jobs |

---

## Job Queueing

### Supported Job Types

Queueing is supported for:
- Notebook jobs triggered from **pipelines**
- Notebook jobs triggered from the **job scheduler**
- **Spark job definitions**

Queueing is NOT supported for:
- Interactive notebook sessions
- Notebook jobs triggered through the notebook public API
- Any jobs on **Trial capacities**
- Jobs when the capacity is in a **throttled state** (all jobs are rejected)

### Queue Behavior

The queue operates as a **FIFO (First-In-First-Out)** system:

1. Job is submitted and capacity is at maximum utilization
2. Job enters the queue with status **Not Started** (visible in Monitoring Hub)
3. Queue constantly checks for available capacity
4. When cores free up, the next job in the queue starts executing
5. Status changes from **Not Started** to **In Progress**

### Queue Expiration

**Queue entries expire after 24 hours** from submission time. After expiration, jobs are removed from the queue and must be resubmitted manually.

### Queue Limits by SKU

Queue sizes scale with capacity SKU (see the full table above). Once the max queue limit is reached, additional jobs are throttled with the HTTP 430 error even for queueable job types.

### How to Enable Queueing

Queueing is enabled by default for supported job types. Ensure:

1. Your capacity is a paid Fabric F or P SKU (not Trial)
2. Jobs are submitted through pipelines, scheduler, or Spark job definitions
3. Capacity is not in a fully throttled state

---

## Burst Factor and Job-Level Bursting

### How Bursting Works

Fabric provides a **3x burst factor** on Spark VCores. An F64 capacity with 128 base VCores can use up to 384 VCores for concurrent execution.

The pool configuration determines max cores a job can use — not just the base SKU allocation. If a workspace admin creates a pool with 48 Medium nodes (8 VCores each) on an F64 capacity, a single job could theoretically use all 384 VCores.

### Job-Level Bursting Control

Capacity admins can control whether a single job can consume all burst capacity:

**Admin Portal path**: Capacity Settings > Data Engineering/Science tab > "Disable Job-Level Bursting" switch

| Setting | Behavior | Best For |
|---------|----------|----------|
| Bursting enabled (default) | A single job can consume all available burst VCores | Large batch jobs, low concurrency |
| Bursting disabled | No single job can use all capacity including burst cores | Multi-tenant, high concurrency, fairness |

### Example Scenarios

**Bursting enabled (F64)**: A large batch notebook job consumes all 384 Spark VCores, assuming no other jobs are running.

**Bursting disabled (F64)**: The Spark engine prevents any single job from monopolizing all 384 VCores, ensuring capacity remains available for concurrent jobs.

---

## Concurrency Optimization Strategies

### Strategy 1: Right-Size Pool Nodes

Smaller node sizes spread capacity across more nodes, allowing more concurrent jobs:

| Node Size | VCores/Node | Memory/Node | F64 Max Nodes |
|-----------|-------------|-------------|---------------|
| Small | 4 | 32 GB | 96 |
| Medium | 8 | 64 GB | 48 |
| Large | 16 | 128 GB | 24 |
| X-Large | 32 | 256 GB | 12 |
| XX-Large | 64 | 512 GB | 6 |

For high-concurrency workloads, prefer **Small or Medium** nodes with lower min-node settings per job.

### Strategy 2: Minimize Idle Sessions

- Set session timeout appropriately (default 20 minutes)
- Explicitly stop sessions after notebook execution completes
- Monitor idle sessions in the Monitoring Hub regularly

### Strategy 3: Separate Interactive and Batch Workloads

- Reserve starter pools for interactive notebook work
- Route batch jobs through pipelines with queueing enabled
- Consider separate workspaces for high-priority vs background workloads

### Strategy 4: Autoscale Configuration

Set a low minimum node count (1 is valid) and appropriate maximum. Jobs start with minimum cores and scale up only as needed, leaving more capacity for other jobs during startup phases.
