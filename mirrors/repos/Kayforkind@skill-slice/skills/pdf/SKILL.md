---
name: pdf
version: 1.1.1
description: "Programmatically extracts, creates, merges, splits, OCRs, encrypts, and form-fills PDFs with pypdf, pdfplumber, reportlab, and pytesseract. Use when a PDF needs code-driven processing rather than manual edits. Not for double-blind author redaction (academic-pdf-redaction) or in-place prose rewriting of a laid-out PDF."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# PDF Processing Guide

## When to Use

Reach for this skill whenever a PDF needs to be processed by code rather than by hand. PDFs are everywhere (invoices, reports, forms, scans), but the format is a *presentation* format: its bytes describe where glyphs and images sit on a page, not a clean data model. That mismatch is why these tasks need dedicated libraries instead of plain string manipulation.

Typical jobs:

- Extracting text and tables from PDF documents for downstream analysis
- Creating new PDFs programmatically (reports, summaries, exports)
- Merging multiple PDFs into one, or splitting one into individual pages
- Filling out PDF forms (load `forms.md` when the task involves AcroForms or field filling)
- Rotating, watermarking, or password-protecting PDFs
- Converting scanned (image-only) PDFs to searchable text via OCR
- Extracting embedded images from PDFs
- Batch-processing large numbers of PDF files

## Prerequisites

### Python libraries (install via pip)

```powershell
pip install pypdf pdfplumber reportlab pandas openpyxl pytesseract pdf2image Pillow
```

### System binaries (not pip-installable — probe before use)

| Binary | Purpose | How to check (PowerShell) |
|--------|---------|--------------------------|
| Tesseract | OCR engine for pytesseract | `tesseract --version` |
| Poppler (`pdftoppm`, `pdftotext`, `pdfimages`) | Rasterization and text extraction for pdf2image | `pdftotext -v` |
| qpdf | Command-line merge/split/decrypt | `qpdf --version` |
| pdftk | Command-line form manipulation | `pdftk --version` |

> **HARD RULE:** Command-line tools (qpdf, pdftk, pdftotext) are not guaranteed on every host. Check with `shutil.which()` and prefer the pure-Python libraries when a binary is absent, so the same script runs in every environment.

> **HARD RULE:** Pin to current, maintained libraries. pypdf supersedes the abandoned PyPDF2. Staying current is how you receive security fixes and features such as AES-256 encryption.

## Procedure

### Tool selection guide

These are guidelines with reasons — knowing the "why" lets you judge edge cases:

| Job | Tool | Why |
|-----|------|-----|
| Read text/tables | **pdfplumber** | Places each character by x/y coordinates, preserving reading order and table structure |
| Merge/split/rotate/encrypt | **pypdf** | Manipulates pages as opaque objects — fast, lossless, never inspects content |
| Create new PDFs | **reportlab** | Canvas (pixel-precise) or Platypus (flowing text with auto-pagination) |
| OCR scanned PDFs | **pytesseract + pdf2image** | Scanned PDFs have no text layer; `extract_text()` returns empty strings |
| Fill PDF forms | **pypdf / pdf-lib** | See `forms.md` for AcroForm field filling |
| Command-line merge | **qpdf** | Fast one-off when installed |

> **HARD RULE:** PDFs are a fixed output, not an editable source. Content is positioned glyph-by-glyph with no paragraph model, so editing text "in place" is fragile and usually corrupts layout. For genuine content changes, regenerate the document from its original source (or rebuild it with reportlab) rather than patching the PDF.

> **HARD RULE:** Prefer pdfplumber over pypdf for layout-sensitive extraction. pypdf reads text in content-stream order, which interleaves columns and breaks tables.

> **HARD RULE:** Scanned/image-only PDFs have no text layer. `extract_text()` returns empty strings for them — that is not a failure to retry, it is a signal to fall back to OCR (pytesseract + pdf2image). Detect the empty result and branch.

> **HARD RULE:** OCR and rasterization need system binaries, not just pip packages. pytesseract requires Tesseract; pdf2image, `pdftotext`, and `pdfimages` require Poppler. Probe for them and degrade gracefully instead of assuming they exist.

> **HARD RULE:** XFA / LiveCycle dynamic forms are not standard AcroForms. pypdf and pdf-lib cannot fill them reliably. Use a dedicated XFA-capable tool, or flatten the form first (see `forms.md`).

### Reference files — when to load

