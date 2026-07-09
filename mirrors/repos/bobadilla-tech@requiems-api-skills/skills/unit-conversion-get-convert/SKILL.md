---
name: unit-conversion-get-convert
api: Unit Conversion
method: GET
path: /v1/technology/convert
base_url: https://api.requiems.xyz
description: Convert a value from one unit to another
---

## Endpoint

**GET https://api.requiems.xyz/v1/technology/convert**

## Convert Units

Convert a value from one unit to another

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `from` | string | yes | query | Source unit key (e.g. miles, kg, c) |
| `to` | string | yes | query | Target unit key (e.g. km, lb, f) |
| `value` | number | yes | query | Numeric value to convert |

## Response Example

```json
{
  "data": {
    "from": "miles",
    "to": "km",
    "input": 10,
    "result": 16.09344,
    "formula": "miles × 1.609344"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `from` | string | Source unit key |
| `to` | string | Target unit key |
| `input` | number | The original input value |
| `result` | number | The converted value (rounded to 6 decimal places) |
| `formula` | string | Human-readable conversion formula |
