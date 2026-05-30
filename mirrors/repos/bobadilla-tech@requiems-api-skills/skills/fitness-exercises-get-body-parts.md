---
name: fitness-exercises-get-body-parts
api: Fitness Exercises
method: GET
path: /v1/health/body-parts
base_url: https://api.requiems.xyz
description: Returns a sorted list of all distinct body part values present in the dataset. Use these as valid values for the body_part filter.
---

## Endpoint

**GET https://api.requiems.xyz/v1/health/body-parts**

## List Body Parts

Returns a sorted list of all distinct body part values present in the dataset. Use these as valid values for the body_part filter.

## Response Example

```json
{
  "data": {
    "items": ["back", "cardio", "chest", "lower arms", "lower legs", "neck", "shoulders", "upper arms", "upper legs", "waist"],
    "total": 10
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `items` | array | Sorted list of all distinct body part names |
| `total` | integer | Total number of distinct body parts |

## Errors

- `500` **internal_error** — Unexpected server error.
