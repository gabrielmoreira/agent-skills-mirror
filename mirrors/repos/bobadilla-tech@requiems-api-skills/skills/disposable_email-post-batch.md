---
name: disposable_email-post-batch
api: Disposable Email Checker
method: POST
path: /v1/networking/disposable/batch
base_url: https://api.requiems.xyz
description: Validate multiple email addresses in a single request (max 100 emails)
---

## Endpoint

**POST https://api.requiems.xyz/v1/networking/disposable/batch**

## Check Batch Emails

Validate multiple email addresses in a single request (max 100 emails)

## Parameters

| Name     | Type  | Required | Location | Description                                 |
| -------- | ----- | -------- | -------- | ------------------------------------------- |
| `emails` | array | yes      | body     | Array of email addresses to check (max 100) |

## Request Example

```json
{
  "emails": [
    "user1@gmail.com",
    "user2@tempmail.com",
    "user3@guerrillamail.com"
  ]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "email": "user1@gmail.com",
        "is_disposable": false,
        "domain": "gmail.com"
      },
      {
        "email": "user2@tempmail.com",
        "is_disposable": true,
        "domain": "tempmail.com"
      },
      {
        "email": "user3@guerrillamail.com",
        "is_disposable": true,
        "domain": "guerrillamail.com"
      }
    ],
    "total": 3
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field     | Type    | Description                           |
| --------- | ------- | ------------------------------------- |
| `results` | array   | Array of check results for each email |
| `total`   | integer | Total number of emails checked        |

## Errors

- `undefined` **400** — The request body is missing or malformed
- `undefined` **400** — The emails field is missing
- `undefined` **400** — Too many emails in the request
