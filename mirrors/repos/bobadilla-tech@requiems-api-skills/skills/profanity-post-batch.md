---
name: profanity-post-batch
api: Profanity Filter
method: POST
path: /v1/validation/profanity/batch
base_url: https://api.requiems.xyz
description: Check up to 50 texts for profanity in a single request. Results are returned in input order.
---

## Endpoint

**POST https://api.requiems.xyz/v1/validation/profanity/batch**

## Batch Check Profanity

Check up to 50 texts for profanity in a single request. Results are returned in input order.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `texts` | array of strings | yes | body | List of texts to check (1–50 items, each non-empty). |

## Request Example

```json
{
  "texts": ["hello world", "some bad word here"]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "text": "hello world",
        "result": { "has_profanity": false, "censored": "hello world", "flagged_words": [] }
      },
      {
        "text": "some bad word here",
        "result": { "has_profanity": true, "censored": "some *** word here", "flagged_words": ["bad"] }
      }
    ],
    "total": 2
  },
  "metadata": { "timestamp": "2026-01-01T00:00:00Z" }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | Per-item results in input order. |
| `results[].text` | string | The original text that was checked. |
| `results[].result.has_profanity` | boolean | Whether any profanity was detected. |
| `results[].result.censored` | string | Text with profane words replaced by asterisks. |
| `results[].result.flagged_words` | array of strings | Deduplicated list of detected profane words (lowercase). |
| `total` | integer | Total number of items processed. |

## Errors

- `422` **validation_failed** — The texts array is missing, empty, or exceeds 50 items.
- `400` **bad_request** — The request body is missing or malformed.
