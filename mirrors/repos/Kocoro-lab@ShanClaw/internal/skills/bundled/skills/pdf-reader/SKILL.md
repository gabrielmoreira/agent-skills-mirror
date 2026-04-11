---
name: pdf-reader
description: Analyze PDF files attached by the user. Activates automatically when user uploads a PDF. Handles both text-based and scanned/image-based PDFs using file_read's built-in PDF rendering.
allowed-tools: file_read bash think
---

# PDF Reader

Analyze PDF files using the `file_read` tool which natively supports PDF rendering.

## How file_read handles PDFs

- `file_read` with a `.pdf` path renders pages as images for vision analysis
- Parameters: `offset` = start page (0-based), `limit` = max pages (default 5)
- Each page is rendered at 144 DPI, resized to 1568px max dimension
- Returns image blocks that you can analyze with vision

## Workflow

1. **Read the PDF**: Call `file_read` with the PDF path. It will render pages as images automatically.
   ```json
   {"path": "/path/to/file.pdf"}
   ```

2. **For multi-page PDFs**: Read in batches using offset and limit.
   ```json
   {"path": "/path/to/file.pdf", "offset": 5, "limit": 5}
   ```

3. **Analyze the content**: The rendered pages come back as images. Describe what you see — text, tables, charts, forms, signatures, stamps, etc.

4. **Extract text if needed**: For text-heavy PDFs where you need exact content, use bash with python:
   ```bash
   python3 -c "
   import subprocess
   subprocess.check_call(['pip3', 'install', 'pymupdf', '-q'])
   import fitz
   doc = fitz.open('/path/to/file.pdf')
   for i, page in enumerate(doc):
       text = page.get_text()
       if text.strip():
           print(f'--- Page {i+1} ---')
           print(text)
   "
   ```

## Tips

- Always start with `file_read` — it handles both scanned and text PDFs via vision
- For scanned PDFs (image-based), vision analysis through `file_read` is the primary method
- For text PDFs where exact character-level accuracy matters, supplement with python text extraction
- When summarizing, note the total page count and which pages you've analyzed
