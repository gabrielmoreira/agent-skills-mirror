---
name: trivia-get-trivia
api: Trivia
method: GET
path: /v1/entertainment/trivia
base_url: https://api.requiems.xyz
description: Returns a random trivia question with multiple-choice answers. Use the optional category and difficulty query parameters to filter the question pool.
---

## Endpoint

**GET https://api.requiems.xyz/v1/entertainment/trivia**

## Get Trivia Question

Returns a random trivia question with multiple-choice answers. Use the optional category and difficulty query parameters to filter the question pool.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `category` | string | no | query | Filter by category. One of: science, history, geography, sports, music, movies, literature, math, technology, nature. |
| `difficulty` | string | no | query | Filter by difficulty. One of: easy, medium, hard. |

## Response Example

```json
{
  "data": {
    "question": "What is the largest planet in our solar system?",
    "options": ["Earth", "Jupiter", "Saturn", "Mars"],
    "answer": "Jupiter",
    "category": "science",
    "difficulty": "easy"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `question` | string | The trivia question text |
| `options` | array[string] | Four multiple-choice answer options |
| `answer` | string | The correct answer — always one of the values in options |
| `category` | string | The category the question belongs to |
| `difficulty` | string | The difficulty level of the question (easy, medium, or hard) |

## Errors

- `400` **bad_request** — An invalid category or difficulty value was provided
- `404` **not_found** — No questions match the given category and difficulty combination
- `401` **unauthorized** — Missing API key
- `403` **forbidden** — Invalid or revoked API key
