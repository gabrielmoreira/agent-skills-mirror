---
name: fitness-exercises-get-muscles
api: Fitness Exercises
method: GET
path: /v1/health/muscles
base_url: https://requiems.xyz
description: Returns a sorted list of all distinct muscle names (combining target and secondary muscles). Use these as valid values for the muscle filter.
---

## Endpoint

**GET https://requiems.xyz/v1/health/muscles**

## List Muscles

Returns a sorted list of all distinct muscle names (combining target and secondary muscles). Use these as valid values for the muscle filter.

## Response Example

```json
{
  "data": {
    "items": ["biceps", "calves", "deltoids", "glutes", "hamstrings", "lats", "pectorals", "quadriceps", "traps", "triceps"],
    "total": 51
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `items` | array<string> | Sorted list of all distinct muscle names |
| `total` | integer | Total number of distinct muscles |

## Errors

- `500` **internal_error** — Unexpected server error.
