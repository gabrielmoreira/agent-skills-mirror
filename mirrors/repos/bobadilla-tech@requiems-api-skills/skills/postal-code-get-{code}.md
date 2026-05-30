---
name: postal-code-get-{code}
api: Postal Code
method: GET
path: /v1/places/postal/{code}
base_url: https://api.requiems.xyz
description: Returns city, state, country, and coordinates for the given postal code.
---

## Endpoint

**GET https://api.requiems.xyz/v1/places/postal/{code}**

## Lookup Postal Code

Returns city, state, country, and coordinates for the given postal code.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `code` | string | yes | path | The postal code to look up (e.g. 10001 for New York, SW1A 1AA for London) |
| `country` | string | no | query | ISO 3166-1 alpha-2 country code (default: US) |

## Response Example

```json
{
  "data": {
    "postal_code": "10001",
    "city": "New York City",
    "state": "New York",
    "country": "US",
    "lat": 40.7484,
    "lon": -73.9967
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `postal_code` | string | The postal code as stored in the dataset |
| `city` | string | Primary city or place name for the postal code |
| `state` | string | State, province, or administrative region name |
| `country` | string | ISO 3166-1 alpha-2 country code (uppercase) |
| `lat` | number | Latitude of the postal code centroid |
| `lon` | number | Longitude of the postal code centroid |

## Errors

- `404` **not_found** — The postal code was not found for the given country.
- `500` **internal_error** — Unexpected server error.
