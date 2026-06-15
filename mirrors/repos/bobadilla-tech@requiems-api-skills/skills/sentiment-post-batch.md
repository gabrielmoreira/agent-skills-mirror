---
name: sentiment-post-batch
api: Sentiment Analysis
method: POST
path: /v1/text/sentiment/batch
base_url: https://api.requiems.xyz
description: Analyzes the sentiment of up to 50 texts in a single request. Results are returned in the same order as the input. Each text counts as one unit of usage.
---

## Endpoint

**POST https://api.requiems.xyz/v1/text/sentiment/batch**

## Analyze Sentiment (Batch)

Analyzes the sentiment of up to 50 texts in a single request. Results are returned in the same order as the input. Each text counts as one unit of usage.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `texts` | array | yes | body | The list of texts to analyze. Between 1 and 50 items. |

## Request Example

```json
{
  "texts": [
    "I love this product! It's absolutely amazing.",
    "This is terrible. I hate it.",
    "The document is on the table."
  ]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "sentiment": "positive",
        "score": 0.91,
        "breakdown": { "positive": 0.91, "negative": 0.02, "neutral": 0.07 }
      },
      {
        "sentiment": "negative",
        "score": 0.88,
        "breakdown": { "positive": 0.03, "negative": 0.88, "neutral": 0.09 }
      },
      {
        "sentiment": "neutral",
        "score": 1.0,
        "breakdown": { "positive": 0.0, "negative": 0.0, "neutral": 1.0 }
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

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | Sentiment results for each input text, in the same order as the input. |
| `results[].sentiment` | string | The dominant sentiment class: positive, negative, or neutral |
| `results[].score` | number | Confidence score for the dominant sentiment, between 0.0 and 1.0 |
| `results[].breakdown.positive` | number | Proportional score for positive sentiment (sums to 1.0 with other classes) |
| `results[].breakdown.negative` | number | Proportional score for negative sentiment (sums to 1.0 with other classes) |
| `results[].breakdown.neutral` | number | Proportional score for neutral sentiment (sums to 1.0 with other classes) |
| `total` | number | Total number of results returned. |

## Errors

- `undefined` **400** — undefined
- `undefined` **422** — undefined
