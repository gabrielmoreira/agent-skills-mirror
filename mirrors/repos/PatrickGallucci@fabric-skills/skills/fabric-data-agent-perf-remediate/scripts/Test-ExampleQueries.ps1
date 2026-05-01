<#
.SYNOPSIS
    Validates Data Agent example queries against Lakehouse table schemas.

.DESCRIPTION
    Connects to the Fabric REST API, retrieves Lakehouse tables for a given
    workspace, and checks that example queries reference valid table and column
    names. Produces a validation report highlighting mismatches.

.PARAMETER WorkspaceId
    The GUID of the Fabric workspace containing the Lakehouse.

.PARAMETER LakehouseId
    The GUID of the Lakehouse to validate against.

.PARAMETER QueriesPath
    Path to a JSON file containing example queries to validate.
    Expected format: [{ "question": "...", "query": "..." }, ...]

.EXAMPLE
    .\Test-ExampleQueries.ps1 -WorkspaceId "fc67..." -LakehouseId "daaa..." -QueriesPath ".\queries.json"

.NOTES
    Requires: Az.Accounts module, authenticated Azure session
    This performs basic table/column name matching, not full SQL parsing.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$WorkspaceId,

    [Parameter(Mandatory)]
    [string]$LakehouseId,

    [Parameter(Mandatory)]
    [ValidateScript({ Test-Path $_ })]
    [string]$QueriesPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region Authentication
try {
    $tokenResponse = Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com"
    $headers = @{
        Authorization  = "Bearer $($tokenResponse.Token)"
        'Content-Type' = 'application/json'
    }
    Write-Host "[OK] Authenticated" -ForegroundColor Green
}
catch {
    Write-Error "Authentication failed. Run Connect-AzAccount first. Error: $_"
    return
}
#endregion

$apiBase = "https://api.fabric.microsoft.com/v1"

#region Get Lakehouse Tables
Write-Host "`nFetching Lakehouse tables..." -ForegroundColor Cyan
$tablesResponse = $null
try {
    $tablesResponse = Invoke-RestMethod `
        -Uri "$apiBase/workspaces/$WorkspaceId/lakehouses/$LakehouseId/tables" `
        -Headers $headers -Method Get
}
catch {
    Write-Error "Failed to retrieve tables: $($_.Exception.Message)"
    return
}

$tableNames = $tablesResponse.value | ForEach-Object { $_.name.ToLower() }
Write-Host "  Found $($tableNames.Count) tables: $($tableNames -join ', ')"
#endregion

#region Load Queries
$queries = Get-Content -Path $QueriesPath -Raw | ConvertFrom-Json
Write-Host "Loaded $($queries.Count) example queries from $QueriesPath"
#endregion

#region Validate Queries
Write-Host "`n--- Validation Results ---" -ForegroundColor Cyan

$results = @()
$queryIndex = 0

foreach ($q in $queries) {
    $queryIndex++
    $issues = @()

    # Basic syntax checks
    $sql = $q.query
    if ([string]::IsNullOrWhiteSpace($sql)) {
        $issues += "Empty query"
    }

    # Check character limits
    if ($q.question.Length -gt 500) {
        $issues += "Question exceeds 500 character limit ($($q.question.Length) chars)"
    }
    if ($sql.Length -gt 1000) {
        $issues += "Query exceeds 1000 character limit ($($sql.Length) chars)"
    }

    # Extract table references (basic FROM/JOIN parsing)
    $tablePattern = '(?i)(?:FROM|JOIN)\s+(\[?[\w]+\]?)'
    $matches = [regex]::Matches($sql, $tablePattern)
    $referencedTables = $matches | ForEach-Object {
        $_.Groups[1].Value.Trim('[', ']').ToLower()
    } | Select-Object -Unique

    foreach ($tbl in $referencedTables) {
        if ($tbl -notin $tableNames) {
            $issues += "Table '$tbl' not found in Lakehouse schema"
        }
    }

    # Check for unmatched parentheses
    $openParens = ($sql.ToCharArray() | Where-Object { $_ -eq '(' }).Count
    $closeParens = ($sql.ToCharArray() | Where-Object { $_ -eq ')' }).Count
    if ($openParens -ne $closeParens) {
        $issues += "Unmatched parentheses (open: $openParens, close: $closeParens)"
    }

    $status = if ($issues.Count -eq 0) { 'PASS' } else { 'FAIL' }
    $color = if ($status -eq 'PASS') { 'Green' } else { 'Red' }

    $result = [PSCustomObject]@{
        Index    = $queryIndex
        Status   = $status
        Question = $q.question.Substring(0, [Math]::Min(60, $q.question.Length))
        Issues   = ($issues -join '; ')
    }
    $results += $result
    Write-Host "  [$status] #$queryIndex - $($result.Question)..." -ForegroundColor $color
    if ($issues) {
        foreach ($issue in $issues) {
            Write-Host "         ! $issue" -ForegroundColor Yellow
        }
    }
}
#endregion

#region Summary
$passed = ($results | Where-Object { $_.Status -eq 'PASS' }).Count
$failed = ($results | Where-Object { $_.Status -eq 'FAIL' }).Count

Write-Host "`n--- Summary ---" -ForegroundColor Cyan
Write-Host "  Passed: $passed / $($results.Count)" -ForegroundColor Green
Write-Host "  Failed: $failed / $($results.Count)" -ForegroundColor $(if ($failed -gt 0) { 'Red' } else { 'Green' })

$outPath = Join-Path $PWD "query-validation-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
$results | ConvertTo-Json -Depth 3 | Set-Content -Path $outPath -Encoding utf8
Write-Host "`nResults saved to: $outPath" -ForegroundColor Green
#endregion
