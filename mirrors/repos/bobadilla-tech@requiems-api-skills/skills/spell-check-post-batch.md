---
name: spell-check-post-batch
api: Spell Check
method: POST
path: /v1/text/spellcheck/batch
base_url: https://api.requiems.xyz
description: Checks multiple texts for spelling mistakes in a single request. Returns a corrected version and per-word corrections for each input text. Results are returned in the same order as the input array.
---

## Endpoint

**POST https://api.requiems.xyz/v1/text/spellcheck/batch**

## Check Spelling (Batch)

Checks multiple texts for spelling mistakes in a single request. Returns a
corrected version and per-word corrections for each input text. Results are
returned in the same order as the input array.

## Parameters

| Name    | Type  | Required | Location | Description                                               |
| ------- | ----- | -------- | -------- | --------------------------------------------------------- |
| `texts` | array | yes      | body     | The list of texts to spell-check. Between 1 and 50 items. |

## Request Example

```json
{
  "texts": ["Ths is a tset", "Smiple example"]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "corrected": "This is a test",
        "corrections": [
          {
            "original": "Ths",
            "suggested": "This",
            "suggestions": ["Th's", "Th", "This"],
            "position": 0
          },
          {
            "original": "tset",
            "suggested": "test",
            "suggestions": ["set", "test", "stet"],
            "position": 9
          }
        ]
      },
      {
        "corrected": "Simple example",
        "corrections": [
          {
            "original": "Smiple",
            "suggested": "Simple",
            "suggestions": ["Simple", "Smile", "Siple"],
            "position": 0
          }
        ]
      }
    ],
    "total": 2
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field     | Type             | Description                                                                                                                                                                                                         |
| --------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `results` | array of objects | One entry per input text, in the same order as the input array. Each item contains corrected (the fixed text) and corrections (list of individual corrections with original, suggested, suggestions, and position). |
| `total`   | integer          | Number of texts processed. Equals the length of the input array.                                                                                                                                                    |

## Errors

- `422` **validation_failed** — The texts field is missing, empty, or exceeds 50
  items.
- `400` **bad_request** — The request body is missing or malformed.
- `500` **internal_error** — Unexpected server error.
