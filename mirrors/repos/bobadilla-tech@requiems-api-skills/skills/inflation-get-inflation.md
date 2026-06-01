---
name: inflation-get-inflation
api: Inflation
method: GET
path: /v1/finance/inflation
base_url: https://api.requiems.xyz
description: Returns the latest annual CPI inflation rate for a country plus the previous 10 years of historical data.
---

## Endpoint

**GET https://api.requiems.xyz/v1/finance/inflation**

## Get Inflation Rate

Returns the latest annual CPI inflation rate for a country plus the previous 10
years of historical data.

## Parameters

| Name      | Type   | Required | Location | Description                                                          |
| --------- | ------ | -------- | -------- | -------------------------------------------------------------------- |
| `country` | string | yes      | query    | ISO 3166-1 alpha-2 country code (e.g. US, GB, DE). Case-insensitive. |

## Response Example

```json
{
  "data": {
    "country": "US",
    "rate": 2.9495,
    "period": "2024",
    "historical": [
      { "period": "2023", "rate": 4.1163 },
      { "period": "2022", "rate": 8.0028 },
      { "period": "2021", "rate": 4.6979 },
      { "period": "2020", "rate": 1.2336 },
      { "period": "2019", "rate": 1.8122 },
      { "period": "2018", "rate": 2.4426 },
      { "period": "2017", "rate": 2.1301 },
      { "period": "2016", "rate": 1.2616 },
      { "period": "2015", "rate": 0.1186 },
      { "period": "2014", "rate": 1.6222 }
    ]
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field                 | Type   | Description                                                                  |
| --------------------- | ------ | ---------------------------------------------------------------------------- |
| `country`             | string | ISO 3166-1 alpha-2 country code, uppercased                                  |
| `rate`                | number | Latest annual CPI inflation rate as a percentage (e.g. 2.9495 means 2.9495%) |
| `period`              | string | Year of the latest data point (e.g. 2024)                                    |
| `historical`          | array  | Up to 10 previous years of inflation data, ordered newest to oldest          |
| `historical[].period` | string | Year of the historical data point                                            |
| `historical[].rate`   | number | Annual CPI inflation rate for that year                                      |

## Errors

- `400` **bad_request** — The country parameter is missing or is not a valid ISO
  3166-1 alpha-2 code.
- `404` **not_found** — No inflation data found for the given country code.
- `500` **internal_error** — Unexpected server error.