| File | Load when |
|------|-----------|
| `forms.md` | Task involves filling PDF form fields, flattening forms, or handling AcroForms/XFA |
| `reference.md` | Need advanced pypdfium2 usage, JavaScript libraries (pdf-lib), or troubleshooting guidance |

### Step 1: Quick-start text extraction (guard against bad inputs)

This minimal reader doubles as a guard: it tells you up front whether a file is present, readable, and text-based before you invest in heavier processing.

```python
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


def load_pdf_text(pdf_path: str | Path) -> str:
    """Return the concatenated text of every page in a PDF.

    pdfplumber gives better layout fidelity, but pypdf is the lightest way to
    confirm a file is a readable, non-encrypted, text-based PDF before doing
    heavier work.
    """
    path = Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(f"No PDF found at: {path}")

    reader = PdfReader(str(path))
    # Many "protected" PDFs are decryptable with an empty password; a falsy
    # result means a real password is required, so fail clearly.
    if reader.is_encrypted and not reader.decrypt(""):
        raise PermissionError(f"PDF is password protected: {path}")

    pages_text: list[str] = []
    for page in reader.pages:
        # extract_text() returns None for pages with no text layer (e.g. a
        # scan), so coerce to "" to keep the return type a clean list[str].
        pages_text.append(page.extract_text() or "")

    return "\n".join(pages_text)


if __name__ == "__main__":
    document_text = load_pdf_text("document.pdf")
    print(f"Extracted {len(document_text)} characters")
```

### Step 2: Structural operations with pypdf

pypdf manipulates pages as opaque objects — exactly what you want for merging, splitting, rotating, and encrypting. It never needs to understand the content, so it is fast and lossless.

#### Merge PDFs

```python
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter


def merge_pdfs(input_paths: list[str | Path], output_path: str | Path) -> Path:
    """Concatenate several PDFs into one, preserving page order.

    Inputs are validated up front so the job fails fast instead of writing a
    half-merged file and only then erroring on a missing input.
    """
    if not input_paths:
        raise ValueError("merge_pdfs requires at least one input PDF")

    resolved_inputs: list[Path] = [Path(p) for p in input_paths]
    missing: list[str] = [str(p) for p in resolved_inputs if not p.is_file()]
    if missing:
        raise FileNotFoundError(f"Input PDF(s) not found: {', '.join(missing)}")

    writer = PdfWriter()
    for pdf_path in resolved_inputs:
        for page in PdfReader(str(pdf_path)).pages:
            writer.add_page(page)

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as output_file:
        writer.write(output_file)

    return destination
```

#### Split a PDF into one file per page

```python
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter


def split_pdf(input_path: str | Path, output_dir: str | Path) -> list[Path]:
    """Write each page of a PDF to its own single-page file.

    Returns the list of created paths so callers can log or post-process them
    instead of reconstructing the filenames by hand.
    """
    source = Path(input_path)
    if not source.is_file():
        raise FileNotFoundError(f"No PDF found at: {source}")

    destination_dir = Path(output_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(source))
    written: list[Path] = []
    for page_number, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)
        page_path = destination_dir / f"{source.stem}_page_{page_number}.pdf"
        with page_path.open("wb") as output_file:
            writer.write(output_file)
        written.append(page_path)

    return written
```

#### Read metadata safely

Metadata is optional in the PDF spec, and individual fields are frequently absent. Normalising everything into a plain dict means callers never have to guard against a missing metadata object.

```python
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


def read_metadata(pdf_path: str | Path) -> dict[str, str | None]:
    """Return common document metadata fields, with None for any that are absent."""
    path = Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(f"No PDF found at: {path}")

    metadata = PdfReader(str(path)).metadata
    if metadata is None:
        return {"title": None, "author": None, "subject": None, "creator": None}

    return {
        "title": metadata.title,
        "author": metadata.author,
        "subject": metadata.subject,
        "creator": metadata.creator,
    }
```

#### Rotate pages

PDF page rotation is stored as metadata and only accepts right-angle multiples. Validating the argument turns a confusing downstream error into a clear one.

```python
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter


def rotate_pdf(
    input_path: str | Path,
    output_path: str | Path,
    degrees: int = 90,
) -> Path:
    """Rotate every page clockwise by a multiple of 90 degrees."""
    if degrees % 90 != 0:
        raise ValueError(f"degrees must be a multiple of 90, got {degrees}")

    source = Path(input_path)
    if not source.is_file():
        raise FileNotFoundError(f"No PDF found at: {source}")

    reader = PdfReader(str(source))
    writer = PdfWriter()
    for page in reader.pages:
        page.rotate(degrees)
        writer.add_page(page)

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as output_file:
        writer.write(output_file)

    return destination
```

