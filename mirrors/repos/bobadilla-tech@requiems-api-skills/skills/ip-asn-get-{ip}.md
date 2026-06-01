---
name: ip-asn-get-{ip}
api: ASN Lookup
method: GET
path: /v1/networking/ip/asn/{ip}
base_url: https://api.requiems.xyz
description: Look up ASN, organization, ISP, and network details for a specific IP address.
---

## Endpoint

**GET https://api.requiems.xyz/v1/networking/ip/asn/{ip}**

## Lookup ASN for IP

Look up ASN, organization, ISP, and network details for a specific IP address.

## Parameters

| Name | Type   | Required | Location | Description                                        |
| ---- | ------ | -------- | -------- | -------------------------------------------------- |
| `ip` | string | yes      | path     | The IP address to look up (supports IPv4 and IPv6) |

## Response Example

```json
{
  "data": {
    "ip": "8.8.8.8",
    "asn": "AS15169",
    "org": "Google LLC",
    "isp": "Google Public DNS",
    "domain": "google.com",
    "route": "8.8.8.0/24",
    "type": "hosting"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field    | Type   | Description                                                   |
| -------- | ------ | ------------------------------------------------------------- |
| `ip`     | string | The IP address that was looked up                             |
| `asn`    | string | Autonomous System Number in format "ASxxxx" (e.g., "AS15169") |
| `org`    | string | Organization name owning the IP address range                 |
| `isp`    | string | Internet Service Provider providing the IP                    |
| `domain` | string | Domain name associated with the IP or IP range                |
| `route`  | string | CIDR notation of the network route (e.g., "8.8.8.0/24")       |
| `type`   | string | Type of network (e.g., "hosting", "isp", "business", "cdn")   |

## Errors

- `400` **bad_request** — The IP address is invalid
- `500` **internal_error** — Unexpected server error
