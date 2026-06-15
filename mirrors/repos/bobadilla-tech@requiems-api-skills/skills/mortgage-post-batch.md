---
name: mortgage-post-batch
api: Mortgage Calculator
method: POST
path: /v1/finance/mortgage/batch
base_url: https://api.requiems.xyz
description: Calculate up to 50 mortgages in a single request. Results are returned in the same order as the input.
---

## Endpoint

**POST https://api.requiems.xyz/v1/finance/mortgage/batch**

## Batch Calculate Mortgages

Calculate up to 50 mortgages in a single request. Results are returned in the same order as the input.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `mortgages` | array | yes | body | Array of mortgages to calculate (min: 1, max: 50). |

## Request Example

```json
{
  "mortgages": [
    {
      "principal": 150000,
      "rate": 6.5,
      "years": 10
    },
    {
      "principal": 250000,
      "rate": 5.2,
      "years": 30
    }
  ]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "principal": 150000,
        "rate": 6.5,
        "years": 10,
        "monthly_payment": 1703.22,
        "total_payment": 204386.36,
        "total_interest": 54386.36,
        "schedule": [
          {
            "month": 1,
            "payment": 1703.22,
            "principal": 890.72,
            "interest": 812.5,
            "balance": 149109.28
          },
          {
            "month": 2,
            "payment": 1703.22,
            "principal": 895.54,
            "interest": 807.68,
            "balance": 148213.74
          }
        ]
      },
      {
        "principal": 250000,
        "rate": 5.2,
        "years": 30,
        "monthly_payment": 1372.78,
        "total_payment": 494199.79,
        "total_interest": 244199.79,
        "schedule": [
          {
            "month": 1,
            "payment": 1372.78,
            "principal": 289.44,
            "interest": 1083.33,
            "balance": 249710.56
          },
          {
            "month": 2,
            "payment": 1372.78,
            "principal": 290.7,
            "interest": 1082.08,
            "balance": 249419.86
          }
        ]
      }
    ],
    "total": 2
  },
  "metadata": {
    "timestamp": "2026-05-10T19:20:02Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | Mortgage calculation result for each mortgage request in the same order as the input. Each item has the same fields as the single mortgage endpoint. |
| `total` | integer | Number of results returned. Matches the length of the input array. |

## Errors

- `422` **validation_failed** — The mortgages array is missing, empty, or contains more than 50 items.
