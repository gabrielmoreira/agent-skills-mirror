---
name: base64-post-encode
api: Base64 Encode / Decode
method: POST
path: /v1/technology/base64/encode
base_url: https://api.requiems.xyz
description: Encode a plain-text string to Base64
---

## Endpoint

**POST https://api.requiems.xyz/v1/technology/base64/encode**

## Encode

Encode a plain-text string to Base64

## Parameters

| Name      | Type   | Required | Location | Description                                                      |
| --------- | ------ | -------- | -------- | ---------------------------------------------------------------- |
| `value`   | string | yes      | body     | The string to encode                                             |
| `variant` | string | no       | body     | Encoding variant: standard (default) or url (URL-safe base64url) |

## Response Example

```json
{
  "data": {
    "result": "SGVsbG8sIHdvcmxkIQ=="
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field    | Type   | Description               |
| -------- | ------ | ------------------------- |
| `result` | string | The Base64-encoded output |

## Errors

- `undefined` **400** — Missing or empty value field
- `undefined` **422** — Validation constraint on the variant field (must be
  standard or url)