#### Add a watermark to every page

`merge_page` overlays the watermark in place, so the watermark PDF needs a *transparent* background — otherwise it paints over the underlying text instead of sitting behind it.

```python
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter


def apply_watermark(
    input_path: str | Path,
    watermark_path: str | Path,
    output_path: str | Path,
) -> Path:
    """Stamp a single-page watermark onto every page of a document."""
    source = Path(input_path)
    stamp = Path(watermark_path)
    for required in (source, stamp):
        if not required.is_file():
            raise FileNotFoundError(f"Required PDF not found: {required}")

    watermark_reader = PdfReader(str(stamp))
    if not watermark_reader.pages:
        raise ValueError(f"Watermark PDF has no pages: {stamp}")
    watermark_page = watermark_reader.pages[0]

    reader = PdfReader(str(source))
    writer = PdfWriter()
    for page in reader.pages:
        page.merge_page(watermark_page)
        writer.add_page(page)

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as output_file:
        writer.write(output_file)

    return destination
```

#### Password-protect a PDF

The user password gates *opening* the file; the owner password gates *permissions* (editing, printing). If you reuse one value for both, anyone who can open the document can also strip its restrictions — so a distinct owner password is the safer default.

```python
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter


def encrypt_pdf(
    input_path: str | Path,
    output_path: str | Path,
    user_password: str,
    owner_password: str | None = None,
) -> Path:
    """Encrypt a PDF with AES-256 using distinct open and permission passwords."""
    if not user_password:
        raise ValueError("user_password must be a non-empty string")

    source = Path(input_path)
    if not source.is_file():
        raise FileNotFoundError(f"No PDF found at: {source}")

    reader = PdfReader(str(source))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(
        user_password=user_password,
        owner_password=owner_password or user_password,
        algorithm="AES-256",
    )

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as output_file:
        writer.write(output_file)

    return destination
```

### Step 3: Text and table extraction with pdfplumber

pdfplumber is the right tool whenever you need to *read* a PDF, because it models character positions. That coordinate awareness is what lets it keep columns, spacing, and table grids intact.

#### Extract text per page, preserving layout

```python
from __future__ import annotations

from pathlib import Path

import pdfplumber


def extract_text_by_page(pdf_path: str | Path) -> list[str]:
    """Extract text for each page in reading order.

    An all-empty result usually means the PDF is a scan with no text layer —
    that is the cue to fall back to OCR (see ocr_pdf below).
    """
    path = Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(f"No PDF found at: {path}")

    pages_text: list[str] = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            pages_text.append(page.extract_text() or "")

    return pages_text
```

#### Extract tables, keyed by page

Returning a dict keyed by page number keeps provenance: when a value looks wrong, you can trace it to the exact page instead of hunting through a flat, anonymous list. A table cell is `str | None` because empty or merged grid positions have no value.

```python
from __future__ import annotations

from pathlib import Path

import pdfplumber

# One extracted table: rows of cells, where a cell is None for an empty position.
Table = list[list[str | None]]


def extract_tables_by_page(pdf_path: str | Path) -> dict[int, list[Table]]:
    """Return every detected table, grouped by its 1-based page number."""
    path = Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(f"No PDF found at: {path}")

    tables_by_page: dict[int, list[Table]] = {}
    with pdfplumber.open(str(path)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            tables: list[Table] = page.extract_tables()
            if tables:
                tables_by_page[page_number] = tables

    return tables_by_page
```

#### Collect every table into one spreadsheet

The header handling here is defensive on purpose: a header row with empty cells usually means the detector merged two adjacent tables, and forcing it as column names would silently misalign the data. In that case we fall back to positional integer columns instead.

```python
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pdfplumber


def tables_to_excel(pdf_path: str | Path, excel_path: str | Path) -> Path:
    """Write all tables from a PDF into a single Excel sheet."""
    source = Path(pdf_path)
    if not source.is_file():
        raise FileNotFoundError(f"No PDF found at: {source}")

    frames: list[pd.DataFrame] = []
    with pdfplumber.open(str(source)) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                if not table or len(table) < 2:
                    continue  # need a header row plus at least one data row
                header_row: list[str | None] = table[0]
                if any(cell is None for cell in header_row):
                    frames.append(pd.DataFrame(table))  # positional columns
                    continue
                columns: list[str] = [str(cell) for cell in header_row]
                frames.append(pd.DataFrame(table[1:], columns=columns))

    if not frames:
        raise ValueError(f"No tables detected in {source}")

    combined = pd.concat(frames, ignore_index=True)
    destination = Path(excel_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    combined.to_excel(destination, index=False)
    return destination
```

