---
name: fitness-exercises-get-exercises
api: Fitness Exercises
method: GET
path: /v1/health/exercises
base_url: https://api.requiems.xyz
description: Returns a paginated list of exercises. All filter parameters are optional and combinable.
---

## Endpoint

**GET https://api.requiems.xyz/v1/health/exercises**

## List Exercises

Returns a paginated list of exercises. All filter parameters are optional and combinable.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `body_part` | string | no | query | Filter by body part (e.g. chest, back, upper legs). Use /v1/health/body-parts for valid values. |
| `equipment` | string | no | query | Filter by equipment type (e.g. barbell, dumbbell, body weight). Use /v1/health/equipment for valid values. |
| `muscle` | string | no | query | Filter by target or secondary muscle (e.g. biceps, glutes). Use /v1/health/muscles for valid values. |
| `search` | string | no | query | Full-text search on exercise name. |
| `page` | integer | no | query | Page number (default: 1) |
| `per_page` | integer | no | query | Results per page, 1–100 (default: 20) |

## Response Example

```json
{
  "data": {
    "items": [
      {
        "id": 1,
        "name": "barbell bench press",
        "body_parts": ["chest"],
        "equipment": ["barbell"],
        "target_muscles": ["pectorals"],
        "secondary_muscles": ["triceps", "deltoids"],
        "instructions": [
          "Lie flat on a bench and grip the barbell slightly wider than shoulder-width.",
          "Lower the bar to your chest under control.",
          "Press the bar back up to full arm extension.",
          "Repeat for the desired number of repetitions."
        ]
      }
    ],
    "total": 312,
    "page": 1,
    "per_page": 20
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `items` | array | Array of exercise objects for the current page |
| `items[].id` | integer | Unique exercise identifier |
| `items[].name` | string | Exercise name |
| `items[].body_parts` | array | Body part categories involved |
| `items[].equipment` | array | Equipment required |
| `items[].target_muscles` | array | Primary muscles targeted |
| `items[].secondary_muscles` | array | Secondary muscles engaged |
| `items[].instructions` | array | Ordered step-by-step instructions |
| `total` | integer | Total number of exercises matching the filters |
| `page` | integer | Current page number |
| `per_page` | integer | Number of results per page |

## Errors

- `400` **bad_request** — A query parameter has an invalid value (e.g. per_page out of range).
- `500` **internal_error** — Unexpected server error.
