---
name: swift-code-get-{code}
api: SWIFT Code
method: GET
path: /v1/finance/swift/{code}
base_url: https://api.requiems.xyz
description: Look up bank metadata for a SWIFT/BIC code.
---

## Endpoint

**GET https://api.requiems.xyz/v1/finance/swift/{code}**

## Get SWIFT Code

Look up bank metadata for a SWIFT/BIC code.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `code` | string | yes | path | SWIFT/BIC code (8 or 11 alphanumeric characters) |

## Response Example

```json
{
  "data": {
    "swift_code": "DEUTDEDBXXX",
    "bank_code": "DEUT",
    "country_code": "DE",
    "location_code": "DB",
    "branch_code": "XXX",
    "bank_name": "Deutsche Bank AG",
    "city": "Frankfurt am Main",
    "country_name": "Germany",
    "is_primary": true
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `swift_code` | string | Full 11-character SWIFT/BIC code |
| `bank_code` | string | Institution code (characters 1-4) |
| `country_code` | string | ISO 3166-1 alpha-2 country code (characters 5-6) |
| `location_code` | string | Location code (characters 7-8) |
| `branch_code` | string | Branch code (characters 9-11), XXX for primary office |
| `bank_name` | string | Bank or institution name |
| `city` | string | City of the branch or primary office |
| `country_name` | string | Full country name |
| `is_primary` | boolean | true when branch_code is XXX |

## Errors

- `400` **bad_request** — Invalid SWIFT/BIC format (must be 8 or 11 valid characters).
- `404` **not_found** — SWIFT/BIC code not found in the dataset.
- `500` **internal_error** — Unexpected server error.
