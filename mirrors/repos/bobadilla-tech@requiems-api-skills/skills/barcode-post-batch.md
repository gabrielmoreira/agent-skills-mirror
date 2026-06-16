---
name: barcode-post-batch
api: Barcode Generator
method: POST
path: /v1/technology/barcode/batch
base_url: https://api.requiems.xyz
description: Generate up to 20 barcodes in a single request. Each barcode is processed independently and results are returned in the same order as the input. Invalid items do not fail the entire request.
---

## Endpoint

**POST https://api.requiems.xyz/v1/technology/barcode/batch**

## Generate Barcodes (Batch)

Generate up to 20 barcodes in a single request. Each barcode is processed independently and results are returned in the same order as the input. Invalid items do not fail the entire request.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `items` | array | yes | body | Array of barcode generation requests. Min: 1, Max: 20. |

## Request Example

```json
{
  "items": [
    {
      "data": "123456789",
      "type": "code128"
    },
    {
      "data": "1234567",
      "type": "ean8"
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
        "image": "iVBORw0KGgoAAAANSUhEUgAA...",
        "type": "code128",
        "width": 300,
        "height": 100,
        "success": true,
        "error": ""
      },
      {
        "image": "iVBORw0KGgoAAAANSUhEUgAA...",
        "type": "ean8",
        "width": 300,
        "height": 100,
        "success": true,
        "error": ""
      }
    ],
    "total": 2
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | List of barcode generation results preserving input order |
| `results[].image` | string | Base64-encoded PNG image |
| `results[].type` | string | Barcode format used |
| `results[].width` | integer | Image width in pixels |
| `results[].height` | integer | Image height in pixels |
| `results[].success` | boolean | Whether barcode generation succeeded |
| `results[].error` | string | Error message when generation fails |
| `total` | integer | Number of items processed |

## Errors

- `422` **validation_failed** — Valid request body that fails validation (empty items array, more than 20 items, missing data field, or unsupported barcode type).
- `400` **bad_request** — Invalid JSON or malformed request body.
- `500` **internal_error** — Unexpected server error.
