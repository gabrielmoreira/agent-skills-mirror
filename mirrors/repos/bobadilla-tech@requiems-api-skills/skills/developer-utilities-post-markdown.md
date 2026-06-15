---
name: developer-utilities-post-markdown
api: Developer Utilities
method: POST
path: /v1/technology/markdown
base_url: https://api.requiems.xyz
description: Convert a Markdown string to HTML. Useful for rendering user-submitted content, documentation previews, or README files.
---

## Endpoint

**POST https://api.requiems.xyz/v1/technology/markdown**

## Render Markdown

Convert a Markdown string to HTML. Useful for rendering user-submitted content, documentation previews, or README files.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `text` | string | yes | body | Markdown string to render |

## Request Example

```json
{
  "text": "# Hello\n\nThis is **bold** text."
}
```

## Response Example

```json
{
  "data": {
    "html": "<h1>Hello</h1>\n<p>This is <strong>bold</strong> text.</p>"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `html` | string | Rendered HTML output |

## Errors

- `undefined` **400** — text field is missing or empty
- `undefined` **401** — Missing or invalid API key
