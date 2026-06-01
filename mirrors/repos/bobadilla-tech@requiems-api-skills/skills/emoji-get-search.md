---
name: emoji-get-search
api: Emoji
method: GET
path: /v1/entertainment/emoji/search
base_url: https://api.requiems.xyz
description: Search for emojis whose name or category contains the given query string (case-insensitive). Returns a list of all matches.
---

## Endpoint

**GET https://api.requiems.xyz/v1/entertainment/emoji/search**

## Search Emoji

Search for emojis whose name or category contains the given query string
(case-insensitive). Returns a list of all matches.

## Parameters

| Name | Type   | Required | Location | Description                                                                       |
| ---- | ------ | -------- | -------- | --------------------------------------------------------------------------------- |
| `q`  | string | yes      | query    | Search term to match against emoji names and categories (e.g. happy, heart, food) |

## Response Example

```json
{
  "data": {
    "items": [
      {
        "emoji": "😄",
        "name": "grinning_face_with_smiling_eyes",
        "category": "Smileys & Emotion",
        "unicode": "U+1F604"
      }
    ],
    "total": 1
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field   | Type    | Description                    |
| ------- | ------- | ------------------------------ |
| `items` | array   | List of matching emoji objects |
| `total` | integer | Total number of matches        |

## Errors

- `400` **bad_request** — The q query parameter is missing or empty.
