---
name: chuck-norris-get-chuck-norris
api: Chuck Norris Facts
method: GET
path: /v1/entertainment/chuck-norris
base_url: https://api.requiems.xyz
description: Returns a randomly selected Chuck Norris fact from the built-in database.
---

## Endpoint

**GET https://api.requiems.xyz/v1/entertainment/chuck-norris**

## Get Random Chuck Norris Fact

Returns a randomly selected Chuck Norris fact from the built-in database.

## Response Example

```json
{
  "data": {
    "id": "cn_0",
    "fact": "Chuck Norris can divide by zero."
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `id` | string | Unique fact identifier in the format cn_<index> (e.g. cn_0, cn_7) |
| `fact` | string | The Chuck Norris fact text |
