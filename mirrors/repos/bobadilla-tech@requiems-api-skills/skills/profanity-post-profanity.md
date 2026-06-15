---
name: profanity-post-profanity
api: Profanity Filter
method: POST
path: /v1/validation/profanity
base_url: https://api.requiems.xyz
description: Checks text for profanity, returning a censored version and the list of flagged words.
---

## Endpoint

**POST https://api.requiems.xyz/v1/validation/profanity**

## Check Profanity

Checks text for profanity, returning a censored version and the list of flagged words.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `text` | string | yes | body | The text to check for profanity. |

## Request Example

```json
{
  "text": "Some text to check"
}
```

## Response Example

```json
{
  "data": {
    "has_profanity": false,
    "censored": "Some text to check",
    "flagged_words": []
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `has_profanity` | boolean | Whether any profanity was detected in the text |
| `censored` | string | The input text with profane words replaced by asterisks |
| `flagged_words` | array of strings | Deduplicated list of profane words found (lowercase) |

## Errors

- `422` **validation_failed** — The text field is missing or empty.
- `400` **bad_request** — The request body is missing or malformed.
- `500` **internal_error** — Unexpected server error.
