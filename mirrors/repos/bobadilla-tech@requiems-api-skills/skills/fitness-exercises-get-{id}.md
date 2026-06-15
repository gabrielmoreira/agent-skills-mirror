---
name: fitness-exercises-get-{id}
api: Fitness Exercises
method: GET
path: /v1/health/exercises/{id}
base_url: https://api.requiems.xyz
description: Returns a single exercise by its numeric ID.
---

## Endpoint

**GET https://api.requiems.xyz/v1/health/exercises/{id}**

## Exercise by ID

Returns a single exercise by its numeric ID.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `id` | integer | yes | path | Numeric exercise ID |

## Response Example

```json
{
  "data": {
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
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `id` | integer | Unique exercise identifier |
| `name` | string | Exercise name |
| `body_parts` | array | Body part categories involved |
| `equipment` | array | Equipment required |
| `target_muscles` | array | Primary muscles targeted |
| `secondary_muscles` | array | Secondary muscles engaged |
| `instructions` | array | Ordered step-by-step instructions |

## Errors

- `400` **bad_request** — The id parameter is not a positive integer.
- `404` **not_found** — No exercise exists with the given ID.
- `500` **internal_error** — Unexpected server error.
