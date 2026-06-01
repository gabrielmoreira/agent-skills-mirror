---
name: whois-post-batch
api: WHOIS Lookup
method: POST
path: /v1/networking/whois/batch
base_url: https://api.requiems.xyz
description: Returns WHOIS information for up to 50 domains in a single request. Results are returned in the same order as the input array. Domains without WHOIS data return found: false instead of failing the entire request.
---

## Endpoint

**POST https://api.requiems.xyz/v1/networking/whois/batch**

## Batch WHOIS Lookup

Returns WHOIS information for up to 50 domains in a single request. Results are
returned in the same order as the input array. Domains without WHOIS data return
found: false instead of failing the entire request.

## Parameters

| Name      | Type  | Required | Location | Description                             |
| --------- | ----- | -------- | -------- | --------------------------------------- |
| `domains` | array | yes      | body     | Array of domain names. Min: 1, Max: 50. |

## Response Example

```json
{
  "data": {
    "results": [
      {
        "domain": "example.com",
        "found": true,
        "data": {
          "domain": "example.com",
          "registrar": "RESERVED-Internet Assigned Numbers Authority",
          "name_servers": [
            "A.IANA-SERVERS.NET",
            "B.IANA-SERVERS.NET"
          ],
          "status": [
            "clientDeleteProhibited"
          ],
          "created_date": "1995-08-14T04:00:00Z",
          "updated_date": "2023-08-14T07:01:38Z",
          "expiry_date": "2024-08-13T04:00:00Z",
          "dnssec": true
        }
      },
      {
        "domain": "doesnotexist.com",
        "found": false,
        "error": "domain not found"
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

| Field              | Type    | Description                                          |
| ------------------ | ------- | ---------------------------------------------------- |
| `results`          | array   | One entry per domain, in the same order as the input |
| `results[].domain` | string  | Domain name requested in the batch                   |
| `results[].found`  | boolean | False when WHOIS data could not be found             |
| `results[].error`  | string  | Error message when found is false                    |
| `results[].data`   | object  | WHOIS information for the domain when found is true  |
| `total`            | integer | Total number of results returned                     |

## Errors

- `422` **validation_failed** — Invalid request body. This includes empty
  arrays, more than 50 domains, invalid domain names, or malformed payloads.
- `500` **internal_error** — Unexpected server error during batch WHOIS lookup.
