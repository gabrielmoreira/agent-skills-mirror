---
name: global-data-get-{country}
api: Global Data System
method: GET
path: /v1/systems/business-calendar/{country}
base_url: https://api.requiems.xyz
description: Retrieve working days, public holidays, and next upcoming holiday for any country and optional year/month. Covers 100+ countries.
---

## Endpoint

**GET https://api.requiems.xyz/v1/systems/business-calendar/{country}**

## Business Calendar

Retrieve working days, public holidays, and next upcoming holiday for any country and optional year/month. Covers 100+ countries.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `country` | string | yes | path | ISO 3166-1 alpha-2 country code (e.g. DE, US, FR) |
| `year` | integer | no | query | Year to retrieve the calendar for. Defaults to the current year. |
| `month` | integer | no | query | Month (1–12). When provided, returns month-scoped working day count, total days, weekend days, and filtered holidays. |

## Request Example

```json
GET /v1/systems/business-calendar/DE?year=2026&month=6
```

## Response Example

```json
{
  "data": {
    "country_code": "DE",
    "year": 2026,
    "month": 6,
    "working_days": 21,
    "total_days": 30,
    "weekend_days": 8,
    "holidays": [],
    "holiday_count": 0,
    "next_holiday": {
      "date": "2026-10-03",
      "name": "German Unity Day",
      "type": "national"
    }
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `country_code` | string | ISO 3166-1 alpha-2 country code echoed from the path parameter |
| `year` | integer | Year the calendar covers |
| `month` | integer or null | Month scope. Present only when the month query parameter was provided. |
| `working_days` | integer | Number of working days (excluding weekends and public holidays) in the scope |
| `total_days` | integer or null | Total calendar days in the month. Present only when month is provided. |
| `weekend_days` | integer or null | Number of weekend days in the month. Present only when month is provided. |
| `holidays` | array | List of public holidays in the scope. Each item: {date: YYYY-MM-DD, name: string, type: national} |
| `holiday_count` | integer | Count of holidays in the holidays array |
| `next_holiday` | object or null | Next public holiday within 90 days from today. Shape: {date, name, type} |

## Errors

- `undefined` **422** — Country is not a 2-letter ISO code, or year/month is out of the valid range
- `undefined` **401** — Missing or invalid API key
