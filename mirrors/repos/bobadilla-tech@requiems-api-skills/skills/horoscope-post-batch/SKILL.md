---
name: horoscope-post-batch
api: Horoscope
method: POST
path: /v1/entertainment/horoscope/batch
base_url: https://api.requiems.xyz
description: Returns up to 12 daily horoscopes in a single request.
---

## Endpoint

**POST https://api.requiems.xyz/v1/entertainment/horoscope/batch**

## Batch Daily Horoscopes

Returns up to 12 daily horoscopes in a single request.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `signs` | array | yes | body | Array of signs to get (min: 1, max: 12). Allowed values: aries, taurus, gemini, cancer, leo, virgo, libra, scorpio, sagittarius, capricorn, aquarius, pisces. |

## Request Example

```json
{
  "signs": ["taurus","cancer","libra"]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "sign": "taurus",
        "date": "2026-05-21",
        "horoscope": "Your patience will be rewarded. Take time to reflect before making important decisions today.",
        "lucky_number": 26,
        "mood": "reflective"
      },
      {
        "sign": "cancer",
        "date": "2026-05-21",
        "horoscope": "Your patience will be rewarded. Take time to reflect before making important decisions today.",
        "lucky_number": 2,
        "mood": "reflective"
      },
      {
        "sign": "libra",
        "date": "2026-05-21",
        "horoscope": "Rest and self-care are essential today. Taking care of yourself enables you to take care of others.",
        "lucky_number": 82,
        "mood": "peaceful"
      }
    ],
    "total": 3
  },
  "metadata": {
    "timestamp": "2026-05-21T04:09:20Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | List of daily horoscopes returned in the same order as the input signs. |
| `results[].sign` | string | Zodiac sign the horoscope corresponds to. |
| `results[].date` | string | Date the horoscope is for, in YYYY-MM-DD format. |
| `results[].horoscope` | string | Daily horoscope reading for the given sign. |
| `results[].lucky_number` | integer | Lucky number for the given sign on that date. |
| `results[].mood` | string | Predicted mood for the given sign on that date. |
| `total` | integer | Total number of horoscopes returned. |

## Errors

- `422` **validation_failed** — The signs array is missing, empty, or contains more than 12 items, or includes unsupported sign values.
- `400` **bad_request** — Invalid JSON, malformed request body, or unexpected field types.
