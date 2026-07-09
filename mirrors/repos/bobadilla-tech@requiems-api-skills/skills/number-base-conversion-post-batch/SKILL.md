---
name: number-base-conversion-post-batch
api: Number Base Conversion
method: POST
path: /v1/technology/base/batch
base_url: https://api.requiems.xyz
description: Convert up to 50 numbers between bases in a single request. Results are returned in input order. Per-item errors are reported inline.
---

## Endpoint

**POST https://api.requiems.xyz/v1/technology/base/batch**

## Batch Convert Base

Convert up to 50 numbers between bases in a single request. Results are returned in input order. Per-item errors are reported inline.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `items` | array of objects | yes | body | List of conversion requests (1–50 items). |
| `items[].from` | integer | yes | body | Source base (2, 8, 10, or 16). |
| `items[].to` | integer | yes | body | Target base (2, 8, 10, or 16). |
| `items[].value` | string | yes | body | The number as a string. Accepts optional prefixes: 0x (hex), 0b (binary), 0o (octal). |

## Request Example

```json
{
  "items": [
    { "from": 10, "to": 16, "value": "255" },
    { "from": 2,  "to": 10, "value": "1111" }
  ]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      { "from": 10, "to": 16, "input": "255",  "result": "ff" },
      { "from": 2,  "to": 10, "input": "1111", "result": "15" }
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
| `results[].from` | integer | The source base used for conversion. |
| `results[].to` | integer | The target base used for conversion. |
| `results[].input` | string | The original value as provided in the request. |
| `results[].result` | string | The converted value in the target base (omitted on error). |
| `results[].error` | string | Error message if this item failed (omitted on success). |
| `total` | integer | Total number of items processed. |

## Errors

- `422` **validation_failed** — The items array is missing, empty, or exceeds 50 items.
- `400` **bad_request** — The request body is missing or malformed.
