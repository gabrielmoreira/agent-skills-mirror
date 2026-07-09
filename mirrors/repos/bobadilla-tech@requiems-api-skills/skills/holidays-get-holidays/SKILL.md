---
name: holidays-get-holidays
api: Holidays
method: GET
path: /v1/places/holidays
base_url: https://api.requiems.xyz
description: Returns a list of public holidays for the specified country and year
---

## Endpoint

**GET https://api.requiems.xyz/v1/places/holidays**

## Get Holidays

Returns a list of public holidays for the specified country and year

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `country` | string | yes | query | ISO 3166-1 alpha-2 country code (e.g., "US", "GB", "DE") |
| `year` | integer | yes | query | Year for which to retrieve holidays (e.g., 2025) |

## Response Example

```json
{
  "data": {
    "country": "US",
    "year": 2025,
    "holidays": [
      {
        "date": "2025-01-01",
        "name": "New Year's Day"
      },
      {
        "date": "2025-07-04",
        "name": "Independence Day"
      }
    ],
    "total": 11
  },
  "metadata": {
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `country` | string | ISO 3166-1 alpha-2 country code |
| `year` | integer | Year for which holidays are returned |
| `holidays` | array | Array of holiday objects |
| `holidays[].date` | string | Holiday date in YYYY-MM-DD format |
| `holidays[].name` | string | Name of the holiday |
| `total` | integer | Total number of holidays for the country/year |

## Errors

- `400` **bad_request** — Missing or invalid country code or year parameter
- `404` **not_found** — No holidays found for the specified country and year
