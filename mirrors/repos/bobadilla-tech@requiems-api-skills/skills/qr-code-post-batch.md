---
name: qr-code-post-batch
api: QR Code Generator
method: POST
path: /v1/technology/qr/base64/batch
base_url: https://api.requiems.xyz
description: Generate up to 50 base64-encoded QR codes in a single request. Results are returned in input order. The PNG endpoint has no batch variant — use this endpoint for batch generation.
---

## Endpoint

**POST https://api.requiems.xyz/v1/technology/qr/base64/batch**

## Batch Generate QR Codes (Base64)

Generate up to 50 base64-encoded QR codes in a single request. Results are returned in input order. The PNG endpoint has no batch variant — use this endpoint for batch generation.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `items` | array of objects | yes | body | List of QR generation requests (1–50 items). |
| `items[].data` | string | yes | body | The text or URL to encode. |
| `items[].size` | integer | no | body | Image size in pixels (50–1000). Defaults to 256. |
| `items[].recovery` | string | no | body | Error-correction level: low, medium, high, highest. Defaults to medium. |

## Request Example

```json
{
  "items": [
    { "data": "https://example.com", "size": 256, "recovery": "medium" },
    { "data": "Hello, World!" }
  ]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      { "data": "https://example.com", "image": "<base64>", "width": 256, "height": 256 },
      { "data": "Hello, World!",        "image": "<base64>", "width": 256, "height": 256 }
    ],
    "total": 2
  },
  "metadata": { "timestamp": "2026-01-01T00:00:00Z" }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | Per-item results in input order. |
| `results[].data` | string | The input text or URL that was encoded. |
| `results[].image` | string | Base64-encoded PNG image data (omitted on error). |
| `results[].width` | integer | Width of the generated image in pixels (omitted on error). |
| `results[].height` | integer | Height of the generated image in pixels (omitted on error). |
| `results[].error` | string | Error message if generation failed (omitted on success). |
| `total` | integer | Total number of items processed. |

## Errors

- `422` **validation_failed** — The items array is missing, empty, or exceeds 50 items.
- `400` **bad_request** — The request body is missing or malformed.
