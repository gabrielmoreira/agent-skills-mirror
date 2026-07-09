---
name: holidays-post-batch
api: Holidays
method: POST
path: /v1/places/holidays/batch
base_url: https://api.requiems.xyz
description: Returns holidays for up to 50 (country, year) pairs in a single request. Each pair is processed independently — if one combination has no data, it returns found:false without failing the entire batch.
---

## Endpoint

**POST https://api.requiems.xyz/v1/places/holidays/batch**

## Batch Get Holidays

Returns holidays for up to 50 (country, year) pairs in a single request. Each pair is processed independently — if one combination has no data, it returns found:false without failing the entire batch.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `queries` | array | yes | body | Array of (country, year) pairs. Min: 1, Max: 50. |

## Response Example

```json
{
  "data": {
    "results": [
      {
        "country": "US",
        "year": 2025,
        "found": true,
        "holidays": [
          { "date": "2025-01-01", "name": "New Year's Day" },
          { "date": "2025-07-04", "name": "Independence Day" }
        ],
        "total": 11
      },
      {
        "country": "AR",
        "year": 2024,
        "found": true,
        "holidays": [
          { "date": "2024-01-01", "name": "Año Nuevo" }
        ],
        "total": 19
      },
      {
        "country": "AQ",
        "year": 2025,
        "found": false
      }
    ],
    "total": 3
  },
  "metadata": {
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | One result per query, in the same order as the request |
| `results[].country` | string | ISO 3166-1 alpha-2 country code |
| `results[].year` | integer | Year queried |
| `results[].found` | boolean | false when no holidays exist for that country/year combination |
| `results[].holidays` | array | List of holidays. Omitted when found is false. |
| `results[].total` | integer | Number of holidays. Omitted when found is false. |
| `total` | integer | Total number of results (equals the number of queries sent) |

## Errors

- `400` **bad_request** — Malformed request body
- `422` **validation_failed** — queries is missing, empty, exceeds 50 items, or contains invalid country codes or years
