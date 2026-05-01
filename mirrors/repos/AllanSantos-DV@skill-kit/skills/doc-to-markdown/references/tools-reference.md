# Tools Reference — Document to Markdown Converters

Detailed comparison of all tools referenced in the skill. Use this to decide which tool fits a specific scenario.

---

## Primary Tool

### markitdown (Microsoft)

- **Install**: `pip install markitdown` or `pip install 'markitdown[all]'`
- **Type**: Python library + CLI
- **License**: MIT
- **Repository**: https://github.com/microsoft/markitdown

**Supported formats**: .docx, .doc, .xlsx, .xls, .csv, .pptx, .ppt, .pdf, .html, .htm, .epub, .zip, .png/.jpg/.jpeg/.gif/.bmp/.tiff (OCR), .mp3/.wav/.m4a (transcription), .ipynb, .msg, .xml (RSS/ATOM feeds)

| Aspect | Detail |
|--------|--------|
| Strengths | Purpose-built for LLM consumption; single tool covers most Office formats; active Microsoft maintenance; CLI for quick use + Python API for integration |
| Weaknesses | OCR requires `[all]` extra deps; no Visio or .mpp support; table output can be rough for complex spreadsheets; limited control over output formatting |
| Best for | General-purpose document → Markdown conversion; batch processing; CI/CD pipelines |
| Avoid when | You need fine-grained control over table formatting, or the source is Visio/MS Project |

**CLI usage**:
```bash
markitdown input.docx > output.md
markitdown input.pdf > output.md
```

**Python API**:
```python
from markitdown import MarkItDown
md = MarkItDown()
result = md.convert("file.docx")
print(result.text_content)
```

---

## Word Document Tools

### mammoth (Node.js)

- **Install**: `npm install mammoth`
- **Type**: Node.js library + CLI
- **License**: BSD-2-Clause

| Aspect | Detail |
|--------|--------|
| Strengths | Excellent semantic HTML output from .docx; preserves document structure (headings, lists, tables) well; small and focused |
| Weaknesses | Only supports .docx (not .doc); outputs HTML by default (needs HTML→Markdown step); no other format support |
| Best for | .docx files with complex formatting where markitdown output is poor |
| Avoid when | You need anything other than .docx |

```bash
# CLI
npx mammoth file.docx --output-format=markdown > output.md
```

```javascript
const mammoth = require("mammoth");
const result = await mammoth.convertToMarkdown({ path: "file.docx" });
console.log(result.value);
```

### pandoc

- **Install**: System package (`apt install pandoc`, `brew install pandoc`, `choco install pandoc`)
- **Type**: Universal CLI tool (Haskell)
- **License**: GPL-2.0

| Aspect | Detail |
|--------|--------|
| Strengths | Supports 40+ input formats; highly configurable; excellent Markdown output; handles footnotes, citations, math |
| Weaknesses | System dependency (not pip-installable); no Python API; slower for batch processing; doesn't handle .xlsx/.pptx |
| Best for | High-quality .docx → Markdown conversion; formats with academic/technical content; when you need specific Markdown flavors (GFM, CommonMark) |
| Avoid when | You need to stay in Python-only toolchain; you need Excel/PowerPoint support |

```bash
pandoc -f docx -t gfm file.docx -o output.md
pandoc -f docx -t markdown --wrap=none file.docx -o output.md
```

### python-docx

- **Install**: `pip install python-docx`
- **Type**: Python library
- **License**: MIT

| Aspect | Detail |
|--------|--------|
| Strengths | Full programmatic access to .docx internals (paragraphs, tables, styles, images); fine-grained control |
| Weaknesses | No built-in Markdown output — you must build the conversion logic yourself; only .docx, not .doc |
| Best for | Custom extraction logic where you need specific parts of a document; metadata extraction |
| Avoid when | You just want text → Markdown (use markitdown or mammoth instead) |

---

## Excel / CSV Tools

### pandas

- **Install**: `pip install pandas tabulate openpyxl`
- **Type**: Python library
- **License**: BSD-3-Clause

