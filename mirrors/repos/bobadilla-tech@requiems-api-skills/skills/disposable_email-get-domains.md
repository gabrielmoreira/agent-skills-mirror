---
name: disposable_email-get-domains
api: Disposable Email Checker
method: GET
path: /v1/networking/disposable/domains
base_url: https://api.requiems.xyz
description: Get a paginated list of all disposable domains in the blocklist
---

## Endpoint

**GET https://api.requiems.xyz/v1/networking/disposable/domains**

## List Domains (Paginated)

Get a paginated list of all disposable domains in the blocklist

## Parameters

| Name       | Type    | Required | Location | Description                              |
| ---------- | ------- | -------- | -------- | ---------------------------------------- |
| `page`     | integer | no       | query    | Page number (default: 1)                 |
| `per_page` | integer | no       | query    | Items per page (default: 100, max: 1000) |

## Response Example

```json
{
  "data": {
    "domains": [
      "tempmail.com",
      "guerrillamail.com",
      "10minutemail.com"
    ],
    "total": 10500,
    "page": 1,
    "per_page": 100,
    "has_more": true
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field      | Type    | Description                            |
| ---------- | ------- | -------------------------------------- |
| `domains`  | array   | Array of domain names                  |
| `total`    | integer | Total number of domains in blocklist   |
| `page`     | integer | Current page number                    |
| `per_page` | integer | Number of items per page               |
| `has_more` | boolean | Whether there are more pages available |
