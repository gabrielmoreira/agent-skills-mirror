---
name: quotes-get-random
api: Random Quotes
method: GET
path: /v1/entertainment/quotes/random
base_url: https://api.requiems.xyz
description: Returns a random inspirational quote with author attribution
---

## Endpoint

**GET https://api.requiems.xyz/v1/entertainment/quotes/random**

## Get Random Quote

Returns a random inspirational quote with author attribution

## Response Example

```json
{
  "data": {
    "id": 42,
    "text": "The only way to do great work is to love what you do.",
    "author": "Steve Jobs"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `id` | integer | Unique identifier for the quote |
| `text` | string | The quote text |
| `author` | string | Name of the person who said or wrote the quote |

## Errors

- `undefined` **503** — No quotes available in the database
