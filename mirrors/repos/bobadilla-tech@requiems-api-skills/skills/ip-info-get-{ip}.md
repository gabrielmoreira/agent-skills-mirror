---
name: ip-info-get-{ip}
api: IP Geolocation
method: GET
path: /v1/networking/ip/{ip}
base_url: https://api.requiems.xyz
description: Get geolocation and network information for a specific IP address.
---

## Endpoint

**GET https://api.requiems.xyz/v1/networking/ip/{ip}**

## Get IP Info for IP

Get geolocation and network information for a specific IP address.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `ip` | string | yes | path | The IP address to look up (supports IPv4 and IPv6) |

## Response Example

```json
{
  "data": {
    "ip": "8.8.8.8",
    "country": "United States",
    "country_code": "US",
    "city": "Mountain View",
    "isp": "Google Public DNS",
    "is_vpn": false
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `ip` | string | The IP address that was looked up |
| `country` | string | Country name where the IP is located |
| `country_code` | string | Two-letter ISO country code (e.g., "US", "GB", "DE") |
| `city` | string | City name where the IP is located |
| `isp` | string | Internet Service Provider providing the IP |
| `is_vpn` | boolean | True when the IP belongs to a known VPN |

## Errors

- `400` **bad_request** — The IP address is invalid
- `500` **internal_error** — Unexpected server error
