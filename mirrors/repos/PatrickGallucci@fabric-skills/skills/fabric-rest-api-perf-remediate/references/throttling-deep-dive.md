# Throttling Deep Dive

## Table of Contents

- [How Fabric Throttling Works](#how-fabric-throttling-works)
- [Retry-After Handling](#retry-after-handling)
- [Exponential Backoff with Jitter](#exponential-backoff-with-jitter)
- [Token Bucket Rate Limiter](#token-bucket-rate-limiter)
- [Caller Isolation Strategy](#caller-isolation-strategy)
- [Request Batching Patterns](#request-batching-patterns)
- [Monitoring and Alerting](#monitoring-and-alerting)

---

## How Fabric Throttling Works

Microsoft Fabric applies throttling at two levels:

1. **Per-user, per-API** — Each authenticated user has a call budget per API endpoint within a sliding time window.
2. **Per-API global** — The API itself may have an overall throughput cap independent of the caller.

When either limit is exceeded, the API returns:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 55
Content-Type: application/json
```

Key behaviors:

- Every Fabric admin and core public API call is subject to throttling.
- The exact rate limits are not published by Microsoft — they can change without notice.
- The `Retry-After` value is the minimum wait time in seconds.
- Continuing to send requests during the cooldown period may extend the throttle duration.

---

## Retry-After Handling

Always parse and honor the `Retry-After` response header.

### PowerShell Implementation

```powershell
function Invoke-FabricApiWithRetry {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Uri,
        [Parameter(Mandatory)][hashtable]$Headers,
        [string]$Method = 'Get',
        [string]$Body,
        [int]$MaxRetries = 3
    )

    $attempt = 0
    do {
        $attempt++
        try {
            $params = @{
                Uri     = $Uri
                Headers = $Headers
                Method  = $Method
            }
            if ($Body) { $params.Body = $Body }

            return Invoke-RestMethod @params
        }
        catch {
            $statusCode = [int]$_.Exception.Response.StatusCode

            if ($statusCode -eq 429 -and $attempt -le $MaxRetries) {
                $retryAfter = $_.Exception.Response.Headers['Retry-After']
                $waitSeconds = if ($retryAfter) { [int]$retryAfter } else { 30 }

                # Add jitter: 0-25% of wait time
                $jitter = Get-Random -Minimum 0 -Maximum ([math]::Ceiling($waitSeconds * 0.25))
                $totalWait = $waitSeconds + $jitter

                Write-Warning "Throttled (attempt $attempt/$MaxRetries). Waiting ${totalWait}s..."
                Start-Sleep -Seconds $totalWait
            }
            else {
                throw
            }
        }
    } while ($attempt -le $MaxRetries)
}
```

### C# Implementation

```csharp
public async Task<HttpResponseMessage> InvokeWithRetryAsync(
    HttpClient client, HttpRequestMessage request, int maxRetries = 3)
{
    for (int attempt = 1; attempt <= maxRetries + 1; attempt++)
    {
        var response = await client.SendAsync(CloneRequest(request));

        if (response.StatusCode != (HttpStatusCode)429 || attempt > maxRetries)
            return response;

        var retryAfter = response.Headers.RetryAfter?.Delta
            ?? TimeSpan.FromSeconds(30);

        // Add jitter
        var jitter = TimeSpan.FromMilliseconds(
            Random.Shared.Next(0, (int)(retryAfter.TotalMilliseconds * 0.25)));

        await Task.Delay(retryAfter + jitter);
    }

    throw new InvalidOperationException("Unreachable");
}
```

---

## Exponential Backoff with Jitter

When `Retry-After` is absent, use exponential backoff with decorrelated jitter.

```powershell
function Get-BackoffDelay {
    param(
        [int]$Attempt,
        [int]$BaseDelayMs = 1000,
        [int]$MaxDelayMs = 60000
    )

    # Exponential: 1s, 2s, 4s, 8s, ...
    $exponential = $BaseDelayMs * [math]::Pow(2, $Attempt - 1)

    # Cap at max
    $capped = [math]::Min($exponential, $MaxDelayMs)

    # Decorrelated jitter: random between base and capped
    $jittered = Get-Random -Minimum $BaseDelayMs -Maximum ([int]$capped + 1)

    return $jittered
}
```

---

## Token Bucket Rate Limiter

Implement client-side rate limiting to avoid triggering server-side throttling.

```powershell
class TokenBucket {
    [int]$MaxTokens
    [double]$RefillRatePerSecond
    [double]$CurrentTokens
    [datetime]$LastRefill

    TokenBucket([int]$maxTokens, [double]$refillRate) {
        $this.MaxTokens = $maxTokens
        $this.RefillRatePerSecond = $refillRate
        $this.CurrentTokens = $maxTokens
        $this.LastRefill = Get-Date
    }

    [bool] TryConsume() {
        $this.Refill()

        if ($this.CurrentTokens -ge 1) {
            $this.CurrentTokens--
            return $true
        }
        return $false
    }

    [double] WaitTimeSeconds() {
        $this.Refill()
        if ($this.CurrentTokens -ge 1) { return 0 }
        return (1 - $this.CurrentTokens) / $this.RefillRatePerSecond
    }

    hidden [void] Refill() {
        $now = Get-Date
        $elapsed = ($now - $this.LastRefill).TotalSeconds
        $this.CurrentTokens = [math]::Min(
            $this.MaxTokens,
            $this.CurrentTokens + ($elapsed * $this.RefillRatePerSecond)
        )
        $this.LastRefill = $now
    }
}

# Usage: Allow 10 requests per second with burst of 20
$limiter = [TokenBucket]::new(20, 10)

foreach ($item in $workItems) {
    $wait = $limiter.WaitTimeSeconds()
    if ($wait -gt 0) {
        Start-Sleep -Milliseconds ([int]($wait * 1000))
    }
    if ($limiter.TryConsume()) {
        Invoke-FabricApiWithRetry -Uri $item.Uri -Headers $headers
    }
}
```

---

## Caller Isolation Strategy

Use separate service principal identities for independent workloads to avoid sharing throttle budgets.

| Workload | Service Principal | Scope |
|----------|------------------|-------|
| CI/CD deployment | `sp-fabric-deploy` | Item.ReadWrite.All |
| Monitoring/governance | `sp-fabric-monitor` | Item.Read.All |
| Data pipeline orchestration | `sp-fabric-pipeline` | Item.Execute.All |
| Ad-hoc automation | User identity | Workspace-scoped |

Each principal has its own per-user rate limit, effectively multiplying your available throughput.

---

## Request Batching Patterns

Reduce total API calls by combining operations:

1. **Use List APIs instead of individual GETs** — One `GET /workspaces/{id}/items` returns all items instead of N individual calls.
2. **Filter server-side** — Use query parameters to reduce response size rather than filtering client-side across multiple pages.
3. **Cache workspace metadata** — Workspace and item IDs change infrequently. Cache for 5-15 minutes.
4. **Batch item creation** — When creating multiple items, space them with controlled delays rather than fire-and-forget.

---

## Monitoring and Alerting

Track these metrics to detect throttling before it impacts production:

| Metric | Threshold | Action |
|--------|-----------|--------|
| HTTP 429 rate | >5% of calls | Reduce call rate, add backoff |
| Avg Retry-After | >60s | Review call patterns, consider caller isolation |
| Requests/minute | >80% of estimated limit | Preemptively throttle client-side |
| Error rate (non-429) | >2% | Investigate auth, permissions, or endpoint issues |
