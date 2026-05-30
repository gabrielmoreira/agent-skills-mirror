---
name: random-user-get-random-user
api: Random User
method: GET
path: /v1/technology/random-user
base_url: https://api.requiems.xyz
description: Returns a randomly generated fake user profile.
---

## Endpoint

**GET https://api.requiems.xyz/v1/technology/random-user**

## Get Random User

Returns a randomly generated fake user profile.

## Response Example

```json
{
  "data": {
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
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `name` | string | Full name of the generated user |
| `email` | string | Email address of the generated user |
| `phone` | string | Phone number of the generated user |
| `address.street` | string | Street address |
| `address.city` | string | City name |
| `address.state` | string | State or region |
| `address.zip` | string | Postal / ZIP code |
| `address.country` | string | Country name |
| `avatar` | string | URL to a unique identicon avatar for the generated user (DiceBear) |

## Errors

- `undefined` **500** — Internal server error
