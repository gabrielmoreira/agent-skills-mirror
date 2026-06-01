---
name: geocode-get-reverse-geocode
api: Geocoding
method: GET
path: /v1/places/reverse-geocode
base_url: https://api.requiems.xyz
description: Converts geographic coordinates into a human-readable address.
---

## Endpoint

**GET https://api.requiems.xyz/v1/places/reverse-geocode**

## Reverse Geocode

Converts geographic coordinates into a human-readable address.

## Parameters

| Name  | Type   | Required | Location | Description                             |
| ----- | ------ | -------- | -------- | --------------------------------------- |
| `lat` | number | yes      | query    | Latitude of the location (-90 to 90)    |
| `lon` | number | yes      | query    | Longitude of the location (-180 to 180) |

## Response Example

```json
{
  "data": {
    "lat": 38.8977,
    "lon": -77.0365,
    "address": "White House, 1600, Pennsylvania Avenue Northwest, Ward 2, Washington, District of Columbia, 20500, United States",
    "city": "Washington",
    "country": "US"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field     | Type   | Description                                                |
| --------- | ------ | ---------------------------------------------------------- |
| `lat`     | number | Latitude as provided in the request                        |
| `lon`     | number | Longitude as provided in the request                       |
| `address` | string | Full display name of the location at the given coordinates |
| `city`    | string | City or town at the given coordinates                      |
| `country` | string | ISO 3166-1 alpha-2 country code (uppercase)                |

## Errors

- `404` **not_found** — No address found for the given coordinates.
- `503` **upstream_error** — The geocoding service is temporarily unavailable.
- `400` **bad_request** — lat or lon is missing or out of range (lat: -90..90,
  lon: -180..180).
