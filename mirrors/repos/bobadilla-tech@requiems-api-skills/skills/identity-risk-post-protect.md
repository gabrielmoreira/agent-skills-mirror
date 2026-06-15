---
name: identity-risk-post-protect
api: Identity & Risk System
method: POST
path: /v1/systems/signup/protect
base_url: https://api.requiems.xyz
description: Evaluate a new user at signup. Returns a full risk decision with per-signal breakdown across email, phone, and IP.
---

## Endpoint

**POST https://api.requiems.xyz/v1/systems/signup/protect**

## Protect Signup

Evaluate a new user at signup. Returns a full risk decision with per-signal breakdown across email, phone, and IP.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `email` | string | no | body | Email address to validate and score. At least one of email, phone, or ip_address is required. |
| `phone` | string | no | body | Phone number in E.164 format to validate and check for VoIP or virtual numbers. |
| `ip_address` | string | no | body | IPv4 or IPv6 address to check for VPN, proxy, TOR, and hosting status. |

## Request Example

```json
{
  "email": "user@tempmail.io",
  "ip_address": "45.33.32.156",
  "phone": "+14155552671"
}
```

## Response Example

```json
{
  "data": {
    "risk_score": 0.87,
    "is_safe": false,
    "confidence": 0.94,
    "flags": ["disposable_email", "vpn_detected"],
    "signals": {
      "email": {
        "valid": true,
        "disposable": true,
        "mx_valid": true,
        "suggestion": null
      },
      "phone": {
        "valid": false,
        "country": "",
        "is_voip": false,
        "is_virtual": false
      },
      "ip": {
        "country_code": "US",
        "is_vpn": true,
        "is_proxy": false,
        "is_tor": false,
        "is_hosting": true,
        "fraud_score": 0.72
      }
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
| `risk_score` | float | Composite risk score from 0.0 (clean) to 1.0 (high risk) |
| `is_safe` | boolean | True when risk_score is below the safety threshold with no critical flags |
| `confidence` | float | Confidence in the decision from 0.0 to 1.0, based on which signals resolved successfully |
| `flags` | array | Array of triggered risk flags. Possible values: disposable_email, vpn_detected, proxy_detected, tor_detected, is_hosting |
| `signals.email` | object | Email validation result including disposable detection and MX check |
| `signals.phone` | object | Phone number validation result with country code and VoIP/virtual detection |
| `signals.ip` | object | IP intelligence including VPN/proxy/TOR status and fraud score |

## Errors

- `undefined` **422** — All of email, phone, and ip_address were omitted. At least one is required.
- `undefined` **401** — Missing or invalid API key in the requiems-api-key header
