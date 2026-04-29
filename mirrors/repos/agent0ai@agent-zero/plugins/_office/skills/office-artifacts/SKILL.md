---
name: office-artifacts
description: Use when creating, opening, reading, or editing editable Office canvas artifacts such as DOCX documents, XLSX spreadsheets, and PPTX presentations with the document_artifact tool.
version: "1.1.0"
author: "Agent Zero Core Team"
tags: ["office", "docx", "xlsx", "pptx", "canvas", "documents", "spreadsheets", "presentations"]
triggers:
  - "office canvas"
  - "editable document"
  - "docx"
  - "xlsx"
  - "pptx"
  - "spreadsheet"
  - "presentation"
allowed_tools:
  - document_artifact
---

# Office Artifacts

Use `document_artifact` for substantial Office deliverables that should remain editable in the canvas. Do not paste long document, spreadsheet, or deck bodies only into chat when the user asked for an editable file.

## Workflow

1. Create or open the artifact with `document_artifact:create` or `document_artifact:open`.
2. Before content-sensitive edits, call `document_artifact:read` with `file_id` or `path`.
3. Apply saved changes with `document_artifact:edit`.
4. Use `version_history` or `restore_version` when the user asks to audit or roll back.

Canvas context may list opened Office files with `file_id`, path, version, size, and timestamp. It intentionally omits full file contents; use `read` when the content matters.

## Minimal Calls

Create:
```json
{
  "tool_name": "document_artifact:create",
  "tool_args": {
    "kind": "document",
    "title": "Project Brief",
    "format": "docx",
    "content": "Draft text here."
  }
}
```

For spreadsheets, `content` can be CSV, TSV, or a Markdown table; the tool writes real cells, not one text blob per row.

Read:
```json
{
  "tool_name": "document_artifact:read",
  "tool_args": {
    "file_id": "abc123"
  }
}
```

Edit text in a DOCX or PPTX:
```json
{
  "tool_name": "document_artifact:edit",
  "tool_args": {
    "file_id": "abc123",
    "operation": "replace_text",
    "find": "old phrase",
    "replace": "new phrase"
  }
}
```

Set spreadsheet cells:
```json
{
  "tool_name": "document_artifact:edit",
  "tool_args": {
    "path": "/a0/usr/workdir/documents/Budget.xlsx",
    "operation": "set_cells",
    "cells": {
      "Sheet1!B2": 12500,
      "Sheet1!B3": 9800
    }
  }
}
```

Create an embedded spreadsheet chart:
```json
{
  "tool_name": "document_artifact:edit",
  "tool_args": {
    "file_id": "abc123",
    "operation": "create_chart",
    "sheet": "Sheet1",
    "chart": {
      "type": "line",
      "title": "Monthly Revenue",
      "data_range": "B1:C13",
      "categories": "A2:A13",
      "position": "E1",
      "width": 18,
      "height": 10
    }
  }
}
```

## Edit Operations

- DOCX: `set_text`, `append_text`, `prepend_text`, `replace_text`, `delete_text`.
- XLSX: `set_cells`, `append_rows`, `set_rows`, `create_chart`, `replace_text`, `delete_text`.
- PPTX: `set_slides`, `append_slide`, `replace_text`, `delete_text`.

Arguments:

- `replace_text` and `delete_text` require `find`; `replace_text` uses `replace`.
- `set_cells` accepts `{ "A1": "value", "Sheet2!B3": 42 }` or `[{"sheet":"Sheet1","cell":"A1","value":"value"}]`.
- `rows` accepts an array of rows. `content` can also be CSV, TSV, or a Markdown table.
- `create_chart` accepts `chart` as an object or JSON string. Supported XLSX chart types: `line`, `bar`, `column`, `pie`, `area`, `scatter`, `stock`, `ohlc`, `candlestick`. Use `data_range`, `categories`/`labels`, `position`, `title`, `width`, and `height`. For stock-style charts only, provide Open/High/Low/Close columns in that order, or rely on a sheet whose headers are `Date, Open, High, Low, Close`.
- `slides` accepts `[{"title":"Slide title","bullets":["point"]}]`. Text slides can be separated with a line containing `---`.
- `count` limits text replacements.

## Practical Rules

- Prefer `file_id` from canvas context or prior tool output; use `path` when that is all you have.
- Use `read` before editing unless the current saved content is already known.
- Use native `create_chart` for embedded spreadsheet charts. Reach for Python/code execution only when the requested chart behavior is not supported by the tool.
- Use `edit` for precise saved changes; use the visual Office canvas for human/manual layout polish.
- Direct edits update version history and refresh the canvas on edit/open results.
