---
name: exchange-rate-get-convert
api: Exchange Rate
method: GET
path: /v1/finance/convert
base_url: https://api.requiems.xyz
description: Converts an amount from one currency to another and returns the rate alongside the converted value.
---

## Endpoint

**GET https://api.requiems.xyz/v1/finance/convert**

## Convert Currency

Converts an amount from one currency to another and returns the rate alongside the converted value.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `from` | string | yes | query | ISO 4217 source currency code (3 letters, e.g. USD) |
| `to` | string | yes | query | ISO 4217 target currency code (3 letters, e.g. EUR) |
| `amount` | number | yes | query | Amount to convert. Must be greater than 0. |

## Response Example

```json
{
  "data": {
    "from": "USD",
    "to": "EUR",
    "rate": 0.92,
    "amount": 100,
    "converted": 92.00,
    "timestamp": "2024-12-15T00:00:00Z"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `from` | string | Source currency code (uppercased) |
| `to` | string | Target currency code (uppercased) |
| `rate` | number | Exchange rate used for the conversion |
| `amount` | number | The original amount passed in the request |
| `converted` | number | Result of amount × rate, rounded to 2 decimal places |
| `timestamp` | string | Date the rate was published by the ECB (ISO 8601) |

## Errors

- `400` **bad_request** — A required parameter is missing, the currency code is not 3 alphabetic characters, or the amount is 0 or negative.
- `422` **invalid_currency** — One or both currency codes are not recognised by the upstream data source.
- `503` **upstream_error** — The exchange rate data source is temporarily unavailable.
