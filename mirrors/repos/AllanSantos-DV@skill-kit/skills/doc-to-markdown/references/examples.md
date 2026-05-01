# Examples — Document to Markdown Conversion

Practical, copy-paste-ready code examples for each format. Python is the primary language; Node.js alternatives are provided where relevant.

---

## Word (.docx) — markitdown

### Basic conversion

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("report.docx")
print(result.text_content)
```

### Save to file with frontmatter

```python
from markitdown import MarkItDown
from pathlib import Path
from datetime import datetime

md = MarkItDown()
result = md.convert("report.docx")

output = f"""---
source: "report.docx"
converted: "{datetime.now().strftime('%Y-%m-%d')}"
format: docx
---

{result.text_content}
"""

Path("report.md").write_text(output, encoding="utf-8")
```

### Fallback: mammoth (Node.js)

```javascript
const mammoth = require("mammoth");
const fs = require("fs");

async function convertDocx(inputPath, outputPath) {
  const result = await mammoth.convertToMarkdown({ path: inputPath });
  fs.writeFileSync(outputPath, result.value, "utf-8");
  if (result.messages.length > 0) {
    console.warn("Warnings:", result.messages);
  }
}

convertDocx("report.docx", "report.md");
```

### Fallback: pandoc CLI

```bash
# GitHub Flavored Markdown output
pandoc -f docx -t gfm --wrap=none report.docx -o report.md

# With table of contents
pandoc -f docx -t gfm --toc report.docx -o report.md

# Extract images to media/ folder
pandoc -f docx -t gfm --extract-media=media report.docx -o report.md
```

---

## Excel (.xlsx) — markitdown

### Basic conversion

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("data.xlsx")
print(result.text_content)
```

### Pandas — all sheets with headers

```python
import pandas as pd

sheets = pd.read_excel("data.xlsx", sheet_name=None)

output = []
for name, df in sheets.items():
    output.append(f"## Sheet: {name}\n")
    output.append(df.to_markdown(index=False))
    output.append("")

print("\n".join(output))
```

### Pandas — specific sheet with filtering

```python
import pandas as pd

df = pd.read_excel("data.xlsx", sheet_name="Sales")
# Filter rows where Amount > 1000
filtered = df[df["Amount"] > 1000]
print(filtered.to_markdown(index=False))
```

### CSV conversion

```python
import pandas as pd

df = pd.read_csv("data.csv")
print(df.to_markdown(index=False))
```

### Large spreadsheet — chunked output

```python
import pandas as pd

df = pd.read_excel("large_file.xlsx")

# Output first 100 rows as preview
print("## Preview (first 100 rows)\n")
print(df.head(100).to_markdown(index=False))
print(f"\n*... {len(df) - 100} more rows omitted*")
```

---

## PowerPoint (.pptx) — markitdown

### Basic conversion

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("presentation.pptx")
print(result.text_content)
```

### Structured extraction with python-pptx

```python
from pptx import Presentation

def pptx_to_markdown(path: str) -> str:
    prs = Presentation(path)
    output = []

    for i, slide in enumerate(prs.slides, 1):
        # Slide title
        title = slide.shapes.title
        title_text = title.text if title else "Untitled"
        output.append(f"## Slide {i}: {title_text}\n")

        # Slide content
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    text = para.text.strip()
                    if text and text != title_text:
                        level = para.level
                        indent = "  " * level
                        output.append(f"{indent}- {text}")

        # Speaker notes
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
            notes = slide.notes_slide.notes_text_frame.text.strip()
            if notes:
                output.append(f"\n> **Speaker Notes**: {notes}")

        output.append("")

    return "\n".join(output)

print(pptx_to_markdown("presentation.pptx"))
```

---

## PDF — markitdown

### Basic conversion

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("document.pdf")
print(result.text_content)
```

### Table-heavy PDF with pdfplumber

```python
import pdfplumber

def pdf_tables_to_markdown(path: str) -> str:
    output = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            output.append(f"## Page {i}\n")

            # Extract text
            text = page.extract_text()
            if text:
                output.append(text)

            # Extract tables
            tables = page.extract_tables()
            for j, table in enumerate(tables):
                if not table or not table[0]:
                    continue
                output.append(f"\n### Table {j + 1}\n")
                # Header
                header = "| " + " | ".join(str(c or "") for c in table[0]) + " |"
                sep = "| " + " | ".join("---" for _ in table[0]) + " |"
                output.append(header)
                output.append(sep)
                # Rows
                for row in table[1:]:
                    output.append("| " + " | ".join(str(c or "") for c in row) + " |")
                output.append("")

    return "\n".join(output)

print(pdf_tables_to_markdown("report.pdf"))
```

