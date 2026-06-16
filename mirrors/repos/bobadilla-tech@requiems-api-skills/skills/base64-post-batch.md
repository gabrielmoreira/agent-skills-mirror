---
name: base64-post-batch
api: Base64 Encode / Decode
method: POST
path: /v1/technology/base64/decode/batch
base_url: https://api.requiems.xyz
description: Decode multiple Base64 strings in a single request
---

## Endpoint

**POST https://api.requiems.xyz/v1/technology/base64/decode/batch**

## Decode Batch

Decode multiple Base64 strings in a single request

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `values` | array[string] | yes | body | List of Base64 strings to decode |
| `variant` | string | no | body | Encoding variant (standard or url) |

## Response Example

```json
{
  "data": {
    "results": [
      {
        "result": "Hello"
      },
      {
        "result": "World"
      }
    ],
    "total": 2
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | Decoded results |
| `total` | integer | Number of processed items |

## Errors

- `undefined` **422** — Invalid variant or values list size outside 1-50
