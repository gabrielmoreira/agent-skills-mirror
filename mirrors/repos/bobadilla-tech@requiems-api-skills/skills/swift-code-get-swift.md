---
name: swift-code-get-swift
api: SWIFT Code
method: GET
path: /v1/finance/swift
base_url: https://api.requiems.xyz
description: List SWIFT records with optional filters and pagination.
---

## Endpoint

**GET https://api.requiems.xyz/v1/finance/swift**

## List SWIFT Codes

List SWIFT records with optional filters and pagination.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `country_code` | string | no | query | Optional 2-letter country code filter (e.g. DE, US) |
| `bank_code` | string | no | query | Optional 4-letter bank code filter (e.g. DEUT) |
| `q` | string | no | query | Optional text search across swift_code, bank_name, and city |
| `limit` | integer | no | query | Max rows to return (default 50, max 200) |
| `offset` | integer | no | query | Number of rows to skip (default 0) |

## Response Example

```json
{
  "data": {
    "items": [
      {
        "swift_code": "DEUTDEDBXXX",
        "bank_code": "DEUT",
        "country_code": "DE",
        "location_code": "DB",
        "branch_code": "XXX",
        "bank_name": "Deutsche Bank Privat-Und Geschaeftskunden Ag - Head Office",
        "city": "Frankfurt Am Main",
        "country_name": "Germany",
        "is_primary": true
      }
    ],
    "limit": 50,
    "offset": 0,
    "returned": 1
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Errors

- `400` **bad_request** — Invalid filter or pagination parameter.
- `500` **internal_error** — Unexpected server error.
