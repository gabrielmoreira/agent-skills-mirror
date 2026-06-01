---
name: emoji-get-{name}
api: Emoji
method: GET
path: /v1/entertainment/emoji/{name}
base_url: https://api.requiems.xyz
description: Returns a specific emoji by its CLDR snake_case name. The name is case-insensitive.
---

## Endpoint

**GET https://api.requiems.xyz/v1/entertainment/emoji/{name}**

## Get Emoji by Name

Returns a specific emoji by its CLDR snake_case name. The name is
case-insensitive.

## Parameters

| Name   | Type   | Required | Location | Description                                                |
| ------ | ------ | -------- | -------- | ---------------------------------------------------------- |
| `name` | string | yes      | path     | CLDR snake_case emoji name (e.g. grinning_face, thumbs_up) |

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

| Field      | Type   | Description                           |
| ---------- | ------ | ------------------------------------- |
| `emoji`    | string | The rendered emoji glyph              |
| `name`     | string | CLDR short name in snake_case         |
| `category` | string | Unicode category                      |
| `unicode`  | string | Unicode code-point in U+XXXX notation |

## Errors

- `404` **not_found** — No emoji found with the given name.
