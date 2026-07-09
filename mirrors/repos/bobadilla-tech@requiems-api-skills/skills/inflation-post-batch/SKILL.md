---
name: inflation-post-batch
api: Inflation
method: POST
path: /v1/finance/inflation/batch
base_url: https://api.requiems.xyz
description: Returns inflation data for up to 50 countries in a single request. Results are in the same order as the input. Countries with no data return found: false instead of failing the whole request. Billing: 1 credit per country (not per HTTP request).
---

## Endpoint

**POST https://api.requiems.xyz/v1/finance/inflation/batch**

## Batch Inflation Rates

Returns inflation data for up to 50 countries in a single request. Results are in the same order as the input. Countries with no data return found: false instead of failing the whole request. Billing: 1 credit per country (not per HTTP request).

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `countries` | array | yes | body | Array of ISO 3166-1 alpha-2 country codes. Min: 1, Max: 50. |

## Response Example

```json
{
  "data": {
    "results": [
      {
        "country": "US",
        "found": true,
        "rate": 2.9495,
        "period": "2024",
        "historical": [
          { "period": "2023", "rate": 4.1163 }
        ]
      },
      {
        "country": "AR",
        "found": true,
        "rate": 211.4,
        "period": "2024",
        "historical": []
      },
      {
        "country": "XX",
        "found": false
      }
    ],
    "total": 3
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | One entry per country, in the same order as the input array |
| `results[].country` | string | ISO 3166-1 alpha-2 country code, uppercased |
| `results[].found` | boolean | false when the country has no data in the World Bank set |
| `results[].rate` | number | Latest CPI inflation rate. Omitted when found: false |
| `results[].period` | string | Year of the latest data point. Omitted when found: false |
| `results[].historical` | array | Up to 10 previous years. Omitted when found: false |
| `total` | integer | Total number of results returned (equals number of countries sent) |

## Errors

- `422` **validation_failed** — Body is invalid: empty array, more than 50 items, or a bad country code.
- `500` **internal_error** — Unexpected server error.
