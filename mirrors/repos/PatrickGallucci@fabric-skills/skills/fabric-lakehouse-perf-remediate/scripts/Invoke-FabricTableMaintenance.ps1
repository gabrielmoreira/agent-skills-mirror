<#
.SYNOPSIS
    Automates Microsoft Fabric Lakehouse table maintenance via REST API.

.DESCRIPTION
    Iterates over specified Delta tables in a Fabric Lakehouse and submits
    table maintenance jobs (OPTIMIZE with V-Order, Z-Order, and/or VACUUM)
    via the Fabric REST API. Polls for job completion with configurable timeout.

.PARAMETER WorkspaceId
    The Fabric workspace GUID.

.PARAMETER LakehouseId
    The Lakehouse item GUID within the workspace.

.PARAMETER Tables
    Array of table configuration objects. Each object supports:
      - TableName (required): Name of the Delta table
      - SchemaName (optional): Schema name, defaults to 'dbo'
      - VOrder (optional): Enable V-Order optimization, defaults to $true
      - ZOrderColumns (optional): Array of column names for Z-Order
      - VacuumRetention (optional): Retention period string, e.g., '7.01:00:00'

.PARAMETER TimeoutMinutes
    Maximum minutes to wait for each maintenance job. Default: 30.

.PARAMETER PollIntervalSeconds
    Seconds between status polls. Default: 15.

.EXAMPLE
    $tables = @(
        @{ TableName = 'sales_fact'; VOrder = $true; ZOrderColumns = @('customer_id'); VacuumRetention = '7.01:00:00' }
        @{ TableName = 'dim_customer'; VOrder = $true }
        @{ TableName = 'dim_product'; VOrder = $true; VacuumRetention = '7.01:00:00' }
    )
    .\Invoke-FabricTableMaintenance.ps1 -WorkspaceId '<guid>' -LakehouseId '<guid>' -Tables $tables

.NOTES
    Requires Az.Accounts module for authentication.
    Run Connect-AzAccount before executing this script.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$WorkspaceId,

    [Parameter(Mandatory)]
    [string]$LakehouseId,

    [Parameter(Mandatory)]
    [hashtable[]]$Tables,

    [int]$TimeoutMinutes = 30,

    [int]$PollIntervalSeconds = 15
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region Functions

function Get-FabricToken {
    <#
    .SYNOPSIS
        Retrieves a Microsoft Entra access token for the Fabric API.
    #>
    try {
        $tokenResponse = Get-AzAccessToken -ResourceUrl 'https://api.fabric.microsoft.com'
        return $tokenResponse.Token
    }
    catch {
        throw "Failed to obtain Fabric API token. Ensure you have run Connect-AzAccount. Error: $_"
    }
}

function Submit-TableMaintenance {
    <#
    .SYNOPSIS
        Submits a table maintenance job via Fabric REST API.
    .OUTPUTS
        The operation ID (GUID) from the Location header.
    #>
    [CmdletBinding()]
    param(
        [string]$Token,
        [string]$WorkspaceId,
        [string]$LakehouseId,
        [hashtable]$TableConfig
    )

    $uri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items/$LakehouseId/jobs/instances?jobType=TableMaintenance"

    $headers = @{
        'Authorization' = "Bearer $Token"
        'Content-Type'  = 'application/json'
    }

    # Build execution data
    $executionData = @{
        tableName  = $TableConfig.TableName
        schemaName = if ($TableConfig.SchemaName) { $TableConfig.SchemaName } else { 'dbo' }
    }

    # Add optimize settings if V-Order or Z-Order requested
    $vOrder = if ($null -ne $TableConfig.VOrder) { $TableConfig.VOrder } else { $true }
    $optimizeSettings = @{ vOrder = $vOrder.ToString().ToLower() }

    if ($TableConfig.ZOrderColumns -and $TableConfig.ZOrderColumns.Count -gt 0) {
        $optimizeSettings.zOrderBy = @($TableConfig.ZOrderColumns)
    }

    $executionData.optimizeSettings = $optimizeSettings

    # Add vacuum settings if retention specified
    if ($TableConfig.VacuumRetention) {
        $executionData.vacuumSettings = @{
            retentionPeriod = $TableConfig.VacuumRetention
        }
    }

    $body = @{ executionData = $executionData } | ConvertTo-Json -Depth 5

    Write-Verbose "Submitting maintenance for table: $($TableConfig.TableName)"
    Write-Verbose "Request body: $body"

    try {
        $response = Invoke-WebRequest -Uri $uri -Method Post -Headers $headers -Body $body -UseBasicParsing

        # Extract operation ID from Location header
        $location = $response.Headers['Location']
        if ($location) {
            $locationStr = if ($location -is [array]) { $location[0] } else { $location }
            $operationId = ($locationStr -split '/')[-1]
            return $operationId
        }
        else {
            Write-Warning "No Location header returned for table $($TableConfig.TableName)."
            return $null
        }
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -eq 409) {
            Write-Warning "Table '$($TableConfig.TableName)': Another maintenance job is already running (409 Conflict). Skipping."
            return $null
        }
        throw "Failed to submit maintenance for table '$($TableConfig.TableName)': $_"
    }
}

