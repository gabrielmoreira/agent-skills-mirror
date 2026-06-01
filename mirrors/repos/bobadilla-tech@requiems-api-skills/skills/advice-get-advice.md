---
name: advice-get-advice
api: Random Advice
method: GET
path: /v1/text/advice
base_url: https://api.requiems.xyz
description: Returns a random piece of advice
---

## Endpoint

**GET https://api.requiems.xyz/v1/text/advice**

## Get Random Advice

Returns a random piece of advice

## Response Example

```json
{
  "data": {
    "id": 42,
    "advice": "Don't compare yourself to others. Compare yourself to the person you were yesterday."
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field    | Type    | Description                      |
| -------- | ------- | -------------------------------- |
| `id`     | integer | Unique identifier for the advice |
| `advice` | string  | A random piece of advice         |
