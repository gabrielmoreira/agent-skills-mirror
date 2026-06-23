---
name: data-integrity-post-batch
api: Data Integrity System
method: POST
path: /v1/systems/input/validate/batch
base_url: https://api.requiems.xyz
description: Validates and scores a batch of up to 50 contact records in a single request. Each record is processed independently — one item failing does not affect others. Returns per-item email, phone, and text validation results with quality scores, normalized values, plus batch-level aggregates including total, valid_count, invalid_count, and average_quality_score.
---

## Endpoint

**POST https://api.requiems.xyz/v1/systems/input/validate/batch**

## Batch Input Validate

Validates and scores a batch of up to 50 contact records in a single request. Each record is processed independently — one item failing does not affect others. Returns per-item email, phone, and text validation results with quality scores, normalized values, plus batch-level aggregates including total, valid_count, invalid_count, and average_quality_score.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `items` | array | yes | body | Array of contact records to validate. Each item must include email and phone. Text is optional. Min: 1, Max: 50. |

## Response Example

```json
{
  "data": {
    "results": [
      {
        "index": 0,
        "email": {
          "valid": true,
          "normalized": "alice@example.com",
          "quality_score": 1,
          "disposable": false
        },
        "phone": {
          "valid": true,
          "normalized": "+1 415-555-0001",
          "quality_score": 1
        },
          "text": null,
          "overall_quality_score": 1,
          "error": null
        },
        {
        "index": 1,
        "email": {
          "valid": true,
          "normalized": "bob@example.com",
          "quality_score": 1,
          "disposable": false
        },
        "phone": {
          "valid": true,
          "normalized": "+1 415-555-0002",
          "quality_score": 1
        },
        "text": null,
        "overall_quality_score": 1,
        "error": null
      }
    ],
    "total": 2,
    "valid_count": 2,
    "invalid_count": 0,
    "average_quality_score": 1
  },
  "metadata": {
    "timestamp": "2026-06-16T21:28:14Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | List of validation results, one per input item. Preserves the original submission order via the index field. |
| `results[].index` | integer | Zero-based position of the item in the original request array. |
| `results[].email` | object or null | Email validation result. Null when email was not provided for this item. |
| `results[].email.valid` | boolean | True when the email passes syntax and MX validation. |
| `results[].email.normalized` | string or null | Normalized form of the email address. Null when syntax is invalid. |
| `results[].email.quality_score` | number | Email quality score from 0.0 to 1.0. Penalized by invalidity, disposable domain, and suggestions. |
| `results[].email.disposable` | boolean | True when the email domain is a known disposable or temporary provider. |
| `results[].phone` | object or null | Phone validation result. Null when phone was not provided for this item. |
| `results[].phone.valid` | boolean | True when the phone number is valid and dialable. |
| `results[].phone.normalized` | string or null | Normalized phone number in international format. Null when the number is invalid. |
| `results[].phone.quality_score` | number | Phone quality score from 0.0 to 1.0. Penalized by invalidity, VoIP, virtual, landline, and unknown type. |
| `results[].text` | object or null | Text analysis result. Null when text was not provided for this item. |
| `results[].overall_quality_score` | number | Weighted quality score from 0.0 to 1.0 combining email and phone fields only. Weights are email 0.5 and phone 0.4, adjusted proportionally when one field is absent. Text does not currently contribute to this score — scoring will be enabled once toxicity_score is available from the sentiment service. Returns 0.0 when only text is provided. |
| `results[].error` | string or null | Error message when this item could not be processed due to an unexpected failure, such as a service timeout or malformed input. Null when the item was processed successfully, regardless of whether the fields passed validation or not. |
| `total` | integer | Total number of items in the batch. |
| `valid_count` | integer | Number of items where all provided fields have valid set to true. |
| `invalid_count` | integer | Number of items where at least one provided field has valid set to false, or where processing failed due to a timeout or unexpected error. |
| `average_quality_score` | number | Average of overall_quality_score across all successfully processed items. Items that failed due to a timeout or unexpected error are excluded from this average. |

## Errors

- `undefined` **422** — The request body is invalid.
- `undefined` **401** — Missing or invalid API key.
