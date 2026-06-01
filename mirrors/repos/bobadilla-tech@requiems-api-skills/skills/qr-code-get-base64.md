---
name: qr-code-get-base64
api: QR Code Generator
method: GET
path: /v1/technology/qr/base64
base_url: https://api.requiems.xyz
description: Returns a JSON envelope containing the QR code as a base64-encoded PNG string, along with its dimensions.
---

## Endpoint

**GET https://api.requiems.xyz/v1/technology/qr/base64**

## Generate QR Code (Base64 JSON)

Returns a JSON envelope containing the QR code as a base64-encoded PNG string,
along with its dimensions.

## Parameters

| Name       | Type    | Required | Location | Description                                                                                |
| ---------- | ------- | -------- | -------- | ------------------------------------------------------------------------------------------ |
| `data`     | string  | yes      | query    | The text or URL to encode in the QR code                                                   |
| `size`     | integer | no       | query    | Image size in pixels (default: 256, min: 50, max: 1000)                                    |
| `recovery` | string  | no       | query    | Error-correction level: low (7%), medium (15%), high (25%), highest (30%). Default: medium |

## Response Example

```json
{
  "data": {
    "image": "<base64-encoded PNG data>",
    "width": 256,
    "height": 256
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field    | Type    | Description                             |
| -------- | ------- | --------------------------------------- |
| `image`  | string  | Base64-encoded PNG image data           |
| `width`  | integer | Width of the generated image in pixels  |
| `height` | integer | Height of the generated image in pixels |

## Errors

- `undefined` **400** — Missing or invalid parameters (e.g. data not provided,
  size out of range, unknown recovery level)
- `undefined` **500** — Failed to generate QR code
