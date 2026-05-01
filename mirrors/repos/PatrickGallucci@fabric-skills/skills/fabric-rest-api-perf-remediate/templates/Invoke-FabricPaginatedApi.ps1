<#
.SYNOPSIS
    Efficiently enumerates all pages of a Microsoft Fabric paginated REST API.

.DESCRIPTION
    Template function for walking Fabric API paginated responses. Uses the
    continuationUri pattern to fetch all pages, with built-in retry logic for
    429 throttling, timing instrumentation, and optional early termination.

    Customize this template for your specific use case.

.PARAMETER InitialUri
    The first API URL to call (e.g., workspaces/{id}/items endpoint).

.PARAMETER Headers
    Authentication headers including Bearer token.

.PARAMETER MaxPages
    Safety limit on number of pages to fetch. Default: 100.

.PARAMETER Filter
    Optional scriptblock filter. If provided, enumeration stops when the first
    matching item is found. Example: { $_.displayName -eq 'TargetNotebook' }

.PARAMETER RetryCount
    Maximum retries per page on 429 throttling. Default: 3.

.EXAMPLE
    # Enumerate all items in a workspace
    $items = Invoke-FabricPaginatedApi `
        -InitialUri "https://api.fabric.microsoft.com/v1/workspaces/$wsId/items" `
        -Headers $headers

.EXAMPLE
    # Find a specific item (early termination)
    $match = Invoke-FabricPaginatedApi `
        -InitialUri "https://api.fabric.microsoft.com/v1/workspaces/$wsId/items" `
        -Headers $headers `
        -Filter { $_.displayName -eq 'MyLakehouse' }

.OUTPUTS
    [PSCustomObject] with properties:
    - Items: Array of all collected items
    - PageCount: Number of pages fetched
    - TotalDurationMs: End-to-end time
    - PageTimings: Array of per-page latency measurements
    - EarlyTermination: Boolean indicating if filter matched before all pages
#>
function Invoke-FabricPaginatedApi {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$InitialUri,

        [Parameter(Mandatory)]
        [hashtable]$Headers,

        [int]$MaxPages = 100,

        [scriptblock]$Filter,

        [int]$RetryCount = 3
    )

    $allItems = [System.Collections.Generic.List[object]]::new()
    $pageTimings = [System.Collections.Generic.List[PSCustomObject]]::new()
    $overallSw = [System.Diagnostics.Stopwatch]::StartNew()

    $currentUri = $InitialUri
    $pageNumber = 0
    $earlyTermination = $false

    while ($currentUri -and $pageNumber -lt $MaxPages) {
        $pageNumber++
        $pageSw = [System.Diagnostics.Stopwatch]::StartNew()

        $response = $null
        $attempt = 0

        # Retry loop for throttling
        do {
            $attempt++
            try {
                $response = Invoke-RestMethod -Uri $currentUri -Headers $Headers -Method Get -ErrorAction Stop
            }
            catch {
                $statusCode = [int]$_.Exception.Response.StatusCode

                if ($statusCode -eq 429 -and $attempt -le $RetryCount) {
                    $retryAfter = $_.Exception.Response.Headers['Retry-After']
                    $waitSeconds = if ($retryAfter) { [int]$retryAfter } else { 30 }

                    # Add jitter
                    $jitter = Get-Random -Minimum 0 -Maximum ([math]::Ceiling($waitSeconds * 0.25))
                    Write-Verbose "Page $pageNumber throttled (attempt $attempt). Waiting $($waitSeconds + $jitter)s..."
                    Start-Sleep -Seconds ($waitSeconds + $jitter)
                }
                else {
                    throw
                }
            }
        } while (-not $response -and $attempt -le $RetryCount)

        $pageSw.Stop()

        if (-not $response) {
            Write-Warning "Page $pageNumber: Failed after $RetryCount retries."
            break
        }

        # Collect items
        $pageItems = $response.value
        $itemCount = if ($pageItems) { $pageItems.Count } else { 0 }

        $pageTimings.Add([PSCustomObject]@{
            Page     = $pageNumber
            Items    = $itemCount
            Ms       = $pageSw.ElapsedMilliseconds
            Attempts = $attempt
        })

        if ($pageItems) {
            # Check filter for early termination
            if ($Filter) {
                foreach ($item in $pageItems) {
                    $allItems.Add($item)
                    if (& $Filter $item) {
                        Write-Verbose "Filter matched on page $pageNumber. Stopping enumeration."
                        $earlyTermination = $true
                        break
                    }
                }
                if ($earlyTermination) { break }
            }
            else {
                $allItems.AddRange($pageItems)
            }
        }

        Write-Verbose "Page $pageNumber: $itemCount items in $($pageSw.ElapsedMilliseconds)ms"

        # Navigate to next page using continuationUri
        $currentUri = $response.continuationUri
    }

    $overallSw.Stop()

    [PSCustomObject]@{
        Items            = $allItems.ToArray()
        PageCount        = $pageNumber
        TotalItems       = $allItems.Count
        TotalDurationMs  = $overallSw.ElapsedMilliseconds
        PageTimings      = $pageTimings.ToArray()
        EarlyTermination = $earlyTermination
        Throughput       = if ($overallSw.ElapsedMilliseconds -gt 0) {
            [math]::Round(($allItems.Count / $overallSw.ElapsedMilliseconds) * 1000, 1)
        } else { 0 }
    }
}

# ============================================================
# Example Usage (uncomment and customize)
# ============================================================

# $token = "your-bearer-token"
# $workspaceId = "your-workspace-guid"
#
# $headers = @{
#     'Authorization' = "Bearer $token"
#     'Content-Type'  = 'application/json'
# }
#
# # Enumerate all items
# $result = Invoke-FabricPaginatedApi `
#     -InitialUri "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/items" `
#     -Headers $headers `
#     -Verbose
#
# Write-Host "Total items: $($result.TotalItems)"
# Write-Host "Pages: $($result.PageCount)"
# Write-Host "Duration: $($result.TotalDurationMs)ms"
# Write-Host "Throughput: $($result.Throughput) items/sec"
# $result.PageTimings | Format-Table -AutoSize
