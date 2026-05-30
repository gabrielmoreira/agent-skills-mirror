---
name: base64-post-decode
api: Base64 Encode / Decode
method: POST
path: /v1/technology/base64/decode
base_url: https://api.requiems.xyz
description: Decode a Base64-encoded string back to plain text
---

## Endpoint

**POST https://api.requiems.xyz/v1/technology/base64/decode**

## Decode

Decode a Base64-encoded string back to plain text

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `value` | string | yes | body | The Base64-encoded string to decode |
| `variant` | string | no | body | Encoding variant: standard (default) or url (URL-safe base64url) |

## Response Example

```json
{
  "data": {
    "result": "Hello, world!"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `result` | string | The decoded plain-text output |

## Errors

- `undefined` **400** — Missing or empty value field
- `undefined` **422** — The value is not valid Base64 and cannot be decoded
