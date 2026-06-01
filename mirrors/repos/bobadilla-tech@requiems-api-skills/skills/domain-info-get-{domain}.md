---
name: domain-info-get-{domain}
api: Domain Info
method: GET
path: /v1/networking/domain/{domain}
base_url: https://api.requiems.xyz
description: Returns DNS records and availability status for the given domain.
---

## Endpoint

**GET https://api.requiems.xyz/v1/networking/domain/{domain}**

## Get Domain Info

Returns DNS records and availability status for the given domain.

## Parameters

| Name     | Type   | Required | Location | Description                              |
| -------- | ------ | -------- | -------- | ---------------------------------------- |
| `domain` | string | yes      | path     | The domain to look up (e.g. example.com) |

## Response Example

```json
{
  "data": {
    "domain": "example.com",
    "available": false,
    "dns": {
      "a": ["93.184.216.34"],
      "aaaa": ["2606:2800:220:1:248:1893:25c8:1946"],
      "mx": [],
      "ns": ["a.iana-servers.net.", "b.iana-servers.net."],
      "txt": ["v=spf1 -all"],
      "cname": ""
    }
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field       | Type             | Description                                                                                                          |
| ----------- | ---------------- | -------------------------------------------------------------------------------------------------------------------- |
| `domain`    | string           | The domain that was looked up                                                                                        |
| `available` | boolean          | True when the domain appears to be unregistered (NS lookup returns NXDOMAIN). False when name servers are delegated. |
| `dns.a`     | array of strings | IPv4 addresses (A records)                                                                                           |
| `dns.aaaa`  | array of strings | IPv6 addresses (AAAA records)                                                                                        |
| `dns.mx`    | array of objects | Mail exchange records, each with host and priority fields                                                            |
| `dns.ns`    | array of strings | Authoritative name server hostnames                                                                                  |
| `dns.txt`   | array of strings | TXT record values (SPF, DKIM, verification tokens, etc.)                                                             |
| `dns.cname` | string           | CNAME alias target, if the domain is an alias. Empty string when no alias exists.                                    |

## Errors

- `400` **bad_request** — The domain parameter is not a valid hostname (e.g.
  missing TLD, invalid characters, or leading/trailing hyphens).
