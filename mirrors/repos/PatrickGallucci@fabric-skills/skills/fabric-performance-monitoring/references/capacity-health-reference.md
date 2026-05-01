# Capacity Health Reference

## Table of Contents

- [ARM REST API for Fabric Capacities](#arm-rest-api-for-fabric-capacities)
- [Fabric REST API for Workspaces](#fabric-rest-api-for-workspaces)
- [Capacity States and Transitions](#capacity-states-and-transitions)
- [Interpreting CU Consumption](#interpreting-cu-consumption)
- [Capacity Metrics App Setup](#capacity-metrics-app-setup)
- [Real-Time Capacity Events](#real-time-capacity-events)
- [PowerShell Quick Reference](#powershell-quick-reference)

---

## ARM REST API for Fabric Capacities

### List Capacities

```
GET https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Fabric/capacities?api-version=2023-11-01
```

### Get Specific Capacity

```
GET https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Fabric/capacities/{capacityName}?api-version=2023-11-01
```

### Response Schema

```json
{
  "id": "/subscriptions/.../providers/Microsoft.Fabric/capacities/mycap",
  "name": "mycap",
  "type": "Microsoft.Fabric/capacities",
  "location": "eastus",
  "sku": {
    "name": "F64",
    "tier": "Fabric"
  },
  "properties": {
    "state": "Active",
    "provisioningState": "Succeeded",
    "administration": {
      "members": ["admin@contoso.com"]
    }
  }
}
```

### Available Operations

| Operation | Method | Description |
|-----------|--------|-------------|
| List by subscription | GET | List all capacities in a subscription |
| List by resource group | GET | List capacities in a resource group |
| Get capacity | GET | Get a specific capacity |
| Create or update | PUT | Create or update a capacity |
| Delete | DELETE | Delete a capacity |
| Suspend | POST | Pause a capacity |
| Resume | POST | Resume a paused capacity |
| Update | PATCH | Update capacity properties |
| Check name availability | POST | Verify capacity name is available |
| List SKUs | GET | List available SKUs |

---

## Fabric REST API for Workspaces

### List Workspace Items

```
GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items
```

### Get Item Job Instances

```
GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{itemId}/jobs/instances
```

### Job Instance Response

```json
{
  "value": [
    {
      "id": "job-instance-id",
      "itemId": "item-id",
      "jobType": "DefaultJob",
      "invokeType": "Manual",
      "status": "Completed",
      "startTimeUtc": "2025-02-01T10:00:00Z",
      "endTimeUtc": "2025-02-01T10:15:00Z",
      "failureReason": null
    }
  ]
}
```

### Job Statuses

| Status | Description |
|--------|-------------|
| NotStarted | Job is queued but has not begun execution |
| InProgress | Job is currently running |
| Completed | Job finished successfully |
| Failed | Job terminated with an error |
| Cancelled | Job was manually or automatically cancelled |

---

## Capacity States and Transitions

| State | Description | Action Available |
|-------|-------------|-----------------|
| Active | Capacity is running and processing workloads | Suspend, Scale, Delete |
| Paused | Capacity is suspended, no CU consumption | Resume, Delete |
| Provisioning | Capacity is being created or updated | Wait |
| Deleting | Capacity is being removed | Wait |
| Failed | Provisioning failed | Retry, Delete |

### State Transition Diagram

```
Provisioning --> Active --> Paused --> Active (Resume)
                  |                      |
                  v                      v
               Deleting              Deleting
```

### Pause/Resume for Cost Optimization

Pausing a capacity stops all CU billing. This is useful for dev/test capacities that are only needed during business hours. When resuming, allow 5 minutes for Spark sessions to become available.

---

## Interpreting CU Consumption

### Key Metrics

| Metric | Description | Source |
|--------|-------------|--------|
| CU Seconds | Raw compute consumption per operation | Capacity Metrics App |
| Smoothed CU | Background operations spread over 24h | Capacity Metrics App |
| Interactive CU | On-demand operations (immediate billing) | Capacity Metrics App |
| Spark VCore Hours | Spark-specific compute (VCores * duration) | Azure Cost Analysis |

### Conversion Formula

```
Spark CU Consumption = Total Spark VCores / 2
1 CU = 2 Spark VCores
Spark VCore Hours = (Number of VCores) * (Duration in Hours)
```

### Reading the Capacity Metrics App

The Capacity Metrics App provides three key views:

1. **Compute tab** - Shows CU consumption by item type and operation. Hover over items to see operation-level detail including OneLake read/write operations.

2. **Timepoint page** - Drill into specific time windows to see interactive vs background operations, user attribution, and operation IDs that link to the Monitoring Hub.

3. **Storage tab** - Shows OneLake storage consumption per workspace and item.

### Background Operation Smoothing

All Spark operations are background operations. CU consumption is smoothed (spread) over a 24-hour period. This means a 10-minute Spark job consuming 100 CU seconds is billed as approximately 0.07 CU seconds per minute over 24 hours rather than all at once.

---

## Capacity Metrics App Setup

### Installation Steps

1. Navigate to AppSource and search for "Microsoft Fabric Capacity Metrics"
2. Install the app to a workspace on the capacity you want to monitor
3. Configure parameters: Capacity ID, Region Name
4. Set up scheduled refresh (recommended: every 30 minutes)
5. Grant Capacity Admin access to viewers who need the app

### Key Filters

| Filter | Purpose |
|--------|---------|
| Select item kind | Filter by Notebook, Lakehouse, SparkJobDefinition |
| Timeframe | Adjust the multi-metric ribbon chart date range |
| Workspace | Filter to specific workspace |
| User | Filter by the user who ran operations |

---

## Real-Time Capacity Events

Fabric emits capacity events to the Real-Time Hub every 30 seconds:

| Event Type | Description | Frequency |
|-----------|-------------|-----------|
| Microsoft.Fabric.Capacity.Summary | Aggregated CU data per 30-second window | Every 30s |
| Microsoft.Fabric.Capacity.State | Capacity state changes (pause/resume) | On change |

### Summary Event Data Fields

| Field | Type | Description |
|-------|------|-------------|
| capacityId | string | Capacity identifier |
| totalCU | number | Total CU consumed in the window |
| interactiveDelayThrottling | number | Percentage of interactive throttling |
| backgroundThrottling | number | Percentage of background throttling |

These events can be consumed by Eventstreams, Activators, or custom applications for real-time alerting.

---

## PowerShell Quick Reference

### Get Capacity with Az.Fabric Module

```powershell
# List all capacities
Get-AzFabricCapacity -SubscriptionId "xxx"

# Get specific capacity
Get-AzFabricCapacity -ResourceGroupName "rg" -CapacityName "cap"

# List available SKUs
Get-AzFabricCapacitySku | Format-List

# Resume a paused capacity
Resume-AzFabricCapacity -ResourceGroupName "rg" -CapacityName "cap"

# Suspend (pause) a capacity
Suspend-AzFabricCapacity -ResourceGroupName "rg" -CapacityName "cap"
```

### Get Fabric API Token

```powershell
$token = (Get-AzAccessToken -ResourceUrl 'https://api.fabric.microsoft.com').Token
$headers = @{ 'Authorization' = "Bearer $token"; 'Content-Type' = 'application/json' }
```

### Quick Workspace Inventory

```powershell
$items = (Invoke-RestMethod -Method Get -Uri "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items" -Headers $headers).value
$items | Group-Object type | Select-Object Name, Count | Format-Table
```