### Step 4: Creating PDFs with reportlab

reportlab offers two levels. The low-level **canvas** gives pixel-precise control but no layout help; the high-level **platypus** flowables handle pagination and wrapping for you. Choose canvas for fixed graphics (labels, stamps, figures) and platypus for flowing text (reports, letters).

#### Canvas: precise placement

> **GOTCHA:** The canvas origin is the *bottom* left, so y grows upward. Measuring from `page_height` downward is what keeps text on the page.

```python
from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen.canvas import Canvas


def create_simple_pdf(output_path: str | Path, lines: list[str]) -> Path:
    """Draw a list of text lines onto a PDF, paginating when a page fills up."""
    if not lines:
        raise ValueError("create_simple_pdf requires at least one line of text")

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    page_height: float = letter[1]
    canvas = Canvas(str(destination), pagesize=letter)

    left_margin = 72.0     # 1 inch, expressed in points
    top_margin = 72.0
    bottom_margin = 72.0
    line_height = 18.0

    y_position = page_height - top_margin
    for line in lines:
        if y_position < bottom_margin:
            canvas.showPage()              # start a fresh page
            y_position = page_height - top_margin
        canvas.drawString(left_margin, y_position, line)
        y_position -= line_height

    canvas.save()
    return destination
```

#### Platypus: flowing multi-page documents

```python
from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Flowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


def create_report(output_path: str | Path, title: str, body: str) -> Path:
    """Build a flowing, multi-page report.

    Platypus lays out pages from a list of "flowables", so you describe content
    and let it handle wrapping and page breaks — far less error-prone than
    positioning every line on a raw canvas.
    """
    if not title.strip():
        raise ValueError("Report title must not be empty")

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()
    story: list[Flowable] = [
        Paragraph(title, styles["Title"]),
        Spacer(1, 12),
        Paragraph(body, styles["Normal"]),
        PageBreak(),
        Paragraph("Appendix", styles["Heading1"]),
        Paragraph("Supplementary content continues here.", styles["Normal"]),
    ]

    SimpleDocTemplate(str(destination), pagesize=letter).build(story)
    return destination
```

#### Embed an image (PNG/JPG) into a PDF

```python
from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas


def embed_image_in_pdf(
    image_path: str | Path,
    output_path: str | Path,
    x: float = 72.0,
    y: float = 72.0,
    width: float = 400.0,
    height: float = 300.0,
) -> Path:
    """Place an image at fixed coordinates on a single-page PDF."""
    source = Path(image_path)
    if not source.is_file():
        raise FileNotFoundError(f"No image found at: {source}")

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    canvas = Canvas(str(destination), pagesize=letter)
    canvas.drawImage(ImageReader(str(source)), x, y, width=width, height=height)
    canvas.save()
    return destination
```

> **Optional — scientific-schematics skill:** A PDF that explains a *process* — an extraction pipeline, form-routing logic, an approval workflow — is often easier to follow with a diagram. If the separate **scientific-schematics** skill is installed, you can generate a figure from a natural-language description and embed it with the helper above. This PDF skill does **not** render diagrams itself. Do not invoke a diagram generator that is not present. Skip diagrams for simple or text-only documents where they only add noise.

### Step 5: OCR for scanned PDFs

Scanned/image-only PDFs have no text layer. `extract_text()` returns empty strings — that is not a failure to retry, it is a signal to fall back to OCR.

```python
from __future__ import annotations

from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from PIL.Image import Image


def ocr_pdf(
    pdf_path: str | Path,
    dpi: int = 300,
) -> str:
    """OCR every page of a scanned PDF and return the combined text."""
    source = Path(pdf_path)
    if not source.is_file():
        raise FileNotFoundError(f"No PDF found at: {source}")

    pages: list[Image] = convert_from_path(str(source), dpi=dpi)
    extracted: list[str] = [pytesseract.image_to_string(image) for image in pages]

    return "\n\n".join(extracted)


def ocr_to_textfile(
    pdf_path: str | Path,
    text_path: str | Path,
    dpi: int = 300,
) -> Path:
    """OCR every page of a scanned PDF and save the combined text as UTF-8."""
    source = Path(pdf_path)
    if not source.is_file():
        raise FileNotFoundError(f"No PDF found at: {source}")

    pages: list[Image] = convert_from_path(str(source), dpi=dpi)
    extracted: list[str] = [pytesseract.image_to_string(image) for image in pages]

    destination = Path(text_path)
    destination.write_text("\n\n".join(extracted), encoding="utf-8")
    return destination
```

