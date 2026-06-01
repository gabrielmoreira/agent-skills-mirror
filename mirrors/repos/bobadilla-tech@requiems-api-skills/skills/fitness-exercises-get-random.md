---
name: fitness-exercises-get-random
api: Fitness Exercises
method: GET
path: /v1/health/exercises/random
base_url: https://api.requiems.xyz
description: Returns a single randomly selected exercise. Accepts the same filter parameters as the list endpoint, so you can get a random chest exercise, a random bodyweight exercise, etc.
---

## Endpoint

**GET https://api.requiems.xyz/v1/health/exercises/random**

## Random Exercise

Returns a single randomly selected exercise. Accepts the same filter parameters
as the list endpoint, so you can get a random chest exercise, a random
bodyweight exercise, etc.

## Parameters

| Name        | Type   | Required | Location | Description                                                       |
| ----------- | ------ | -------- | -------- | ----------------------------------------------------------------- |
| `body_part` | string | no       | query    | Restrict random selection to this body part.                      |
| `equipment` | string | no       | query    | Restrict random selection to this equipment type.                 |
| `muscle`    | string | no       | query    | Restrict random selection to exercises targeting this muscle.     |
| `search`    | string | no       | query    | Restrict random selection to exercises matching this search term. |

## Response Example

```json
{
  "data": {
    "id": 42,
    "name": "dumbbell curl",
    "body_parts": ["upper arms"],
    "equipment": ["dumbbell"],
    "target_muscles": ["biceps"],
    "secondary_muscles": ["brachialis"],
    "instructions": [
      "Stand with a dumbbell in each hand, arms fully extended.",
      "Curl the weights toward your shoulders, keeping your elbows close to your torso.",
      "Squeeze at the top, then lower the weights slowly.",
      "Repeat for the desired number of repetitions."
    ]
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Errors

- `404` **not_found** — No exercises match the given filters.
- `500` **internal_error** — Unexpected server error.
