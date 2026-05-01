# Capacity Throttling Guide

Understanding and resolving Microsoft Fabric capacity throttling, Spark job queueing, and compute limit errors.

## Table of Contents

- [Understanding Capacity Throttling](#understanding-capacity-throttling)
- [Spark Job Queueing](#spark-job-queueing)
- [Throttling Error Messages](#throttling-error-messages)
- [Diagnostic Steps](#diagnostic-steps)
- [Resolution Strategies](#resolution-strategies)
- [Capacity Planning](#capacity-planning)

## Understanding Capacity Throttling

Microsoft Fabric capacities have fixed compute limits based on the purchased SKU. When the total demand for compute exceeds the capacity limits, the system either queues or rejects new jobs.

### Throttling vs Queueing

| Behavior | Condition | Result |
|----------|-----------|--------|
| Queueing | Compute at max but queue not full | Job enters FIFO queue, retries automatically |
| Throttling | Queue is full or capacity is throttled | Job rejected with HTTP 430 error |
| Rejection | Trial capacity (no queueing support) | Job fails immediately |

### Capacity States

1. **Normal**: Compute available, jobs start immediately
2. **At Limit**: Max cores in use, new jobs queue
3. **Throttled**: Capacity in throttled state, all new jobs rejected

## Spark Job Queueing

Fabric supports automatic queueing for background Spark jobs when compute limits are reached.

### Supported Job Types

- Notebook jobs triggered by pipelines
- Notebook jobs triggered by scheduler
- Spark job definitions triggered by pipelines

### NOT Supported

- Interactive notebook jobs (will fail, not queue)
- Notebook jobs triggered through public API
- All jobs on Trial capacities

### Queue Behavior

1. Job is submitted and capacity is at max compute
2. Job enters FIFO queue with "Not Started" status
3. Queue retries periodically as compute frees up
4. When capacity is available, job transitions to "In Progress"
5. **Queue expires after 24 hours**; expired jobs must be resubmitted

### Queue Limits by SKU

| Fabric SKU | Queue Limit |
|-----------|-------------|
| F2 | 4 |
| F4 | 4 |
| F8 | 8 |
| F16 | 16 |
| F32 | 32 |
| F64 | 64 |
| F128 | 128 |
| F256 | 256 |
| F512 | 512 |
| F1024 | 1024 |
| F2048 | 2048 |
| Trial | N/A (no queueing) |

## Throttling Error Messages

### TooManyRequestsForCapacity

```
[TooManyRequestsForCapacity] This spark job can't be run because you have hit a 
spark compute or API rate limit. To run this spark job, cancel an active Spark job 
through the Monitoring hub, choose a larger capacity SKU, or try again later. 
HTTP status code: 430
```

**Immediate actions:**

1. Open the Monitoring Hub and identify active Spark jobs
2. Cancel any non-critical or stuck jobs
3. Wait for running jobs to complete
4. If persistent, upgrade the capacity SKU

### HTTP 430 Error

This error indicates the capacity queue is full. All new job submissions will fail until existing jobs complete or are cancelled.

### Rate Limit Errors (Databricks)

Error 3202: `There were already 1000 jobs created in past 3600 seconds`

This applies to Azure Databricks activities. Distribute workloads across multiple Databricks workspaces or reduce job frequency.

## Diagnostic Steps

### Step 1: Check Current Capacity Utilization

1. Navigate to the **Monitoring Hub** in the Fabric portal
2. Review all active items across the workspace
3. Filter by "In Progress" status to see running jobs
4. Count active Spark sessions

### Step 2: Identify Resource-Heavy Jobs

Look for jobs consuming disproportionate compute:

- Large notebook jobs with many executors
- Copy activities with high parallelism
- Dataflow Gen2 refreshes with complex transformations

### Step 3: Check Capacity Admin Settings

1. Go to **Admin Portal** > **Capacity settings**
2. Verify the capacity SKU and its limits
3. Check if the capacity is in a throttled state
4. Review Spark Compute settings for the workspace

### Step 4: Review Historical Patterns

Use workspace monitoring KQL queries to identify patterns:

```kql
ItemJobEventLogs
| where ItemKind == "Pipeline" or ItemKind == "Notebook"
| where Timestamp > ago(7d)
| summarize JobCount = count() by bin(Timestamp, 1h), JobStatus
| render timechart
```

## Resolution Strategies

### Immediate Relief

1. **Cancel non-critical jobs**: Free up compute for priority workloads
2. **Stagger pipeline triggers**: Avoid burst submissions at the same time
3. **Reduce parallelism**: Lower `parallelCopies` and ITO settings

### Short-Term Optimization

1. **Optimize Spark configurations**: Use resource profiles (writeHeavy, readHeavyForSpark)
2. **Right-size Spark pools**: Reduce node count for small workloads
3. **Use autoscale**: Let Spark pools scale based on demand
4. **Consolidate pipelines**: Combine small pipelines to reduce overhead

### Long-Term Solutions

1. **Upgrade capacity SKU**: Move to a higher SKU for more compute headroom
2. **Distribute across workspaces**: Spread workloads across multiple capacities
3. **Implement scheduling windows**: Separate batch and interactive workloads by time
4. **Enable queueing**: Ensure pipelines use queueing-eligible patterns (pipeline-triggered notebooks)

## Capacity Planning

### Estimating Required SKU

Consider these factors:

1. **Peak concurrent jobs**: Maximum number of simultaneous Spark sessions
2. **Average job duration**: How long each job runs
3. **Job frequency**: How often jobs are triggered
4. **Data volume**: Amount of data processed per job
5. **Interactive vs batch**: Ratio of interactive to scheduled workloads

### Rule of Thumb

```
Required Queue Limit >= (Peak Jobs per Hour * Average Job Duration in Hours)
```

If this number approaches your current SKU's queue limit, plan to upgrade before hitting throttling.

### Monitoring for Capacity Planning

Track these KPIs weekly:

- Peak concurrent active jobs
- Average queue wait time
- Number of throttling errors (HTTP 430)
- Capacity utilization percentage over time
