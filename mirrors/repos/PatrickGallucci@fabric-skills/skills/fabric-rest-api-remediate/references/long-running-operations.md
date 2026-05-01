# Long Running Operations (LRO) in Microsoft Fabric REST APIs

Complete guide to implementing and remediate asynchronous polling patterns.

## Table of Contents

- [How LROs Work](#how-lros-work)
- [Response Headers](#response-headers)
- [Polling Patterns](#polling-patterns)
- [PowerShell Implementation](#powershell-implementation)
- [C# Implementation](#c-implementation)
- [Common LRO Failures](#common-lro-failures)
- [Best Practices](#best-practices)

---

## How LROs Work

Long Running Operations handle tasks too slow for a single request-response cycle — large data uploads, batch processing, resource provisioning, and complex computations.

**Flow:**

1. Client sends the initial API request
2. Fabric returns HTTP **200/201** (sync success) or **202 Accepted** (async, LRO started)
3. If 202, the response body is empty but headers contain polling information
4. Client polls the operation status URL until a terminal state is reached
5. If the operation has a result, client fetches it from the result URL

**Not all LROs produce a result.** Some operations simply run to completion without a result URL.

---

## Response Headers

When an API returns 202 Accepted, three headers are added:

| Header | Purpose | Example |
|--------|---------|---------|
| `Location` | URL for polling operation status | `https://api.fabric.microsoft.com/v1/operations/{operationId}` |
| `x-ms-operation-id` | Operation GUID (for constructing URLs manually) | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `Retry-After` | Seconds to wait before first poll | `30` |

---

## Polling Patterns

### Approach 1: Use Location Header Directly (Recommended)

The `Location` header points to the `Get Operation State` API for the ongoing operation.

```
GET {Location header value}
Authorization: Bearer {token}
```

### Approach 2: Construct the URL Manually

Using the `x-ms-operation-id` header:

```
GET https://api.fabric.microsoft.com/v1/operations/{operationId}
Authorization: Bearer {token}
```

### Operation Status Values

| Status | Terminal? | Action |
|--------|----------|--------|
| `NotStarted` | No | Continue polling |
| `Running` | No | Continue polling |
| `Succeeded` | Yes | Fetch result if available |
| `Failed` | Yes | Check error in response body |
| `Undefined` | — | Unexpected; log and retry |

### Getting the Result

If the operation succeeded and has a result:

```
GET https://api.fabric.microsoft.com/v1/operations/{operationId}/result
Authorization: Bearer {token}
```

---

## PowerShell Implementation

### Basic LRO Polling

```powershell
function Invoke-FabricLongRunningOperation {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$InitialUri,

        [Parameter(Mandatory)]
        [string]$Method,

        [Parameter(Mandatory)]
        [string]$Token,

        [string]$Body,

        [int]$MaxPollSeconds = 300,

        [int]$DefaultPollIntervalSeconds = 10
    )

    $headers = @{
        Authorization  = "Bearer $Token"
        'Content-Type' = 'application/json'
    }

    # Send initial request
    $params = @{
        Uri     = $InitialUri
        Method  = $Method
        Headers = $headers
    }
    if ($Body) { $params.Body = $Body }

    try {
        $response = Invoke-WebRequest @params
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Error "Initial request failed with HTTP $statusCode"
        throw
    }

    $statusCode = $response.StatusCode

    # Synchronous success
    if ($statusCode -in @(200, 201)) {
        return ($response.Content | ConvertFrom-Json)
    }

    # LRO started
    if ($statusCode -eq 202) {
        $locationUrl = $response.Headers['Location']
        $operationId = $response.Headers['x-ms-operation-id']
        $retryAfter  = $response.Headers['Retry-After']

        if (-not $locationUrl -and $operationId) {
            $locationUrl = "https://api.fabric.microsoft.com/v1/operations/$operationId"
        }

        if (-not $locationUrl) {
            throw "LRO returned 202 but no Location header or operation ID"
        }

        $pollInterval = if ($retryAfter) { [int]$retryAfter } else { $DefaultPollIntervalSeconds }
        $elapsed = 0

        Write-Host "LRO started (operation: $operationId). Polling every ${pollInterval}s..."

        while ($elapsed -lt $MaxPollSeconds) {
            Start-Sleep -Seconds $pollInterval
            $elapsed += $pollInterval

            $pollResponse = Invoke-RestMethod -Uri $locationUrl -Headers $headers
            $status = $pollResponse.status

            Write-Host "  [$elapsed s] Status: $status"

            switch ($status) {
                'Succeeded' {
                    Write-Host "Operation completed successfully."
                    # Try to get result
                    $resultUrl = "${locationUrl}/result"
                    try {
                        return (Invoke-RestMethod -Uri $resultUrl -Headers $headers)
                    }
                    catch {
                        # No result available (operation completed without result)
                        return $pollResponse
                    }
                }
                'Failed' {
                    Write-Error "Operation failed: $($pollResponse | ConvertTo-Json -Depth 5)"
                    throw "LRO failed"
                }
                { $_ -in @('Running', 'NotStarted') } {
                    continue
                }
                default {
                    Write-Warning "Unexpected status: $status"
                }
            }
        }

        throw "LRO timed out after $MaxPollSeconds seconds (last status: $status)"
    }

    throw "Unexpected HTTP status: $statusCode"
}
```

### Usage Example

```powershell
# Create a lakehouse (returns 202 for LRO)
$result = Invoke-FabricLongRunningOperation `
    -InitialUri "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/lakehouses" `
    -Method "POST" `
    -Token $token `
    -Body '{"displayName": "MyLakehouse"}'

Write-Host "Lakehouse created: $($result.id)"
```

---

## C# Implementation

```csharp
using System.Net;
using System.Net.Http.Headers;

public class FabricLroClient
{
    private readonly HttpClient _client;

    public FabricLroClient(string token)
    {
        _client = new HttpClient();
        _client.DefaultRequestHeaders.Authorization =
            new AuthenticationHeaderValue("Bearer", token);
        _client.BaseAddress = new Uri("https://api.fabric.microsoft.com/v1/");
    }

    public async Task<string> ExecuteWithLroAsync(
        HttpMethod method,
        string relativeUri,
        string? body = null,
        int maxPollSeconds = 300)
    {
        var request = new HttpRequestMessage(method, relativeUri);
        if (body != null)
        {
            request.Content = new StringContent(body, System.Text.Encoding.UTF8, "application/json");
        }

        var response = await _client.SendAsync(request);

        // Synchronous success
        if (response.StatusCode is HttpStatusCode.OK or HttpStatusCode.Created)
        {
            return await response.Content.ReadAsStringAsync();
        }

        // LRO started
        if (response.StatusCode == HttpStatusCode.Accepted)
        {
            var locationUrl = response.Headers.Location?.ToString();
            var retryAfterHeader = response.Headers.RetryAfter;
            int pollInterval = retryAfterHeader?.Delta?.Seconds ?? 10;

            if (string.IsNullOrEmpty(locationUrl))
                throw new Exception("LRO 202 but no Location header");

            int elapsed = 0;
            while (elapsed < maxPollSeconds)
            {
                await Task.Delay(pollInterval * 1000);
                elapsed += pollInterval;

                var pollResponse = await _client.GetAsync(locationUrl);
                var pollBody = await pollResponse.Content.ReadAsStringAsync();
                // Parse status from JSON
                // Handle Succeeded, Failed, Running states
            }

            throw new TimeoutException($"LRO timed out after {maxPollSeconds}s");
        }

        throw new HttpRequestException($"Unexpected: {response.StatusCode}");
    }
}
```

---

## Common LRO Failures

| Symptom | Cause | Resolution |
|---------|-------|------------|
| No `Location` header on 202 | API may not use LRO, or a proxy stripped headers | Check `x-ms-operation-id` header; construct URL manually |
| Poll returns 401 | Token expired during long operation | Refresh the bearer token and retry the poll |
| Poll returns 404 | Operation expired or invalid operation ID | Restart the original operation |
| Status stuck on `Running` | Operation is legitimately long-running | Increase timeout; check Fabric Monitoring Hub |
| `Failed` status with no details | Internal service error during operation | Log the `requestId`; retry the original operation |
| Result endpoint returns 404 | Operation completed without a result | Not all LROs produce results; this is expected |

---

## Best Practices

1. **Always capture all three response headers** from the initial 202 response
2. **Respect `Retry-After`** — don't poll faster than the service requests
3. **Set a reasonable timeout** — default to 5 minutes, extend for known long operations
4. **Refresh tokens** if the operation runs longer than your token lifetime (typically 60 minutes)
5. **Log the operation ID** for every LRO — essential for debugging and support
6. **Handle both terminal states** — Succeeded and Failed — and fall through to timeout
7. **Don't assume a result exists** — some operations complete without a result URL
