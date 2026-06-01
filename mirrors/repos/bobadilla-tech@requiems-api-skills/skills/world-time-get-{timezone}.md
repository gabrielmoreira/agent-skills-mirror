---
name: world-time-get-{timezone}
api: World Time
method: GET
path: /v1/places/time/{timezone}
base_url: https://api.requiems.xyz
description: Returns the current time for the given IANA timezone identifier. The timezone is supplied as a path parameter (e.g. `America/New_York`, `Europe/London`, `UTC`).
---

## Endpoint

**GET https://api.requiems.xyz/v1/places/time/{timezone}**

## Get Current Time by Timezone

Returns the current time for the given IANA timezone identifier. The timezone is
supplied as a path parameter (e.g. `America/New_York`, `Europe/London`, `UTC`).

## Parameters

| Name       | Type   | Required | Location | Description                                                                         |
| ---------- | ------ | -------- | -------- | ----------------------------------------------------------------------------------- |
| `timezone` | string | yes      | path     | IANA timezone identifier (e.g. 'America/New_York', 'Europe/London', 'Asia/Kolkata') |

## Response Example

```json
{
  "data": {
    "timezone": "America/New_York",
    "offset": "-05:00",
    "current_time": "2024-12-15T14:30:00Z",
    "is_dst": false
  },
  "metadata": {
    "timestamp": "2024-12-15T14:30:00Z"
  }
}
```

## Response Fields

| Field          | Type    | Description                                                              |
| -------------- | ------- | ------------------------------------------------------------------------ |
| `timezone`     | string  | IANA timezone identifier (e.g. "America/New_York")                       |
| `offset`       | string  | UTC offset in +HH:MM or -HH:MM format (e.g. '-05:00', '+05:30')          |
| `current_time` | string  | Current time in UTC, formatted as RFC 3339 (e.g. "2024-12-15T14:30:00Z") |
| `is_dst`       | boolean | Whether the timezone is currently observing daylight saving time         |
