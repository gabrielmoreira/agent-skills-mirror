---
name: dad-jokes-get-dad
api: Dad Jokes
method: GET
path: /v1/entertainment/jokes/dad
base_url: https://api.requiems.xyz
description: Returns a randomly selected dad joke from the collection.
---

## Endpoint

**GET https://api.requiems.xyz/v1/entertainment/jokes/dad**

## Get Random Dad Joke

Returns a randomly selected dad joke from the collection.

## Response Example

```json
{
  "data": {
    "id": "joke_7",
    "joke": "Why don't scientists trust atoms? Because they make up everything!"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `id` | string | Stable identifier for the joke (e.g. "joke_7") |
| `joke` | string | The full text of the dad joke |

## Errors

- `401` **unauthorized** — Missing API key
- `403` **forbidden** — Invalid or revoked API key
