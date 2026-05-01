---
type: skill
lifecycle: stable
inheritance: inheritable
name: azure-cost-management-api
description: In PowerShell, inline JSON for Cost Management API causes "Unsupported Media Type" errors:
tier: standard
applyTo: '**/*azure*,**/*cost*,**/*management*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Azure Cost Management API

## The Problem

In PowerShell, inline JSON for Cost Management API causes "Unsupported Media Type" errors:

```powershell
# This fails silently or with 415 error
az rest --method POST --uri $uri --body '{"type":"Usage","timeframe":"MonthToDate"}'
```

The shell mangles the JSON.

## The Solution

Write JSON to a file, then reference with `@`:

```powershell
# 1. Create body file
$body = @{
    type = "Usage"
    timeframe = "MonthToDate"
    dataset = @{
        granularity = "Daily"
        aggregation = @{
            totalCost = @{
                name = "Cost"
                function = "Sum"
            }
        }
    }
} | ConvertTo-Json -Depth 10

$bodyFile = "$env:TEMP\cost-query-body.json"
$body | Out-File -FilePath $bodyFile -Encoding utf8

# 2. Call with file reference
$uri = "/subscriptions/$subscriptionId/providers/Microsoft.CostManagement/query?api-version=2023-03-01"
az rest --method POST --uri $uri --body "@$bodyFile"
```

## Common Queries

### Monthly Cost by Resource Group

```json
{
  "type": "Usage",
  "timeframe": "MonthToDate",
  "dataset": {
    "granularity": "None",
    "aggregation": {
      "totalCost": { "name": "Cost", "function": "Sum" }
    },
    "grouping": [
      { "type": "Dimension", "name": "ResourceGroup" }
    ]
  }
}
```

### Daily Cost Trend

```json
{
  "type": "Usage",
  "timeframe": "MonthToDate",
  "dataset": {
    "granularity": "Daily",
    "aggregation": {
      "totalCost": { "name": "Cost", "function": "Sum" }
    }
  }
}
```

## Verification

```powershell
# Should return JSON with "rows" array
$result = az rest --method POST --uri $uri --body "@$bodyFile" | ConvertFrom-Json
$result.properties.rows | Format-Table
```

## When to Apply

- Any Azure Cost Management API call from PowerShell
- Complex JSON bodies in az rest commands
- Budget alerts and cost analysis scripts

## Tags

`azure` `cost-management` `api` `powershell`
