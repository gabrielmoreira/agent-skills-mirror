---
name: commodities-get-{commodity}
api: Commodity Prices
method: GET
path: /v1/finance/commodities/{commodity}
base_url: https://api.requiems.xyz
description: Returns the latest annual average price and up to 10 years of historical data for the requested commodity slug.
---

## Endpoint

**GET https://api.requiems.xyz/v1/finance/commodities/{commodity}**

## Get Commodity Price

Returns the latest annual average price and up to 10 years of historical data for the requested commodity slug.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `commodity` | string | yes | path | Commodity slug (e.g. gold, silver, oil). See supported slugs below. |

## Response Example

```json
{
  "data": {
    "commodity": "gold",
    "name": "Gold",
    "price": 2386.3300,
    "unit": "oz",
    "currency": "USD",
    "change_24h": 23.01,
    "historical": [
      { "period": "2023", "price": 1940.5400 },
      { "period": "2022", "price": 1800.1200 },
      { "period": "2021", "price": 1798.5200 },
      { "period": "2020", "price": 1769.6400 },
      { "period": "2019", "price": 1392.6000 },
      { "period": "2018", "price": 1268.9300 },
      { "period": "2017", "price": 1257.1500 },
      { "period": "2016", "price": 1251.6500 },
      { "period": "2015", "price": 1160.0600 },
      { "period": "2014", "price": 1266.4000 }
    ]
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `commodity` | string | The commodity slug as provided in the request path |
| `name` | string | Human-readable commodity name |
| `price` | number | Latest annual average price in the commodity's display unit |
| `unit` | string | Price unit (oz, barrel, mmbtu, lb, or metric_ton) |
| `currency` | string | Currency code — always USD |
| `change_24h` | number | Year-over-year percentage change from the prior year's annual average (positive = price increased) |
| `historical` | array | Up to 10 prior years of annual average prices, ordered newest to oldest |
| `historical[].period` | string | Year of the historical data point |
| `historical[].price` | number | Annual average price for that year |

## Errors

- `404` **not_found** — No data found for the given commodity slug. Check the supported slugs list.
- `500` **internal_error** — Unexpected server error.
