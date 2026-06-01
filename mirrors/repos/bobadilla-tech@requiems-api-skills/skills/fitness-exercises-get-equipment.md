---
name: fitness-exercises-get-equipment
api: Fitness Exercises
method: GET
path: /v1/health/equipment
base_url: https://api.requiems.xyz
description: Returns a sorted list of all distinct equipment types. Use these as valid values for the equipment filter.
---

## Endpoint

**GET https://api.requiems.xyz/v1/health/equipment**

## List Equipment

Returns a sorted list of all distinct equipment types. Use these as valid values
for the equipment filter.

## Response Example

```json
{
  "data": {
    "items": [
      "band",
      "barbell",
      "body weight",
      "cable",
      "dumbbell",
      "ez barbell",
      "kettlebell",
      "medicine ball",
      "stability ball",
      "tire"
    ],
    "total": 28
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field   | Type    | Description                                 |
| ------- | ------- | ------------------------------------------- |
| `items` | array   | Sorted list of all distinct equipment names |
| `total` | integer | Total number of distinct equipment types    |

## Errors

- `500` **internal_error** — Unexpected server error.
