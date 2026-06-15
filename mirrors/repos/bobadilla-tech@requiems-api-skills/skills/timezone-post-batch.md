---
name: timezone-post-batch
api: Timezone
method: POST
path: /v1/places/timezone/batch
base_url: https://api.requiems.xyz
description: Look up timezone information for up to 50 locations in a single request. Each item can specify a timezone name, city, or lat/lon coordinates. Priority is timezone name > city > coordinates. Results are returned in input order.
---

## Endpoint

**POST https://api.requiems.xyz/v1/places/timezone/batch**

## Batch Timezone Lookup

Look up timezone information for up to 50 locations in a single request. Each item can specify a timezone name, city, or lat/lon coordinates. Priority is timezone name > city > coordinates. Results are returned in input order.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `items` | array of objects | yes | body | List of timezone lookup requests (1–50 items). |
| `items[].timezone` | string | no | body | IANA timezone name (e.g. 'America/New_York'). Highest priority. |
| `items[].city` | string | no | body | City name for city-based lookup. Used when timezone is not set. |
| `items[].lat` | number | no | body | Latitude (-90 to 90). Used when neither timezone nor city is set. |
| `items[].lon` | number | no | body | Longitude (-180 to 180). Used alongside lat for coordinate-based lookup. |

## Request Example

```json
{
  "items": [
    { "timezone": "America/New_York" },
    { "city": "Tokyo" },
    { "lat": 51.5, "lon": -0.1 }
  ]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      { "info": { "timezone": "America/New_York", "offset": "-05:00", "current_time": "2026-01-01T09:00:00Z", "is_dst": false } },
      { "info": { "timezone": "Asia/Tokyo",       "offset": "+09:00", "current_time": "2026-01-01T23:00:00Z", "is_dst": false } },
      { "info": { "timezone": "Europe/London",    "offset": "+00:00", "current_time": "2026-01-01T14:00:00Z", "is_dst": false } }
    ],
    "total": 3
  },
  "metadata": { "timestamp": "2026-01-01T00:00:00Z" }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | Per-item results in input order. |
| `results[].info.timezone` | string | IANA timezone identifier. |
| `results[].info.offset` | string | UTC offset in +HH:MM or -HH:MM format. |
| `results[].info.current_time` | string | Current time in UTC (RFC 3339). |
| `results[].info.is_dst` | boolean | Whether daylight saving time is currently active. |
| `results[].error` | string | Error message if this item failed (omitted on success). |
| `total` | integer | Total number of items processed. |

## Errors

- `422` **validation_failed** — The items array is missing, empty, or exceeds 50 items.
- `400` **bad_request** — The request body is missing or malformed.
