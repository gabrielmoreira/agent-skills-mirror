---
name: horoscope-get-{sign}
api: Horoscope
method: GET
path: /v1/entertainment/horoscope/{sign}
base_url: https://api.requiems.xyz
description: Returns a daily horoscope reading for the specified zodiac sign.
---

## Endpoint

**GET https://api.requiems.xyz/v1/entertainment/horoscope/{sign}**

## Get Daily Horoscope

Returns a daily horoscope reading for the specified zodiac sign.

## Parameters

| Name   | Type   | Required | Location | Description                                                                                                                                           |
| ------ | ------ | -------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `sign` | string | yes      | path     | Zodiac sign (case-insensitive). Supported values: aries, taurus, gemini, cancer, leo, virgo, libra, scorpio, sagittarius, capricorn, aquarius, pisces |

## Response Example

```json
{
  "data": {
    "sign": "aries",
    "date": "2024-12-15",
    "horoscope": "Today is a great day for new beginnings. Trust your instincts and take that first step toward your goals.",
    "lucky_number": 7,
    "mood": "energetic"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field          | Type    | Description                             |
| -------------- | ------- | --------------------------------------- |
| `sign`         | string  | Normalized zodiac sign (lowercase)      |
| `date`         | string  | Today's date in YYYY-MM-DD format (UTC) |
| `horoscope`    | string  | Daily horoscope reading                 |
| `lucky_number` | integer | Lucky number for the day (1-99)         |
| `mood`         | string  | Suggested mood for the day              |
