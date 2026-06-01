---
name: thesaurus-get-{word}
api: Thesaurus
method: GET
path: /v1/text/thesaurus/{word}
base_url: https://api.requiems.xyz
description: Returns synonyms and antonyms for the given word.
---

## Endpoint

**GET https://api.requiems.xyz/v1/text/thesaurus/{word}**

## Thesaurus Lookup

Returns synonyms and antonyms for the given word.

## Parameters

| Name   | Type   | Required | Location | Description                          |
| ------ | ------ | -------- | -------- | ------------------------------------ |
| `word` | string | yes      | path     | The word to look up in the thesaurus |

## Response Example

```json
{
  "data": {
    "word": "happy",
    "synonyms": [
      "joyful",
      "cheerful",
      "content",
      "pleased",
      "delighted",
      "glad",
      "elated",
      "blissful"
    ],
    "antonyms": [
      "sad",
      "unhappy",
      "miserable",
      "sorrowful",
      "dejected",
      "gloomy",
      "melancholy"
    ]
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field      | Type             | Description                                         |
| ---------- | ---------------- | --------------------------------------------------- |
| `word`     | string           | The normalized (lowercased) word that was looked up |
| `synonyms` | array of strings | List of words with similar meaning                  |
| `antonyms` | array of strings | List of words with opposite meaning                 |

## Errors

- `404` **not_found** — The word was not found in the thesaurus dataset.
- `400` **bad_request** — The word path parameter is missing.
