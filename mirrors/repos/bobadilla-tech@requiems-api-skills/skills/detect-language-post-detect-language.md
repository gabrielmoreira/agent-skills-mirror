---
name: detect-language-post-detect-language
api: Language Detection
method: POST
path: /v1/text/detect-language
base_url: https://api.requiems.xyz
description: Identifies the language of the provided text and returns the language name, ISO 639-1 code, and confidence score.
---

## Endpoint

**POST https://api.requiems.xyz/v1/text/detect-language**

## Detect Language

Identifies the language of the provided text and returns the language name, ISO 639-1 code, and confidence score.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `text` | string | yes | body | The text whose language should be detected. |

## Request Example

```json
{
  "text": "Bonjour, comment ça va?"
}
```

## Response Example

```json
{
  "data": {
    "language": "French",
    "code": "fr",
    "confidence": 0.98
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `language` | string | Full name of the detected language (e.g. French, English, Spanish) |
| `code` | string | ISO 639-1 two-letter language code (e.g. fr, en, es). Empty string when detection is unreliable. |
| `confidence` | float | Confidence score between 0.0 and 1.0. 0.0 is returned when the language cannot be reliably detected. |

## Errors

- `422` **validation_failed** — The text field is missing or empty.
- `400` **bad_request** — The request body is missing or malformed.
- `500` **internal_error** — Unexpected server error.
