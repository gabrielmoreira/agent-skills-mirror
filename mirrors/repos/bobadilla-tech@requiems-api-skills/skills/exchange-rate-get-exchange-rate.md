---
name: exchange-rate-get-exchange-rate
api: Exchange Rate
method: GET
path: /v1/finance/exchange-rate
base_url: https://api.requiems.xyz
description: Returns the current exchange rate between two currencies.
---

## Endpoint

**GET https://api.requiems.xyz/v1/finance/exchange-rate**

## Get Exchange Rate

Returns the current exchange rate between two currencies.

## Parameters

| Name   | Type   | Required | Location | Description                                         |
| ------ | ------ | -------- | -------- | --------------------------------------------------- |
| `from` | string | yes      | query    | ISO 4217 source currency code (3 letters, e.g. USD) |
| `to`   | string | yes      | query    | ISO 4217 target currency code (3 letters, e.g. EUR) |

## Response Example

```json
{
  "data": {
    "from": "USD",
    "to": "EUR",
    "rate": 0.92,
    "timestamp": "2024-12-15T00:00:00Z"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field       | Type   | Description                                                   |
| ----------- | ------ | ------------------------------------------------------------- |
| `from`      | string | Source currency code (uppercased)                             |
| `to`        | string | Target currency code (uppercased)                             |
| `rate`      | number | Exchange rate — how many units of `to` equal 1 unit of `from` |
| `timestamp` | string | Date the rate was published by the ECB (ISO 8601)             |

## Errors

- `400` **bad_request** — A required parameter is missing or the currency code
  is not exactly 3 alphabetic characters.
- `422` **invalid_currency** — One or both currency codes are not recognised by
  the upstream data source.
- `503` **upstream_error** — The exchange rate data source is temporarily
  unavailable.
