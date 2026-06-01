---
name: mx-lookup-get-{domain}
api: MX Lookup
method: GET
path: /v1/networking/mx/{domain}
base_url: https://api.requiems.xyz
description: Retrieve all MX records for a domain. Results are sorted by priority ascending (lowest numeric value has highest mail delivery priority per RFC 5321).
---

## Endpoint

**GET https://api.requiems.xyz/v1/networking/mx/{domain}**

## MX Lookup

Retrieve all MX records for a domain. Results are sorted by priority ascending
(lowest numeric value has highest mail delivery priority per RFC 5321).

## Parameters

| Name     | Type   | Required | Location | Description                                                |
| -------- | ------ | -------- | -------- | ---------------------------------------------------------- |
| `domain` | string | yes      | path     | The domain name to look up MX records for (e.g. gmail.com) |

## Response Example

```json
{
  "data": {
    "domain": "gmail.com",
    "records": [
      { "host": "gmail-smtp-in.l.google.com.", "priority": 5 },
      { "host": "alt1.gmail-smtp-in.l.google.com.", "priority": 10 },
      { "host": "alt2.gmail-smtp-in.l.google.com.", "priority": 20 },
      { "host": "alt3.gmail-smtp-in.l.google.com.", "priority": 30 },
      { "host": "alt4.gmail-smtp-in.l.google.com.", "priority": 40 }
    ]
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field                | Type    | Description                                                                         |
| -------------------- | ------- | ----------------------------------------------------------------------------------- |
| `domain`             | string  | The domain that was queried                                                         |
| `records`            | array   | List of MX records, sorted by priority ascending (lowest number = highest priority) |
| `records[].host`     | string  | Fully-qualified hostname of the mail server (typically ends with a trailing dot)    |
| `records[].priority` | integer | MX priority value. Lower values have higher delivery priority per RFC 5321.         |

## Errors

- `400` **bad_request** — The domain parameter is not a valid domain name.
- `404` **not_found** — No MX records were found for the domain (domain may not
  accept email).
- `500` **internal_error** — DNS lookup failed due to an unexpected server
  error.
