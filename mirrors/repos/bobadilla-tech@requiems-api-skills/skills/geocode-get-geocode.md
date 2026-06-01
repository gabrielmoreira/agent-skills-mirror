---
name: geocode-get-geocode
api: Geocoding
method: GET
path: /v1/places/geocode
base_url: https://api.requiems.xyz
description: Converts a free-text address into latitude and longitude coordinates.
---

## Endpoint

**GET https://api.requiems.xyz/v1/places/geocode**

## Geocode Address

Converts a free-text address into latitude and longitude coordinates.

## Parameters

| Name      | Type   | Required | Location | Description                                                        |
| --------- | ------ | -------- | -------- | ------------------------------------------------------------------ |
| `address` | string | yes      | query    | The address to geocode (street, city, country, or any combination) |

## Response Example

```json
{
  "data": {
    "address": "White House, 1600, Pennsylvania Avenue Northwest, Ward 2, Washington, District of Columbia, 20500, United States",
    "city": "Washington",
    "country": "US",
    "lat": 38.8976763,
    "lon": -77.0365298
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field     | Type   | Description                                 |
| --------- | ------ | ------------------------------------------- |
| `address` | string | Full display name of the matched location   |
| `city`    | string | City or town of the matched location        |
| `country` | string | ISO 3166-1 alpha-2 country code (uppercase) |
| `lat`     | number | Latitude of the matched location            |
| `lon`     | number | Longitude of the matched location           |

## Errors

- `404` **not_found** — No results found for the given address.
- `503` **upstream_error** — The geocoding service is temporarily unavailable.
- `400` **bad_request** — The address parameter is missing.
