---
name: disposable_email-get-stats
api: Disposable Email Checker
method: GET
path: /v1/networking/disposable/stats
base_url: https://api.requiems.xyz
description: Get statistics about the disposable email blocklist
---

## Endpoint

**GET https://api.requiems.xyz/v1/networking/disposable/stats**

## Get Statistics

Get statistics about the disposable email blocklist

## Response Example

```json
{
  "data": {
    "total_domains": 10500
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field           | Type    | Description                                         |
| --------------- | ------- | --------------------------------------------------- |
| `total_domains` | integer | Total number of disposable domains in the blocklist |
