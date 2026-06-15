---
name: markdown-post-markdown
api: Markdown to HTML
method: POST
path: /v1/technology/markdown
base_url: https://api.requiems.xyz
description: Converts a Markdown string to HTML. Pass sanitize true to strip potentially unsafe tags like script and iframe from the output.
---

## Endpoint

**POST https://api.requiems.xyz/v1/technology/markdown**

## Convert Markdown to HTML

Converts a Markdown string to HTML. Pass sanitize true to strip potentially unsafe tags like script and iframe from the output.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `markdown` | string | yes | body | The Markdown text to convert. |
| `sanitize` | boolean | no | body | When true, sanitizes the HTML output to remove unsafe tags and attributes. |

## Request Example

```json
{
  "markdown": "# Hello\n\nThis is **bold** and _italic_ text.",
  "sanitize": true
}
```

## Response Example

```json
{
  "data": {
    "html": "<h1>Hello</h1>\n<p>This is <strong>bold</strong> and <em>italic</em> text.</p>\n"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `html` | string | The rendered HTML output |

## Errors

- `undefined` **422** — undefined
