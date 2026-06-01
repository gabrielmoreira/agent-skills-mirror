---
name: color-conversion-get-color
api: Color Format Conversion
method: GET
path: /v1/technology/color
base_url: https://api.requiems.xyz
description: Convert a color value from one format to another. The response always includes all four formats.
---

## Endpoint

**GET https://api.requiems.xyz/v1/technology/color**

## Convert Color

Convert a color value from one format to another. The response always includes
all four formats.

## Parameters

| Name    | Type   | Required | Location | Description                                                                                            |
| ------- | ------ | -------- | -------- | ------------------------------------------------------------------------------------------------------ |
| `from`  | string | yes      | query    | Source color format: hex, rgb, hsl, or cmyk                                                            |
| `to`    | string | yes      | query    | Target color format: hex, rgb, hsl, or cmyk                                                            |
| `value` | string | yes      | query    | Color value in the source format (e.g. #ff5733, rgb(255,87,51), hsl(11,100%,60%), cmyk(0%,66%,80%,0%)) |

## Response Example

```json
{
  "data": {
    "input": "#ff5733",
    "result": "hsl(11, 100%, 60%)",
    "formats": {
      "hex": "#ff5733",
      "rgb": "rgb(255, 87, 51)",
      "hsl": "hsl(11, 100%, 60%)",
      "cmyk": "cmyk(0%, 66%, 80%, 0%)"
    }
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field          | Type   | Description                                      |
| -------------- | ------ | ------------------------------------------------ |
| `input`        | string | The original value passed in the value parameter |
| `result`       | string | The color expressed in the requested to format   |
| `formats.hex`  | string | HEX representation (#rrggbb)                     |
| `formats.rgb`  | string | RGB representation (rgb(r, g, b))                |
| `formats.hsl`  | string | HSL representation (hsl(h, s%, l%))              |
| `formats.cmyk` | string | CMYK representation (cmyk(c%, m%, y%, k%))       |

## Errors

- `400` **bad_request** — One or more of from, to, or value parameters is
  missing or the from/to value is not one of: hex, rgb, hsl, cmyk.
- `422` **invalid_color** — The value cannot be parsed in the specified from
  format.
- `500` **internal_error** — Unexpected server error.
