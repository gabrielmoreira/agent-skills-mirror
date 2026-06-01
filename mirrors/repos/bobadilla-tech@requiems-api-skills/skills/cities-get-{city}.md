---
name: cities-get-{city}
api: Cities
method: GET
path: /v1/places/cities/{city}
base_url: https://api.requiems.xyz
description: Returns metadata for a city by name. Lookup is case-insensitive.
---

## Endpoint

**GET https://api.requiems.xyz/v1/places/cities/{city}**

## Get City Info

Returns metadata for a city by name. Lookup is case-insensitive.

## Parameters

| Name   | Type   | Required | Location | Description                                              |
| ------ | ------ | -------- | -------- | -------------------------------------------------------- |
| `city` | string | yes      | path     | City name to look up (e.g. london, tokyo, new york city) |

## Response Example

```json
{
  "data": {
    "name": "London",
    "country": "GB",
    "population": 7556900,
    "timezone": "Europe/London",
    "lat": 51.5085,
    "lon": -0.1257
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field        | Type    | Description                                                     |
| ------------ | ------- | --------------------------------------------------------------- |
| `name`       | string  | Official city name as listed in the GeoNames dataset            |
| `country`    | string  | ISO 3166-1 alpha-2 country code (uppercase)                     |
| `population` | integer | City population from the GeoNames dataset                       |
| `timezone`   | string  | IANA timezone identifier for the city (e.g. "America/New_York") |
| `lat`        | number  | Latitude of the city centre                                     |
| `lon`        | number  | Longitude of the city centre                                    |

## Errors

- `404` **not_found** — No city with that name was found in the dataset.
- `500` **internal_error** — Unexpected server error.
