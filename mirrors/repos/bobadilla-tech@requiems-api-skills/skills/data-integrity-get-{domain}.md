---
name: data-integrity-get-{domain}
api: Data Integrity System
method: GET
path: /v1/systems/domain/trust/{domain}
base_url: https://api.requiems.xyz
description: Evaluate the trustworthiness of a domain by analyzing DNS records, WHOIS registration data, and MX configuration — in a single call.
---

## Endpoint

**GET https://api.requiems.xyz/v1/systems/domain/trust/{domain}**

## Domain Trust

Evaluate the trustworthiness of a domain by analyzing DNS records, WHOIS registration data, and MX configuration — in a single call.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `domain` | string | yes | path | The domain name to evaluate for trust. Must be a valid domain format (e.g. github.com). |

## Response Example

```json
{
  "data": {
    "domain": "github.com",
    "trust_score": 1,
    "trust_level": "high",
    "who_is": {
      "registrar": "MarkMonitor Inc.",
      "created_at": "2007-10-09T18:20:50Z",
      "expires_at": "2026-10-09T18:20:50Z",
      "age_days": 6814,
      "status": [
        "clientDeleteProhibited",
        "clientTransferProhibited",
        "clientUpdateProhibited"
      ]
    },
    "dns": {
      "has_a_records": true,
      "has_mx_records": true,
      "has_ns_records": true,
      "available": false
    },
    "mx_records": [
      {
        "host_name": "github-com.mail.protection.outlook.com.",
        "priority": 0
      }
    ],
    "flags": []
  },
  "metadata": {
    "timestamp": "2026-06-05T21:01:18Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `domain` | string | The domain name that was evaluated. |
| `trust_score` | float | Computed trust score between 0.0 and 1.0. Starts at 1.0 with penalties applied based on domain signals. |
| `trust_level` | string | Coarse trust label derived from the score. Possible values are "high" (>= 0.75), "medium" (0.4 - 0.74), or "low" (< 0.4). |
| `who_is` | object | WHOIS registration data for the domain. Omitted from the response if WHOIS is unavailable for the TLD or if the domain is not registered. |
| `who_is.registrar` | string | The registrar where the domain was registered. |
| `who_is.created_at` | string | The date the domain was first registered in RFC3339 format. |
| `who_is.expires_at` | string | The date the domain registration expires in RFC3339 format. |
| `who_is.age_days` | integer | Number of days since the domain was registered. |
| `who_is.status` | array | WHOIS status codes indicating the domain transfer and update permissions. |
| `dns` | object | DNS health check results for the domain. Fields default to false if the domain is not registered. |
| `dns.has_a_records` | boolean | True if the domain has at least one A record pointing to an IP address. |
| `dns.has_mx_records` | boolean | True if the domain has MX records configured for receiving email. |
| `dns.has_ns_records` | boolean | True if the domain has NS records indicating it is delegated to a nameserver. |
| `dns.available` | boolean | True if the domain is unregistered and available for purchase. When true, trust_score is 0.0 and evaluation stops immediately. |
| `mx_records` | array | List of MX records found for the domain. Empty array if none exist or if the domain is not registered. |
| `mx_records[].host_name` | string | The hostname of the mail server. |
| `mx_records[].priority` | integer | Mail server priority. Lower value means higher priority. |
| `flags` | array | List of signal flags raised during evaluation. Possible values are "new_domain", "young_domain", "no_mx", "no_a_records", "no_ns_records", "expiring_soon", "whois_unavailable", "domain_not_registered". Only "domain_not_registered" is returned when the domain is not registered. |

## Errors

- `400` **bad_request** — Invalid or malformed domain value in the request path.
