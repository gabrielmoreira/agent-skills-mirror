---
name: timezone-get-timezone
api: Timezone
method: GET
path: /v1/places/timezone
base_url: https://api.requiems.xyz
description: Returns timezone information for the given coordinates or city name. Provide either `city` or both `lat` and `lon`.
---

## Endpoint

**GET https://api.requiems.xyz/v1/places/timezone**

## Get Timezone

Returns timezone information for the given coordinates or city name. Provide
either `city` or both `lat` and `lon`.

## Parameters

| Name   | Type   | Required | Location | Description                                                                                    |
| ------ | ------ | -------- | -------- | ---------------------------------------------------------------------------------------------- |
| `lat`  | float  | no       | query    | Latitude of the location (-90 to 90). Required when using coordinate-based lookup.             |
| `lon`  | float  | no       | query    | Longitude of the location (-180 to 180). Required when using coordinate-based lookup.          |
| `city` | string | no       | query    | City name for city-based lookup (e.g. 'Tokyo', 'London'). Required when not using coordinates. |

## Response Example

```json
{
  "timezone": "Europe/London",
  "offset": "+00:00",
  "current_time": "2024-12-15T14:30:00Z",
  "is_dst": false
}
```

## Response Fields

| Field          | Type    | Description                                                              |
| -------------- | ------- | ------------------------------------------------------------------------ |
| `timezone`     | string  | IANA timezone identifier (e.g. "Europe/London", "Asia/Tokyo")            |
| `offset`       | string  | UTC offset in +HH:MM or -HH:MM format (e.g. '+05:30', '-05:00')          |
| `current_time` | string  | Current time in UTC, formatted as RFC 3339 (e.g. "2024-12-15T14:30:00Z") |
| `is_dst`       | boolean | Whether the location is currently observing daylight saving time         |
