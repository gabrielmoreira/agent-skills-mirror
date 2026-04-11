---
name: pdf
description: Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining or merging multiple PDFs into one, splitting PDFs apart, rotating pages, adding watermarks, creating new PDFs, filling PDF forms, encrypting/decrypting PDFs, extracting images, and OCR on scanned PDFs to make them searchable. If the user mentions a .pdf file or asks to produce one, use this skill.
license: Proprietary. LICENSE.txt has complete terms
---

# PDF Processing Guide

## Overview

This guide covers essential PDF processing operations using Python libraries and command-line tools. For advanced features, JavaScript libraries, and detailed examples, see REFERENCE.md. If you need to fill out a PDF form, read FORMS.md and follow its instructions.

## ⚠️ Important: Avoid Common Mistakes

**Problem**: PDF content overflow, missing text, no line wrapping

**Root Cause**: Using `drawString()` instead of `Paragraph()`

**❌ Wrong**:
```python
c = canvas.Canvas("output.pdf")
c.drawString(100, 750, "Long text will overflow and be lost...")
```

**✅ Correct**:
```python
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import ParagraphStyle

doc = SimpleDocTemplate("output.pdf")
style = ParagraphStyle('Custom', fontName='STSong-Light', fontSize=11)
story = [Paragraph("Long text will wrap automatically", style)]
doc.build(story)
```

**📖 See**: [BEST_PRACTICES.md](BEST_PRACTICES.md) for detailed solutions

## Quick Start

### Creating PDFs (Recommended Approach)

```python
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# Register Chinese font
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

# Create document
doc = SimpleDocTemplate("output.pdf", pagesize=A4,
                       rightMargin=2*cm, leftMargin=2*cm,
                       topMargin=2*cm, bottomMargin=2*cm)

# Create style
style = ParagraphStyle(
    'CustomBody',
    fontName='STSong-Light',
    fontSize=11,
    leading=16,
    firstLineIndent=22
)

# Build content
story = []
story.append(Paragraph("标题文本", ParagraphStyle('Title', fontName='STSong-Light', fontSize=18)))
story.append(Paragraph("正文内容会自动换行，不会超出页面边界。", style))

# Generate PDF
doc.build(story)
```

**Key Points**:
- ✅ Use `Paragraph` for automatic line wrapping
- ✅ Use `SimpleDocTemplate` for proper margins
- ✅ Register `STSong-Light` for Chinese text
- ✅ Use `Times-Roman` for English text (PDF built-in, no registration needed)

### Reading PDFs

```python
from pypdf import PdfReader

# Read a PDF
reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# Extract text
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## Chinese Font Support

This skill includes intelligent font support with automatic font selection for Chinese and English text.

### Available Fonts

**Primary Fonts (Recommended)**:
- **STSong-Light (宋体)** - CIDFont, built-in to PDF readers, no file needed
- **Times-Roman (新罗马)** - PDF built-in font, similar to Times New Roman, no file needed

**Fallback Fonts (TTF/OTF)**:
- **Noto Serif CJK SC (宋体)** - OTF version, requires font file
- **Noto Sans CJK (黑体)** - Alternative Chinese font
- **WenQuanYi Zen Hei (文泉驿正黑)** - Alternative Chinese font
- **WenQuanYi Micro Hei (文泉驿微米黑)** - Lightweight Chinese font
- **Liberation Serif** - TTF version of Times New Roman

### Why CIDFont is Better

**STSong-Light (CIDFont)** advantages:
- ✅ **No font files needed** - Built into PDF readers
- ✅ **Smaller PDF files** - No font embedding required
- ✅ **Perfect compatibility** - Standard Adobe CID font
- ✅ **Full Unicode support** - Complete Chinese character set
- ✅ **Faster processing** - No font file loading
- ✅ **Avoids TTC errors** - No TTC format compatibility issues

### ⚠️ Important: TTC File Format Issue

**Problem**: ReportLab does not support TTC (TrueType Collection) font files.
- Error: `TTFError: TTC file "xxx.ttc": postscript outlines are not supported`
- TTC files like `NotoSerifCJK-Regular.ttc` cannot be used directly

**Solution**:
1. **Use CIDFont (STSong-Light)** - Recommended, no file needed
2. **Use OTF or TTF format** - Supported by ReportLab
3. **This skill automatically skips TTC files** - Prevents errors

**Supported Font Formats**:
| Format | Support | Description |
|--------|---------|-------------|
| CIDFont | ✅ Recommended | Built-in to PDF readers |
| OTF | ✅ Supported | OpenType fonts |
| TTF | ✅ Supported | TrueType fonts |
| TTC | ❌ Not supported | TrueType Collection, causes errors |

### Font Selection Rules

The system automatically selects fonts based on text content:
- **Chinese characters** → STSong-Light (宋体 CIDFont, PDF built-in)
- **English text and numbers** → Times-Roman (新罗马, PDF built-in)

**Important**: Both fonts are built into PDF readers - no font files needed!

### Register Fonts

```python
import sys
sys.path.append('scripts')
from register_fonts import register_chinese_fonts, get_chinese_font_name, get_english_font_name

