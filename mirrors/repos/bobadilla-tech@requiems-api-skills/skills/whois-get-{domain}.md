---
name: whois-get-{domain}
api: WHOIS Lookup
method: GET
path: /v1/networking/whois/{domain}
base_url: https://api.requiems.xyz
description: Returns WHOIS registration information for a domain name.
---

## Endpoint

**GET https://api.requiems.xyz/v1/networking/whois/{domain}**

## WHOIS Lookup

Returns WHOIS registration information for a domain name.

## Parameters

| Name     | Type   | Required | Location | Description                                   |
| -------- | ------ | -------- | -------- | --------------------------------------------- |
| `domain` | string | yes      | path     | The domain name to look up (e.g. example.com) |

## Response Example

```json
{
  "data": {
    "domain": "example.com",
    "registrar": "RESERVED-Internet Assigned Numbers Authority",
    "name_servers": [
      "A.IANA-SERVERS.NET",
      "B.IANA-SERVERS.NET"
    ],
    "status": [
      "clientDeleteProhibited",
      "clientTransferProhibited",
      "clientUpdateProhibited"
    ],
    "created_date": "1995-08-14T04:00:00Z",
    "updated_date": "2023-08-14T07:01:38Z",
    "expiry_date": "2024-08-13T04:00:00Z",
    "dnssec": true
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field          | Type             | Description                                                     |
| -------------- | ---------------- | --------------------------------------------------------------- |
| `domain`       | string           | The domain name that was looked up                              |
| `registrar`    | string           | The name of the registrar holding the domain registration       |
| `name_servers` | array of strings | List of authoritative name servers for the domain               |
| `status`       | array of strings | EPP status codes for the domain (e.g. clientTransferProhibited) |
| `created_date` | string           | Date the domain was first registered (ISO 8601)                 |
| `updated_date` | string           | Date the domain record was last updated (ISO 8601)              |
| `expiry_date`  | string           | Date the domain registration expires (ISO 8601)                 |
| `dnssec`       | boolean          | True when DNSSEC is enabled for the domain                      |

## Errors

- `400` **bad_request** — The domain name format is invalid.
- `404` **not_found** — No WHOIS record was found for the domain.
- `500` **internal_error** — Unexpected server error or upstream WHOIS query
  failure.
