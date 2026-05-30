---
name: email-normalize-post-batch
api: Email Normalizer
method: POST
path: /v1/text/normalize/batch
base_url: https://api.requiems.xyz
description: Normalizes up to 100 email addresses in one request. Results are in the same order as the input. Each item includes valid (boolean); when false, only original and message are set. Usage is billed per email processed (see gateway usage headers).
---

## Endpoint

**POST https://api.requiems.xyz/v1/text/normalize/batch**

## Normalize Email Batch

Normalizes up to 100 email addresses in one request. Results are in the same order as the input. Each item includes valid (boolean); when false, only original and message are set. Usage is billed per email processed (see gateway usage headers).

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `emails` | array | yes | body | Array of addresses to normalize (min 1, max 100; each entry non-empty) |

## Request Example

```json
{
  "emails": [
    "user@example.com",
    "not-an-email",
    "te.st@gmail.com"
  ]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "original": "user@example.com",
        "normalized": "user@example.com",
        "local": "user",
        "domain": "example.com",
        "changes": [],
        "valid": true
      },
      {
        "original": "not-an-email",
        "valid": false,
        "message": "invalid email address"
      },
      {
        "original": "te.st@gmail.com",
        "normalized": "test@gmail.com",
        "local": "test",
        "domain": "gmail.com",
        "changes": ["lowercased", "removed_dots"],
        "valid": true
      }
    ],
    "total": 3
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | One normalization result per input email, in order |
| `total` | integer | Number of emails in the batch (same as results length) |

## Errors

- `422` **validation_failed** — Missing emails, empty array, too many items, or empty string in the array
- `400` **bad_request** — Invalid JSON or unknown fields in the body
