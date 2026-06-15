---
name: phone-validation-post-batch
api: Phone Validation
method: POST
path: /v1/validation/phone/batch
base_url: https://api.requiems.xyz
description: Validates up to 50 phone numbers in a single request. Results are returned in the same order as the input.
---

## Endpoint

**POST https://api.requiems.xyz/v1/validation/phone/batch**

## Batch Validate Phone Numbers

Validates up to 50 phone numbers in a single request. Results are returned in the same order as the input.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `numbers` | array | yes | body | Array of phone numbers to validate (min: 1, max: 50). Each must include the country calling code. |

## Request Example

```json
{
  "numbers": ["+447400123456", "+12015551234", "12345"]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "number": "+447400123456",
        "valid": true,
        "country": "GB",
        "type": "mobile",
        "formatted": "+44 7400 123456",
        "carrier": { "name": "Three", "source": "metadata" },
        "risk": { "is_voip": false, "is_virtual": false }
      },
      {
        "number": "+12015551234",
        "valid": true,
        "country": "US",
        "type": "landline_or_mobile",
        "formatted": "+1 201-555-1234",
        "risk": { "is_voip": false, "is_virtual": false }
      },
      {
        "number": "12345",
        "valid": false
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
| `results` | array | Validation result for each number in the same order as the input. Each item has the same fields as the single validate endpoint. |
| `total` | integer | Number of results returned. Matches the length of the input array. |

## Errors

- `422` **validation_failed** — The numbers array is missing, empty, or contains more than 50 items.
