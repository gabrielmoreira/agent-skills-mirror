---
name: email-normalize-post-normalize
api: Email Normalizer
method: POST
path: /v1/text/normalize
base_url: https://api.requiems.xyz
description: Normalizes a single email address and returns the canonical form together with a breakdown of all transformations applied.
---

## Endpoint

**POST https://api.requiems.xyz/v1/text/normalize**

## Normalize Email

Normalizes a single email address and returns the canonical form together with a breakdown of all transformations applied.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `email` | string | yes | body | The email address to normalize. Must be a syntactically valid address. |

## Request Example

```json
{
  "email": "Te.st.User+spam@Googlemail.com"
}
```

## Response Example

```json
{
  "data": {
    "original": "Te.st.User+spam@Googlemail.com",
    "normalized": "testuser@gmail.com",
    "local": "testuser",
    "domain": "gmail.com",
    "changes": [
      "lowercased",
      "removed_dots",
      "removed_plus_tag",
      "canonicalised_domain"
    ]
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `original` | string | The email address exactly as supplied in the request body |
| `normalized` | string | The canonical form of the address after all transformations |
| `local` | string | The local part (before @) of the normalized address |
| `domain` | string | The domain part (after @) of the normalized address |
| `changes` | array | Ordered list of transformations applied. Possible values: lowercased, trimmed_whitespace, removed_dots, removed_plus_tag, canonicalised_domain. Empty array when no changes were needed. |

## Errors

- `422` **validation_failed** — The email field is missing or not a valid email address format.
- `400` **bad_request** — The request body is missing, not valid JSON, or contains unknown fields.
- `500` **internal_error** — Unexpected server error.
