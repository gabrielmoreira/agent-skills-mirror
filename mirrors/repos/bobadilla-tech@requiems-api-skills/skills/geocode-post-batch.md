---
name: geocode-post-batch
api: Geocoding
method: POST
path: /v1/places/reverse-geocode/batch
base_url: https://api.requiems.xyz
description: Convert up to 20 coordinate pairs to addresses in a single request. Processed concurrently; results are returned in input order. Per-item errors are reported inline.
---

## Endpoint

**POST https://api.requiems.xyz/v1/places/reverse-geocode/batch**

## Batch Reverse Geocode

Convert up to 20 coordinate pairs to addresses in a single request. Processed concurrently; results are returned in input order. Per-item errors are reported inline.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `items` | array of objects | yes | body | List of coordinate pairs to reverse-geocode (1–20 items). Max 20 due to Nominatim usage policy. |
| `items[].lat` | number | yes | body | Latitude (-90 to 90). |
| `items[].lon` | number | yes | body | Longitude (-180 to 180). |

## Request Example

```json
{
  "items": [
    { "lat": 38.8977, "lon": -77.0365 },
    { "lat": 48.8584, "lon": 2.2945 }
  ]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "lat": 38.8977, "lon": -77.0365,
        "result": { "lat": 38.8977, "lon": -77.0365, "address": "White House, 1600, Pennsylvania Avenue Northwest...", "city": "Washington", "country": "US" }
      },
      {
        "lat": 48.8584, "lon": 2.2945,
        "result": { "lat": 48.8584, "lon": 2.2945, "address": "Tour Eiffel, 5, Avenue Anatole France, Paris...", "city": "Paris", "country": "FR" }
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
| `results[].lat` | number | Latitude as provided in the request. |
| `results[].lon` | number | Longitude as provided in the request. |
| `results[].result` | object | Reverse geocoding result (omitted on error). Same fields as the single-item endpoint. |
| `results[].error` | string | Error message if reverse geocoding failed (omitted on success). |
| `total` | integer | Total number of items processed. |

## Errors

- `422` **validation_failed** — The items array is missing, empty, or exceeds 20 items.
- `400` **bad_request** — The request body is missing or malformed.
