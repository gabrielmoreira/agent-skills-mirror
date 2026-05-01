# Troubleshooting — Document to Markdown Conversion

Common issues encountered during document-to-Markdown conversion and their solutions.

---

## Installation Issues

### markitdown fails to install

**Symptom**: `pip install markitdown` fails with dependency errors.

**Solutions**:
1. Ensure Python 3.9+: `python --version`
2. Upgrade pip: `pip install --upgrade pip`
3. Install in a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   pip install markitdown
   ```
4. For `markitdown[all]` failures, install base first, then optional deps:
   ```bash
   pip install markitdown
   pip install 'markitdown[all]'
   ```

### OCR features not working

**Symptom**: Image-based content is not extracted; empty output for scanned PDFs or images.

**Solutions**:
1. Install with OCR support: `pip install 'markitdown[all]'`
2. Verify Tesseract is available: `tesseract --version`
3. On Windows, install Tesseract separately and add to PATH
4. On Linux: `apt install tesseract-ocr`
5. On macOS: `brew install tesseract`

### LibreOffice headless not found

**Symptom**: `libreoffice: command not found` or `'libreoffice' is not recognized`.

**Solutions**:
- Windows: Add LibreOffice to PATH, typically `C:\Program Files\LibreOffice\program\`
- Linux: `apt install libreoffice` or `snap install libreoffice`
- macOS: `brew install --cask libreoffice` then use `/Applications/LibreOffice.app/Contents/MacOS/soffice --headless`
- Docker: Use `libreoffice/libreoffice` image

---

## Encoding Issues

### Garbled characters in output

**Symptom**: Output contains `â€™`, `Ã©`, `â€"` or similar mojibake.

**Solutions**:
1. Ensure output is written as UTF-8:
   ```python
   Path("output.md").write_text(content, encoding="utf-8")
   ```
2. In CLI, redirect with encoding:
   ```bash
   markitdown file.docx | iconv -f utf-8 -t utf-8 > output.md
   ```
3. PowerShell: Set output encoding first:
   ```powershell
   [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
   markitdown file.docx | Set-Content output.md -Encoding UTF8
   ```

### Non-Latin scripts (CJK, Arabic, Hebrew) missing

**Symptom**: Characters from non-Latin scripts are replaced with `?` or boxes.

**Solutions**:
1. markitdown generally handles Unicode well — verify the source file actually contains the text (open in original app)
2. For PDFs: CJK fonts may not be embedded. Try pdfplumber which handles font mapping better
3. For OCR: Install language packs for Tesseract:
   ```bash
   apt install tesseract-ocr-chi-sim  # Chinese Simplified
   apt install tesseract-ocr-jpn      # Japanese
   apt install tesseract-ocr-ara      # Arabic
   ```

---

## Format-Specific Issues

### Word: Tables not rendering correctly

**Symptom**: Word tables appear as flat text or lose column alignment.

**Solutions**:
1. Try mammoth for better table preservation:
   ```bash
   npx mammoth file.docx --output-format=markdown
   ```
2. Try pandoc:
   ```bash
   pandoc -f docx -t gfm --columns=120 file.docx -o output.md
   ```
3. For complex/nested tables: extract programmatically with python-docx and build Markdown tables manually

### Word: Images appear as empty references

**Symptom**: Output contains `![](image1.png)` but no actual image content.

**Solutions**:
1. Use `markitdown[all]` for OCR-based image descriptions
2. Use pandoc with `--extract-media`:
   ```bash
   pandoc -f docx -t gfm --extract-media=./media file.docx -o output.md
   ```
3. Accept that binary images can't be represented in Markdown text — describe their purpose in alt-text or skip

### Excel: Large spreadsheets produce unreadable output

**Symptom**: Markdown table is thousands of rows; columns are misaligned or too wide.

**Solutions**:
1. Limit rows with pandas:
   ```python
   df = pd.read_excel("file.xlsx")
   print(f"Total rows: {len(df)}\n")
   print(df.head(50).to_markdown(index=False))
   ```
2. Select specific columns:
   ```python
   cols = ["Name", "Date", "Amount"]
   print(df[cols].to_markdown(index=False))
   ```
3. Split into multiple tables by sheet:
   ```python
   sheets = pd.read_excel("file.xlsx", sheet_name=None)
   for name, df in sheets.items():
       print(f"## {name}\n{df.head(100).to_markdown(index=False)}\n")
   ```

### Excel: Formulas instead of values

**Symptom**: Cells show formulas like `=SUM(A1:A10)` instead of computed values.

**Solutions**:
1. markitdown and pandas both read computed values by default — this usually means the workbook was saved without recalculating
2. Open in Excel, press Ctrl+Shift+F9 to recalculate, save, then convert
3. With openpyxl, explicitly request data_only:
   ```python
   from openpyxl import load_workbook
   wb = load_workbook("file.xlsx", data_only=True)
   ```

### PowerPoint: Slide layout lost / text is flat

**Symptom**: All text from a slide is dumped in one block without structure.

**Solutions**:
1. Use python-pptx for structured extraction (see examples.md)
2. Accept that spatial layout can't map to linear Markdown — focus on extracting the semantic content (titles, bullets, notes)
3. Include speaker notes which often contain the slide's narrative

