---
name: disposable_email-post-check
api: Disposable Email Checker
method: POST
path: /v1/networking/disposable/check
base_url: https://api.requiems.xyz
description: Validate whether an email address uses a disposable domain
---

## Endpoint

**POST https://api.requiems.xyz/v1/networking/disposable/check**

## Check Single Email

Validate whether an email address uses a disposable domain

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `email` | string | yes | body | The email address to check |

## Request Example

```json
{
  "email": "user@tempmail.com"
}
```

## Response Example

```json
{
  "data": {
    "email": "user@tempmail.com",
    "is_disposable": true,
    "domain": "tempmail.com"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `email` | string | The email address that was checked |
| `is_disposable` | boolean | Whether the email uses a disposable domain |
| `domain` | string | The domain part of the email address |

## Errors

- `undefined` **400** — The request body is missing or malformed
- `undefined` **400** — The email address format is invalid
