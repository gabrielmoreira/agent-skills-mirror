---
name: spell-check-post-spellcheck
api: Spell Check
method: POST
path: /v1/text/spellcheck
base_url: https://api.requiems.xyz
description: Checks the input text for spelling mistakes and returns a corrected version along with per-word corrections.
---

## Endpoint

**POST https://api.requiems.xyz/v1/text/spellcheck**

## Check Spelling

Checks the input text for spelling mistakes and returns a corrected version along with per-word corrections.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `text` | string | yes | body | The text to spell-check. |

## Request Example

```json
{
  "text": "Ths is a smiple tset"
}
```

## Response Example

```json
{
  "data": {
    "corrected": "This is a simple test",
    "corrections": [
      {
        "original": "Ths",
        "suggested": "This",
        "suggestions": ["Th's", "Th", "This"],
        "position": 0
      },
      {
        "original": "smiple",
        "suggested": "simple",
        "suggestions": ["simple", "smile", "Siple"],
        "position": 9
      },
      {
        "original": "tset",
        "suggested": "test",
        "suggestions": ["set", "test", "stet"],
        "position": 16
      }
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
| `corrected` | string | The full input text with all misspelled words replaced by the top-ranked suggestion |
| `corrections` | array of objects | List of individual corrections. Each item contains: original (the misspelled word), suggested (the top-ranked replacement applied to corrected), suggestions (up to 3 ranked alternatives returned by LanguageTool, from most to least likely), and position (0-based Unicode character offset in the original text) |

## Errors

- `422` **validation_failed** — The text field is missing or empty.
- `400` **bad_request** — The request body is missing or malformed.
- `500` **internal_error** — Unexpected server error.