### PDF: Scanned/image-based PDFs produce empty output

**Symptom**: markitdown returns blank or very little text from a PDF.

**Solutions**:
1. The PDF is likely image-based (scanned). Install OCR:
   ```bash
   pip install 'markitdown[all]'
   ```
2. Use PyMuPDF with OCR:
   ```python
   import fitz
   doc = fitz.open("scanned.pdf")
   for page in doc:
       # Try text extraction first
       text = page.get_text("text")
       if not text.strip():
           # Fall back to OCR
           pix = page.get_pixmap(dpi=300)
           # Save image and OCR externally
   ```
3. For high-volume scanned PDFs, consider a dedicated OCR service

### PDF: Tables are broken or columns merged

**Symptom**: Table data runs together; columns are not separated correctly.

**Solutions**:
1. Use pdfplumber — it has the best table detection:
   ```python
   import pdfplumber
   with pdfplumber.open("file.pdf") as pdf:
       for page in pdf.pages:
           for table in page.extract_tables():
               print(table)
   ```
2. Adjust pdfplumber's table settings:
   ```python
   table_settings = {
       "vertical_strategy": "text",
       "horizontal_strategy": "text",
       "snap_tolerance": 5,
   }
   tables = page.extract_tables(table_settings)
   ```
3. As last resort: use Tabula (`pip install tabula-py`, requires Java) which uses a different extraction algorithm

---

## Performance Issues

### Conversion is very slow for large files

**Symptom**: Converting a 100+ page document or 50MB+ file takes minutes.

**Solutions**:
1. For PDFs, use PyMuPDF (fastest Python PDF library):
   ```python
   import fitz
   doc = fitz.open("large.pdf")
   for page in doc:
       print(page.get_text("text"))
   ```
2. For Excel, use specific sheets/ranges instead of loading everything:
   ```python
   df = pd.read_excel("large.xlsx", sheet_name="Summary", usecols="A:E", nrows=1000)
   ```
3. Process in chunks — convert N pages/sheets at a time
4. For batch processing, use multiprocessing:
   ```python
   from concurrent.futures import ProcessPoolExecutor
   from markitdown import MarkItDown

   def convert_one(path):
       md = MarkItDown()
       return md.convert(str(path)).text_content

   with ProcessPoolExecutor(max_workers=4) as pool:
       results = pool.map(convert_one, file_list)
   ```

### Out of memory on large files

**Symptom**: Python process killed or MemoryError.

**Solutions**:
1. Process page-by-page instead of loading entire document
2. For Excel: use `openpyxl` in read-only mode:
   ```python
   from openpyxl import load_workbook
   wb = load_workbook("huge.xlsx", read_only=True)
   ```
3. For PDFs: process one page at a time with PyMuPDF (it's already memory-efficient)
4. Increase system swap space for truly massive files

---

## Corrupted or Protected Files

### Password-protected files

**Symptom**: `InvalidFileException`, `PasswordRequired`, or empty output.

**Solutions**:
1. markitdown does not handle encryption — file must be decrypted first
2. For PDFs with known password:
   ```bash
   qpdf --password=SECRET --decrypt protected.pdf decrypted.pdf
   markitdown decrypted.pdf > output.md
   ```
3. For Office files: open in the respective app, remove protection, re-save
4. With `msoffcrypto-tool` for Office files:
   ```bash
   pip install msoffcrypto-tool
   msoffcrypto-tool -p PASSWORD encrypted.docx decrypted.docx
   ```

### Corrupted files

**Symptom**: `BadZipFile`, `Invalid file format`, or similar errors.

**Solutions**:
1. Verify the file opens in its native application
2. Try LibreOffice headless repair:
   ```bash
   libreoffice --headless --infilter="Microsoft Word 2007-2019 XML" --convert-to docx corrupted.docx
   ```
3. For ZIP-based formats (.docx, .xlsx, .pptx): try extracting content.xml manually:
   ```python
   import zipfile
   with zipfile.ZipFile("corrupted.docx") as z:
       z.printdir()  # See what's inside
   ```
4. Accept that severely corrupted files may not be recoverable

---

## Output Quality

### Excessive whitespace in output

**Solution**: Post-process the Markdown:
```python
import re

def clean_markdown(text: str) -> str:
    # Collapse 3+ blank lines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip trailing whitespace per line
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return text.strip() + "\n"
```

### Heading levels are inconsistent

**Solution**: Normalize heading hierarchy:
```python
import re

def normalize_headings(text: str) -> str:
    headings = re.findall(r"^(#{1,6})\s", text, re.MULTILINE)
    if not headings:
        return text
    min_level = min(len(h) for h in headings)
    offset = min_level - 1
    if offset > 0:
        text = re.sub(
            r"^(#{1,6})(\s)",
            lambda m: "#" * (len(m.group(1)) - offset) + m.group(2),
            text,
            flags=re.MULTILINE,
        )
    return text
```

### Converted content is too long for LLM context

**Solution**: Summarize or chunk the output:
1. Split by sections/headings and process individually
2. Extract only key sections (ToC, summary, specific pages)
3. For Excel: include only column headers + first few rows as a schema
4. For PowerPoint: extract slide titles + first bullet only for an outline
