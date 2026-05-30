---
name: phone-validation-get-phone
api: Phone Validation
method: GET
path: /v1/validation/phone
base_url: https://api.requiems.xyz
description: Validates a single phone number and returns its country, type, formatted representation, carrier, and VOIP/virtual risk flags.
---

## Endpoint

**GET https://api.requiems.xyz/v1/validation/phone**

## Validate Phone Number

Validates a single phone number and returns its country, type, formatted representation, carrier, and VOIP/virtual risk flags.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `number` | string | yes | query | The phone number to validate. Must include the country calling code (e.g. +12015551234). |

## Response Example

```json
{
  "data": {
    "number": "+447400123456",
    "valid": true,
    "country": "GB",
    "type": "mobile",
    "formatted": "+44 7400 123456",
    "carrier": {
      "name": "Three",
      "source": "metadata"
    },
    "risk": {
      "is_voip": false,
      "is_virtual": false
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
| `number` | string | The original number as supplied in the request |
| `valid` | boolean | Whether the number is a valid, dialable phone number |
| `country` | string | ISO 3166-1 alpha-2 country code (omitted when valid is false) |
| `type` | string | Number type: mobile, landline, landline_or_mobile, toll_free, voip, premium_rate, shared_cost, personal_number, pager, uan, voicemail, or unknown (omitted when valid is false) |
| `formatted` | string | International format of the number, e.g. +44 7400 123456 (omitted when valid is false) |
| `carrier.name` | string | Carrier name from phone prefix metadata (omitted when carrier cannot be determined) |
| `carrier.source` | string | How the carrier was determined. Always "metadata" when present |
| `risk.is_voip` | boolean | true when the number type is voip |
| `risk.is_virtual` | boolean | true when the number is not tied to a physical SIM or fixed line: voip, personal_number, uan, pager, or voicemail |

## Errors

- `400` **bad_request** — The number query parameter is missing.
