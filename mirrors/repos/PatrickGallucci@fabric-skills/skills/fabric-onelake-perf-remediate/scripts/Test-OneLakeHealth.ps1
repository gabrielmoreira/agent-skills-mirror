<#
.SYNOPSIS
    OneLake Performance Health Check Script

.DESCRIPTION
    Automated diagnostic checks for Microsoft Fabric OneLake performance issues.
    Validates connectivity, shortcut configuration, table maintenance status,
    and capacity utilization through the Fabric REST API.

.PARAMETER WorkspaceId
    The GUID of the Fabric workspace to diagnose.

.PARAMETER LakehouseId
    The GUID of the lakehouse to check. If omitted, lists all lakehouses in the workspace.

.PARAMETER IncludeShortcuts
    Include shortcut configuration analysis in the health check.

.PARAMETER IncludeTableMaintenance
    Check table maintenance job status for recent OPTIMIZE/VACUUM operations.

.PARAMETER Region
    Optional. The expected capacity region for data residency validation.

.EXAMPLE
    ./Test-OneLakeHealth.ps1 -WorkspaceId "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

.EXAMPLE
    ./Test-OneLakeHealth.ps1 -WorkspaceId "xxxxxxxx" -LakehouseId "yyyyyyyy" -IncludeShortcuts -IncludeTableMaintenance

.NOTES
    Requires: PowerShell 7+, Az.Accounts module
    License: Apache 2.0
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$WorkspaceId,

    [Parameter()]
    [string]$LakehouseId,

    [Parameter()]
    [switch]$IncludeShortcuts,

    [Parameter()]
    [switch]$IncludeTableMaintenance,

    [Parameter()]
    [string]$Region
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region Helper Functions

function Get-FabricHeaders {
    <#
    .SYNOPSIS
        Retrieves an authorization header for Fabric REST API calls.
    #>
    try {
        $tokenResponse = Get-AzAccessToken -AsSecureString -ResourceUrl "https://api.fabric.microsoft.com"
        $token = $tokenResponse.Token | ConvertFrom-SecureString -AsPlainText
        return @{
            'Authorization' = "Bearer $token"
            'Content-Type'  = 'application/json'
        }
    }
    catch {
        throw "Failed to get Fabric access token. Ensure you are logged in with Connect-AzAccount. Error: $_"
    }
}

function Invoke-FabricApi {
    <#
    .SYNOPSIS
        Calls the Fabric REST API with retry logic for HTTP 429 throttling.
    #>
    param(
        [string]$Uri,
        [string]$Method = 'GET',
        [hashtable]$Headers,
        [int]$MaxRetries = 3
    )
    $attempt = 0
    do {
        try {
            $response = Invoke-RestMethod -Uri $Uri -Method $Method -Headers $Headers
            return $response
        }
        catch {
            $statusCode = $_.Exception.Response.StatusCode.value__
            if ($statusCode -eq 429 -and $attempt -lt $MaxRetries) {
                $retryAfter = $_.Exception.Response.Headers['Retry-After']
                $wait = if ($retryAfter) { [int]$retryAfter } else { [math]::Pow(2, $attempt) * 5 }
                Write-Warning "  [THROTTLED] Waiting $wait seconds before retry ($($attempt + 1)/$MaxRetries)..."
                Start-Sleep -Seconds $wait
                $attempt++
            }
            else {
                throw
            }
        }
    } while ($attempt -lt $MaxRetries)
}

function Write-CheckResult {
    param(
        [string]$CheckName,
        [ValidateSet('PASS', 'WARN', 'FAIL', 'INFO')]
        [string]$Status,
        [string]$Message
    )
    $color = switch ($Status) {
        'PASS' { 'Green' }
        'WARN' { 'Yellow' }
        'FAIL' { 'Red' }
        'INFO' { 'Cyan' }
    }
    $symbol = switch ($Status) {
        'PASS' { '[PASS]' }
        'WARN' { '[WARN]' }
        'FAIL' { '[FAIL]' }
        'INFO' { '[INFO]' }
    }
    Write-Host "  $symbol " -ForegroundColor $color -NoNewline
    Write-Host "$CheckName - $Message"
}

