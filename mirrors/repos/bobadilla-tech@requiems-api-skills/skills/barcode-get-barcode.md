---
name: barcode-get-barcode
api: Barcode Generator
method: GET
path: /v1/technology/barcode
base_url: https://api.requiems.xyz
description: Returns a raw PNG image of the barcode. Ideal for direct embedding or file download.
---

## Endpoint

**GET https://api.requiems.xyz/v1/technology/barcode**

## Generate Barcode (PNG)

Returns a raw PNG image of the barcode. Ideal for direct embedding or file download.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `data` | string | yes | query | The text or numeric string to encode in the barcode |
| `type` | string | yes | query | Barcode format: code128, code93, code39, ean8, ean13 |

## Response Example

```json
<binary PNG image data>
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `(binary)` | bytes | Raw PNG image bytes. Content-Type is image/png. |

## Errors

- `undefined` **400** — Missing or invalid parameters (e.g. data not provided, unsupported type)
- `undefined` **422** — Data is invalid for the chosen barcode type (e.g. wrong digit count for EAN-8/EAN-13, non-numeric EAN data)
