---
name: iban-post-batch
api: IBAN Validator
method: POST
path: /v1/finance/iban/batch
base_url: https://api.requiems.xyz
description: Validates up to 50 iban numbers in a single request. Results are returned in the same order as the input.
---

## Endpoint

**POST https://api.requiems.xyz/v1/finance/iban/batch**

## Batch Validate IBANs

Validates up to 50 iban numbers in a single request. Results are returned in the same order as the input.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `numbers` | array | yes | body | Array of iban numbers to validate (min: 1, max: 50). |

## Request Example

```json
{
  "numbers": ["GB29NWBK60161331926819", "DE89370400440532013000", "XX89370400440532013000"]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "iban": "GB29NWBK60161331926819",
        "valid": true,
        "country": "United Kingdom",
        "bank_code": "NWBK",
        "account": "31926819"
      },
      {
        "iban": "DE89370400440532013000",
        "valid": true,
        "country": "Germany",
        "bank_code": "37040044",
        "account": "0532013000"
      },
      {
        "iban": "XX89370400440532013000",
        "valid": false,
        "country": "",
        "bank_code": "",
        "account": ""
      }
    ],
    "total": 3
  },
  "metadata": {
    "timestamp": "2026-05-03T19:25:02Z"
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
