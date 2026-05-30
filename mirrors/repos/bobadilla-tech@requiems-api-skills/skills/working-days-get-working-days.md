---
name: working-days-get-working-days
api: Working Days Calculator
method: GET
path: /v1/places/working-days
base_url: https://api.requiems.xyz
description: Calculate the number of working days between two dates, optionally accounting for country-specific holidays
---

## Endpoint

**GET https://api.requiems.xyz/v1/places/working-days**

## Calculate Working Days

Calculate the number of working days between two dates, optionally accounting for country-specific holidays

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `from` | string | yes | query | Start date in YYYY-MM-DD format (ISO 8601) |
| `to` | string | yes | query | End date in YYYY-MM-DD format (ISO 8601). Must be >= from date. |
| `country` | string | no | query | ISO 3166-1 alpha-2 country code (e.g., "US", "GB", "FR"). When provided, country-specific holidays are excluded from working days count. |
| `subdivision` | string | no | query | ISO 3166-2 subdivision code for state/region within the country (e.g., "NY" for New York, "CA" for California). Only used when country is provided. |

## Response Example

```json
{
  "data": {
    "working_days": 4,
    "from": "2024-02-23",
    "to": "2024-02-28",
    "country": "US",
    "subdivision": "NY"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `working_days` | integer | Number of working days between the two dates (excluding weekends and optionally holidays) |
| `from` | string | Start date (echoed from request) |
| `to` | string | End date (echoed from request) |
| `country` | string | Country code (echoed from request, empty string if not provided) |
| `subdivision` | string | Subdivision code (echoed from request, empty string if not provided) |

## Errors

- `undefined` **400** — The from and to parameters are required, or to date is before from date, or invalid date format
