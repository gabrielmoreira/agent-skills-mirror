---
name: unit-conversion-post-batch
api: Unit Conversion
method: POST
path: /v1/technology/convert/batch
base_url: https://api.requiems.xyz
description: convert up to 50 unit conversion operations in a single request.
---

## Endpoint

**POST https://api.requiems.xyz/v1/technology/convert/batch**

## Batch Convert Units

convert up to 50 unit conversion operations in a single request.

## Parameters

| Name         | Type  | Required | Location | Description                                       |
| ------------ | ----- | -------- | -------- | ------------------------------------------------- |
| `operations` | array | yes      | body     | Array of operations to convert (min: 1, max: 50). |

## Request Example

```json
{
  "operations": [
    {
      "from": "kg",
      "to": "lb",
      "value": 10
    },
    {
      "from": "c",
      "to": "f",
      "value": 5
    }
  ]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "from": "kg",
        "to": "lb",
        "success": true,
        "data": {
          "from": "kg",
          "to": "lb",
          "input": 10,
          "result": 22.046244,
          "formula": "kg × 2.204624"
        }
      },
      {
        "from": "c",
        "to": "f",
        "success": true,
        "data": {
          "from": "c",
          "to": "f",
          "input": 5,
          "result": 41,
          "formula": "°C × 9/5 + 32"
        }
      }
    ],
    "total": 2
  },
  "metadata": {
    "timestamp": "2026-05-15T21:52:05Z"
  }
}
```

## Response Fields

| Field                    | Type    | Description                                                                         |
| ------------------------ | ------- | ----------------------------------------------------------------------------------- |
| `results`                | array   | List of unit conversion results returned in the same order as the input operations. |
| `results[].from`         | string  | Source unit used for the conversion.                                                |
| `results[].to`           | string  | Target unit used for the conversion.                                                |
| `results[].success`      | boolean | Indicates whether the conversion operation was successful.                          |
| `results[].error`        | string  | Error message if the conversion failed. Empty when success is true.                 |
| `results[].data`         | object  | Conversion result details. Contains empty values when the conversion fails.         |
| `results[].data.from`    | string  | Source unit.                                                                        |
| `results[].data.to`      | string  | Target unit.                                                                        |
| `results[].data.input`   | number  | Original numeric value provided for conversion.                                     |
| `results[].data.result`  | number  | Converted numeric result.                                                           |
| `results[].data.formula` | string  | Formula or conversion factor used to calculate the result.                          |
| `total`                  | integer | Total number of conversion results returned.                                        |

## Errors

- `422` **validation_failed** — The operations array is missing, empty, or
  contains more than 50 items.
- `400` **bad_request** — Invalid JSON, malformed request body, or unexpected
  field types.
