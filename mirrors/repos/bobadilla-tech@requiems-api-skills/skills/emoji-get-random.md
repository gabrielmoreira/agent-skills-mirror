---
name: emoji-get-random
api: Emoji
method: GET
path: /v1/entertainment/emoji/random
base_url: https://api.requiems.xyz
description: Returns a randomly selected emoji with its full metadata.
---

## Endpoint

**GET https://api.requiems.xyz/v1/entertainment/emoji/random**

## Get Random Emoji

Returns a randomly selected emoji with its full metadata.

## Response Example

```json
{
  "data": {
    "emoji": "😀",
    "name": "grinning_face",
    "category": "Smileys & Emotion",
    "unicode": "U+1F600"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field      | Type   | Description                                                 |
| ---------- | ------ | ----------------------------------------------------------- |
| `emoji`    | string | The rendered emoji glyph                                    |
| `name`     | string | CLDR short name in snake_case (e.g. grinning_face)          |
| `category` | string | Unicode category (e.g. Smileys & Emotion, Animals & Nature) |
| `unicode`  | string | Unicode code-point in U+XXXX notation (e.g. U+1F600)        |
