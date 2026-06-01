---
name: sentiment-post-sentiment
api: Sentiment Analysis
method: POST
path: /v1/text/sentiment
base_url: https://api.requiems.xyz
description: Analyzes the sentiment of the provided text and returns a classification, confidence score, and a full breakdown across all three sentiment classes.
---

## Endpoint

**POST https://api.requiems.xyz/v1/text/sentiment**

## Analyze Sentiment

Analyzes the sentiment of the provided text and returns a classification,
confidence score, and a full breakdown across all three sentiment classes.

## Parameters

| Name   | Type   | Required | Location | Description          |
| ------ | ------ | -------- | -------- | -------------------- |
| `text` | string | yes      | body     | The text to analyze. |

## Request Example

```json
{
  "text": "I absolutely love this product, it exceeded my expectations!"
}
```

## Response Example

```json
{
  "data": {
    "sentiment": "positive",
    "score": 0.97,
    "breakdown": {
      "positive": 0.97,
      "negative": 0.01,
      "neutral": 0.02
    }
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field                | Type   | Description                                                                |
| -------------------- | ------ | -------------------------------------------------------------------------- |
| `sentiment`          | string | The dominant sentiment class: positive, negative, or neutral               |
| `score`              | number | Confidence score for the dominant sentiment, between 0.0 and 1.0           |
| `breakdown.positive` | number | Proportional score for positive sentiment (sums to 1.0 with other classes) |
| `breakdown.negative` | number | Proportional score for negative sentiment (sums to 1.0 with other classes) |
| `breakdown.neutral`  | number | Proportional score for neutral sentiment (sums to 1.0 with other classes)  |

## Errors

- `undefined` **422** — undefined
