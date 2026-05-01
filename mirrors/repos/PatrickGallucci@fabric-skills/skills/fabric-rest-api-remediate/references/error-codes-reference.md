# Fabric REST API Error Codes Reference

Complete reference for error codes returned by Microsoft Fabric REST APIs. Use this alongside the main remediate workflows in [SKILL.md](../SKILL.md).

## Table of Contents

- [ErrorResponse Schema](#errorresponse-schema)
- [HTTP 401 Error Codes](#http-401--unauthorized)
- [HTTP 403 Error Codes](#http-403--forbidden)
- [HTTP 404 Error Codes](#http-404--not-found)
- [HTTP 429 Throttling](#http-429--too-many-requests)
- [HTTP 430 Spark Limits](#http-430--spark-compute-limit)
- [HTTP 5xx Server Errors](#http-5xx--server-errors)
- [Fabric-Specific Error Patterns](#fabric-specific-error-patterns)
- [Capacity SKU Queue Limits](#capacity-sku-queue-limits)

---

## ErrorResponse Schema

All Fabric API errors return this structure:

```json
{
  "errorCode": "string",
  "message": "string",
  "moreDetails": [
    {
      "errorCode": "string",
      "message": "string",
      "relatedResource": {
        "resourceId": "string",
        "resourceType": "string"
      }
    }
  ],
  "relatedResource": {
    "resourceId": "string",
    "resourceType": "string"
  },
  "requestId": "string"
}
```

**Rules:**

- `errorCode` is stable and contract-based — use it in error-handling logic
- `message` may change — never parse it programmatically
- `requestId` is required when contacting Microsoft Support
- `relatedResource` identifies the specific resource involved in the error

---

## HTTP 401 — Unauthorized

Authentication or token validation failed.

| errorCode | Description | Resolution |
|-----------|-------------|------------|
| `TokenExpired` | Access token has expired | Acquire a new token via MSAL and retry |
| `InsufficientScopes` | Token lacks required API scopes | Update MSAL scope request to include required scopes; update Entra ID app permissions if needed |

### Token Inspection Checklist

1. Decode JWT payload and check `exp` claim against current time
2. Verify `aud` (audience) is `https://api.fabric.microsoft.com`
3. Confirm `scp` (scopes) includes the permission the API requires
4. Ensure `tid` (tenant ID) matches the target Fabric tenant

---

## HTTP 403 — Forbidden

Caller is authenticated but lacks authorization for the operation.

| errorCode | Description | Resolution |
|-----------|-------------|------------|
| `InsufficientPrivileges` | Missing workspace or resource permissions | Have a workspace admin grant Contributor (or higher) role |

### Common 403 Scenarios

- **User lacks workspace role**: Assign at least Viewer (read) or Contributor (write) role in Fabric workspace settings
- **Service principal without tenant setting**: Enable "Service principals can use Fabric APIs" in Fabric Admin > Tenant settings
- **Admin API without admin role**: APIs under `/v1/admin/` require Fabric Administrator role
- **Downstream item doesn't support identity type**: Creating items that don't support service principals will fail even if the Create Item API does

---

## HTTP 404 — Not Found

Requested resource doesn't exist or isn't accessible.

| errorCode | Description | Resolution |
|-----------|-------------|------------|
| `WorkspaceNotFound` | Workspace GUID is invalid or inaccessible | Verify workspace ID using List Workspaces API |
| `EntityNotFound` | Resource GUID is invalid or inaccessible | Check `relatedResource` field; verify the item ID and type |

### Validation Steps

1. List workspaces: `GET /v1/workspaces` — find the correct workspace ID
2. List items: `GET /v1/workspaces/{workspaceId}/items` — find the correct item ID
3. Confirm the resource type matches what the API expects
4. Check that the workspace hasn't been deleted or the item moved

---

## HTTP 429 — Too Many Requests

Rate limit exceeded. Throttling is per caller identity per API within one-minute windows.

| errorCode | Description | Resolution |
|-----------|-------------|------------|
| `RequestBlocked` | Rate limit exceeded | Honor `Retry-After` header; implement exponential backoff |

### Retry-After Information Sources

1. **`Retry-After` HTTP header** — number of seconds to wait (preferred)
2. **Response body `message`** — may include UTC timestamp: `"Request is blocked by the upstream service until: 12/24/2025 17:02:20 (UTC)"`

### Mitigation Strategies

- Use bulk/batch operations where available
- Prefer `List Items` over repeated single-item GETs
- Cache workspace and item metadata locally
- Distribute requests evenly (add random jitter)
- Process paginated results completely before starting new queries

---

## HTTP 430 — Spark Compute Limit

Fabric-specific status code for Spark job queue limits.

| Error | Description | Resolution |
|-------|-------------|------------|
| `TooManyRequestsForCapacity` | Spark compute or API rate limit hit | Cancel active Spark jobs, upgrade SKU, or retry later |

### Capacity SKU Queue Limits

| Fabric SKU | Power BI Equivalent | Queue Limit |
|------------|-------------------|-------------|
| F2 | — | 4 |
| F4 | — | 4 |
| F8 | — | 8 |
| F16 | — | 16 |
| F32 | — | 32 |
| F64 | P1 | 64 |
| F128 | P2 | 128 |
| F256 | P3 | 256 |
| F512 | P4 | 512 |
| F1024 | — | 1024 |
| F2048 | — | 2048 |
| Trial | P1 | No queueing supported |

---

## HTTP 5xx — Server Errors

| Status | Meaning | Action |
|--------|---------|--------|
| 500 | Internal Server Error | Retry with backoff; log `requestId` |
| 502 | Bad Gateway | Transient; retry after 5-10 seconds |
| 503 | Service Unavailable | Check Fabric service health; retry with backoff |

### Escalation Checklist

If a 5xx error persists after 3+ retries over 5 minutes:

1. Capture the `requestId` from the response
2. Note the exact UTC timestamp of the failure
3. Record the full request (method, URL, headers, body)
4. Check [Microsoft 365 Service Health](https://admin.microsoft.com/Adminportal/Home#/servicehealth)
5. Open a support ticket with the above information

---

## Fabric-Specific Error Patterns

### Item Creation Failures

When creating items via `POST /v1/workspaces/{workspaceId}/items`:

- Verify `type` field matches a valid Fabric item type exactly (case-sensitive)
- Ensure `displayName` doesn't conflict with an existing item in the workspace
- Check that the item type is supported for your capacity SKU

### Definition Update Failures

When updating item definitions via `POST /v1/workspaces/{workspaceId}/items/{itemId}/updateDefinition`:

- Ensure the payload structure matches the item type's definition schema
- Validate base64-encoded parts if the definition includes binary payloads
- Check that the item isn't locked by another operation

### Capacity API Errors (Azure REST)

Fabric capacity APIs (`Microsoft.Fabric/capacities`) use Azure Resource Manager patterns:

- **CheckNameAvailability** — Returns whether the capacity name is available
- **Create/Update** — Requires Azure Subscription Owner or Contributor role
- **Resume/Suspend** — May return 202 (LRO) for async operations

---

## Quick Diagnostic Commands (PowerShell)

```powershell
# List accessible workspaces (validates authentication)
Invoke-RestMethod -Uri "https://api.fabric.microsoft.com/v1/workspaces" `
    -Headers @{ Authorization = "Bearer $token" }

# Get specific workspace (validates workspace ID)
Invoke-RestMethod -Uri "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId" `
    -Headers @{ Authorization = "Bearer $token" }

# List items in workspace (validates workspace access)
Invoke-RestMethod -Uri "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/items" `
    -Headers @{ Authorization = "Bearer $token" }
```