# Register all available fonts
# Priority: CIDFont (STSong-Light) > TTF fonts
registered = register_chinese_fonts()

# Get recommended fonts
chinese_font = get_chinese_font_name()  # STSong-Light (CIDFont, PDF built-in)
english_font = get_english_font_name()  # Times-Roman (PDF built-in)
print(f"Chinese font: {chinese_font}")
print(f"English font: {english_font}")
```

**Note**: Both fonts are PDF built-in fonts, no font files needed!

### Using Fonts in PDF Creation

#### With reportlab (Built-in Fonts - Recommended)

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# Register CIDFont for Chinese (no font file needed!)
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

# Create document with proper margins
doc = SimpleDocTemplate("output.pdf", pagesize=letter,
                       rightMargin=2*cm, leftMargin=2*cm,
                       topMargin=2*cm, bottomMargin=2*cm)

# Create styles
styles = getSampleStyleSheet()
body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['Normal'],
    fontName='STSong-Light',  # Chinese font
    fontSize=11,
    leading=16,
    firstLineIndent=22  # First line indent
)

# Build content with automatic line wrapping
story = []
story.append(Paragraph("中文内容会自动换行，不会超出页面边界。", body_style))
story.append(Paragraph("English content with Times-Roman will also wrap automatically.", 
                      ParagraphStyle('English', fontName='Times-Roman', fontSize=11)))

doc.build(story)
```

**Key Points**:
- Use `Paragraph` instead of `drawString` for automatic line wrapping
- `STSong-Light` is a CIDFont, requires registration but no font file
- `Times-Roman` is a PDF built-in font, no registration needed
- Both fonts are built into PDF readers, no font files needed!

#### ⚠️ Common Mistakes to Avoid

**❌ Wrong: Using drawString (no auto-wrap)**
```python
# This will cause text to overflow page boundaries
c = canvas.Canvas("output.pdf", pagesize=letter)
c.setFont('STSong-Light', 12)
c.drawString(100, 750, "很长的文本不会自动换行，会超出页面边界导致内容丢失...")
```

**✅ Correct: Using Paragraph (auto-wrap)**
```python
# This will automatically wrap text within margins
doc = SimpleDocTemplate("output.pdf", pagesize=letter)
story = [Paragraph("很长的文本会自动换行，不会超出页面边界。", body_style)]
doc.build(story)
```

#### With reportlab (TTF - Fallback)

```python
from reportlab.pdfbase.ttfonts import TTFont

# Register TTF font (requires font file)
pdfmetrics.registerFont(TTFont('NotoSerifCJK', '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'))
pdfmetrics.registerFont(TTFont('TimesNewRoman', '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'))

# Use in canvas
c = canvas.Canvas("mixed.pdf", pagesize=letter)
c.setFont('NotoSerifCJK', 14)
c.drawString(100, 750, "中文内容")
c.setFont('TimesNewRoman', 14)
c.drawString(100, 720, "English Content 123")
c.save()
```

#### With pypdf (Form Filling)

When filling PDF forms, the system automatically detects text type and uses the appropriate font:

```python
# The fill_pdf_form_with_annotations.py script automatically:
# 1. Detects Chinese characters in text
# 2. Uses STSong-Light (CIDFont) for Chinese text
# 3. Uses Times-Roman for English text and numbers

# In your fields.json:
{
  "form_fields": [
    {
      "entry_text": {
        "text": "张三",  // Will use STSong-Light (CIDFont)
        "font_size": 12
      }
    },
    {
      "entry_text": {
        "text": "John Smith",  // Will use Times-Roman
        "font_size": 12
      }
    }
  ]
}
```

## Advanced Features

### Creating PDFs from Markdown (Optional)

If you have markdown content and want to convert it to PDF with automatic formatting:

```python
from markdown_to_pdf import markdown_to_pdf, markdown_file_to_pdf

# From markdown text
markdown_text = """
# 标题

## 二级标题

正文内容会自动换行...

**粗体文本** 和普通文本。
"""

markdown_to_pdf(markdown_text, "output.pdf", title="文档标题")

# Or from markdown file
markdown_file_to_pdf("input.md", "output.pdf")
```

**Features**:
- ✅ Automatic line wrapping
- ✅ Markdown format support (headers, bold, lists)
- ✅ Proper page margins
- ✅ Chinese and English font support

**Note**: This is an optional helper tool. For most cases, use the direct `Paragraph` approach shown above.

## Common Tasks

To see all available fonts in the system:

```bash
# Run from the pdf skill directory
python scripts/register_fonts.py
```

