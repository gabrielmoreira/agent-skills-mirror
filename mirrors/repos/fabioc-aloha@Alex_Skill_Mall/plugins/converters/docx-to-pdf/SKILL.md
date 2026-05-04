---
type: skill
lifecycle: stable
inheritance: inheritable
name: docx-to-pdf
description: Convert Word documents (.docx) to PDF. Preserves headings, paragraphs, lists, tables, and inline images with best-effort layout fidelity.
tier: standard
applyTo: '**/*pdf*,**/*docx*,**/*convert*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Convert Word Document to PDF

Convert `.docx` files to PDF with preserved structure and formatting.

## When to Use

- User provides a `.docx` file and wants a PDF version
- User says "convert to PDF", "export as PDF", "make a PDF from this Word doc"
- User needs a portable read-only version of a Word document

## How to Respond

### Step 1: Validate the input file

Confirm the file exists and is a `.docx` (ZIP-based OOXML) file.
Legacy `.doc` (OLE2 binary) files are **not supported** — ask the user to
re-save as `.docx` from Word first.

### Step 2: Run the converter

```bash
python plugins/docx-to-pdf/scripts/venv-run.py plugins/docx-to-pdf/scripts/docx-to-pdf.py "<input.docx>" -o "<output.pdf>"
```

If `-o` is omitted, the PDF is written alongside the input file with the same
stem (e.g., `report.docx` → `report.pdf`).

### Step 3: Review the output

Open the generated PDF and confirm the content looks correct.

## Supported Content

| Word Element         | PDF Output                         |
|----------------------|------------------------------------|
| Title / Heading 1-4  | Bold headings with scaled font sizes |
| Normal paragraph     | Wrapped body text                  |
| Bold / Italic        | Inline formatting preserved        |
| Bullet list          | • prefixed items                   |
| Numbered list        | Numbered items                     |
| Table                | Grid table with borders            |
| Inline image         | Embedded and scaled to fit page    |

## Limitations

- This is a **best-effort content export**, not a pixel-perfect Word renderer
- Complex layouts (columns, text boxes, SmartArt) are not supported
- Headers/footers from the Word document are not transferred
- Page breaks are respected but section-level formatting is simplified
- Legacy `.doc` files must be converted to `.docx` first
