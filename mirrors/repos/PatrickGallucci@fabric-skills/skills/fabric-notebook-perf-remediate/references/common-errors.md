# Common Errors and Resolution

Quick-reference guide for common Fabric notebook errors, their root causes, and resolution steps.

## Table of Contents

- [Error Message Index](#error-message-index)
- [Timeouts](#timeouts)
- [Connectivity Issues](#connectivity-issues)
- [Capacity and Throttling](#capacity-and-throttling)
- [Access and Permissions](#access-and-permissions)
- [Save Failures](#save-failures)
- [Spark Code Errors](#spark-code-errors)
- [Excessive Query Complexity](#excessive-query-complexity)
- [Collaboration Conflicts](#collaboration-conflicts)

## Error Message Index

| Error Message | Category |
|--------------|----------|
| Your session timed out after inactivity | Timeouts |
| Your session expired | Connectivity / Timeouts |
| Your notebook disconnected | Connectivity / Timeouts |
| Failed to retrieve MWC token | Connectivity |
| You're currently offline | Connectivity |
| Can't connect to the collaboration server | Connectivity |
| Error when shutting down kernel due to ajax error 410 | Connectivity |
| Access denied | Access |
| Unable to fetch high concurrency sessions | Access |
| Unable to save your notebook | Save failures / Access / Paused capacity |
| The capacity with ID is paused | Paused capacity |
| Your organization has reached its compute capacity limit | Paused capacity |
| Item not found | Missing items |
| Cannot call methods on a stopped SparkContext | Spark code issue |
| HTTP 430: Spark compute or API rate limit | Throttling |
| TooManyRequestsForCapacity | Throttling / Queue full |

## Timeouts

**Why it happens:** Notebook sessions automatically shut down after inactivity. Default timeout is 20 minutes.

**Resolution:**

1. Rerun the notebook to restart the session.
2. Adjust timeout at notebook level: click **Session Ready** indicator → update duration.
3. Adjust timeout at workspace level: Workspace Settings → Data Engineering/Science → Spark Settings → Jobs tab.

## Connectivity Issues

**Why it happens:** Network instability or temporary backend delay.

**Resolution:**

1. Retry after a few moments.
2. Check your network connection.
3. Start a new session using Connect, Run All, or Run on a specific cell.

## Capacity and Throttling

**HTTP 430 Error:**

```
This Spark job can't be run because you have hit a Spark compute or API rate limit.
To run this Spark job, cancel an active Spark job through the Monitoring hub,
or choose a larger capacity SKU or try again later.
```

**Resolution:**

1. Open Monitoring Hub and cancel idle Spark sessions.
2. Stop unused notebook sessions (they consume CUs while idle).
3. Wait for queued jobs to complete — pipeline and scheduled jobs auto-queue in FIFO order.
4. Consider upgrading capacity SKU if throttling is frequent.
5. Enable Autoscale Billing for Spark for bursty workloads.

**Queue full (TooManyRequestsForCapacity):**

Jobs are rejected when both active slots and queue slots are exhausted. Queue limits are based on SKU size. Queueing is not supported when capacity is in throttled state.

> Queueing is not supported for interactive notebook jobs or trial capacities.

## Access and Permissions

**Why it happens:**

- Incorrect sign-in credentials
- Expired login session
- Missing permissions for Notebook, Lakehouse, or Workspace
- Tenant restrictions

**Resolution:**

1. Verify sign-in with the correct Microsoft Entra account.
2. Re-authenticate if session expired.
3. Confirm you have Contributor or Admin role on the workspace.
4. Check tenant admin settings for any Fabric restrictions.

## Save Failures

**Why it happens:** Network drops before changes are saved, or session timed out.

**Resolution:**

1. Check network connectivity.
2. Save a copy of the notebook to avoid losing unsaved changes.
3. Ensure AutoSave is enabled (Edit menu).
4. Create a checkpoint via the History button → + Version.

## Spark Code Errors

### Cannot call methods on a stopped SparkContext

The Spark session has ended. Restart by running a cell or clicking Connect.

### Out of Memory (OOM)

**Resolution:**

1. Increase `spark.task.cpus` to allocate more memory per task.
2. Reduce partition sizes with `repartition()`.
3. Use `coalesce()` to reduce output partitions for writes.
4. Check for data skew causing one partition to be oversized.
5. Switch to a larger node size in custom Spark pool settings.

## Excessive Query Complexity

**Error:** Spark's Catalyst optimizer has produced a very large logical/physical plan.

**Why it happens:** Deeply chained DataFrame transformations create an execution plan too complex for the optimizer.

**Resolution:** Break complex pipelines into smaller staged queries with intermediate writes.

**Before (problematic):**

```python
df = (
    spark.read.parquet("...")
         .filter(...)
         .join(...)
         .groupBy(...)
         .agg(...)
         .join(...)
         .filter(...)
         .withColumn(...)
         .join(...)
)
```

**After (resolved):**

```python
df1 = spark.read.parquet("...").filter(...)
df2 = df1.join(...).groupBy(...).agg(...)
df2.write.parquet("/tmp/intermediate1")

df3 = spark.read.parquet("/tmp/intermediate1").join(...).filter(...)
```

Breaking the chain forces Spark to materialize intermediate results, resetting the execution plan complexity.

## Collaboration Conflicts

**Why it happens:** The same notebook was modified by another user outside of a collaboration session (VS Code, Update Definition API, manual save mode, deployment pipeline, or Git sync).

**Resolution:**

1. Click **View changes** on the error bar and choose a version.
2. Use the History button → Version history panel to find the external record.
3. Restore or save a copy of the desired version.