### Step 6: Command-line tools (when installed)

Use these for fast one-off jobs. Always probe with `shutil.which()` first.

```bash
# Combine two documents into one. --empty avoids inheriting either file's
# metadata; the closing "--" terminates the --pages argument list.
qpdf --empty --pages first.pdf second.pdf -- merged.pdf
```

## Examples

### Example 1: Merge every PDF in a directory

```python
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter


def merge_directory(folder: str | Path, output_path: str | Path) -> Path:
    """Merge all *.pdf files in a folder, in sorted (stable) filename order."""
    source_dir = Path(folder)
    if not source_dir.is_dir():
        raise NotADirectoryError(f"Not a directory: {source_dir}")

    pdf_files: list[Path] = sorted(source_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDFs found in {source_dir}")

    writer = PdfWriter()
    for pdf_file in pdf_files:
        for page in PdfReader(str(pdf_file)).pages:
            writer.add_page(page)

    destination = Path(output_path)
    with destination.open("wb") as output_file:
        writer.write(output_file)
    return destination


if __name__ == "__main__":
    result = merge_directory("invoices/", "all_invoices.pdf")
    print(f"Merged into {result}")
```

### Example 2: Export the first table on each page to CSV

```python
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pdfplumber


def first_table_to_csv(pdf_path: str | Path, csv_path: str | Path) -> Path:
    """Find the first usable table in a PDF and write it to CSV."""
    source = Path(pdf_path)
    if not source.is_file():
        raise FileNotFoundError(f"No PDF found at: {source}")

    with pdfplumber.open(str(source)) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables and len(tables[0]) >= 2:
                header: list[str] = [str(cell) for cell in tables[0][0]]
                frame = pd.DataFrame(tables[0][1:], columns=header)
                destination = Path(csv_path)
                frame.to_csv(destination, index=False)
                return destination

    raise ValueError(f"No usable table found in {source}")
```

### Example 3: Build a report from titled sections

```python
from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate, Spacer


def build_section_report(
    output_path: str | Path,
    sections: dict[str, str],
) -> Path:
    """Render an ordered mapping of {heading: body} into a multi-section PDF."""
    if not sections:
        raise ValueError("sections must contain at least one heading -> body pair")

    styles = getSampleStyleSheet()
    story: list[Flowable] = []
    for heading, body in sections.items():
        story.append(Paragraph(heading, styles["Heading1"]))
        story.append(Paragraph(body, styles["Normal"]))
        story.append(Spacer(1, 18))

    destination = Path(output_path)
    SimpleDocTemplate(str(destination), pagesize=letter).build(story)
    return destination


if __name__ == "__main__":
    build_section_report(
        "summary.pdf",
        {
            "Overview": "This report summarises Q2 processing throughput.",
            "Details": "Each pipeline stage is described in the sections below.",
        },
    )
```

### Example 4: Command-line merge with qpdf

```bash
qpdf --empty --pages first.pdf second.pdf -- merged.pdf
```

### Example 5: OCR a scanned PDF to a text file

```python
from __future__ import annotations

from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from PIL.Image import Image


def ocr_to_textfile(
    pdf_path: str | Path,
    text_path: str | Path,
    dpi: int = 300,
) -> Path:
    """OCR every page of a scanned PDF and save the combined text as UTF-8."""
    source = Path(pdf_path)
    if not source.is_file():
        raise FileNotFoundError(f"No PDF found at: {source}")

    pages: list[Image] = convert_from_path(str(source), dpi=dpi)
    extracted: list[str] = [pytesseract.image_to_string(image) for image in pages]

    destination = Path(text_path)
    destination.write_text("\n\n".join(extracted), encoding="utf-8")
    return destination
```

### Example 6: Watermark every page of a document

