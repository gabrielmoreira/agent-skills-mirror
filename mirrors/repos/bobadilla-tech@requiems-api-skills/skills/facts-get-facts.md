---
name: facts-get-facts
api: Random Facts
method: GET
path: /v1/entertainment/facts
base_url: https://api.requiems.xyz
description: Returns a randomly selected fact, optionally filtered by category.
---

## Endpoint

**GET https://api.requiems.xyz/v1/entertainment/facts**

## Get Random Fact

Returns a randomly selected fact, optionally filtered by category.

## Parameters

| Name       | Type   | Required | Location | Description                                                                         |
| ---------- | ------ | -------- | -------- | ----------------------------------------------------------------------------------- |
| `category` | string | no       | query    | Filter by category. Valid values: science, history, technology, nature, space, food |

## Response Example

```json
{
  "data": {
    "fact": "Honey never spoils. Archaeologists have found 3,000-year-old honey in Egyptian tombs that was still perfectly edible.",
    "category": "science",
    "source": "National Geographic"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field      | Type   | Description                                         |
| ---------- | ------ | --------------------------------------------------- |
| `fact`     | string | The fact text                                       |
| `category` | string | The category the fact belongs to                    |
| `source`   | string | The source or publication the fact is attributed to |

## Errors

- `undefined` **400** — undefined
