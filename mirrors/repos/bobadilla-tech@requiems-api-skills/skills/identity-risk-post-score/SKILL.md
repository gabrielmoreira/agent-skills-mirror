---
name: identity-risk-post-score
api: Identity & Risk System
method: POST
path: /v1/systems/risk/score
base_url: https://api.requiems.xyz
description: Score a user for risk without the full signal breakdown. Lower latency than /signup/protect, suited for background re-scoring and rate limiting.
---

## Endpoint

**POST https://api.requiems.xyz/v1/systems/risk/score**

## Score Risk

Score a user for risk without the full signal breakdown. Lower latency than /signup/protect, suited for background re-scoring and rate limiting.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `email` | string | no | body | Email address to include in the risk score. |
| `phone` | string | no | body | Phone number in E.164 format. |
| `ip_address` | string | no | body | IPv4 or IPv6 address to check. |

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
    "risk_score": 0.34,
    "is_safe": true,
    "confidence": 0.88,
    "flags": []
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `risk_score` | float | Composite risk score from 0.0 to 1.0 |
| `is_safe` | boolean | True when the risk score is below the safety threshold |
| `confidence` | float | Confidence in the score based on resolved signals |
| `flags` | array | Array of triggered risk flags |

## Errors

- `undefined` **422** — All of email, phone, and ip_address were omitted
- `undefined` **401** — Missing or invalid API key
