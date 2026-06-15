---
name: disposable_email-get-{domain}
api: Disposable Email Checker
method: GET
path: /v1/networking/disposable/domain/{domain}
base_url: https://api.requiems.xyz
description: Check if a specific domain is in the disposable blocklist
---

## Endpoint

**GET https://api.requiems.xyz/v1/networking/disposable/domain/{domain}**

## Check Domain

Check if a specific domain is in the disposable blocklist

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `domain` | string | yes | path | The domain to check |

## Response Example

```json
{
  "data": {
    "domain": "tempmail.com",
    "is_disposable": true
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `domain` | string | The domain that was checked |
| `is_disposable` | boolean | Whether the domain is in the disposable blocklist |

## Errors

- `undefined` **400** — The domain parameter is missing