This will display all registered fonts and the recommended fonts for Chinese and English text.

## Python Libraries

### pypdf - Basic Operations

#### Merge PDFs
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### Split PDF
```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

#### Extract Metadata
```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
print(f"Subject: {meta.subject}")
print(f"Creator: {meta.creator}")
```

#### Rotate Pages
```python
reader = PdfReader("input.pdf")
writer = PdfWriter()

page = reader.pages[0]
page.rotate(90)  # Rotate 90 degrees clockwise
writer.add_page(page)

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - Text and Table Extraction

#### Extract Text with Layout
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### Extract Tables
```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"Table {j+1} on page {i+1}:")
            for row in table:
                print(row)
```

#### Advanced Table Extraction
```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:  # Check if table is not empty
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# Combine all tables
if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - Create PDFs

#### Basic PDF Creation
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter

# Add text
c.drawString(100, height - 100, "Hello World!")
c.drawString(100, height - 120, "This is a PDF created with reportlab")

# Add a line
c.line(100, height - 140, 400, height - 140)

# Save
c.save()
```

#### Create PDF with Multiple Pages
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

# Add content
title = Paragraph("Report Title", styles['Title'])
story.append(title)
story.append(Spacer(1, 12))

body = Paragraph("This is the body of the report. " * 20, styles['Normal'])
story.append(body)
story.append(PageBreak())

# Page 2
story.append(Paragraph("Page 2", styles['Heading1']))
story.append(Paragraph("Content for page 2", styles['Normal']))

# Build PDF
doc.build(story)
```

#### Subscripts and Superscripts

**IMPORTANT**: Never use Unicode subscript/superscript characters (₀₁₂₃₄₅₆₇₈₉, ⁰¹²³⁴⁵⁶⁷⁸⁹) in ReportLab PDFs. The built-in fonts do not include these glyphs, causing them to render as solid black boxes.

Instead, use ReportLab's XML markup tags in Paragraph objects:
```python
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()

# Subscripts: use <sub> tag
chemical = Paragraph("H<sub>2</sub>O", styles['Normal'])

# Superscripts: use <super> tag
squared = Paragraph("x<super>2</super> + y<super>2</super>", styles['Normal'])
```

For canvas-drawn text (not Paragraph objects), manually adjust font the size and position rather than using Unicode subscripts/superscripts.

## Command-Line Tools

### pdftotext (poppler-utils)
```bash
# Extract text
pdftotext input.pdf output.txt

# Extract text preserving layout
pdftotext -layout input.pdf output.txt

# Extract specific pages
pdftotext -f 1 -l 5 input.pdf output.txt  # Pages 1-5
```

### qpdf
```bash
# Merge PDFs
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Split pages
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf --pages . 6-10 -- pages6-10.pdf

# Rotate pages
qpdf input.pdf output.pdf --rotate=+90:1  # Rotate page 1 by 90 degrees

# Remove password
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```

### pdftk (if available)
```bash
# Merge
pdftk file1.pdf file2.pdf cat output merged.pdf

# Split
pdftk input.pdf burst

# Rotate
pdftk input.pdf rotate 1east output rotated.pdf
```

## Common Tasks

### Extract Text from Scanned PDFs
```python
# Requires: pip install pytesseract pdf2image
import pytesseract
from pdf2image import convert_from_path

# Convert PDF to images
images = convert_from_path('scanned.pdf')

# OCR each page
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"

print(text)
```

### Add Watermark
```python
from pypdf import PdfReader, PdfWriter

# Create watermark (or load existing)
watermark = PdfReader("watermark.pdf").pages[0]

# Apply to all pages
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### Extract Images
```bash
# Using pdfimages (poppler-utils)
pdfimages -j input.pdf output_prefix

# This extracts all images as output_prefix-000.jpg, output_prefix-001.jpg, etc.
```

### Password Protection
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# Add password
writer.encrypt("userpassword", "ownerpassword")

with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

## Quick Reference

| Task | Best Tool | Command/Code |
|------|-----------|--------------|
| Merge PDFs | pypdf | `writer.add_page(page)` |
| Split PDFs | pypdf | One page per file |
| Extract text | pdfplumber | `page.extract_text()` |
| Extract tables | pdfplumber | `page.extract_tables()` |
| Create PDFs | reportlab | Canvas or Platypus |
| Command line merge | qpdf | `qpdf --empty --pages ...` |
| OCR scanned PDFs | pytesseract | Convert to image first |
| Fill PDF forms | pdf-lib or pypdf (see FORMS.md) | See FORMS.md |

## Next Steps

- For advanced pypdfium2 usage, see REFERENCE.md
- For JavaScript libraries (pdf-lib), see REFERENCE.md
- If you need to fill out a PDF form, follow the instructions in FORMS.md
- For troubleshooting guides, see REFERENCE.md
