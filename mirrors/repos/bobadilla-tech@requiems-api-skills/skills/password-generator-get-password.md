---
name: password-generator-get-password
api: Password Generator
method: GET
path: /v1/technology/password
base_url: https://api.requiems.xyz
description: Generate a cryptographically secure random password with customizable character sets and length
---

## Endpoint

**GET https://api.requiems.xyz/v1/technology/password**

## Generate Password

Generate a cryptographically secure random password with customizable character
sets and length

## Parameters

| Name        | Type    | Required | Location | Description                                    |
| ----------- | ------- | -------- | -------- | ---------------------------------------------- |
| `length`    | integer | no       | query    | Password length (8-128 characters)             |
| `uppercase` | boolean | no       | query    | Include uppercase letters (A-Z)                |
| `numbers`   | boolean | no       | query    | Include numbers (0-9)                          |
| `symbols`   | boolean | no       | query    | Include special characters (!@#$%^&*()-_=+[]{} |

## Response Example

```json
{
  "data": {
    "password": "aB3#cDeFgHiJkLmN",
    "length": 16,
    "strength": "strong"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field      | Type    | Description                                            |
| ---------- | ------- | ------------------------------------------------------ |
| `password` | string  | The generated password                                 |
| `length`   | integer | Length of the generated password                       |
| `strength` | string  | Password strength assessment (weak, medium, or strong) |

## Errors

- `undefined` **400** — The length parameter is out of valid range (8-128)
- `undefined` **500** — Failed to generate password (rare cryptographic failure)
