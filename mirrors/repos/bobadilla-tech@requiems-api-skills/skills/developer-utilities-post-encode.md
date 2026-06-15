---
name: developer-utilities-post-encode
api: Developer Utilities
method: POST
path: /v1/technology/base64/encode
base_url: https://api.requiems.xyz
description: Encode a plain-text string to Base64. Supports standard (RFC 4648) and URL-safe (base64url) variants.
---

## Endpoint

**POST https://api.requiems.xyz/v1/technology/base64/encode**

## Base64 Encode

Encode a plain-text string to Base64. Supports standard (RFC 4648) and URL-safe (base64url) variants.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `value` | string | yes | body | The string to encode |
| `variant` | string | no | body | Encoding variant: standard (default) or url (URL-safe base64url, RFC 4648 §5) |

## Request Example

```json
{
  "value": "Hello, world!",
  "variant": "standard"
}
```

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

| Field | Type | Description |
| ----- | ---- | ----------- |
| `result` | string | The Base64-encoded output string |

## Errors

- `undefined` **400** — value field is missing or empty
- `undefined` **422** — variant is not standard or url
- `undefined` **401** — Missing or invalid API key
