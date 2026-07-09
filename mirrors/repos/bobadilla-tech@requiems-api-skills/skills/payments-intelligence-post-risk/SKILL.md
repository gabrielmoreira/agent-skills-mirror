---
name: payments-intelligence-post-risk
api: Payments Intelligence System
method: POST
path: /v1/systems/transaction/risk
base_url: https://api.requiems.xyz
description: Score a transaction for fraud risk by cross-checking the card BIN country against IP geolocation and billing country. Detects VPN, proxy, and TOR use.
---

## Endpoint

**POST https://api.requiems.xyz/v1/systems/transaction/risk**

## Score Transaction Risk

Score a transaction for fraud risk by cross-checking the card BIN country against IP geolocation and billing country. Detects VPN, proxy, and TOR use.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `card_bin` | string | yes | body | Card BIN (first 6–8 digits) to look up card issuing country. |
| `ip_address` | string | yes | body | Customer's IPv4 or IPv6 address. Must be a valid IP. |
| `billing_country` | string | no | body | ISO 3166-1 alpha-2 billing country code. When provided, country mismatch checks are more precise. |
| `amount_usd` | number | no | body | Transaction amount in USD. High-value transactions via VPN incur an additional risk score boost. |

## Request Example

```json
{
  "card_bin": "424242",
  "ip_address": "92.168.1.1",
  "billing_country": "DE",
  "amount_usd": 250.00
}
```

## Response Example

```json
{
  "data": {
    "risk_score": 0.55,
    "is_safe": false,
    "flags": ["ip_country_mismatch", "country_mismatch", "vpn_detected"],
    "signals": {
      "ip_country": "NL",
      "billing_country": "DE",
      "bin_country": "US",
      "vpn_detected": true,
      "is_proxy": false,
      "is_tor": false,
      "country_mismatch": true
    }
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `risk_score` | float | Transaction risk score from 0.0 to 1.0 |
| `is_safe` | boolean | True when score is below 0.5 and no TOR or proxy detected |
| `flags` | array | Triggered flags. Possible values: ip_country_mismatch, bin_country_mismatch, country_mismatch, vpn_detected, proxy_detected, tor_detected, high_value_vpn |
| `signals.ip_country` | string | Country code resolved from the IP address |
| `signals.billing_country` | string or null | Billing country provided in the request, or null if omitted |
| `signals.bin_country` | string | Country of the card issuer resolved from the BIN |
| `signals.country_mismatch` | boolean | True when any country comparison produced a mismatch |

## Errors

- `undefined` **422** — ip_address is not a valid IPv4 or IPv6 address, or card_bin is missing
- `undefined` **401** — Missing or invalid API key
