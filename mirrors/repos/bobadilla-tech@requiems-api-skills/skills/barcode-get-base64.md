---
name: barcode-get-base64
api: Barcode Generator
method: GET
path: /v1/technology/barcode/base64
base_url: https://api.requiems.xyz
description: Returns a JSON envelope containing the barcode as a base64-encoded PNG string, along with its type and dimensions.
---

## Endpoint

**GET https://api.requiems.xyz/v1/technology/barcode/base64**

## Generate Barcode (Base64 JSON)

Returns a JSON envelope containing the barcode as a base64-encoded PNG string,
along with its type and dimensions.

## Parameters

| Name   | Type   | Required | Location | Description                                          |
| ------ | ------ | -------- | -------- | ---------------------------------------------------- |
| `data` | string | yes      | query    | The text or numeric string to encode in the barcode  |
| `type` | string | yes      | query    | Barcode format: code128, code93, code39, ean8, ean13 |

## Response Example

```json
{
  "data": {
    "image": "<base64-encoded PNG data>",
    "type": "code128",
    "width": 300,
    "height": 100
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
| `type`   | string  | The barcode format that was used        |
| `width`  | integer | Width of the generated image in pixels  |
| `height` | integer | Height of the generated image in pixels |

## Errors

- `undefined` **400** — Missing or invalid parameters (e.g. data not provided,
  unsupported type)
- `undefined` **422** — Data is invalid for the chosen barcode type (e.g. wrong
  digit count for EAN-8/EAN-13, non-numeric EAN data)
