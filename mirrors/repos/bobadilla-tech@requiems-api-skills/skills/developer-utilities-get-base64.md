---
name: developer-utilities-get-base64
api: Developer Utilities
method: GET
path: /v1/technology/qr/base64
base_url: https://api.requiems.xyz
description: Generate a QR code for any string and return a base64-encoded PNG. Configurable size and error correction level.
---

## Endpoint

**GET https://api.requiems.xyz/v1/technology/qr/base64**

## Generate QR Code

Generate a QR code for any string and return a base64-encoded PNG. Configurable size and error correction level.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `data` | string | yes | query | The string to encode into the QR code (URL, text, or any string). |
| `size` | integer | no | query | Output image size in pixels (width and height). Min 50, max 1000. Defaults to 256. |
| `recovery` | string | no | query | Error correction level: low, medium, high, or highest. Higher levels allow more of the QR code to be damaged while still scanning. |

## Request Example

```json
GET /v1/technology/qr/base64?data=https%3A%2F%2Frequiems.xyz&size=256&recovery=medium
```

## Response Example

```json
{
  "data": {
    "image": "iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAYAAABccqhmAAAA...",
    "width": 256,
    "height": 256
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `image` | string | Base64-encoded PNG image of the QR code |
| `width` | integer | Image width in pixels, equal to the requested size |
| `height` | integer | Image height in pixels, equal to the requested size |

## Errors

- `undefined` **400** — data query parameter is missing
- `undefined` **422** — size is outside 50–1000 or recovery is not one of the valid values
- `undefined` **401** — Missing or invalid API key
