---
name: ip-info-get-ip
api: IP Geolocation
method: GET
path: /v1/networking/ip
base_url: https://api.requiems.xyz
description: Get geolocation and network information for the requesting client's IP address. Useful when you want information about the user making the request without specifying an IP explicitly.
---

## Endpoint

**GET https://api.requiems.xyz/v1/networking/ip**

## Get IP Info (Caller IP)

Get geolocation and network information for the requesting client's IP address. Useful when you want information about the user making the request without specifying an IP explicitly.

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
| `ip` | string | The IP address that was looked up (the requesting client's IP) |
| `country` | string | Country name where the IP is located |
| `country_code` | string | Two-letter ISO country code (e.g., "US", "GB", "DE") |
| `city` | string | City name where the IP is located |
| `isp` | string | Internet Service Provider providing the IP |
| `is_vpn` | boolean | True when the IP belongs to a known VPN |

## Errors

- `500` **internal_error** — Unexpected server error
