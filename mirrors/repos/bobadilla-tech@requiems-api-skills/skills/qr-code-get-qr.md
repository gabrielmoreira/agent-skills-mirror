---
name: qr-code-get-qr
api: QR Code Generator
method: GET
path: /v1/technology/qr
base_url: https://api.requiems.xyz
description: Returns a raw PNG image of the QR code. Ideal for direct embedding or file download.
---

## Endpoint

**GET https://api.requiems.xyz/v1/technology/qr**

## Generate QR Code (PNG)

Returns a raw PNG image of the QR code. Ideal for direct embedding or file
download.

## Parameters

| Name       | Type    | Required | Location | Description                                                                                                                                                            |
| ---------- | ------- | -------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `data`     | string  | yes      | query    | The text or URL to encode in the QR code                                                                                                                               |
| `size`     | integer | no       | query    | Image size in pixels (default: 256, min: 50, max: 1000)                                                                                                                |
| `recovery` | string  | no       | query    | Error-correction level: low (7%), medium (15%), high (25%), highest (30%). Higher levels are more robust to physical damage but produce larger images. Default: medium |

## Response Example

```json
<binary PNG image data>
```

## Response Fields

| Field      | Type  | Description                                     |
| ---------- | ----- | ----------------------------------------------- |
| `(binary)` | bytes | Raw PNG image bytes. Content-Type is image/png. |

## Errors

- `undefined` **400** — Missing or invalid parameters (e.g. data not provided,
  size out of range, unknown recovery level)
- `undefined` **500** — Failed to generate QR code
