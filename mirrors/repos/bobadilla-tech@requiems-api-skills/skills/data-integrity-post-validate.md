---
name: data-integrity-post-validate
api: Data Integrity System
method: POST
path: /v1/systems/input/validate
base_url: https://api.requiems.xyz
description: Validates and scores a single email address, phone number, or text input — or any combination of the three. Returns per-field quality scores, normalized values, risk flags, and an overall quality score for gating or enriching input data.
---

## Endpoint

**POST https://api.requiems.xyz/v1/systems/input/validate**

## Input Validate

Validates and scores a single email address, phone number, or text input — or any combination of the three. Returns per-field quality scores, normalized values, risk flags, and an overall quality score for gating or enriching input data.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `email` | string | no | body | The email address to validate. At least one of email, phone, or text must be provided. |
| `phone` | string | no | body | The phone number to validate. Must include country code in E.164 format. At least one of email, phone, or text must be provided. |
| `text` | string | no | body | The text content to analyze for profanity, toxicity, and sentiment. At least one of email, phone, or text must be provided. |

## Request Example

```json
{
  "email": "user@example.com",
  "phone": "+12015551234",
  "text": "I just wanted to say that your customer service team was incredibly helpful and resolved my issue faster than expected."
}
```

## Response Example

```json
{
  "data": {
    "email": {
      "valid": true,
      "normalized": "user@example.com",
      "original": "user@example.com",
      "syntax_valid": true,
      "mx_valid": true,
      "disposable": false,
      "suggestion": null,
      "flags": null,
      "quality_score": 1
    },
    "phone": {
      "valid": true,
      "normalized": "+1 201-555-1234",
      "country": "US",
      "type": "landline_or_mobile",
      "carrier": null,
      "risk": {
        "is_voip": false,
        "is_virtual": false
      },
      "flags": null,
      "quality_score": 1
    },
    "text": {
      "is_safe": true,
      "toxicity_score": null,
      "sentiment": "positive",
      "flags": null
    },
    "overall_quality_score": 1
  },
  "metadata": {
    "timestamp": "2026-06-09T23:20:55Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `email` | object or null | Email validation result. Null when email was not provided. |
| `email.valid` | boolean | True when the email passes syntax and MX validation. |
| `email.normalized` | string or null | Normalized form of the email address. Null when syntax is invalid. |
| `email.original` | string | The original email address as provided in the request. |
| `email.syntax_valid` | boolean | True when the email address has a valid structure. |
| `email.mx_valid` | boolean | True when the email domain has valid MX records. |
| `email.disposable` | boolean | True when the email domain is a known disposable or temporary provider. |
| `email.suggestion` | string or null | Suggested correction when a typo is detected in the domain (e.g. gmial.com → gmail.com). Null otherwise. |
| `email.flags` | array or null | Triggered flags. Possible values: email_syntax_invalid, email_mx_invalid, email_disposable, email_has_suggestion. |
| `email.quality_score` | number | Email quality score from 0.0 to 1.0. Penalized by invalidity, disposable domain, and suggestions. |
| `phone` | object or null | Phone validation result. Null when phone was not provided. |
| `phone.valid` | boolean | True when the phone number is valid and dialable. |
| `phone.normalized` | string or null | Normalized phone number in international format. Null when the number is invalid. |
| `phone.country` | string or null | ISO 3166-1 alpha-2 country code detected from the number (e.g. US, CO). Null when the number is invalid. |
| `phone.type` | string or null | Line type. Null when the number is invalid. Possible values: mobile, landline, voip, toll_free, unknown. |
| `phone.carrier` | object or null | Carrier information. Null when not available. |
| `phone.carrier.name` | string | Name of the carrier or operator associated with the number. |
| `phone.risk` | object or null | Risk signals associated with the phone number. Null when the validator could not determine risk information. |
| `phone.risk.is_voip` | boolean | True when the number is confirmed as a VoIP line. False when explicitly confirmed as non-VoIP. |
| `phone.risk.is_virtual` | boolean | True when the number is confirmed as a virtual number. False when explicitly confirmed as non-virtual. |
| `phone.flags` | array or null | Triggered flags. Possible values: phone_invalid, phone_voip, phone_virtual, phone_unknown_type, phone_landline. |
| `phone.quality_score` | number | Phone quality score from 0.0 to 1.0. Penalized by invalidity, VoIP, virtual, landline, and unknown type. |
| `text` | object or null | Text analysis result. Null when text was not provided. |
| `text.is_safe` | boolean | False when any moderation flag is triggered. True otherwise. |
| `text.toxicity_score` | number or null | Reserved for future use. Currently always null. |
| `text.sentiment` | string | Detected sentiment: positive, negative, or neutral. |
| `text.flags` | array or null | Triggered moderation flags. Possible values: text_profanity. |
| `overall_quality_score` | number | Weighted quality score from 0.0 to 1.0 combining email and phone fields only. Weights are email 0.5 and phone 0.4, adjusted proportionally when one field is absent. Text does not currently contribute to this score — scoring will be enabled once toxicity_score is available from the sentiment service. Returns 0.0 when only text is provided. |

## Errors

- `undefined` **422** — All fields (email, phone, text) are absent or empty. At least one must be provided.
- `undefined` **401** — Missing or invalid API key.
