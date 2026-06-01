---
name: email-validate-post-batch
api: Email Validator
method: POST
path: /v1/validation/email/batch
base_url: https://api.requiems.xyz
description: Validates up to 50 email addresses in a single request. Each email is processed independently and returns a full validation breakdown (syntax, MX record, disposable check, normalization, and typo suggestion). Invalid emails do not fail the request. Billing: 1 credit per email.
---

## Endpoint

**POST https://api.requiems.xyz/v1/validation/email/batch**

## Validate Emails (Batch)

Validates up to 50 email addresses in a single request. Each email is processed
independently and returns a full validation breakdown (syntax, MX record,
disposable check, normalization, and typo suggestion). Invalid emails do not
fail the request. Billing: 1 credit per email.

## Parameters

| Name     | Type  | Required | Location | Description                                            |
| -------- | ----- | -------- | -------- | ------------------------------------------------------ |
| `emails` | array | yes      | body     | Array of email addresses to validate. Min: 1, Max: 50. |

## Request Example

```json
{
  "emails": ["user@gmail.com", "user@gmial.com"]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "email": "user@gmail.com",
        "valid": true,
        "syntax_valid": true,
        "mx_valid": true,
        "disposable": false,
        "normalized": "user@gmail.com",
        "domain": "gmail.com",
        "suggestion": null
      },
      {
        "email": "user@gmial.com",
        "valid": false,
        "syntax_valid": true,
        "mx_valid": false,
        "disposable": false,
        "normalized": "user@gmial.com",
        "domain": "gmial.com",
        "suggestion": "gmail.com"
      }
    ],
    "total": 2
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field                    | Type    | Description                                                       |
| ------------------------ | ------- | ----------------------------------------------------------------- |
| `results`                | array   | List of validation results for each email, preserving input order |
| `results[].email`        | string  | null                                                              |
| `results[].valid`        | boolean | Overall validity (syntax + MX record)                             |
| `results[].syntax_valid` | boolean | Whether the email is syntactically valid (RFC 5322)               |
| `results[].mx_valid`     | boolean | Whether the domain has valid MX records                           |
| `results[].disposable`   | boolean | Whether the email comes from a disposable domain                  |
| `results[].normalized`   | string  | null                                                              |
| `results[].domain`       | string  | null                                                              |
| `results[].suggestion`   | string  | null                                                              |
| `total`                  | integer | Number of emails processed in the batch                           |

## Errors

- `422` **validation_failed** — Valid JSON body that fails field validation
  (empty array or more than 50 emails).
- `400` **bad_request** — Invalid JSON, malformed request body, or unexpected
  field types.
- `500` **internal_error** — Unexpected server error
