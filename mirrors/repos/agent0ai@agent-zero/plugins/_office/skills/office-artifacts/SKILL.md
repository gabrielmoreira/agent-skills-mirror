---
name: office-artifacts
description: Use when creating, opening, reading, or editing editable document canvas artifacts such as Markdown documents, DOCX documents, XLSX spreadsheets, and PPTX presentations with the document_artifact tool.
version: "1.3.0"
author: "Agent Zero Core Team"
tags: ["documents", "markdown", "md", "docx", "xlsx", "pptx", "canvas", "spreadsheets", "presentations"]
triggers:
  - "document canvas"
  - "markdown document"
  - "editable document"
  - "md"
  - "docx"
  - "xlsx"
  - "pptx"
  - "spreadsheet"
  - "presentation"
allowed_tools:
  - document_artifact
---

# Document Artifacts

Use `document_artifact` for substantial deliverables that should remain editable in the custom document canvas. Markdown is the first-class document format and the default for writing, notes, reports, briefs, and drafts. Use DOCX, XLSX, or PPTX only when the user explicitly asks for that binary format, provides an existing file in that format, or needs a Word/Excel/PowerPoint-compatible artifact.

The canvas is user-owned UI. Creating, reading, or editing an artifact must save the file and update its state, but it must not open the canvas automatically if the user has not opened it. Tool results provide explicit Download and Open in canvas actions for the user.

For format-specific work, prefer the matching skill when available:

- `markdown-documents` for Markdown-first editable writing.
- `word-documents` for DOCX/Word-compatible files.
- `excel-workbooks` for XLSX/Excel-compatible spreadsheets.
- `presentation-decks` for PPTX/PowerPoint-compatible decks.

## Workflow

1. Create or open the artifact with `document_artifact:create` / `document_artifact:open`, or with `tool_name: "document_artifact"` plus `method: "create"` / `method: "open"`.
2. Before content-sensitive edits, call `document_artifact:read` with `file_id` or `path`.
3. Apply saved changes with `document_artifact:edit`.
4. Use `version_history` or `restore_version` when the user asks to audit or roll back.

Canvas context may list opened files with `file_id`, path, version, size, and timestamp. It intentionally omits full file contents; use `read` when the content matters.

## Minimal Calls

Create:
```json
{
  "tool_name": "document_artifact:create",
  "tool_args": {
    "kind": "document",
    "title": "Project Brief",
    "format": "md",
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

Edit text in a Markdown, DOCX, or PPTX file:
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

- MD and DOCX: `set_text`, `append_text`, `prepend_text`, `replace_text`, `delete_text`.
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
- Do not create an artifact for tiny one-shot edits or answers the agent can finish cleanly in chat or by directly editing the file.
- For document-style requests with no requested binary format, create Markdown and let the custom Markdown editor be the primary interactive surface.
- The Desktop runtime may be warmed during Agent Zero startup, but visible Desktop/canvas use remains opt-in. Treat LibreOffice GUI work as appropriate for explicit GUI requests, binary Office visual polish, or final layout inspection.
- Never open the canvas automatically from a tool result. If the user has not opened the canvas, leave the saved artifact available through the normal UI affordance.
- Do not create ODT, ODS, or ODP in this pass; return a clear unsupported response if asked.
- Use native `create_chart` for embedded spreadsheet charts. Reach for Python/code execution only when the requested chart behavior is not supported by the tool.
- Use `edit` for precise saved changes; use the visual document canvas for human/manual layout polish.
- Direct edits update version history and refresh the canvas on edit/open results.
