---
name: dictionary-get-{word}
api: Dictionary
method: GET
path: /v1/text/dictionary/{word}
base_url: https://api.requiems.xyz
description: Returns the definition, phonetics, examples, and synonyms for the given word.
---

## Endpoint

**GET https://api.requiems.xyz/v1/text/dictionary/{word}**

## Dictionary Lookup

Returns the definition, phonetics, examples, and synonyms for the given word.

## Parameters

| Name   | Type   | Required | Location | Description                           |
| ------ | ------ | -------- | -------- | ------------------------------------- |
| `word` | string | yes      | path     | The word to look up in the dictionary |

## Response Example

```json
{
  "data": {
    "word": "ephemeral",
    "phonetic": "/ɪˈfɛm(ə)rəl/",
    "definitions": [
      {
        "partOfSpeech": "adjective",
        "definition": "lasting for a very short time",
        "example": "ephemeral pleasures"
      }
    ],
    "synonyms": ["transient", "fleeting", "momentary", "brief", "short-lived"]
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field                        | Type             | Description                                                                                       |
| ---------------------------- | ---------------- | ------------------------------------------------------------------------------------------------- |
| `word`                       | string           | The normalized (lowercased) word that was looked up                                               |
| `phonetic`                   | string           | IPA phonetic transcription of the word (may be omitted if unavailable)                            |
| `definitions`                | array of objects | One or more definitions for the word, each with partOfSpeech, definition, and an optional example |
| `definitions[].partOfSpeech` | string           | Grammatical category (e.g. noun, verb, adjective)                                                 |
| `definitions[].definition`   | string           | Plain-text definition of the word                                                                 |
| `definitions[].example`      | string           | Example sentence using the word (may be omitted)                                                  |
| `synonyms`                   | array of strings | List of words with similar meaning                                                                |

## Errors

- `404` **not_found** — The word was not found in the dictionary dataset.
- `400` **bad_request** — The word path parameter is missing.
