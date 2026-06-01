---
name: quotes-post-batch
api: Random Quotes
method: POST
path: /v1/entertainment/quotes/random/batch
base_url: https://api.requiems.xyz
description: Returns up to 50 random quotes in a single request. Each quote counts as one unit of usage.
---

## Endpoint

**POST https://api.requiems.xyz/v1/entertainment/quotes/random/batch**

## Get Random Quotes (Batch)

Returns up to 50 random quotes in a single request. Each quote counts as one
unit of usage.

## Parameters

| Name    | Type    | Required | Location | Description                                          |
| ------- | ------- | -------- | -------- | ---------------------------------------------------- |
| `count` | integer | yes      | body     | Number of random quotes to return. Between 1 and 50. |

## Request Example

```json
{
  "count": 5
}
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "id": 42,
        "text": "The only way to do great work is to love what you do.",
        "author": "Steve Jobs"
      },
      {
        "id": 7,
        "text": "In the middle of every difficulty lies opportunity.",
        "author": "Albert Einstein"
      },
      {
        "id": 15,
        "text": "It does not matter how slowly you go as long as you do not stop.",
        "author": "Confucius"
      },
      {
        "id": 3,
        "text": "Life is what happens when you're busy making other plans.",
        "author": "John Lennon"
      },
      {
        "id": 88,
        "text": "Spread love everywhere you go.",
        "author": "Mother Teresa"
      }
    ],
    "total": 5
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field              | Type    | Description                                                         |
| ------------------ | ------- | ------------------------------------------------------------------- |
| `results`          | array   | Array of random quotes, one per requested count.                    |
| `results[].id`     | integer | Unique identifier for the quote.                                    |
| `results[].text`   | string  | The quote text.                                                     |
| `results[].author` | string  | Name of the person who said or wrote the quote. May be empty.       |
| `total`            | integer | Total number of quotes returned. Always equals the requested count. |

## Errors

- `undefined` **400** — Request body is missing or not valid JSON.
- `undefined` **422** — count is missing, less than 1, or greater than 50.
