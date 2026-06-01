---
name: counter-get-{namespace}
api: Counter
method: GET
path: /v1/technology/counter/{namespace}
base_url: https://api.requiems.xyz
description: Get the current value of a counter without incrementing it
---

## Endpoint

**GET https://api.requiems.xyz/v1/technology/counter/{namespace}**

## Get Counter Value

Get the current value of a counter without incrementing it

## Parameters

| Name        | Type   | Required | Location | Description                                                      |
| ----------- | ------ | -------- | -------- | ---------------------------------------------------------------- |
| `namespace` | string | yes      | path     | Counter namespace (1-64 chars: alphanumeric, hyphen, underscore) |

## Response Example

```json
{
  "data": {
    "namespace": "page-views",
    "value": 42
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field       | Type    | Description                                                    |
| ----------- | ------- | -------------------------------------------------------------- |
| `namespace` | string  | The counter namespace                                          |
| `value`     | integer | The current counter value (returns 0 if counter doesn't exist) |

## Errors

- `undefined` **400** — Invalid namespace: must be 1–64 chars, alphanumeric,
  hyphen or underscore only
- `undefined` **500** — Internal server error
