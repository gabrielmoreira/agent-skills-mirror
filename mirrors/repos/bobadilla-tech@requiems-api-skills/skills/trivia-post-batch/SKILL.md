---
name: trivia-post-batch
api: Trivia
method: POST
path: /v1/entertainment/trivia/batch
base_url: https://api.requiems.xyz
description: Returns up to 50 trivia questions in a single request.
---

## Endpoint

**POST https://api.requiems.xyz/v1/entertainment/trivia/batch**

## Get Batch Trivia Questions

Returns up to 50 trivia questions in a single request.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `filters` | array | yes | body | Array of filters to get (min: 1, max: 50). |

## Request Example

```json
{
  "filters": [{"category": "sports", "difficulty": "easy"},{"category": "history", "difficulty": "medium"}]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "category": "sports",
        "difficulty": "easy",
        "data": {
          "question": "In which country did the ancient Olympic Games originate?",
          "options": [
            "Italy",
            "Turkey",
            "Greece",
            "Egypt"
          ],
          "answer": "Greece",
          "category": "sports",
          "difficulty": "easy"
        }
      },
      {
        "category": "history",
        "difficulty": "medium",
        "data": {
          "question": "In what year was the Magna Carta signed?",
          "options": [
            "1215",
            "1066",
            "1415",
            "1305"
          ],
          "answer": "1215",
          "category": "history",
          "difficulty": "medium"
        }
      }
    ],
    "total": 2
  },
  "metadata": {
    "timestamp": "2026-05-22T22:27:35Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | List of trivia questions returned in the same order as the input filters. |
| `results[].category` | string | The topic filter used to retrieve the trivia question. |
| `results[].difficulty` | string | The complexity level filter used to retrieve the trivia question. |
| `results[].error` | string | Describes why the question could not be retrieved for this filter. Omitted if the query was successful. |
| `results[].data` | object | The trivia question returned for this filter. Empty if the query failed. |
| `results[].data.question` | string | The trivia question text. |
| `results[].data.options` | array | List of possible answers for the question. |
| `results[].data.answer` | string | The correct answer to the trivia question. |
| `results[].data.category` | string | The category the trivia question belongs to. |
| `results[].data.difficulty` | string | The difficulty level of the trivia question. |
| `total` | integer | Total number of trivia results returned. |

## Errors

- `422` **validation_failed** — The filters array is missing, empty, or contains more than 50 items.
- `400` **bad_request** — Invalid JSON, malformed request body, or unexpected field types.
- `401` **unauthorized** — Missing API key.
- `403` **forbidden** — Invalid or revoked API key.
