---
name: payments-intelligence-post-validate
api: Payments Intelligence System
method: POST
path: /v1/systems/payment/validate
base_url: https://api.requiems.xyz
description: Validate and cross-check BIN, IBAN, and SWIFT identifiers in one call. Returns per-field results and a consistency check that flags country and bank mismatches.
---

## Endpoint

**POST https://api.requiems.xyz/v1/systems/payment/validate**

## Validate Payment

Validate and cross-check BIN, IBAN, and SWIFT identifiers in one call. Returns per-field results and a consistency check that flags country and bank mismatches.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `bin` | string | no | body | Card BIN (first 6–8 digits). At least one of bin, iban, or swift is required. |
| `iban` | string | no | body | IBAN string to validate. Checksum and format are verified. |
| `swift` | string | no | body | SWIFT/BIC code to look up institution and country. |

## Request Example

```json
{
  "bin": "424242",
  "iban": "DE89370400440532013000",
  "swift": "DEUTDEDB"
}
```

## Response Example

```json
{
  "data": {
    "bin": {
      "valid": true,
      "scheme": "visa",
      "card_type": "debit",
      "card_level": "classic",
      "country_code": "US",
      "issuer": "JPMorgan Chase",
      "prepaid": false,
      "luhn": true
    },
    "iban": {
      "valid": true,
      "country_code": "DE",
      "bank_code": "37040044",
      "account_number": "0532013000"
    },
    "swift": {
      "valid": true,
      "institution": "Deutsche Bank",
      "country": "DE",
      "branch": "Frankfurt"
    },
    "consistency": {
      "ok": false,
      "flags": ["country_mismatch_bin_iban"]
    }
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `bin` | object or null | BIN result. Null when bin was not provided. Contains valid, scheme, card_type, card_level, country_code, issuer, prepaid, luhn. |
| `iban` | object or null | IBAN result. Null when iban was not provided. Contains valid, country_code, bank_code, account_number. |
| `swift` | object or null | SWIFT result. Null when swift was not provided. Contains valid, institution, country, branch. |
| `consistency.ok` | boolean | True when no cross-field mismatches were detected |
| `consistency.flags` | array | Mismatch flags. Possible values: country_mismatch_bin_iban, country_mismatch_bin_swift, country_mismatch_iban_swift, bank_mismatch_iban_swift |

## Errors

- `undefined` **422** — All of bin, iban, and swift were omitted. At least one is required.
- `undefined` **401** — Missing or invalid API key
