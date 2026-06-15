---
name: identity-risk-post-verify
api: Identity & Risk System
method: POST
path: /v1/systems/user/verify
base_url: https://api.requiems.xyz
description: Deep-verify an email address using domain-level signals including WHOIS age, MX records, and domain availability. Optional IP check. Use for high-value or suspicious accounts.
---

## Endpoint

**POST https://api.requiems.xyz/v1/systems/user/verify**

## Verify User

Deep-verify an email address using domain-level signals including WHOIS age, MX records, and domain availability. Optional IP check. Use for high-value or suspicious accounts.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `email` | string | yes | body | Email address to verify. Domain-level WHOIS, MX, and DNS checks are run automatically. |
| `ip_address` | string | no | body | Optional IPv4 or IPv6 address. When provided, VPN and proxy signals are added to the result. |

## Request Example

```json
{
  "email": "user@example.com",
  "ip_address": "45.33.32.156"
}
```

## Response Example

```json
{
  "data": {
    "verified": true,
    "confidence": 0.92,
    "risk_score": 0.08,
    "flags": [],
    "signals": {
      "email": {
        "valid": true,
        "disposable": false,
        "mx_valid": true
      },
      "domain": {
        "age_days": 4521,
        "has_mx": true,
        "has_a_records": true,
        "available": false
      },
      "ip": {
        "is_vpn": false,
        "is_proxy": false,
        "fraud_score": 0.02
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
| `verified` | boolean | True when risk score is below 0.3, confidence is above 0.5, email is valid, domain has MX, and domain is registered |
| `confidence` | float | Confidence in the verification result, based on how many signals resolved |
| `risk_score` | float | Composite risk score from 0.0 to 1.0 |
| `flags` | array | Triggered risk flags. Possible values: email_invalid, disposable_email, no_mx, domain_not_registered, young_domain, whois_unavailable, ip_risk |
| `signals.email` | object | Email validation result |
| `signals.domain` | object | Domain intelligence including WHOIS age, MX and A record presence, and registration status |
| `signals.ip` | object or null | IP risk signals. Null when ip_address was not provided |

## Errors

- `undefined` **422** — email field is missing or empty
- `undefined` **401** — Missing or invalid API key