### PyMuPDF — fast extraction with page control

```python
import fitz  # PyMuPDF

def pdf_to_markdown_fast(path: str, max_pages: int | None = None) -> str:
    doc = fitz.open(path)
    output = []
    pages = doc[:max_pages] if max_pages else doc

    for i, page in enumerate(pages, 1):
        output.append(f"## Page {i}\n")
        output.append(page.get_text("text"))
        output.append("")

    return "\n".join(output)

print(pdf_to_markdown_fast("large_document.pdf", max_pages=50))
```

### Node.js — pdf-parse

```javascript
const fs = require("fs");
const pdfParse = require("pdf-parse");

async function pdfToMarkdown(inputPath) {
  const buffer = fs.readFileSync(inputPath);
  const data = await pdfParse(buffer);
  return data.text;
}

pdfToMarkdown("document.pdf").then(console.log);
```

---

## Visio (.vsd, .vsdx)

### LibreOffice headless → PDF → markitdown

```bash
# Step 1: Convert Visio to PDF
libreoffice --headless --convert-to pdf diagram.vsdx --outdir /tmp

# Step 2: Convert PDF to Markdown
markitdown /tmp/diagram.pdf > diagram.md
```

### LibreOffice headless → Image → OCR

```bash
# Step 1: Convert to PNG
libreoffice --headless --convert-to png diagram.vsdx --outdir /tmp

# Step 2: OCR with markitdown (requires markitdown[all])
pip install 'markitdown[all]'
markitdown /tmp/diagram.png > diagram.md
```

### Python automation

```python
import subprocess
from pathlib import Path
from markitdown import MarkItDown

def visio_to_markdown(visio_path: str) -> str:
    visio = Path(visio_path)

    # Convert to PDF via LibreOffice
    subprocess.run([
        "libreoffice", "--headless", "--convert-to", "pdf",
        str(visio), "--outdir", str(visio.parent)
    ], check=True)

    pdf_path = visio.with_suffix(".pdf")
    md = MarkItDown()
    result = md.convert(str(pdf_path))

    # Cleanup intermediate PDF
    pdf_path.unlink(missing_ok=True)

    return result.text_content

print(visio_to_markdown("architecture.vsdx"))
```

---

## MS Project (.mpp)

### mpxj — task list extraction

```python
import jpype
import jpype.imports

if not jpype.isJVMStarted():
    jpype.startJVM()

from net.sf.mpxj.reader import UniversalProjectReader

def mpp_to_markdown(path: str) -> str:
    reader = UniversalProjectReader()
    project = reader.read(path)

    output = [f"# {project.getProjectProperties().getProjectTitle() or 'Project'}\n"]

    output.append("| ID | Task | Start | Finish | Duration | % Complete |")
    output.append("|----|------|-------|--------|----------|------------|")

    for task in project.getTasks():
        if task.getName() is None:
            continue
        tid = task.getID() or ""
        name = task.getName() or ""
        start = str(task.getStart() or "")
        finish = str(task.getFinish() or "")
        duration = str(task.getDuration() or "")
        pct = str(task.getPercentageComplete() or "0")
        output.append(f"| {tid} | {name} | {start} | {finish} | {duration} | {pct}% |")

    return "\n".join(output)

print(mpp_to_markdown("project.mpp"))
```

### From exported CSV

```python
import pandas as pd

df = pd.read_csv("project_tasks.csv")
print(df.to_markdown(index=False))
```

### From exported XML

```python
import xml.etree.ElementTree as ET

def mpp_xml_to_markdown(xml_path: str) -> str:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = {"ms": "http://schemas.microsoft.com/project"}

    output = ["| Task | Start | Finish | Duration |"]
    output.append("|------|-------|--------|----------|")

    for task in root.findall(".//ms:Task", ns):
        name = task.findtext("ms:Name", default="", namespaces=ns)
        start = task.findtext("ms:Start", default="", namespaces=ns)[:10]  # date only
        finish = task.findtext("ms:Finish", default="", namespaces=ns)[:10]
        duration = task.findtext("ms:Duration", default="", namespaces=ns)
        if name:
            output.append(f"| {name} | {start} | {finish} | {duration} |")

    return "\n".join(output)

print(mpp_xml_to_markdown("project.xml"))
```

