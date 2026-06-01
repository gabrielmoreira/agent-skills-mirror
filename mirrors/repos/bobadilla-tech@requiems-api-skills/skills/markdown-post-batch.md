---
name: markdown-post-batch
api: Markdown to HTML
method: POST
path: /v1/technology/markdown/batch
base_url: https://api.requiems.xyz
description: Converts multiple Markdown strings into HTML in a single request. Results are returned in the same order as the input array. Supports optional sanitization to remove unsafe HTML tags such as script and iframe.
---

## Endpoint

**POST https://api.requiems.xyz/v1/technology/markdown/batch**

## Convert Markdown Batch

Converts multiple Markdown strings into HTML in a single request. Results are
returned in the same order as the input array. Supports optional sanitization to
remove unsafe HTML tags such as script and iframe.

## Parameters

| Name        | Type    | Required | Location | Description                                                            |
| ----------- | ------- | -------- | -------- | ---------------------------------------------------------------------- |
| `markdowns` | array   | yes      | body     | Array of Markdown strings. Min: 1, Max: 50.                            |
| `sanitize`  | boolean | no       | body     | When true, sanitizes HTML output to remove unsafe tags and attributes. |

## Request Example

```json
{
  "markdowns": [
    "# Hello",
    "**bold**",
    "- item one"
  ],
  "sanitize": true
}
```

## Response Example

```json
{
  "data": {
    "results": [
      { "html": "<h1>Hello</h1>" },
      { "html": "<p><strong>bold</strong></p>" },
      { "html": "<ul>\n<li>item one</li>\n</ul>" }
    ]
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field            | Type   | Description                                                |
| ---------------- | ------ | ---------------------------------------------------------- |
| `results`        | array  | One HTML result per Markdown input, preserving input order |
| `results[].html` | string | Rendered HTML output for each Markdown string              |

## Errors

- `422` **validation_failed** — Body is invalid: empty array, more than 50
  items, or invalid Markdown entry.
- `400` **bad_request** — Missing or malformed request body.
- `500` **internal_error** — Unexpected server error.
