---
name: iban-get-{iban}
api: IBAN Validator
method: GET
path: /v1/finance/iban/{iban}
base_url: https://api.requiems.xyz
description: Validates an IBAN and returns the country, bank code, and account number. Spaces in the input are stripped automatically. Always returns HTTP 200 — check the valid field to determine whether the IBAN is valid.
---

## Endpoint

**GET https://api.requiems.xyz/v1/finance/iban/{iban}**

## Validate IBAN

Validates an IBAN and returns the country, bank code, and account number. Spaces in the input are stripped automatically. Always returns HTTP 200 — check the valid field to determine whether the IBAN is valid.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `iban` | string | yes | path | The IBAN to validate. Spaces are stripped. Case-insensitive. |

## Response Example

```json
{
  "data": {
    "iban": "DE89370400440532013000",
    "valid": true,
    "country": "Germany",
    "bank_code": "37040044",
    "account": "0532013000"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `iban` | string | The normalised IBAN (spaces stripped, uppercased) |
| `valid` | boolean | true if the IBAN passed length and ISO 13616 checksum validation |
| `country` | string | Full country name (empty if the country code is not in the registry) |
| `bank_code` | string | Bank identifier extracted from the BBAN (empty if country not in registry or positions not defined) |
| `account` | string | Account number extracted from the BBAN (empty if country not in registry or positions not defined) |

## Errors

- `500` **internal_error** — Unexpected server error (e.g. database unreachable).
