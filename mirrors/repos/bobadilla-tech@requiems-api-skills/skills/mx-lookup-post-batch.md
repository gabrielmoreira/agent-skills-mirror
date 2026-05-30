---
name: mx-lookup-post-batch
api: MX Lookup
method: POST
path: /v1/networking/mx/batch
base_url: https://api.requiems.xyz
description: Retrieve MX records for up to 50 domains in a single request. Results for each domain are sorted by priority ascending (lowest numeric value has the highest mail delivery priority per RFC 5321).
---

## Endpoint

**POST https://api.requiems.xyz/v1/networking/mx/batch**

## Batch MX Lookup

Retrieve MX records for up to 50 domains in a single request. Results for each domain are sorted by priority ascending (lowest numeric value has the highest mail delivery priority per RFC 5321).

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `domains` | array | yes | body | Array of domains to lookup (min: 1, max: 50). |

## Request Example

```json
{
  "domains": ["outlook.com", "yahoo.com"]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "domain": "outlook.com",
        "found": true,
        "data": {
          "domain": "outlook.com",
          "records": [
            {
              "host": "outlook-com.olc.protection.outlook.com.",
              "priority": 5
            }
          ]
          }
        },
        {
          "domain": "yahoo.com",
          "found": true,
          "data": {
            "domain": "yahoo.com",
            "records": [
              {
                "host": "mta5.am0.yahoodns.net.",
                "priority": 1
              },
              {
                "host": "mta7.am0.yahoodns.net.",
                "priority": 1
              },
              {
                "host": "mta6.am0.yahoodns.net.",
                "priority": 1
              }
            ]
          }
        }
      }
    ],
    "total": 2
  },
  "metadata": {
    "timestamp": "2026-05-13T21:34:51Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | MX lookup results for each input domain, in the same order as the input. |
| `results[].domain` | string | The domain name that was queried. |
| `results[].found` | boolean | Whether MX records were found for the domain. |
| `results[].error` | string | Error message if the lookup failed. Empty if found is true. |
| `results[].data` | object | MX lookup data. Present only when found is true. |
| `results[].data.domain` | string | The domain name associated with the MX records. |
| `results[].data.records` | array | List of MX records sorted by priority ascending (lower value means higher priority). |
| `results[].data.records[].host` | string | Hostname of the mail server. |
| `results[].data.records[].priority` | number | Priority of the mail server. Lower value means higher priority. |
| `total` | number | Total number of results returned. |

## Errors

- `422` **validation_failed** — The domains array is missing, empty, or contains more than 50 items.
- `500` **internal_error** — DNS lookup failed due to an unexpected server error.