```python
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter


def watermark_all_pages(
    document_path: str | Path,
    watermark_path: str | Path,
    output_path: str | Path,
) -> Path:
    """Overlay a single-page (transparent) watermark on every page."""
    document = Path(document_path)
    stamp = Path(watermark_path)
    for required in (document, stamp):
        if not required.is_file():
            raise FileNotFoundError(f"Required PDF not found: {required}")

    overlay = PdfReader(str(stamp)).pages[0]
    writer = PdfWriter()
    for page in PdfReader(str(document)).pages:
        page.merge_page(overlay)
        writer.add_page(page)

    destination = Path(output_path)
    with destination.open("wb") as output_file:
        writer.write(output_file)
    return destination
```

## Pitfalls

1. **Empty `extract_text()` on scanned PDFs is not a bug — it is a signal.** Do not retry or "fix" it. Branch to OCR (pytesseract + pdf2image) instead.

2. **pypdf reads in content-stream order, not visual order.** Multi-column layouts and tables will be interleaved and garbled. Use pdfplumber for any layout-sensitive extraction.

3. **Editing text in-place corrupts layout.** PDFs have no paragraph model — content is positioned glyph-by-glyph. Regenerate from source or rebuild with reportlab instead of patching.

4. **Watermark PDF must have a transparent background.** `merge_page` overlays in place; an opaque background paints over the underlying text instead of sitting behind it.

5. **reportlab canvas origin is bottom-left.** y grows upward. Measuring from `page_height` downward is what keeps text on the page.

6. **XFA / LiveCycle dynamic forms are not AcroForms.** pypdf and pdf-lib cannot fill them reliably. Use a dedicated XFA-capable tool or flatten first (see `forms.md`).

7. **System binaries are not pip packages.** pytesseract needs Tesseract; pdf2image needs Poppler; qpdf/pdftk/pdftotext are separate installs. Probe with `shutil.which()` and degrade gracefully.

8. **Header rows with empty cells signal merged tables.** Forcing such a row as column names silently misaligns data. Fall back to positional integer columns instead.

9. **Reusing the same password for user and owner defeats permission restrictions.** Anyone who can open the document can also strip its restrictions. Use a distinct owner password.

10. **PyPDF2 is abandoned.** Always use `pypdf` (the maintained successor) to receive security fixes and AES-256 encryption support.

## Verification

Run these checks after changing the skill or before relying on it in a new environment — they confirm both the code and its system dependencies are in place:

```powershell
# 1. Verify Python libraries are installed
python -c "import pypdf, pdfplumber, reportlab, pandas; print('Python libs OK')"

# 2. Verify system binaries (optional but needed for OCR/CLI)
python -c "import shutil; print('tesseract:', shutil.which('tesseract')); print('pdftotext:', shutil.which('pdftotext')); print('qpdf:', shutil.which('qpdf'))"

# 3. Functional checks
python -c "from pypdf import PdfReader; r = PdfReader('test.pdf'); print(f'Pages: {len(r.pages)}, Encrypted: {r.is_encrypted}')"
python -c "import pdfplumber; pdf = pdfplumber.open('test.pdf'); print(f'Text on page 1: {len(pdf.pages[0].extract_text() or \"\")} chars'); pdf.close()"
```

Checklist:

- [ ] `merge_pdfs` produces a combined file and rejects a missing input
- [ ] `split_pdf` writes one file-per-page into the target directory
- [ ] `extract_text_by_page` returns text for a born-digital PDF
- [ ] `extract_tables_by_page` recovers a known table
- [ ] `create_report` / `create_simple_pdf` produce a valid PDF
- [ ] Command-line tools resolve via `shutil.which()` (qpdf, pdftotext) where used
- [ ] `ocr_pdf` returns text for a scanned PDF (Tesseract + Poppler installed)
- [ ] `apply_watermark` overlays a transparent watermark without hiding content
- [ ] `encrypt_pdf` produces a file that requires the password to open
- [ ] All code examples run without raising on valid inputs

## Related skills

- **scientific-schematics** (optional, external) — generates publication-quality diagrams from natural-language descriptions. Useful for embedding workflow or pipeline figures into a PDF, but only when a diagram genuinely aids the reader. This PDF skill does not bundle a diagram generator of its own.
- **forms.md** — PDF form-filling instructions and advanced form handling. Load when the task involves AcroForm fields or XFA forms.
- **reference.md** — advanced pypdfium2 usage, JavaScript libraries (pdf-lib), and troubleshooting guides. Load when you need pypdfium2, pdf-lib, or encounter errors not covered above.
