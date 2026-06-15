---
name: vpn-detection-get-{ip}
api: VPN & Proxy Detection
method: GET
path: /v1/networking/ip/vpn/{ip}
base_url: https://api.requiems.xyz
description: Analyze an IP address to determine if it's a VPN, proxy, Tor exit node, or hosting provider. Returns detailed threat indicators and scores.
---

## Endpoint

**GET https://api.requiems.xyz/v1/networking/ip/vpn/{ip}**

## Check IP Address

Analyze an IP address to determine if it's a VPN, proxy, Tor exit node, or hosting provider. Returns detailed threat indicators and scores.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `ip` | string | yes | path | The IP address to check (supports IPv4 and IPv6) |

## Response Example

```json
{
  "data": {
    "ip": "8.8.8.8",
    "is_vpn": false,
    "is_proxy": false,
    "is_tor": false,
    "is_hosting": true,
    "score": 1,
    "threat": 1,
    "fraud_score": 0,
    "asn_org": "GOOGLE-ASN"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `ip` | string | The analyzed IP address |
| `is_vpn` | boolean | True when the IP belongs to a known VPN provider |
| `is_proxy` | boolean | True when the IP is a known public or web proxy |
| `is_tor` | boolean | True when the IP is a known Tor exit node |
| `is_hosting` | boolean | True when the IP belongs to a data-centre or hosting provider (DCH) |
| `score` | integer | Raw threat score (0-9+). Tor contributes 3, VPN or Proxy each contribute 2, Hosting contributes 1 |
| `threat` | integer | Threat level derived from score: 0 = None, 1 = Low, 2–3 = Medium, 4–5 = High, 6+ = Critical |
| `fraud_score` | integer | Fraud risk score from 0 (no risk) to 100 (high risk). Available when using IP2Proxy PX5 or higher |
| `asn_org` | string | Organization name owning the Autonomous System containing the IP (e.g. "DIGITALOCEAN-ASN") |

## Errors

- `400` **bad_request** — The IP address is missing or invalid
- `500` **internal_error** — Unexpected server error
