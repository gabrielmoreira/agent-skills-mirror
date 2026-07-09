---
name: crypto-get-{symbol}
api: Crypto Prices
method: GET
path: /v1/finance/crypto/{symbol}
base_url: https://api.requiems.xyz
description: Returns current price data for the given cryptocurrency symbol.
---

## Endpoint

**GET https://api.requiems.xyz/v1/finance/crypto/{symbol}**

## Get Crypto Price

Returns current price data for the given cryptocurrency symbol.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `symbol` | string | yes | path | Uppercase ticker symbol (e.g. BTC, ETH, SOL) |

## Response Example

```json
{
  "data": {
    "symbol": "BTC",
    "name": "Bitcoin",
    "price_usd": 42000.50,
    "change_24h": 2.5,
    "market_cap": 820000000000,
    "volume_24h": 25000000000
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `symbol` | string | Uppercase ticker symbol |
| `name` | string | Full coin name |
| `price_usd` | number | Current price in USD |
| `change_24h` | number | Price change over the last 24 hours as a percentage |
| `market_cap` | number | Total market capitalisation in USD |
| `volume_24h` | number | Total trading volume over the last 24 hours in USD |

## Errors

- `422` **unknown_symbol** — The symbol is not in the supported coin list.
- `503` **upstream_error** — CoinGecko is unavailable or returned an unexpected response.
