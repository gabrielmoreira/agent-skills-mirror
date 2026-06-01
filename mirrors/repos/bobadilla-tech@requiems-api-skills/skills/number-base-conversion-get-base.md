---
name: number-base-conversion-get-base
api: Number Base Conversion
method: GET
path: /v1/technology/base
base_url: https://api.requiems.xyz
description: Convert an integer from one number base to another.
---

## Endpoint

**GET https://api.requiems.xyz/v1/technology/base**

## Convert Base

Convert an integer from one number base to another.

## Parameters

| Name    | Type    | Required | Location | Description                                                                           |
| ------- | ------- | -------- | -------- | ------------------------------------------------------------------------------------- |
| `from`  | integer | yes      | query    | Source base (2, 8, 10, or 16)                                                         |
| `to`    | integer | yes      | query    | Target base (2, 8, 10, or 16)                                                         |
| `value` | string  | yes      | query    | The number as a string. Accepts optional prefixes: 0x (hex), 0b (binary), 0o (octal). |

## Response Example

```json
{
  "data": {
    "input": "255",
    "from": 10,
    "to": 16,
    "result": "ff"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field    | Type    | Description                                   |
| -------- | ------- | --------------------------------------------- |
| `input`  | string  | The original value as provided in the request |
| `from`   | integer | The source base                               |
| `to`     | integer | The target base                               |
| `result` | string  | The converted value in the target base        |

## Errors

- `400` **bad_request** — A required parameter is missing, the base is not one
  of 2/8/10/16, or value is not valid for the given base.
