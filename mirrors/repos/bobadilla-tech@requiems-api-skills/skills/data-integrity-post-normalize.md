---
name: data-integrity-post-normalize
api: Data Integrity System
method: POST
path: /v1/systems/text/normalize
base_url: https://api.requiems.xyz
description: Apply a composable pipeline of normalization operations to a string. Trim whitespace, fix encoding, normalize unicode, strip HTML, and more — in a single call.
---

## Endpoint

**POST https://api.requiems.xyz/v1/systems/text/normalize**

## Normalize Text

Apply a composable pipeline of normalization operations to a string. Trim whitespace, fix encoding, normalize unicode, strip HTML, and more — in a single call.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `text` | string | yes | body | The text to normalize. Required. |
| `operations` | array | yes | body | Ordered list of normalization operations to apply. At least one required. Valid values: trim, lowercase, uppercase, normalize_unicode, collapse_whitespace, strip_html, remove_punctuation |

## Request Example

```json
{
  "text": "  Hello,   World!  ",
  "operations": ["trim", "lowercase", "collapse_whitespace"]
}
```

## Response Example

```json
{
  "data": {
    "original": "  Hello,   World!  ",
    "normalized": "hello, world!",
    "operations": ["trim", "lowercase", "collapse_whitespace"]
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `original` | string | The input text as provided |
| `normalized` | string | The text after all operations have been applied in order |
| `operations` | array | The operations list echoed from the request |

## Errors

- `undefined` **422** — text is empty or operations array is empty or missing
- `undefined` **401** — Missing or invalid API key
