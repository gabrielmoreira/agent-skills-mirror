# OneLake Diagnostics Guide

Setup, configuration, event analysis, and best practices for OneLake diagnostics in
Microsoft Fabric.

## Table of Contents

- [Overview](#overview)
- [Prerequisites and Setup](#prerequisites-and-setup)
- [Diagnostic Event Schema](#diagnostic-event-schema)
- [Transforming Logs to Delta Tables](#transforming-logs-to-delta-tables)
- [Performance Analysis Queries](#performance-analysis-queries)
- [Immutable Logs](#immutable-logs)
- [Operational Considerations](#operational-considerations)

---

## Overview

OneLake diagnostics provides end-to-end visibility into data access patterns across your
Fabric environment. Events are captured at the workspace level and streamed as JSON logs
into a lakehouse within the same capacity.

### What Gets Logged

- **Fabric UI actions**: User access via the web experience
- **API/SDK access**: Programmatic access via ADLS/Blob APIs, pipelines, analytics engines
- **Cross-workspace shortcuts**: Events captured from the source workspace
- **External integrations**: Access via connectors and third-party tools

### Logging Granularity

- **Fabric UI and ADLS/Blob APIs**: Every operation is logged
- **Fabric workload access**: Records that temporary access was granted (use engine-specific
  logs for deeper detail)

---

## Prerequisites and Setup

### Requirements

- Lakehouse in the **same capacity** as the monitored workspace
- Workspace admin role for enabling diagnostics
- Contributor role on the destination lakehouse
- If private links are used, lakehouse must be in the same virtual network

### Enable OneLake Diagnostics

1. Open **Workspace settings**
2. Navigate to the **OneLake** tab
3. Toggle **"Add diagnostic events to a Lakehouse"** to On
4. Select the destination lakehouse

> Events begin flowing within ~1 hour of enablement.

### Best Practice: Centralized Logging

Use a **dedicated workspace** for diagnostic storage. If monitoring multiple workspaces
within the same capacity, point all diagnostics to a single lakehouse for consolidated
analysis.

---

## Diagnostic Event Schema

Events are stored as JSON files at:

```
Files/DiagnosticLogs/OneLake/Workspaces/<WorkspaceId>/y=YYYY/m=MM/d=DD/h=HH/m=00/PT1H.json
```

### Event Properties

| Property | Description |
|----------|-------------|
| workspaceId | GUID of the monitored workspace |
| itemId | GUID of the Fabric item (lakehouse, warehouse, etc.) |
| itemType | Kind of item performing the operation |
| tenantId | Tenant performing the operation |
| executingPrincipalId | GUID of the Entra principal |
| correlationId | GUID for correlating related operations |
| operationName | OneLake operation name (not provided for internal Fabric operations) |
| operationCategory | Broad category (e.g., Read, Write) |
| executingUPN | Entra UPN (not provided for internal operations) |
| executingPrincipalType | User, Service Principal, etc. |
| accessStartTime | When the operation began |
| accessEndTime | When the operation completed |
| originatingApp | Workload or user agent string for external access |
| serviceEndpoint | DFS, Blob, or Other |
| Resource | Resource path relative to workspace |
| capacityId | Capacity performing the operation |
| httpStatusCode | Status code returned |
| isShortcut | Whether access was via shortcut |
| accessedViaResource | Shortcut location when isShortcut is true |
| callerIPAddress | Caller IP address |

### Privacy Controls

Tenant admins can disable `executingUPN` and `callerIPAddress` collection by toggling
**"Include end-user identifiers in OneLake diagnostic logs"** in the Admin portal.

---

## Transforming Logs to Delta Tables

Convert raw JSON logs into queryable Delta tables for analysis:

```python
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Read raw diagnostic JSON files
raw_logs = spark.read.json(
    "Files/DiagnosticLogs/OneLake/Workspaces/*/y=*/m=*/d=*/h=*/m=*/*.json"
)

# Write as Delta table for efficient querying
raw_logs.write \
    .mode("overwrite") \
    .format("delta") \
    .saveAsTable("onelake_diagnostic_events")

# For incremental loads, use merge or append with date partitioning
raw_logs.write \
    .mode("append") \
    .partitionBy("operationCategory") \
    .format("delta") \
    .saveAsTable("onelake_diagnostic_events_partitioned")
```

---

## Performance Analysis Queries

### Top Accessed Resources (Last 7 Days)

```sql
SELECT Resource,
       operationCategory,
       COUNT(*) AS access_count,
       COUNT(DISTINCT executingPrincipalId) AS unique_users
FROM onelake_diagnostic_events
WHERE accessStartTime >= DATEADD(DAY, -7, CURRENT_TIMESTAMP())
GROUP BY Resource, operationCategory
ORDER BY access_count DESC
LIMIT 20;
```

### Failed Operations (Error Detection)

```sql
SELECT httpStatusCode,
       operationName,
       COUNT(*) AS error_count,
       MIN(accessStartTime) AS first_seen,
       MAX(accessStartTime) AS last_seen
FROM onelake_diagnostic_events
WHERE httpStatusCode >= 400
GROUP BY httpStatusCode, operationName
ORDER BY error_count DESC;
```

### Shortcut Access Patterns

```sql
SELECT accessedViaResource AS shortcut_path,
       Resource AS target_resource,
       operationCategory,
       COUNT(*) AS access_count
FROM onelake_diagnostic_events
WHERE isShortcut = true
GROUP BY accessedViaResource, Resource, operationCategory
ORDER BY access_count DESC;
```

### Latency Analysis (Operation Duration)

```sql
SELECT operationCategory,
       operationName,
       AVG(DATEDIFF(MILLISECOND, accessStartTime, accessEndTime)) AS avg_duration_ms,
       MAX(DATEDIFF(MILLISECOND, accessStartTime, accessEndTime)) AS max_duration_ms,
       COUNT(*) AS operation_count
FROM onelake_diagnostic_events
WHERE accessEndTime IS NOT NULL
GROUP BY operationCategory, operationName
ORDER BY avg_duration_ms DESC;
```

### Access by Principal Type

```sql
SELECT executingPrincipalType,
       originatingApp,
       operationCategory,
       COUNT(*) AS operation_count
FROM onelake_diagnostic_events
GROUP BY executingPrincipalType, originatingApp, operationCategory
ORDER BY operation_count DESC;
```

---

## Immutable Logs

For compliance and audit requirements, OneLake diagnostic events can be made immutable
(WORM — write once, read many).

### Configuration

1. Enable diagnostics and set a destination lakehouse in a workspace
2. In that workspace's OneLake settings, enter the required **immutability period**
3. Press **Apply**

> **Warning**: Once applied, the immutability policy cannot be changed. Files cannot be
> modified or deleted until the retention period passes.

Immutability is built on Azure Blob Storage immutable storage. The setting applies to
all diagnostic events stored in the workspace.

---

## Operational Considerations

### Capacity and Region Changes

- **Capacity change**: Diagnostics are disabled when a workspace moves to a different
  capacity. Re-enable with a new lakehouse in the new capacity.
- **Workspace deletion**: Diagnostics data is deleted with the workspace. Restored
  workspaces recover their diagnostic data.
- **BCDR enabled**: Diagnostic data is replicated to the secondary region.

### Lakehouse Changes

- Changing the destination lakehouse preserves old events in the original lakehouse
- New events go to the newly selected lakehouse
- Re-enabling after disable uses the previously configured lakehouse

### Audit Trail

All diagnostics configuration changes (enable, disable, lakehouse update) are recorded
as `ModifyOneLakeDiagnosticSettings` events in Microsoft 365 security logs.

### CU Consumption

Diagnostics consume capacity:
- Write operations: 1,626 CU seconds per 10,000 (4 MB each)
- BCDR write operations: 3,056 CU seconds per 10,000
- Data transfer: 1.389 CU hours per GB

Enable diagnostics selectively on workspaces that require monitoring to control costs.
