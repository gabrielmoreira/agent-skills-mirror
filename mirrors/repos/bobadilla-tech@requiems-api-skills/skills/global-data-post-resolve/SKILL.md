---
name: global-data-post-resolve
api: Global Data System
method: POST
path: /v1/systems/location/resolve
base_url: https://api.requiems.xyz
description: Resolve an address or coordinates into a full location profile — city, country, timezone, UTC offset, current time, working days this month, and next holiday.
---

## Endpoint

**POST https://api.requiems.xyz/v1/systems/location/resolve**

## Resolve Location

Resolve an address or coordinates into a full location profile — city, country, timezone, UTC offset, current time, working days this month, and next holiday.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `address` | string | no | body | Human-readable address string to geocode. Either address or coordinates is required. |
| `coordinates` | object | no | body | Coordinates object for reverse geocoding. Either address or coordinates is required. Shape: {lat: float, lng: float} |
| `country_code` | string | no | body | ISO 3166-1 alpha-2 country code hint. Overrides the geocoder-inferred country code when provided. |

## Request Example

```json
{
  "address": "Alexanderplatz 1, Berlin",
  "country_code": "DE"
}
```

## Response Example

```json
{
  "data": {
    "address": "Alexanderplatz 1, 10178 Berlin, Germany",
    "city": "Berlin",
    "country": "Germany",
    "country_code": "DE",
    "coordinates": {
      "lat": 52.5219,
      "lng": 13.4132
    },
    "timezone": "Europe/Berlin",
    "utc_offset": "+02:00",
    "current_time": "2026-06-15T14:32:00+02:00",
    "is_holiday_today": false,
    "working_days_this_month": 21,
    "next_holiday": {
      "date": "2026-10-03",
      "name": "German Unity Day",
      "type": "national"
    },
    "flags": []
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `address` | string | Normalized full address returned by the geocoder |
| `city` | string | City name |
| `country` | string | Full country name |
| `country_code` | string | ISO 3166-1 alpha-2 country code |
| `coordinates` | object | Resolved lat/lng coordinates |
| `timezone` | string or null | IANA timezone identifier (e.g. Europe/Berlin). Null when timezone resolution fails. |
| `utc_offset` | string or null | UTC offset string (e.g. +02:00). Null when timezone resolution fails. |
| `current_time` | string or null | Current local time in RFC3339 format. Null when timezone resolution fails. |
| `is_holiday_today` | boolean | True when today is a public holiday in the resolved country |
| `working_days_this_month` | integer | Number of working days (excluding weekends and public holidays) in the current calendar month |
| `next_holiday` | object or null | Next public holiday within 90 days. Shape: {date: YYYY-MM-DD, name: string, type: national} |
| `flags` | array | Non-fatal warnings. Possible values: timezone_unavailable, calendar_unavailable |

## Errors

- `undefined` **422** — Neither address nor coordinates was provided
- `undefined` **422** — Geocoding service was unavailable
- `undefined` **401** — Missing or invalid API key
