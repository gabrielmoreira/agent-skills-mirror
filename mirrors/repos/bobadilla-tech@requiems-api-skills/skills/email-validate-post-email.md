---
name: email-validate-post-email
api: Email Validator
method: POST
path: /v1/validation/email
base_url: https://api.requiems.xyz
description: Validates a single email address and returns a full breakdown of syntax validity, MX record status, disposable domain check, normalized form, and any typo suggestion.
---

## Endpoint

**POST https://api.requiems.xyz/v1/validation/email**

## Validate Email

Validates a single email address and returns a full breakdown of syntax
validity, MX record status, disposable domain check, normalized form, and any
typo suggestion.

## Parameters

| Name    | Type   | Required | Location | Description                    |
| ------- | ------ | -------- | -------- | ------------------------------ |
| `email` | string | yes      | body     | The email address to validate. |

## Request Example

```json
{
  "email": "user@gmial.com"
}
```

## Response Example

```json
{
  "data": {
    "email": "user@gmial.com",
    "valid": false,
    "syntax_valid": true,
    "mx_valid": false,
    "disposable": false,
    "normalized": "user@gmial.com",
    "domain": "gmial.com",
    "suggestion": "gmail.com"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field          | Type    | Description                                                                                                                                                                                  |
| -------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `email`        | string  | null                                                                                                                                                                                         |
| `valid`        | boolean | Overall validity. True only when the address passes syntax validation and the domain has at least one MX record                                                                              |
| `syntax_valid` | boolean | Whether the address is syntactically valid according to RFC 5322                                                                                                                             |
| `mx_valid`     | boolean | Whether the domain has at least one MX record, meaning it can receive email                                                                                                                  |
| `disposable`   | boolean | Whether the address uses a known disposable or temporary email domain                                                                                                                        |
| `normalized`   | string  | null                                                                                                                                                                                         |
| `domain`       | string  | null                                                                                                                                                                                         |
| `suggestion`   | string  | A corrected domain name when the supplied domain looks like a typo of a well-known provider (e.g. gmial.com → gmail.com). Null when no close match is found or the domain is already correct |

## Errors

- `422` **validation_failed** — The email field is missing from the request
  body.
- `400` **bad_request** — The request body is missing, not valid JSON, or
  contains unknown fields.
- `500` **internal_error** — Unexpected server error.
