---
name: password-generator-post-batch
api: Password Generator
method: POST
path: /v1/technology/password/batch
base_url: https://api.requiems.xyz
description: Generate up to 50 passwords in a single request. Each item can have its own length and character set options. Results are returned in input order.
---

## Endpoint

**POST https://api.requiems.xyz/v1/technology/password/batch**

## Batch Generate Passwords

Generate up to 50 passwords in a single request. Each item can have its own length and character set options. Results are returned in input order.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `items` | array of objects | yes | body | List of password generation requests (1–50 items). |
| `items[].length` | integer | no | body | Password length (8–128). Defaults to 16 when omitted. |
| `items[].uppercase` | boolean | no | body | Include uppercase letters (A–Z). Defaults to false. |
| `items[].numbers` | boolean | no | body | Include numbers (0–9). Defaults to false. |
| `items[].symbols` | boolean | no | body | Include special characters. Defaults to false. |

## Request Example

```json
{
  "items": [
    { "length": 16, "uppercase": true, "numbers": true, "symbols": true },
    { "length": 12 }
  ]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      { "result": { "password": "aB3#cDeFgHiJkLmN", "length": 16, "strength": "strong" } },
      { "result": { "password": "abcdefghijkl",     "length": 12, "strength": "weak"   } }
    ],
    "total": 2
  },
  "metadata": { "timestamp": "2026-01-01T00:00:00Z" }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | Per-item results in input order. |
| `results[].result.password` | string | The generated password (omitted on error). |
| `results[].result.length` | integer | Length of the generated password. |
| `results[].result.strength` | string | Strength assessment (weak, medium, or strong). |
| `results[].error` | string | Error message if generation failed (omitted on success). |
| `total` | integer | Total number of items processed. |

## Errors

- `422` **validation_failed** — The items array is missing, empty, or exceeds 50 items.
- `400` **bad_request** — The request body is missing or malformed.