| Aspect | Detail |
|--------|--------|
| Strengths | Excellent `.to_markdown()` method; handles multi-sheet workbooks; powerful data filtering/transformation before export; reads .xlsx, .xls, .csv, .tsv |
| Weaknesses | Heavy dependency for just conversion; requires `tabulate` for `.to_markdown()`; not a document converter — it's a data tool |
| Best for | Spreadsheets where you need to filter, transform, or select specific sheets/columns before Markdown output |
| Avoid when | You just need raw conversion (markitdown is simpler) |

```python
import pandas as pd
df = pd.read_excel("file.xlsx", sheet_name="Sheet1")
print(df.to_markdown(index=False))
```

### openpyxl

- **Install**: `pip install openpyxl`
- **Type**: Python library
- **License**: MIT

| Aspect | Detail |
|--------|--------|
| Strengths | Full access to Excel internals: cell values, formulas, styles, charts metadata; lightweight |
| Weaknesses | No Markdown output — manual conversion needed; only .xlsx (not .xls) |
| Best for | When you need to extract formulas, cell formatting, or specific named ranges |
| Avoid when | You just need a table dump (use pandas or markitdown) |

---

## PowerPoint Tools

### python-pptx

- **Install**: `pip install python-pptx`
- **Type**: Python library
- **License**: MIT

| Aspect | Detail |
|--------|--------|
| Strengths | Full access to slides, shapes, text frames, notes, images; structured extraction |
| Weaknesses | No Markdown output — manual conversion; only .pptx (not .ppt); no rendering of charts |
| Best for | Structured slide-by-slide extraction with titles, bullet points, and speaker notes |
| Avoid when | Simple text dump is enough (markitdown handles this) |

---

## PDF Tools

### PyMuPDF (fitz)

- **Install**: `pip install PyMuPDF`
- **Type**: Python library
- **License**: AGPL-3.0 (or commercial)

| Aspect | Detail |
|--------|--------|
| Strengths | Fast; preserves text positioning; can extract images; handles scanned PDFs (with OCR integration); page-level control |
| Weaknesses | AGPL license may be restrictive for commercial use; table extraction is basic |
| Best for | Large PDFs; PDFs with mixed content (text + images); when speed matters |
| Avoid when | You need excellent table extraction (use pdfplumber) or have AGPL concerns |

```python
import fitz  # PyMuPDF
doc = fitz.open("file.pdf")
for page in doc:
    print(page.get_text("text"))
```

### pdfplumber

- **Install**: `pip install pdfplumber`
- **Type**: Python library
- **License**: MIT

| Aspect | Detail |
|--------|--------|
| Strengths | Best-in-class table extraction from PDFs; precise text positioning; MIT license; visual debugging tools |
| Weaknesses | Slower than PyMuPDF; doesn't handle scanned/image PDFs; no OCR |
| Best for | PDFs with tables (financial reports, invoices, data sheets) |
| Avoid when | PDF is scanned/image-based (use PyMuPDF + OCR or markitdown[all]) |

```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        text = page.extract_text()
```

### pdf-parse (Node.js)

- **Install**: `npm install pdf-parse`
- **Type**: Node.js library
- **License**: MIT

| Aspect | Detail |
|--------|--------|
| Strengths | Simple API; fast; good for text-only PDFs |
| Weaknesses | No table extraction; no image handling; Node.js only |
| Best for | Quick text extraction from simple PDFs in Node.js projects |
| Avoid when | PDF has tables, images, or complex layouts |

---

## Visio Tools

There is no reliable open-source Visio-to-Markdown converter. All approaches involve intermediate conversions:

| Approach | Steps | Quality |
|----------|-------|---------|
| LibreOffice headless | `.vsdx` → PDF → markitdown | Medium — loses connector semantics |
| LibreOffice + OCR | `.vsdx` → PNG → markitdown[all] (OCR) | Low-Medium — text extraction only |
| Manual export | User exports as SVG/PDF from Visio → convert | Best available |
| PPTX export | User re-saves as .pptx → python-pptx | Medium — if diagram is simple |

