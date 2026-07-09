---
name: random-word-get-random
api: Random Word
method: GET
path: /v1/text/words/random
base_url: https://api.requiems.xyz
description: Returns a random word with its definition and part of speech
---

## Endpoint

**GET https://api.requiems.xyz/v1/text/words/random**

## Get Random Word

Returns a random word with its definition and part of speech

## Response Example

```json
{
  "data": {
    "id": 123,
    "word": "ephemeral",
    "definition": "lasting for a very short time",
    "part_of_speech": "adjective"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `id` | integer | Unique identifier for the word |
| `word` | string | The random word |
| `definition` | string | Dictionary definition of the word |
| `part_of_speech` | string | Grammatical classification (e.g., noun, verb, adjective, adverb) |

## Errors

- `undefined` **503** — No words available in the database
