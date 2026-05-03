---
name: excel-workbooks
description: Use when creating, opening, or editing Excel-compatible XLSX spreadsheets, workbooks, tables, budgets, formulas, sheets, or charts.
version: "1.0.0"
author: "Agent Zero Core Team"
tags: ["excel", "xlsx", "spreadsheet", "workbook", "calc", "tables", "charts", "budget"]
triggers:
  - "Excel"
  - "XLSX"
  - "xlsx"
  - "spreadsheet"
  - "workbook"
  - "budget"
  - "sheet"
  - "chart"
allowed_tools:
  - document_artifact
---

# Excel Workbooks

Use XLSX when the user asks for Excel, a spreadsheet, a workbook, tables that should remain editable as cells, formulas, or embedded spreadsheet charts.

The canvas is user-owned UI. Creating or editing an XLSX must save the workbook and return action buttons, but must not open the canvas automatically. Use Desktop/Calc only for explicit GUI requests, visual chart/layout polish, or final visual confirmation.

## Workflow

Create a workbook:

```json
{
  "tool_name": "document_artifact:create",
  "tool_args": {
    "kind": "spreadsheet",
    "title": "Budget",
    "format": "xlsx",
    "content": "Item,Amount\nPlatform,1000"
  }
}
```

For a blank workbook request, create a simple workbook with the requested title and `format: "xlsx"`; do not call `status` first unless the user asked for availability.

Edit cells:

```json
{
  "tool_name": "document_artifact:edit",
  "tool_args": {
    "file_id": "abc123",
    "operation": "set_cells",
    "cells": {
      "Sheet1!A1": "Item",
      "Sheet1!B1": "Amount"
    }
  }
}
```

Practical rules:

- `content` may be CSV, TSV, or a Markdown table; the tool writes real spreadsheet cells.
- Use `rows` for whole-table replacement, `append_rows` for adding records, and `set_cells` for precise edits.
- Use `create_chart` with a chart object for embedded charts before reaching for code execution.
- Do not open Calc/canvas automatically. The user can choose Open in canvas when they want the visible spreadsheet.
