---
name: document-query
description: Use when reading, extracting, summarizing, comparing, OCRing, or answering questions over local or remote documents, code files, PDFs, Office files, HTML/text files, and text-heavy document images or scans with the document_query tool.
version: 1.0.0
author: Agent Zero Team
tags: ["documents", "ocr", "qa", "pdf", "code", "analysis"]
trigger_patterns:
  - document query
  - read document
  - ask questions about a document
  - summarize document
  - compare documents
  - extract text from image
  - OCR document
  - analyze code file
---

# Document Query

Use the `document_query` tool to read, extract, summarize, compare, or answer questions over documents and document-like files.

## When To Use

Use `document_query` for:

- Local files and URLs containing document text: PDF, HTML, Office files, plain text, Markdown, CSV/TSV, XML/JSON, logs, code files, and similar content.
- Q&A over one or more documents.
- Summaries, comparisons, entity extraction, key-point extraction, and table/text extraction.
- Code-file Q&A when the user points to specific files or URLs and wants answers from their contents.
- Text-heavy images, scans, screenshots, and document images when the task is OCR/text extraction or Q&A over visible text.
- Image OCR when vision tools are unavailable, when the main chat model is not multimodal, or when the user wants document text rather than visual scene understanding.

Do not use `document_query` for purely visual questions that require spatial/visual reasoning beyond document text; use vision tools when available for those cases.

## Inputs

`document_query` accepts:

- `document`: required. A single local path/URL or a list of local paths/URLs.
- `queries`: optional. A list of questions. When omitted, the tool returns extracted document content.
- `query`: optional compatibility shortcut for a single question.

Local paths must be full paths. `file://` is optional for local files. URLs should use `http://` or `https://`.

For directories or codebases, first identify the relevant files with file/search tools, then pass the files themselves to `document_query`. Do not pass a directory path as the document.

## Workflow

1. Use `document_query` directly after this skill is loaded.
2. If the user asks for an answer, summary, comparison, or extraction, pass natural-language questions in `queries`.
3. If the user asks to inspect raw contents or you need to see the extracted text first, omit `queries`.
4. For multiple documents, pass a list in `document` and ask comparison or extraction questions in `queries`.
5. Keep parser/runtime details internal. Do not tell the user which parser, OCR runtime, or fallback path was used unless they explicitly ask about internals.
6. Answer from the returned document evidence. If the document does not contain the answer, say that it is not found in the document.

## Examples

### Return Extracted Content

```json
{
    "thoughts": [
        "The user wants the document text, so I should extract the content."
    ],
    "headline": "Extracting document content",
    "tool_name": "document_query",
    "tool_args": {
        "document": "/a0/usr/workdir/report.pdf"
    }
}
```

### Answer Questions Over A Document

```json
{
    "thoughts": [
        "The user asks questions whose answers should come from the PDF."
    ],
    "headline": "Answering questions from the document",
    "tool_name": "document_query",
    "tool_args": {
        "document": "/a0/usr/workdir/report.pdf",
        "queries": [
            "What is the report's main conclusion?",
            "What dates or deadlines does it mention?"
        ]
    }
}
```

### Compare Multiple Documents

```json
{
    "thoughts": [
        "The user wants a comparison across two source documents."
    ],
    "headline": "Comparing documents",
    "tool_name": "document_query",
    "tool_args": {
        "document": [
            "https://example.com/policy-2025.pdf",
            "/a0/usr/workdir/policy-2026.pdf"
        ],
        "queries": [
            "Compare the main changes between the two documents.",
            "Which requirements appear only in the second document?"
        ]
    }
}
```

### OCR Or Q&A Over A Document Image

```json
{
    "thoughts": [
        "The user wants text from a scanned document image."
    ],
    "headline": "Reading text from the scanned document",
    "tool_name": "document_query",
    "tool_args": {
        "document": "/a0/usr/workdir/scan.png",
        "queries": [
            "What text is visible in the document?",
            "What is the document title?"
        ]
    }
}
```

### Code File Q&A

```json
{
    "thoughts": [
        "The user asks about specific code files, so I can query those files as documents."
    ],
    "headline": "Answering from code files",
    "tool_name": "document_query",
    "tool_args": {
        "document": [
            "/a0/usr/workdir/src/app.py",
            "/a0/usr/workdir/src/config.py"
        ],
        "queries": [
            "Where is the database connection configured?",
            "Which environment variables are required?"
        ]
    }
}
```
