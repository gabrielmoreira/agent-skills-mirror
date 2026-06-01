---
name: counter-post-{namespace}
api: Counter
method: POST
path: /v1/technology/counter/{namespace}
base_url: https://api.requiems.xyz
description: Atomically increment a counter in the specified namespace and return the new value
---

## Endpoint

**POST https://api.requiems.xyz/v1/technology/counter/{namespace}**

## Increment Counter

Atomically increment a counter in the specified namespace and return the new
value

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

| Field       | Type    | Description                           |
| ----------- | ------- | ------------------------------------- |
| `namespace` | string  | The counter namespace                 |
| `value`     | integer | The new counter value after increment |

## Errors

- `undefined` **400** — Invalid namespace: must be 1–64 chars, alphanumeric,
  hyphen or underscore only
- `undefined` **500** — Internal server error
