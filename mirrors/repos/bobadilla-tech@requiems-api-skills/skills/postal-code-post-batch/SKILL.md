---
name: postal-code-post-batch
api: Postal Code
method: POST
path: /v1/places/postal/batch
base_url: https://api.requiems.xyz
description: Look up city, state, and coordinates for up to 50 postal codes in a single request. Results are returned in input order.
---

## Endpoint

**POST https://api.requiems.xyz/v1/places/postal/batch**

## Batch Lookup Postal Codes

Look up city, state, and coordinates for up to 50 postal codes in a single request. Results are returned in input order.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `items` | array of objects | yes | body | List of postal code lookups (1–50 items). |
| `items[].code` | string | yes | body | The postal code to look up. |
| `items[].country` | string | no | body | ISO 3166-1 alpha-2 country code (default: US). |

## Request Example

```json
{
  "items": [
    { "code": "10001", "country": "US" },
    { "code": "SW1A1AA", "country": "GB" }
  ]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "code": "10001", "country": "US", "found": true,
        "result": { "postal_code": "10001", "city": "New York City", "state": "New York", "country": "US", "lat": 40.7484, "lon": -73.9967 }
      },
      {
        "code": "SW1A1AA", "country": "GB", "found": true,
        "result": { "postal_code": "SW1A 1AA", "city": "London", "state": "England", "country": "GB", "lat": 51.5010, "lon": -0.1247 }
      }
    ],
    "total": 2
  },
  "metadata": { "timestamp": "2026-01-01T00:00:00Z" }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | Per-item results in input order. |
| `results[].code` | string | The postal code as provided in the request. |
| `results[].country` | string | The country code used for the lookup (defaulted to US when omitted). |
| `results[].found` | boolean | Whether the postal code was found in the dataset. |
| `results[].result` | object | Postal code details (omitted when found is false). |
| `total` | integer | Total number of items processed. |

## Errors

- `422` **validation_failed** — The items array is missing, empty, or exceeds 50 items.
- `400` **bad_request** — The request body is missing or malformed.
