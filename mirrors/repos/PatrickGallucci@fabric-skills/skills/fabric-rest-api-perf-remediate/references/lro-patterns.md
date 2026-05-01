# Long Running Operation (LRO) Patterns

## Table of Contents

- [LRO Lifecycle](#lro-lifecycle)
- [Polling State Machine](#polling-state-machine)
- [PowerShell Polling Implementation](#powershell-polling-implementation)
- [C# Polling Implementation](#csharp-polling-implementation)
- [Parallel LRO Management](#parallel-lro-management)
- [Cancellation Patterns](#cancellation-patterns)
- [Common Pitfalls](#common-pitfalls)

---

## LRO Lifecycle

When a Fabric API initiates a long running operation, the flow is:

```
Client                          Fabric API
  │                                │
  │── POST /create-item ──────────>│
  │                                │
  │<── 202 Accepted ──────────────│
  │    Location: /operations/{id}  │
  │    x-ms-operation-id: {id}     │
  │    Retry-After: 30             │
  │                                │
  │ (wait Retry-After seconds)     │
  │                                │
  │── GET /operations/{id} ───────>│
  │<── 200 { status: "Running" } ──│
  │                                │
  │ (wait with backoff)            │
  │                                │
  │── GET /operations/{id} ───────>│
  │<── 200 { status: "Succeeded" }─│
  │    Location: /operations/{id}/result
  │                                │
  │── GET /operations/{id}/result ─>│
  │<── 200 { item details }  ──────│
```

**Response Headers on 202:**

| Header | Value | Purpose |
|--------|-------|---------|
| `Location` | Operation state URL | Polling endpoint |
| `x-ms-operation-id` | GUID | Build polling URL manually |
| `Retry-After` | Integer (seconds) | Minimum wait before first poll |

**Terminal Statuses:** `Succeeded`, `Failed`, `Skipped`, `Completed`

Not all LROs produce a result. Some operations run to completion without a result URL. Check API documentation for specific endpoints.

---

## Polling State Machine

```
                    ┌──────────────┐
                    │   Initial    │
                    │  (202 recv)  │
                    └──────┬───────┘
                           │
                    Wait Retry-After
                           │
                    ┌──────▼───────┐
              ┌─────│   Polling    │─────┐
              │     └──────┬───────┘     │
              │            │             │
        ┌─────▼────┐ ┌────▼─────┐ ┌─────▼────┐
        │ Succeeded │ │  Failed  │ │ Skipped  │
        └─────┬────┘ └────┬─────┘ └────┬─────┘
              │            │             │
        Fetch Result   Log Error    Log Skip
```

**State Transitions:**

- `Running` → `Running` (still processing, poll again)
- `Running` → `Succeeded` (done, fetch result)
- `Running` → `Failed` (error occurred)
- `Running` → `Skipped` (operation was bypassed)

---

## PowerShell Polling Implementation

### Basic Polling Loop

```powershell
function Wait-FabricOperation {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$OperationUrl,
        [Parameter(Mandatory)][hashtable]$Headers,
        [int]$InitialWaitSeconds = 5,
        [int]$MaxWaitMinutes = 30,
        [int]$MaxWaitSeconds = 60
    )

    $deadline = (Get-Date).AddMinutes($MaxWaitMinutes)
    $waitSeconds = $InitialWaitSeconds

    Write-Verbose "Polling operation: $OperationUrl"

    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds $waitSeconds

        try {
            $response = Invoke-WebRequest -Uri $OperationUrl -Headers $Headers -Method Get
            $operation = $response.Content | ConvertFrom-Json

            Write-Verbose "Status: $($operation.status) | Progress: $($operation.percentComplete)%"

            switch ($operation.status) {
                'Succeeded' {
                    # Check if Location header now points to result
                    $resultUrl = $response.Headers['Location']
                    if ($resultUrl) {
                        $result = Invoke-RestMethod -Uri $resultUrl -Headers $Headers -Method Get
                        return @{
                            Status = 'Succeeded'
                            Result = $result
                            OperationUrl = $OperationUrl
                        }
                    }
                    return @{
                        Status    = 'Succeeded'
                        Operation = $operation
                    }
                }
                'Failed' {
                    return @{
                        Status = 'Failed'
                        Error  = $operation.error
                    }
                }
                { $_ -in 'Skipped', 'Completed' } {
                    return @{
                        Status    = $_
                        Operation = $operation
                    }
                }
                'Running' {
                    # Update wait from Retry-After if present
                    $retryAfter = $response.Headers['Retry-After']
                    if ($retryAfter) {
                        $waitSeconds = [int]$retryAfter
                    }
                    else {
                        # Exponential backoff capped at MaxWaitSeconds
                        $waitSeconds = [math]::Min($waitSeconds * 2, $MaxWaitSeconds)
                    }
                }
            }
        }
        catch {
            $httpStatus = [int]$_.Exception.Response.StatusCode
            if ($httpStatus -eq 429) {
                $retryAfter = $_.Exception.Response.Headers['Retry-After']
                $waitSeconds = if ($retryAfter) { [int]$retryAfter } else { 60 }
                Write-Warning "Throttled during polling. Waiting ${waitSeconds}s..."
            }
            else {
                throw
            }
        }
    }

    throw "Operation timed out after $MaxWaitMinutes minutes."
}
```

### Usage

```powershell
# After receiving 202 from a create operation
$locationUrl = $createResponse.Headers['Location']

$result = Wait-FabricOperation `
    -OperationUrl $locationUrl `
    -Headers $headers `
    -InitialWaitSeconds 10 `
    -MaxWaitMinutes 15

if ($result.Status -eq 'Succeeded') {
    Write-Host "Item created: $($result.Result.id)"
}
```

---

## C# Polling Implementation

```csharp
public async Task<OperationResult> PollOperationAsync(
    HttpClient client, string operationUrl,
    TimeSpan? initialDelay = null, TimeSpan? maxDuration = null,
    CancellationToken ct = default)
{
    var delay = initialDelay ?? TimeSpan.FromSeconds(5);
    var deadline = DateTime.UtcNow + (maxDuration ?? TimeSpan.FromMinutes(30));
    var maxDelay = TimeSpan.FromSeconds(60);

    while (DateTime.UtcNow < deadline)
    {
        await Task.Delay(delay, ct);

        var response = await client.GetAsync(operationUrl, ct);

        if (response.StatusCode == (HttpStatusCode)429)
        {
            delay = response.Headers.RetryAfter?.Delta ?? TimeSpan.FromSeconds(60);
            continue;
        }

        response.EnsureSuccessStatusCode();
        var operation = await response.Content
            .ReadFromJsonAsync<FabricOperation>(cancellationToken: ct);

        switch (operation.Status)
        {
            case "Succeeded":
                var resultUrl = response.Headers.Location?.ToString();
                object? result = resultUrl != null
                    ? await client.GetFromJsonAsync<object>(resultUrl, ct)
                    : null;
                return new OperationResult("Succeeded", result);

            case "Failed":
                return new OperationResult("Failed", operation.Error);

            case "Skipped":
            case "Completed":
                return new OperationResult(operation.Status, null);

            default: // Running
                if (response.Headers.RetryAfter?.Delta is { } ra)
                    delay = ra;
                else
                    delay = TimeSpan.FromMilliseconds(
                        Math.Min(delay.TotalMilliseconds * 2, maxDelay.TotalMilliseconds));
                break;
        }
    }

    throw new TimeoutException($"Operation timed out: {operationUrl}");
}
```

---

## Parallel LRO Management

When creating multiple items that each trigger LROs:

```powershell
# Stage 1: Submit all operations
$operations = foreach ($item in $itemsToCreate) {
    $response = Invoke-WebRequest -Uri $createUri -Headers $headers `
        -Method Post -Body ($item | ConvertTo-Json)

    if ($response.StatusCode -eq 202) {
        [PSCustomObject]@{
            Name         = $item.displayName
            OperationUrl = $response.Headers['Location']
            OperationId  = $response.Headers['x-ms-operation-id']
            Status       = 'Pending'
        }
    }
}

# Stage 2: Poll all operations with staggered checks
$pending = [System.Collections.Generic.List[object]]($operations)

while ($pending.Count -gt 0) {
    Start-Sleep -Seconds 10  # Batch polling interval

    $stillPending = [System.Collections.Generic.List[object]]::new()

    foreach ($op in $pending) {
        $pollResponse = Invoke-RestMethod -Uri $op.OperationUrl -Headers $headers
        $op.Status = $pollResponse.status

        if ($pollResponse.status -in 'Succeeded', 'Failed', 'Skipped') {
            Write-Host "$($op.Name): $($pollResponse.status)"
        }
        else {
            $stillPending.Add($op)
        }
    }

    $pending = $stillPending
    Write-Host "  $($pending.Count) operations still running..."
}
```

---

## Cancellation Patterns

Some Fabric LROs support cancellation. For example, environment publish operations:

```powershell
# Cancel an in-progress publish
POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/environments/{artifactId}/staging/cancelPublish
```

Check individual API documentation to determine if cancellation is supported for a given operation type.

---

## Common Pitfalls

| Pitfall | Impact | Fix |
|---------|--------|-----|
| Polling immediately after 202 | Wasted call, always returns Running | Honor Retry-After from initial response |
| Fixed 1-second poll interval | Excessive calls, risks throttling | Use exponential backoff |
| Not checking for Failed | Infinite loop | Always handle terminal statuses |
| Ignoring Location header transitions | Missing result data | Location changes from State URL to Result URL on completion |
| Not handling 429 during polling | Polling loop crashes | Wrap poll in retry-with-backoff logic |
| Fire-and-forget multiple LROs | No visibility into failures | Track all operations, poll in batch |
