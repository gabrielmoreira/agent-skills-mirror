---
name: mortgage-get-mortgage
api: Mortgage Calculator
method: GET
path: /v1/finance/mortgage
base_url: https://api.requiems.xyz
description: Returns the monthly payment, total cost, and full amortization schedule for a fixed-rate mortgage.
---

## Endpoint

**GET https://api.requiems.xyz/v1/finance/mortgage**

## Calculate Mortgage

Returns the monthly payment, total cost, and full amortization schedule for a
fixed-rate mortgage.

## Parameters

| Name        | Type    | Required | Location | Description                                                                       |
| ----------- | ------- | -------- | -------- | --------------------------------------------------------------------------------- |
| `principal` | number  | yes      | query    | Loan amount in your chosen currency (e.g. 300000 for $300,000)                    |
| `rate`      | number  | yes      | query    | Annual interest rate as a percentage (e.g. 6.5 for 6.5%). Must be greater than 0. |
| `years`     | integer | yes      | query    | Loan term in years (1–50)                                                         |

## Response Example

```json
{
  "data": {
    "principal": 300000,
    "rate": 6.5,
    "years": 30,
    "monthly_payment": 1896.2,
    "total_payment": 682632.0,
    "total_interest": 382632.0,
    "schedule": [
      {
        "month": 1,
        "payment": 1896.2,
        "principal": 271.2,
        "interest": 1625.0,
        "balance": 299728.8
      },
      {
        "month": 2,
        "payment": 1896.2,
        "principal": 272.67,
        "interest": 1623.53,
        "balance": 299456.13
      }
    ]
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field                  | Type    | Description                                                           |
| ---------------------- | ------- | --------------------------------------------------------------------- |
| `principal`            | number  | The original loan amount passed in the request                        |
| `rate`                 | number  | The annual interest rate passed in the request                        |
| `years`                | integer | The loan term in years passed in the request                          |
| `monthly_payment`      | number  | Fixed monthly payment amount (rounded to 2 decimal places)            |
| `total_payment`        | number  | Total amount paid over the life of the loan                           |
| `total_interest`       | number  | Total interest paid (total_payment minus principal)                   |
| `schedule`             | array   | Full amortization schedule — one entry per month (years × 12 entries) |
| `schedule[].month`     | integer | Month number (1 to years × 12)                                        |
| `schedule[].payment`   | number  | Total payment for this month                                          |
| `schedule[].principal` | number  | Portion of this month's payment applied to principal                  |
| `schedule[].interest`  | number  | Portion of this month's payment applied to interest                   |
| `schedule[].balance`   | number  | Remaining loan balance after this payment                             |

## Errors

- `400` **bad_request** — A required parameter is missing, not a valid number,
  or out of range (e.g. years > 50 or rate <= 0).
- `500` **internal_error** — Unexpected server error.