---

## Images (.png, .jpg) — OCR via markitdown

### Basic OCR conversion

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("scanned_document.png")
print(result.text_content)
```

### Batch image OCR

```python
from markitdown import MarkItDown
from pathlib import Path

md = MarkItDown()
image_dir = Path("scanned_pages")

for img in sorted(image_dir.glob("*.png")):
    result = md.convert(str(img))
    print(f"## {img.name}\n")
    print(result.text_content)
    print()
```

---

## Audio (.mp3, .wav) — Transcription via markitdown

### Basic transcription

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("meeting.mp3")
print(result.text_content)
```

### Fallback: OpenAI Whisper (higher quality)

```bash
pip install openai-whisper
whisper meeting.mp3 --output_format txt --language pt
```

```python
import whisper

model = whisper.load_model("base")
result = model.transcribe("meeting.mp3")
print(result["text"])
```

---

## Jupyter Notebook (.ipynb) — markitdown

### Basic conversion

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("analysis.ipynb")
print(result.text_content)
```

### Fallback: nbconvert

```bash
jupyter nbconvert --to markdown analysis.ipynb
```

```python
import subprocess
subprocess.run(["jupyter", "nbconvert", "--to", "markdown", "analysis.ipynb"], check=True)
```

---

## ZIP Archive (.zip) — markitdown

### Basic extraction and conversion

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("documents.zip")
print(result.text_content)
```

---

## Outlook Email (.msg) — markitdown

### Basic conversion

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("email.msg")
print(result.text_content)
```

### Fallback: extract-msg

```python
import extract_msg

msg = extract_msg.Message("email.msg")
print(f"# {msg.subject}\n")
print(f"**From**: {msg.sender}")
print(f"**To**: {msg.to}")
print(f"**Date**: {msg.date}\n")
print(msg.body)
```

---

## Batch Conversion

### Convert entire directory

```python
from markitdown import MarkItDown
from pathlib import Path
from datetime import datetime

SUPPORTED = {".docx", ".doc", ".xlsx", ".xls", ".csv", ".pptx", ".ppt", ".pdf", ".html", ".epub", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".mp3", ".wav", ".m4a", ".ipynb", ".zip", ".msg"}

def batch_convert(input_dir: str, output_dir: str | None = None):
    md = MarkItDown()
    src = Path(input_dir)
    dst = Path(output_dir) if output_dir else src

    results = {"converted": [], "failed": []}

    for file in sorted(src.rglob("*")):
        if file.suffix.lower() not in SUPPORTED:
            continue
        try:
            result = md.convert(str(file))

            out_file = dst / file.relative_to(src).with_suffix(".md")
            out_file.parent.mkdir(parents=True, exist_ok=True)

            frontmatter = (
                f"---\n"
                f"source: \"{file.name}\"\n"
                f"converted: \"{datetime.now().strftime('%Y-%m-%d')}\"\n"
                f"format: \"{file.suffix.lstrip('.')}\"\n"
                f"---\n\n"
            )
            out_file.write_text(frontmatter + result.text_content, encoding="utf-8")
            results["converted"].append(str(file.name))
        except Exception as e:
            results["failed"].append({"file": str(file.name), "error": str(e)})

    # Summary
    print(f"## Conversion Summary\n")
    print(f"- Converted: {len(results['converted'])}")
    print(f"- Failed: {len(results['failed'])}")
    if results["failed"]:
        print("\n### Failed Files\n")
        for f in results["failed"]:
            print(f"- **{f['file']}**: {f['error']}")

batch_convert("./documents", "./markdown_output")
```

### Bash one-liner (Linux/macOS)

```bash
find docs/ -type f \( -name "*.docx" -o -name "*.pdf" -o -name "*.pptx" \) \
  -exec sh -c 'markitdown "$1" > "${1%.*}.md"' _ {} \;
```

### PowerShell one-liner (Windows)

```powershell
Get-ChildItem -Path docs -Recurse -Include *.docx,*.pdf,*.pptx | ForEach-Object {
    $out = $_.FullName -replace '\.[^.]+$', '.md'
    markitdown $_.FullName | Set-Content $out -Encoding UTF8
}
```
