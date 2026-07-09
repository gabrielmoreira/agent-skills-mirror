---
name: data-integrity-post-moderate
api: Data Integrity System
method: POST
path: /v1/systems/content/moderate
base_url: https://api.requiems.xyz
description: Check text for profanity, toxicity, sentiment, and language. Returns per-category flags and an is_safe boolean for gating content.
---

## Endpoint

**POST https://api.requiems.xyz/v1/systems/content/moderate**

## Moderate Content

Check text for profanity, toxicity, sentiment, and language. Returns per-category flags and an is_safe boolean for gating content.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `text` | string | yes | body | The text to moderate. Any language. Required. |
| `language` | string | no | body | ISO 639-1 language code (e.g. en, de, fr). When provided, language detection is skipped and confidence is set to 1.0. |

## Request Example

```json
{
  "text": "This is some user-generated content.",
  "language": "en"
}
```

## Response Example

```json
{
  "data": {
    "is_safe": true,
    "toxicity_score": null,
    "sentiment": "neutral",
    "language": "en",
    "language_confidence": 1.0,
    "flags": [],
    "categories": {
      "profanity": false,
      "hate_speech": false,
      "spam": false,
      "violence": false
    }
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `is_safe` | boolean | False when any moderation category is triggered. True otherwise. |
| `toxicity_score` | number or null | Reserved for future use. Currently always null. |
| `sentiment` | string | Detected sentiment: positive, negative, or neutral |
| `language` | string or null | Detected or provided ISO 639-1 language code. Null when detection confidence is 0. |
| `language_confidence` | number or null | Confidence in the detected language from 0.0 to 1.0. 1.0 when language was explicitly provided. |
| `flags` | array | Triggered moderation flags. Currently possible: text_profanity |
| `categories` | object | Per-category boolean flags: profanity, hate_speech, spam, violence |

## Errors

- `undefined` **422** — text field is missing or empty
- `undefined` **401** — Missing or invalid API key
