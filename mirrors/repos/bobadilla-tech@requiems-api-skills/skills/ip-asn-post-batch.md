---
name: ip-asn-post-batch
api: ASN Lookup
method: POST
path: /v1/networking/ip/asn/batch
base_url: https://api.requiems.xyz
description: Look up ASN data for up to 50 IP addresses in a single request. Results are returned in input order. Private and reserved IPs return an empty result with no error.
---

## Endpoint

**POST https://api.requiems.xyz/v1/networking/ip/asn/batch**

## Batch ASN Lookup

Look up ASN data for up to 50 IP addresses in a single request. Results are returned in input order. Private and reserved IPs return an empty result with no error.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `ips` | array of strings | yes | body | List of IP addresses to look up (1–50 items, each must be a valid IPv4 or IPv6 address). |

## Request Example

```json
{
  "ips": ["8.8.8.8", "1.1.1.1"]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "ip": "8.8.8.8",
        "result": { "ip": "8.8.8.8", "asn": "AS15169", "org": "Google LLC", "isp": "Google Public DNS", "domain": "google.com", "route": "8.8.8.0/24", "type": "hosting" }
      },
      {
        "ip": "1.1.1.1",
        "result": { "ip": "1.1.1.1", "asn": "AS13335", "org": "Cloudflare, Inc.", "isp": "Cloudflare", "domain": "cloudflare.com", "route": "1.1.1.0/24", "type": "hosting" }
      }
    ],
    "total": 2
  },
  "metadata": { "timestamp": "2026-01-01T00:00:00Z" }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | Per-item results in input order. |
| `results[].ip` | string | The IP address that was looked up. |
| `results[].result` | object | ASN data (omitted on error). Same fields as the single-item endpoint. |
| `results[].error` | string | Error message if the lookup failed (omitted on success). |
| `total` | integer | Total number of items processed. |

## Errors

- `422` **validation_failed** — The ips array is missing, empty, exceeds 50 items, or contains an invalid IP address.
- `400` **bad_request** — The request body is missing or malformed.
