# Pipeline Stuck Resolution

Guide for diagnosing and resolving stuck or unresponsive pipeline activities in Microsoft Fabric Data Factory.

## Table of Contents

- [Identifying Stuck Activities](#identifying-stuck-activities)
- [Common Causes](#common-causes)
- [Resolution Steps by Activity Type](#resolution-steps-by-activity-type)
- [Payload Size Issues](#payload-size-issues)
- [Error Code Reference](#error-code-reference)

## Identifying Stuck Activities

An activity is considered stuck when it runs significantly longer than normal with no visible progress. Check for:

1. **Duration exceeds historical average** by 3x or more
2. **No data movement progress** in the copy activity details
3. **Status remains "In Progress"** with no output updates
4. **No error messages** in the activity output

### How to Check

1. Open the **Monitoring Hub** in the Fabric portal
2. Filter by pipeline name and current time range
3. Click the run details icon (glasses) on the in-progress run
4. Review the Duration Breakdown and progress indicators
5. Compare against previous successful runs

## Common Causes

| Cause | Symptoms | Resolution |
|-------|----------|------------|
| Source database lock contention | Copy activity stuck in transfer phase | Check source DB for blocking queries |
| Network interruption | Intermittent connectivity to source/sink | Verify network, retry with retry settings |
| Capacity exhaustion | Activity queued with "Not Started" status | Check capacity utilization, cancel other jobs |
| Payload too large | Pipeline fails before activity starts | Reduce parameter sizes below 896 KB |
| Credential expiration | Authentication failures | Refresh tokens and connection credentials |
| Destination throttling | Slow writes, timeout errors | Reduce parallelism, check destination limits |
| Unsupported compression | Activity succeeds but data corrupted | Re-compress source with deflate algorithm |

## Resolution Steps by Activity Type

### Copy Activity

1. **Cancel and retry**: First attempt - cancel the stuck run and trigger a new one
2. **Check source connectivity**: Verify the source is accessible and responsive
3. **Review retry settings**: Configure `sourceRetryCount` (2-3) and `sourceRetryWait`
4. **Reduce parallelism**: If destination is overwhelmed, reduce `parallelCopies`
5. **Check for locks**: Query the source database for blocking sessions

For SQL Server source, check blocking:

```sql
SELECT
    r.session_id,
    r.blocking_session_id,
    r.wait_type,
    r.wait_time,
    t.text AS query_text
FROM sys.dm_exec_requests r
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t
WHERE r.blocking_session_id <> 0;
```

### Notebook Activity

1. Check if the Spark session is active in the Monitoring Hub
2. Review Spark job status for errors or resource contention
3. Verify the notebook code does not have infinite loops or deadlocks
4. Check Spark pool compute limits and queue status

### Dataflow Activity

1. Check Dataflow Gen2 refresh status independently
2. Verify connector credentials and source availability
3. Review query folding status (non-folding queries are slow)
4. Check for memory-intensive transformations

### Execute Pipeline (Nested)

1. Check the child pipeline status in the Monitoring Hub
2. Verify parameters are passed correctly (array vs string issue)
3. Review child pipeline for its own stuck activities

## Payload Size Issues

### Symptom

Error message: `The payload including configurations on activity/data/connection is too large.`

### Cause

Activity payload (configuration + data + connections) exceeds the **896 KB** limit.

### Resolution

1. Identify which parameter or output is too large
2. Avoid passing actual data between activities in control flow
3. Instead of passing large datasets through parameters, write to intermediate storage and read in the next activity
4. Reduce the number of dynamic expressions that expand to large values

### Array Parameter Issue

When Execute Pipeline passes an array parameter, it may be received as a string in the child pipeline.

**Fix**: Use the `createArray()` function in the child pipeline to convert the string back to an array:

```
@createArray(pipeline().parameters.myArrayParam)
```

## Error Code Reference

### General Pipeline Errors

| Error Code | Message | Cause | Fix |
|-----------|---------|-------|-----|
| 2001 | Execution output over 4 MB limit | Web activity output too large | Reduce response payload |
| 2002 | Payload too large | Config exceeds 896 KB | Reduce parameter sizes |
| 2003 | Substantial concurrent executions | Too many activities running | Reduce concurrency, stagger triggers |
| 2103 | Missing required property | Property not provided | Check activity configuration |
| 2104 | Incorrect property type | Wrong data type | Fix property type |
| 2105 | Invalid JSON | Malformed dynamic content | Validate JSON expressions |
| 2106 | Invalid connection string | Bad storage connection | Re-enter connection string |
| 2108 | Error calling endpoint | URL unreachable | Verify URL and network access |

### Copy Activity Specific

| Error | Cause | Fix |
|-------|-------|-----|
| Source retry exhausted | Transient source failures | Increase `sourceRetryCount`, check source health |
| Sink retry exhausted | Destination write failures | Increase `sinkRetryCount`, reduce parallelism |
| Incompatible row | Schema mismatch | Enable `enableSkipIncompatibleRow` or fix schema |
| Data consistency failed | Source/sink mismatch | Investigate data changes during copy |

### Databricks Activity Errors

| Error Code | Cause | Fix |
|-----------|-------|-----|
| 3200 | Access token expired | Create new token (valid 90 days) |
| 3201 | Bad configuration | Verify notebook path, cluster, permissions |
| 3202 | Rate limit (1000 jobs/hour) | Reduce job frequency, use separate workspace |
| 3203 | Cluster terminated | Use job clusters instead of interactive |
| 3204 | Job execution failed | Check Databricks logs |
| 3208 | Network error | Verify network connectivity |

### Azure Function Errors

| Error Code | Cause | Fix |
|-----------|-------|-----|
| 3602 | Invalid HTTP method | Use PUT, POST, GET, DELETE, OPTIONS, HEAD, TRACE |
| 3603 | Invalid JSON response | Return valid JSON from function |
| 3606-3612 | Missing configuration | Check function key, name, URL, method, connection |

## Prevention Strategies

1. **Set activity timeouts**: Configure appropriate timeout values for each activity
2. **Enable retry policies**: Set retry count and interval for transient failures
3. **Monitor proactively**: Enable workspace monitoring and create KQL alerts
4. **Test with representative data**: Validate pipelines with production-scale test data
5. **Document known issues**: Maintain a runbook of common failures and resolutions
