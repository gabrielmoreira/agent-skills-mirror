---
name: fitness-exercises-post-batch
api: Fitness Exercises
method: POST
path: /v1/health/exercises/batch
base_url: https://api.requiems.xyz
description: Fetches up to 50 exercises by their numeric IDs in a single request. IDs that do not exist are silently skipped. Results are returned in the same order as the input array.
---

## Endpoint

**POST https://api.requiems.xyz/v1/health/exercises/batch**

## Batch Get Exercises

Fetches up to 50 exercises by their numeric IDs in a single request. IDs that do not exist are silently skipped. Results are returned in the same order as the input array.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `ids` | array | yes | body | Array of numeric exercise IDs to fetch. Must contain between 1 and 50 items. Each ID must be a positive integer. |

## Request Example

```json
{
  "ids": [1, 7, 42]
}
```

## Response Example

```json
{
  "data": {
    "results": [
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
      },
      {
        "id": 7,
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
      }
    ],
    "total": 2
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | Exercises found for the given IDs, in input order. IDs not found are omitted. |
| `results[].id` | integer | Unique exercise identifier |
| `results[].name` | string | Exercise name |
| `results[].body_parts` | array | Body part categories involved |
| `results[].equipment` | array | Equipment required |
| `results[].target_muscles` | array | Primary muscles targeted |
| `results[].secondary_muscles` | array | Secondary muscles engaged |
| `results[].instructions` | array | Ordered step-by-step instructions |
| `total` | integer | Number of exercises returned |

## Errors

- `400` **bad_request** — The request body is missing or not valid JSON.
- `422` **validation_failed** — The ids array is empty, exceeds 50 items, or contains a non-positive integer.
