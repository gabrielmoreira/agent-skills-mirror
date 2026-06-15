---
name: lorem-ipsum-post-batch
api: Lorem Ipsum Generator
method: POST
path: /v1/text/lorem/batch
base_url: https://api.requiems.xyz
description: Generate multiple Lorem Ipsum placeholder texts in a single request. Processes items in bulk and returns partial successes.
---

## Endpoint

**POST https://api.requiems.xyz/v1/text/lorem/batch**

## Generate Lorem Ipsum (Batch)

Generate multiple Lorem Ipsum placeholder texts in a single request. Processes items in bulk and returns partial successes.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `items` | array | yes | body | Array of text generation requests. Minimum 1 item, maximum 50 items. |
| `items[].paragraphs` | integer | no | body | Number of paragraphs to generate (1-20) |
| `items[].sentences` | integer | no | body | Number of sentences per paragraph (1-20) |

## Response Example

```json
{
  "data": [
    {
      "data": {
        "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit...",
        "paragraphs": 2,
        "word_count": 90
      }
    },
    {
      "error": "sentences must be between 1 and 20"
    }
  ],
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z",
    "usage_count": 2
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `data[].data` | object | Contains the generated text if the specific item was successful |
| `data[].error` | string | Error message if the specific item failed to generate |

## Errors

- `undefined` **422** — The request body is malformed, missing the items array, or exceeds the maximum batch size of 50 items.
