---
name: global-data-get-{ip}
api: Global Data System
method: GET
path: /v1/systems/timezone/from-ip/{ip}
base_url: https://api.requiems.xyz
description: Resolve the timezone, UTC offset, and DST status for any IPv4 or IPv6 address without needing an address string.
---

## Endpoint

**GET https://api.requiems.xyz/v1/systems/timezone/from-ip/{ip}**

## Timezone from IP

Resolve the timezone, UTC offset, and DST status for any IPv4 or IPv6 address without needing an address string.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `ip` | string | yes | path | IPv4 or IPv6 address to resolve |

## Request Example

```json
GET /v1/systems/timezone/from-ip/92.168.1.1
```

## Response Example

```json
{
  "data": {
    "ip": "92.168.1.1",
    "city": "Berlin",
    "country_code": "DE",
    "timezone": "Europe/Berlin",
    "utc_offset": "+02:00",
    "dst_active": true,
    "current_time": "2026-06-15T14:32:00+02:00"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `ip` | string | The IP address as provided |
| `city` | string | City resolved from the IP |
| `country_code` | string | ISO 3166-1 alpha-2 country code |
| `timezone` | string or null | IANA timezone identifier. Null when timezone resolution fails. |
| `utc_offset` | string or null | UTC offset string. Null when timezone resolution fails. |
| `dst_active` | boolean or null | True when daylight saving time is currently active. Null when timezone resolution fails. |
| `current_time` | string or null | Current local time in RFC3339 format |

## Errors

- `undefined` **422** — The IP address could not be geolocated
- `undefined` **401** — Missing or invalid API key