**Recommendation**: Always ask the user if they can export from Visio directly. If automation is required, use LibreOffice headless as the first step.

---

## MS Project Tools

### mpxj

- **Install**: `pip install mpxj` (requires Java JDK + jpype1)
- **Type**: Java library with Python bindings
- **License**: LGPL-2.1

| Aspect | Detail |
|--------|--------|
| Strengths | Only reliable open-source .mpp reader; reads .mpp, .mpx, .mspdi (XML), Primavera formats |
| Weaknesses | Requires JVM; complex setup; Java-style API via jpype |
| Best for | Programmatic access to MS Project task data when export isn't possible |
| Avoid when | User can export to CSV/XML from MS Project (much simpler to parse) |

**Alternative**: Ask the user to export from MS Project as CSV or XML, then use markitdown (CSV) or xml.etree (XML).

---

## OCR Tools

### pytesseract

- **Install**: `pip install pytesseract` (requires Tesseract OCR engine installed on system)
- **Type**: Python wrapper for Tesseract OCR
- **License**: Apache-2.0

| Aspect | Detail |
|--------|--------|
| Strengths | Industry-standard OCR; supports 100+ languages; highly configurable; good accuracy on clean printed text |
| Weaknesses | Requires separate Tesseract binary install; poor on handwriting; needs image preprocessing for best results |
| Best for | High-volume image OCR; multi-language documents; when markitdown OCR quality is insufficient |
| Avoid when | markitdown `[all]` produces acceptable output; images contain handwriting |

```python
import pytesseract
from PIL import Image

text = pytesseract.image_to_string(Image.open("scan.png"))
print(text)
```

### EasyOCR

- **Install**: `pip install easyocr`
- **Type**: Python library (deep learning-based)
- **License**: Apache-2.0

| Aspect | Detail |
|--------|--------|
| Strengths | Better accuracy than Tesseract on noisy/low-quality images; supports 80+ languages; no system dependency — pure pip install |
| Weaknesses | Slower than Tesseract; large model downloads on first use; GPU recommended for speed |
| Best for | Low-quality scans; images with noise or unusual fonts; when Tesseract fails |
| Avoid when | Speed is critical; images are clean printed text (Tesseract is faster) |

```python
import easyocr

reader = easyocr.Reader(["en"])
results = reader.readtext("scan.png", detail=0)
print("\n".join(results))
```

---

## Audio Transcription Tools

### Whisper (OpenAI)

- **Install**: `pip install openai-whisper`
- **Type**: Python library (deep learning-based)
- **License**: MIT

| Aspect | Detail |
|--------|--------|
| Strengths | State-of-the-art accuracy; supports 99 languages; multiple model sizes (tiny → large); handles noisy audio well |
| Weaknesses | Slow on CPU (GPU strongly recommended); large model downloads; high memory usage for larger models |
| Best for | Meeting transcription; voice notes; any audio where accuracy matters |
| Avoid when | markitdown `[all]` transcription is acceptable; you need real-time transcription |

```python
import whisper

model = whisper.load_model("base")
result = model.transcribe("meeting.mp3")
print(result["text"])
```

```bash
# CLI usage
whisper meeting.mp3 --output_format txt --language en
```

### SpeechRecognition

- **Install**: `pip install SpeechRecognition`
- **Type**: Python library (wraps multiple engines)
- **License**: BSD-3-Clause

| Aspect | Detail |
|--------|--------|
| Strengths | Simple API; supports multiple backends (Google, Sphinx, Whisper); lightweight |
| Weaknesses | Online backends require internet; offline (Sphinx) has poor accuracy; limited audio format support without pydub |
| Best for | Quick transcription with online API access; prototyping |
| Avoid when | You need offline high-quality transcription (use Whisper); long audio files |

---

## Notebook Tools

### nbconvert

- **Install**: `pip install nbconvert` (often included with Jupyter)
- **Type**: Python library + CLI
- **License**: BSD-3-Clause

