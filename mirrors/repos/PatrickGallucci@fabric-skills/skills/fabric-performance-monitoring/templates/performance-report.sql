/*
    Microsoft Fabric Lakehouse Performance Report Template
    
    Purpose: Query the SQL analytics endpoint to analyze Delta table health,
    storage metrics, and query patterns for performance optimization.
    
    Target: Lakehouse SQL analytics endpoint (T-SQL)
    
    Usage: Connect to your Lakehouse SQL analytics endpoint and execute
    these queries to gather performance-relevant metrics. Replace 
    placeholder schema/table names with your actual table names.
    
    Note: The SQL analytics endpoint provides read-only T-SQL access
    to Delta tables in the Lakehouse. These queries help identify
    optimization opportunities.
*/

-- =============================================================
-- Section 1: Table Inventory and Row Counts
-- =============================================================
-- Lists all tables with approximate row counts to identify
-- large tables that may benefit from partitioning or optimization.

SELECT 
    s.[name]                    AS SchemaName,
    t.[name]                    AS TableName,
    p.[rows]                    AS ApproxRowCount,
    SUM(a.total_pages) * 8      AS TotalSpaceKB,
    SUM(a.used_pages) * 8       AS UsedSpaceKB,
    (SUM(a.total_pages) - SUM(a.used_pages)) * 8 AS UnusedSpaceKB
FROM sys.tables t
INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
INNER JOIN sys.indexes i ON t.object_id = i.object_id
INNER JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
INNER JOIN sys.allocation_units a ON p.partition_id = a.container_id
WHERE t.is_ms_shipped = 0
GROUP BY s.[name], t.[name], p.[rows]
ORDER BY p.[rows] DESC;


-- =============================================================
-- Section 2: Column Statistics Overview
-- =============================================================
-- Check which tables have statistics created, which helps the
-- query optimizer choose efficient execution plans.

SELECT 
    OBJECT_SCHEMA_NAME(s.object_id)    AS SchemaName,
    OBJECT_NAME(s.object_id)           AS TableName,
    s.[name]                           AS StatisticsName,
    s.auto_created                     AS AutoCreated,
    s.user_created                     AS UserCreated,
    sp.last_updated                    AS LastUpdated,
    sp.[rows]                          AS RowsWhenUpdated,
    sp.modification_counter            AS ModificationsSinceUpdate
FROM sys.stats s
CROSS APPLY sys.dm_db_stats_properties(s.object_id, s.stats_id) sp
WHERE OBJECTPROPERTY(s.object_id, 'IsUserTable') = 1
ORDER BY sp.modification_counter DESC;


-- =============================================================
-- Section 3: Index Usage Analysis
-- =============================================================
-- Identifies indexes and their usage patterns. High scan counts
-- with low seek counts may indicate missing or suboptimal indexes.

SELECT 
    OBJECT_SCHEMA_NAME(i.object_id)    AS SchemaName,
    OBJECT_NAME(i.object_id)           AS TableName,
    i.[name]                           AS IndexName,
    i.type_desc                        AS IndexType,
    ius.user_seeks                     AS UserSeeks,
    ius.user_scans                     AS UserScans,
    ius.user_lookups                   AS UserLookups,
    ius.user_updates                   AS UserUpdates,
    ius.last_user_seek                 AS LastSeek,
    ius.last_user_scan                 AS LastScan
FROM sys.indexes i
LEFT JOIN sys.dm_db_index_usage_stats ius 
    ON i.object_id = ius.object_id 
    AND i.index_id = ius.index_id
WHERE OBJECTPROPERTY(i.object_id, 'IsUserTable') = 1
ORDER BY ius.user_scans DESC;


-- =============================================================
-- Section 4: Active Sessions and Requests
-- =============================================================
-- Check currently running queries against the SQL analytics
-- endpoint to identify long-running or resource-heavy operations.

SELECT 
    s.session_id,
    s.login_name,
    s.status                            AS SessionStatus,
    r.status                            AS RequestStatus,
    r.command,
    r.cpu_time,
    r.total_elapsed_time,
    r.reads,
    r.writes,
    r.logical_reads,
    SUBSTRING(
        qt.[text], 
        (r.statement_start_offset / 2) + 1,
        ((CASE r.statement_end_offset
            WHEN -1 THEN DATALENGTH(qt.[text])
            ELSE r.statement_end_offset
        END - r.statement_start_offset) / 2) + 1
    )                                   AS QueryText
FROM sys.dm_exec_sessions s
LEFT JOIN sys.dm_exec_requests r ON s.session_id = r.session_id
OUTER APPLY sys.dm_exec_sql_text(r.sql_handle) qt
WHERE s.is_user_process = 1
    AND s.session_id <> @@SPID
ORDER BY r.total_elapsed_time DESC;


-- =============================================================
-- Section 5: Wait Statistics
-- =============================================================
-- Identify the most common wait types to understand where the
-- SQL analytics endpoint is spending time waiting.

SELECT TOP 20
    wait_type,
    waiting_tasks_count,
    wait_time_ms,
    max_wait_time_ms,
    signal_wait_time_ms,
    CAST(wait_time_ms * 100.0 / SUM(wait_time_ms) OVER() AS DECIMAL(5,2)) AS WaitPct
FROM sys.dm_os_wait_stats
WHERE wait_type NOT IN (
    'SLEEP_TASK', 'BROKER_TASK_STOP', 'BROKER_EVENTHANDLER',
    'CLR_AUTO_EVENT', 'CLR_MANUAL_EVENT', 'LAZYWRITER_SLEEP',
    'RESOURCE_QUEUE', 'SQLTRACE_BUFFER_FLUSH', 'WAITFOR',
    'XE_TIMER_EVENT', 'XE_DISPATCHER_WAIT', 'FT_IFTS_SCHEDULER_IDLE_WAIT',
    'DISPATCHER_QUEUE_SEMAPHORE', 'CHECKPOINT_QUEUE', 'REQUEST_FOR_DEADLOCK_SEARCH'
)
AND waiting_tasks_count > 0
ORDER BY wait_time_ms DESC;


-- =============================================================
-- Section 6: Delta Table Health Check Template
-- =============================================================
-- Template query to check specific Delta table properties.
-- Replace <your_schema> and <your_table> with actual names.

/*
-- Uncomment and modify for your specific tables:

SELECT 
    COUNT(*)                           AS TotalRows,
    COUNT(DISTINCT <partition_col>)    AS DistinctPartitions,
    MIN(<date_col>)                    AS EarliestRecord,
    MAX(<date_col>)                    AS LatestRecord,
    DATEDIFF(DAY, MIN(<date_col>), MAX(<date_col>)) AS DateRangeDays
FROM <your_schema>.<your_table>;
*/
