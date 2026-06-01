---
name: lorem-ipsum-get-lorem
api: Lorem Ipsum Generator
method: GET
path: /v1/text/lorem
base_url: https://api.requiems.xyz
description: Generate Lorem Ipsum placeholder text with customizable length and format
---

## Endpoint

**GET https://api.requiems.xyz/v1/text/lorem**

## Generate Lorem Ipsum

Generate Lorem Ipsum placeholder text with customizable length and format

## Parameters

| Name         | Type    | Required | Location | Description                              |
| ------------ | ------- | -------- | -------- | ---------------------------------------- |
| `paragraphs` | integer | no       | query    | Number of paragraphs to generate (1-20)  |
| `sentences`  | integer | no       | query    | Number of sentences per paragraph (1-20) |

## Response Example

```json
{
  "data": {
    "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.",
    "paragraphs": 1,
    "wordCount": 45
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field        | Type    | Description                             |
| ------------ | ------- | --------------------------------------- |
| `text`       | string  | Generated Lorem Ipsum text              |
| `paragraphs` | integer | Number of paragraphs generated          |
| `wordCount`  | integer | Total number of words in generated text |

## Errors

- `undefined` **400** — The paragraphs parameter is out of valid range
- `undefined` **400** — The sentences parameter is out of valid range