function Wait-MaintenanceCompletion {
    <#
    .SYNOPSIS
        Polls the maintenance operation status until completion or timeout.
    #>
    [CmdletBinding()]
    param(
        [string]$Token,
        [string]$WorkspaceId,
        [string]$LakehouseId,
        [string]$OperationId,
        [string]$TableName,
        [int]$TimeoutMinutes,
        [int]$PollIntervalSeconds
    )

    $uri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items/$LakehouseId/jobs/instances/$OperationId"
    $headers = @{ 'Authorization' = "Bearer $Token" }

    $deadline = (Get-Date).AddMinutes($TimeoutMinutes)

    while ((Get-Date) -lt $deadline) {
        try {
            $status = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get

            switch ($status.status) {
                'Completed' {
                    Write-Host "  [OK] Table '$TableName' maintenance completed." -ForegroundColor Green
                    return $status
                }
                'Failed' {
                    Write-Warning "  [FAIL] Table '$TableName' maintenance failed. Reason: $($status.failureReason)"
                    return $status
                }
                'Canceled' {
                    Write-Warning "  [CANCELED] Table '$TableName' maintenance was canceled."
                    return $status
                }
                'Deduped' {
                    Write-Warning "  [SKIPPED] Table '$TableName' maintenance deduped (another job running)."
                    return $status
                }
                default {
                    Write-Verbose "  Table '$TableName' status: $($status.status). Waiting $PollIntervalSeconds seconds..."
                    Start-Sleep -Seconds $PollIntervalSeconds
                }
            }
        }
        catch {
            Write-Warning "  Error polling status for '$TableName': $_. Retrying..."
            Start-Sleep -Seconds $PollIntervalSeconds
        }
    }

    Write-Warning "  [TIMEOUT] Table '$TableName' maintenance did not complete within $TimeoutMinutes minutes."
    return @{ status = 'Timeout'; tableName = $TableName }
}

#endregion Functions

#region Main

Write-Host "`n=== Fabric Lakehouse Table Maintenance ===" -ForegroundColor Cyan
Write-Host "Workspace: $WorkspaceId"
Write-Host "Lakehouse: $LakehouseId"
Write-Host "Tables:    $($Tables.Count)"
Write-Host ""

# Authenticate
Write-Host "Authenticating..." -ForegroundColor Yellow
$token = Get-FabricToken
Write-Host "Authentication successful.`n" -ForegroundColor Green

# Process each table
$results = @()

foreach ($tableConfig in $Tables) {
    $tableName = $tableConfig.TableName
    Write-Host "Processing table: $tableName" -ForegroundColor Cyan

    $operationId = Submit-TableMaintenance -Token $token `
        -WorkspaceId $WorkspaceId `
        -LakehouseId $LakehouseId `
        -TableConfig $tableConfig

    if ($operationId) {
        Write-Host "  Submitted. Operation ID: $operationId"
        $result = Wait-MaintenanceCompletion -Token $token `
            -WorkspaceId $WorkspaceId `
            -LakehouseId $LakehouseId `
            -OperationId $operationId `
            -TableName $tableName `
            -TimeoutMinutes $TimeoutMinutes `
            -PollIntervalSeconds $PollIntervalSeconds

        $results += @{
            TableName   = $tableName
            OperationId = $operationId
            Status      = $result.status
            StartTime   = $result.startTimeUtc
            EndTime     = $result.endTimeUtc
        }
    }
    else {
        $results += @{
            TableName   = $tableName
            OperationId = $null
            Status      = 'Skipped'
            StartTime   = $null
            EndTime     = $null
        }
    }

    Write-Host ""
}

# Summary
Write-Host "`n=== Maintenance Summary ===" -ForegroundColor Cyan
$results | ForEach-Object {
    $color = switch ($_.Status) {
        'Completed' { 'Green' }
        'Skipped'   { 'Yellow' }
        default     { 'Red' }
    }
    Write-Host "  $($_.TableName): $($_.Status)" -ForegroundColor $color
}

Write-Host "`nDone." -ForegroundColor Cyan

#endregion Main