| Aspect | Detail |
|--------|--------|
| Strengths | Official Jupyter tool; full control over output (Markdown, HTML, PDF, LaTeX); template system for custom formatting |
| Weaknesses | Heavier dependency (pulls in Jupyter ecosystem); slower than markitdown for simple conversion |
| Best for | When you need fine-grained control over notebook output format; custom templates |
| Avoid when | markitdown output is acceptable (simpler, faster) |

```bash
jupyter nbconvert --to markdown notebook.ipynb
jupyter nbconvert --to markdown --no-input notebook.ipynb  # hide code cells
```

---

## Email Tools

### extract-msg

- **Install**: `pip install extract-msg`
- **Type**: Python library
- **License**: GPL-3.0

| Aspect | Detail |
|--------|--------|
| Strengths | Pure Python; extracts headers, body, and attachments from .msg files; saves attachments to disk |
| Weaknesses | GPL license; only handles .msg (not .eml); attachment content not auto-converted |
| Best for | When you need to extract and save attachments separately; when markitdown output is insufficient |
| Avoid when | markitdown handles the .msg file acceptably |

```python
import extract_msg

msg = extract_msg.Message("email.msg")
print(msg.subject, msg.sender, msg.body)
msg.save_attachments()  # saves to current dir
```

### python-oletools

- **Install**: `pip install oletools`
- **Type**: Python library
- **License**: BSD-2-Clause

| Aspect | Detail |
|--------|--------|
| Strengths | Analyzes OLE2 files (including .msg); security analysis capabilities; extracts metadata and embedded objects |
| Weaknesses | More of a forensic/security tool than a converter; low-level API |
| Best for | Security analysis of .msg files; extracting embedded OLE objects |
| Avoid when | You just need email text (use markitdown or extract-msg) |

---

## Feed Tools

### feedparser

- **Install**: `pip install feedparser`
- **Type**: Python library
- **License**: BSD-2-Clause

| Aspect | Detail |
|--------|--------|
| Strengths | Robust RSS/ATOM parsing; handles malformed feeds; normalizes feed data across formats |
| Weaknesses | No Markdown output — manual formatting needed; only for feeds, not arbitrary XML |
| Best for | When markitdown feed parsing is insufficient; when you need structured access to individual feed entries |
| Avoid when | markitdown handles the feed file acceptably |

```python
import feedparser

feed = feedparser.parse("feed.xml")
for entry in feed.entries:
    print(f"## {entry.title}\n")
    print(f"*{entry.published}*\n")
    print(entry.summary)
    print()
```

---

## Universal Fallbacks

### LibreOffice headless

- **Install**: System package (`apt install libreoffice`, `brew install --cask libreoffice`, or download)
- **Type**: CLI

Converts between many Office formats:
```bash
libreoffice --headless --convert-to docx file.doc
libreoffice --headless --convert-to pdf file.vsdx
libreoffice --headless --convert-to csv file.xlsx
```

| Aspect | Detail |
|--------|--------|
| Strengths | Handles almost every Office format; good conversion fidelity; batch capable |
| Weaknesses | Heavy install (~500MB+); slow startup; requires display server or `--headless`; output may differ from original |
| Best for | Legacy formats (.doc, .ppt, .xls, .vsd) that modern Python libs can't read directly |
| Avoid when | markitdown handles the format natively |

### textract (Python)

- **Install**: `pip install textract` (needs system deps)
- **Type**: Python library

| Aspect | Detail |
|--------|--------|
| Strengths | Unified API for many formats |
| Weaknesses | Unmaintained; complex system dependencies; installation often fails on modern systems |
| Best for | Avoid — use markitdown instead as the modern replacement |

---

## Decision Flowchart

1. **Is the format supported by markitdown?** → Yes → Use markitdown
2. **Is the output quality acceptable?** → Yes → Done
3. **No** → Check the fallback tool for that format in the mapping table
4. **Is it Visio or MS Project?** → Use the specific cascade documented in SKILL.md
5. **Is it a legacy format (.doc, .ppt, .xls)?** → Try markitdown first, then LibreOffice headless → modern format → markitdown