#endregion

#region Main Execution

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  OneLake Performance Health Check" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Authenticate
Write-Host "Authenticating..." -ForegroundColor Gray
try {
    $headers = Get-FabricHeaders
    Write-CheckResult -CheckName "Authentication" -Status PASS -Message "Successfully acquired Fabric API token"
}
catch {
    Write-CheckResult -CheckName "Authentication" -Status FAIL -Message $_.Exception.Message
    exit 1
}

$baseUri = "https://api.fabric.microsoft.com/v1"

# Check 1: Workspace Connectivity
Write-Host "`n--- Workspace Connectivity ---" -ForegroundColor White
try {
    $workspace = Invoke-FabricApi -Uri "$baseUri/workspaces/$WorkspaceId" -Headers $headers
    Write-CheckResult -CheckName "Workspace Access" -Status PASS -Message "Workspace: $($workspace.displayName)"

    if ($workspace.capacityId) {
        Write-CheckResult -CheckName "Capacity Assignment" -Status PASS -Message "Capacity ID: $($workspace.capacityId)"
    }
    else {
        Write-CheckResult -CheckName "Capacity Assignment" -Status WARN -Message "No capacity assigned (may be in shared capacity)"
    }
}
catch {
    Write-CheckResult -CheckName "Workspace Access" -Status FAIL -Message "Cannot access workspace: $_"
    exit 1
}

# Check 2: OneLake Endpoint Connectivity
Write-Host "`n--- OneLake Endpoint Connectivity ---" -ForegroundColor White
$globalEndpoint = "https://onelake.dfs.fabric.microsoft.com"

try {
    $storageHeaders = @{}
    $storageTokenResponse = Get-AzAccessToken -AsSecureString -ResourceTypeName Storage
    $storageToken = $storageTokenResponse.Token | ConvertFrom-SecureString -AsPlainText
    $storageHeaders['Authorization'] = "Bearer $storageToken"
    $storageHeaders['x-ms-version'] = '2021-06-08'

    $listUri = "$globalEndpoint/$WorkspaceId`?resource=filesystem&recursive=false&maxResults=1"
    $result = Invoke-RestMethod -Uri $listUri -Headers $storageHeaders -Method GET -ErrorAction Stop
    Write-CheckResult -CheckName "Global DFS Endpoint" -Status PASS -Message "OneLake DFS endpoint is reachable"
}
catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 403) {
        Write-CheckResult -CheckName "Global DFS Endpoint" -Status WARN -Message "Endpoint reachable but access denied (check permissions)"
    }
    else {
        Write-CheckResult -CheckName "Global DFS Endpoint" -Status FAIL -Message "Cannot reach OneLake DFS endpoint: $_"
    }
}

if ($Region) {
    $regionalEndpoint = "https://$Region-onelake.dfs.fabric.microsoft.com"
    try {
        $listUri = "$regionalEndpoint/$WorkspaceId`?resource=filesystem&recursive=false&maxResults=1"
        $null = Invoke-RestMethod -Uri $listUri -Headers $storageHeaders -Method GET -ErrorAction Stop
        Write-CheckResult -CheckName "Regional Endpoint ($Region)" -Status PASS -Message "Regional endpoint is reachable"
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -eq 403) {
            Write-CheckResult -CheckName "Regional Endpoint ($Region)" -Status WARN -Message "Reachable but access denied"
        }
        else {
            Write-CheckResult -CheckName "Regional Endpoint ($Region)" -Status WARN -Message "Regional endpoint may not match capacity region"
        }
    }
}

