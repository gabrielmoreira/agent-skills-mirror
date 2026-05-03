---
name: word-documents
description: Use when creating, opening, or editing Word-compatible DOCX documents, including requests for Word files, DOCX reports, memos, contracts, resumes, or documents that must work in Microsoft Word or LibreOffice Writer.
version: "1.0.0"
author: "Agent Zero Core Team"
tags: ["word", "docx", "writer", "documents", "reports", "memos", "contracts"]
triggers:
  - "Word"
  - "DOCX"
  - "docx"
  - "Microsoft Word"
  - "LibreOffice Writer"
  - "Word document"
allowed_tools:
  - document_artifact
---

# Word Documents

Use DOCX only when the user explicitly asks for Word/DOCX compatibility, provides an existing `.docx`, or needs a binary Office file. For ordinary writing with no binary requirement, use Markdown instead.

The canvas is user-owned UI. Creating or editing a DOCX must save the file and return action buttons, but must not open the canvas automatically. Use Desktop/Writer only for explicit GUI requests, visual layout polish, or final visual confirmation.

## Workflow

Create:

```json
{
  "tool_name": "document_artifact:create",
  "tool_args": {
    "kind": "document",
    "title": "Board Memo",
    "format": "docx",
    "content": "Memo body text."
  }
}
```

Edit:

1. Use `document_artifact:read` with `file_id` or `path` before content-sensitive edits.
2. Use `document_artifact:edit` for deterministic saved changes: `set_text`, `append_text`, `prepend_text`, `replace_text`, or `delete_text`.
3. Use the Desktop only when the user asks to see Writer or when layout cannot be handled reliably through structured edits.

Practical rules:

- Keep DOCX content clean and structured. Use headings and paragraphs; avoid over-formatting unless requested.
- Do not create ODT in this workflow.
- Do not say the document is open. Say it was created or updated, and rely on the Open in canvas action for user-controlled viewing.
