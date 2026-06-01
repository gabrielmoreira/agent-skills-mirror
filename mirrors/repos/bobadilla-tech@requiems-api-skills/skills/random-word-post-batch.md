---
name: random-word-post-batch
api: Random Word
method: POST
path: /v1/text/words/batch
base_url: https://api.requiems.xyz
description: Resolve multiple words in a single request. Returns dictionary entries when found, or error information when a word is not in the dataset.
---

## Endpoint

**POST https://api.requiems.xyz/v1/text/words/batch**

## Batch Define Words

Resolve multiple words in a single request. Returns dictionary entries when
found, or error information when a word is not in the dataset.

## Parameters

| Name    | Type  | Required | Location | Description                                      |
| ------- | ----- | -------- | -------- | ------------------------------------------------ |
| `items` | array | yes      | body     | List of words to look up in batch (max 50 items) |

## Request Example

```json
{
  "items": ["ephemeral", "serendipity", "melancholy"]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "word": "serendipity",
        "found": true,
        "entry": {
          "word": "serendipity",
          "phonetic": "/ˌserənˈdipədē/",
          "definitions": [
            {
              "partOfSpeech": "noun",
              "definition": "the occurrence of events by chance in a happy way"
            }
          ],
          "synonyms": ["fluke", "chance", "fortuity"]
        }
      },
      {
        "word": "fakeword",
        "found": false,
        "error": "word not found: fakeword"
      }
    ],
    "total": 3
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field     | Type    | Description                     |
| --------- | ------- | ------------------------------- |
| `results` | array   | List of batch lookup results    |
| `total`   | integer | Total number of items processed |

## Errors

- `undefined` **422** — Invalid or empty items array