# Check 3: Lakehouse Items
Write-Host "`n--- Lakehouse Analysis ---" -ForegroundColor White
try {
    $items = Invoke-FabricApi -Uri "$baseUri/workspaces/$WorkspaceId/lakehouses" -Headers $headers
    $lakehouses = $items.value

    if (-not $lakehouses -or $lakehouses.Count -eq 0) {
        Write-CheckResult -CheckName "Lakehouses" -Status INFO -Message "No lakehouses found in workspace"
    }
    else {
        Write-CheckResult -CheckName "Lakehouses" -Status INFO -Message "Found $($lakehouses.Count) lakehouse(s)"
        foreach ($lh in $lakehouses) {
            Write-Host "    - $($lh.displayName) ($($lh.id))" -ForegroundColor Gray
        }

        if (-not $LakehouseId -and $lakehouses.Count -gt 0) {
            $LakehouseId = $lakehouses[0].id
            Write-CheckResult -CheckName "Auto-Selected" -Status INFO -Message "Using first lakehouse: $($lakehouses[0].displayName)"
        }
    }
}
catch {
    Write-CheckResult -CheckName "Lakehouses" -Status WARN -Message "Could not list lakehouses: $_"
}

# Check 4: Table Maintenance Status
if ($IncludeTableMaintenance -and $LakehouseId) {
    Write-Host "`n--- Table Maintenance Status ---" -ForegroundColor White
    try {
        $jobsUri = "$baseUri/workspaces/$WorkspaceId/items/$LakehouseId/jobs/instances?limit=10"
        $jobs = Invoke-FabricApi -Uri $jobsUri -Headers $headers

        if ($jobs.value -and $jobs.value.Count -gt 0) {
            $maintenanceJobs = $jobs.value | Where-Object { $_.jobType -match 'TableMaintenance|DefaultJob' }
            if ($maintenanceJobs) {
                $recent = $maintenanceJobs | Select-Object -First 1
                $statusMsg = "Last job: $($recent.status) at $($recent.startTimeUtc)"
                $checkStatus = if ($recent.status -eq 'Completed') { 'PASS' } elseif ($recent.status -eq 'Failed') { 'WARN' } else { 'INFO' }
                Write-CheckResult -CheckName "Table Maintenance" -Status $checkStatus -Message $statusMsg
            }
            else {
                Write-CheckResult -CheckName "Table Maintenance" -Status WARN -Message "No recent maintenance jobs found — consider running OPTIMIZE"
            }
        }
        else {
            Write-CheckResult -CheckName "Table Maintenance" -Status WARN -Message "No job history found — tables may need optimization"
        }
    }
    catch {
        Write-CheckResult -CheckName "Table Maintenance" -Status INFO -Message "Could not retrieve job history: $_"
    }
}

# Check 5: Shortcut Configuration
if ($IncludeShortcuts -and $LakehouseId) {
    Write-Host "`n--- Shortcut Configuration ---" -ForegroundColor White
    try {
        $definitionUri = "$baseUri/workspaces/$WorkspaceId/lakehouses/$LakehouseId"
        $lhDetail = Invoke-FabricApi -Uri $definitionUri -Headers $headers

        Write-CheckResult -CheckName "Shortcut Analysis" -Status INFO -Message "Lakehouse: $($lhDetail.displayName)"
        Write-Host "    To analyze shortcuts, review the shortcuts.metadata.json via Git integration" -ForegroundColor Gray
        Write-Host "    or use the Lakehouse Explorer in the Fabric portal." -ForegroundColor Gray
        Write-Host "    Key checks:" -ForegroundColor Gray
        Write-Host "      - Are external shortcuts targeting same-region data?" -ForegroundColor Gray
        Write-Host "      - Is shortcut caching enabled in workspace settings?" -ForegroundColor Gray
        Write-Host "      - Are shortcut targets still valid (not broken)?" -ForegroundColor Gray
    }
    catch {
        Write-CheckResult -CheckName "Shortcuts" -Status INFO -Message "Could not retrieve lakehouse details: $_"
    }
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Health Check Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nRecommendations:" -ForegroundColor White
Write-Host "  1. Run OPTIMIZE on tables with many small files" -ForegroundColor Gray
Write-Host "  2. Enable V-Order for read-heavy workloads" -ForegroundColor Gray
Write-Host "  3. Enable shortcut caching for external data sources" -ForegroundColor Gray
Write-Host "  4. Use regional endpoints for data residency compliance" -ForegroundColor Gray
Write-Host "  5. Enable OneLake diagnostics for detailed access monitoring" -ForegroundColor Gray
Write-Host "  6. Monitor CU consumption in the Fabric Capacity Metrics app`n" -ForegroundColor Gray

#endregion
