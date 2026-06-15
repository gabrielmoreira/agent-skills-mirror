---
name: bin-lookup-get-{bin}
api: BIN Lookup
method: GET
path: /v1/finance/bin/{bin}
base_url: https://api.requiems.xyz
description: Returns card metadata for the given 6–8 digit BIN prefix.
---

## Endpoint

**GET https://api.requiems.xyz/v1/finance/bin/{bin}**

## BIN Lookup

Returns card metadata for the given 6–8 digit BIN prefix.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `bin` | string | yes | path | 6–8 digit Bank Identification Number. Dashes and spaces are stripped automatically. |

## Response Example

```json
{
  "data": {
    "bin": "424242",
    "scheme": "visa",
    "card_type": "credit",
    "card_level": "classic",
    "issuer_name": "Chase",
    "issuer_url": "www.chase.com",
    "issuer_phone": "+18002324000",
    "country_code": "US",
    "country_name": "United States",
    "prepaid": false,
    "luhn": true,
    "confidence": 0.92
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `bin` | string | The normalised BIN prefix used for the lookup |
| `scheme` | string | Card network: visa, mastercard, amex, discover, jcb, diners, unionpay, maestro, mir, rupay, private_label |
| `card_type` | string | credit, debit, prepaid, or charge |
| `card_level` | string | classic, gold, platinum, infinite, business, signature, or standard |
| `issuer_name` | string | Name of the card-issuing bank |
| `issuer_url` | string | Bank website URL |
| `issuer_phone` | string | Bank customer service phone number |
| `country_code` | string | ISO 3166-1 alpha-2 country code of the issuing bank (e.g. US, GB, DE) |
| `country_name` | string | Full country name of the issuing bank |
| `prepaid` | boolean | Whether the card is a prepaid card |
| `luhn` | boolean | Whether the BIN prefix passes the Luhn algorithm check |
| `confidence` | number | Data quality score (0.00–1.00). Multi-source confirmed records score higher. |

## Errors

- `400` **bad_request** — BIN is not 6–8 digits or contains non-digit characters.
- `404` **not_found** — BIN prefix not found in the database.
- `500` **internal_error** — Unexpected server error.
