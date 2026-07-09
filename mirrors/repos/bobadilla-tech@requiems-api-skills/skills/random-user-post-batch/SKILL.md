---
name: random-user-post-batch
api: Random User
method: POST
path: /v1/technology/random-user/batch
base_url: https://api.requiems.xyz
description: Returns multiple randomly generated fake user profiles in a single request. Each call consumes count units of quota. Maximum 50 users per request.
---

## Endpoint

**POST https://api.requiems.xyz/v1/technology/random-user/batch**

## Batch Generate Users

Returns multiple randomly generated fake user profiles in a single request. Each call consumes count units of quota. Maximum 50 users per request.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `count` | integer | yes | body | Number of users to generate (min: 1, max: 50). |

## Request Example

```json
{
  "count": 2
}
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "name": "Grace Lopez",
        "email": "grace.lopez@example.org",
        "phone": "555-123-4567",
        "address": {
          "street": "4821 Maple Avenue",
          "city": "North Judyton",
          "state": "California",
          "zip": "94103",
          "country": "United States of America"
        },
        "avatar": "https://api.dicebear.com/9.x/identicon/svg?seed=Grace+Lopez"
      },
      {
        "name": "John Smith",
        "email": "john.smith@example.com",
        "phone": "555-987-6543",
        "address": {
          "street": "12 Oak Street",
          "city": "Springfield",
          "state": "Illinois",
          "zip": "62701",
          "country": "United States of America"
        },
        "avatar": "https://api.dicebear.com/9.x/identicon/svg?seed=John+Smith"
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

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | Ordered list of generated user profiles. Same fields as the single-user endpoint. |
| `total` | integer | Number of users returned. Matches the requested count. |

## Errors

- `undefined` **422** — count is missing, less than 1, or greater than 50
- `undefined` **400** — Request body is malformed or not valid JSON
- `undefined` **500** — Internal server error
