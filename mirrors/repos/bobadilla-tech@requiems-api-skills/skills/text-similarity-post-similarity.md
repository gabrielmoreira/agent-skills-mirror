---
name: text-similarity-post-similarity
api: Text Similarity
method: POST
path: /v1/text/similarity
base_url: https://api.requiems.xyz
description: Compares two texts and returns a cosine similarity score.
---

## Endpoint

**POST https://api.requiems.xyz/v1/text/similarity**

## Compare Text Similarity

Compares two texts and returns a cosine similarity score.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `text1` | string | yes | body | The first text to compare. |
| `text2` | string | yes | body | The second text to compare. |

## Request Example

```json
{
  "text1": "The cat sat on the mat",
  "text2": "A cat was sitting on a mat"
}
```

## Response Example

```json
{
  "data": {
    "similarity": 0.4364,
    "method": "cosine"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `similarity` | number | Cosine similarity score between the two texts, in the range [0, 1]. |
| `method` | string | The algorithm used. Currently always 'cosine'. |

## Errors

- `422` **validation_failed** — One or both text fields are missing or empty.
- `400` **bad_request** — The request body is missing or malformed.
- `500` **internal_error** — Unexpected server error.
