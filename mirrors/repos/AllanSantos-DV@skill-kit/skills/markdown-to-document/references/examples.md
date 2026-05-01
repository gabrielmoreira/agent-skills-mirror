# Examples — Markdown to Document Generation

Practical, copy-paste-ready code examples for each format. All examples use Python.

---

## PowerPoint (.pptx) — With Template

```python
from pptx import Presentation
import json

# Load template and data
prs = Presentation("template.pptx")
with open("slides.json", encoding="utf-8") as f:
    data = json.load(f)

for slide_data in data["slides"]:
    # Match layout by name, fall back to index 1
    layout = None
    for sl in prs.slide_layouts:
        if sl.name == slide_data.get("layout", ""):
            layout = sl
            break
    if layout is None:
        layout = prs.slide_layouts[1]

    slide = prs.slides.add_slide(layout)

    if slide.shapes.title and slide_data.get("title"):
        slide.shapes.title.text = slide_data["title"]

    # Body goes to placeholder index 1 (typically content area)
    if len(slide.placeholders) > 1 and slide_data.get("body"):
        slide.placeholders[1].text = slide_data["body"]

    # Speaker notes
    if slide_data.get("notes"):
        slide.notes_slide.notes_text_frame.text = slide_data["notes"]

prs.save("output.pptx")
print("Generated: output.pptx")
```

---

## PowerPoint (.pptx) — Without Template

```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()

# Title slide
title_layout = prs.slide_layouts[0]
slide = prs.slides.add_slide(title_layout)
slide.shapes.title.text = "Quarterly Review"
slide.placeholders[1].text = "Q1 2026 Results"

# Content slides
content_layout = prs.slide_layouts[1]
slides_content = [
    ("Revenue", "- Total: $1.2M\n- Growth: +15%\n- Target: $1.5M"),
    ("Users", "- Active: 45,000\n- New: 5,200\n- Churn: 2.1%"),
]

for title, body in slides_content:
    slide = prs.slides.add_slide(content_layout)
    slide.shapes.title.text = title
    slide.placeholders[1].text = body

prs.save("presentation.pptx")
print("Generated: presentation.pptx")
```

---

## PowerPoint (.pptx) — From Markdown

```python
import re
from pptx import Presentation

md_content = """
## Introduction

Welcome to the quarterly review.

## Key Metrics

- Revenue: $1.2M
- Users: 45,000
- Growth: 15%

## Next Steps

- Expand to new markets
- Improve retention
- Launch v2.0
"""

# Parse Markdown: each ## heading starts a new slide
slides = []
current = None
for line in md_content.strip().split("\n"):
    if line.startswith("## "):
        if current:
            slides.append(current)
        current = {"title": line[3:].strip(), "body": ""}
    elif current is not None:
        current["body"] += line + "\n"
if current:
    slides.append(current)

prs = Presentation()
for s in slides:
    layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(layout)
    slide.shapes.title.text = s["title"]
    slide.placeholders[1].text = s["body"].strip()

prs.save("from_markdown.pptx")
print("Generated: from_markdown.pptx")
```

---

## Word (.docx) — With Jinja2 Template

```python
from docxtpl import DocxTemplate
import json

# Template (.docx) contains: {{ title }}, {% for item in items %}...{% endfor %}
doc = DocxTemplate("report_template.docx")

with open("data.json", encoding="utf-8") as f:
    context = json.load(f)["data"]

doc.render(context)
doc.save("report.docx")
print("Generated: report.docx")
```

**Example template content in Word:**
```
{{ title }}

Date: {{ date }}
Author: {{ author }}

Summary: {{ summary }}

| Name | Description | Status |
{% for item in items %}
| {{ item.name }} | {{ item.description }} | {{ item.status }} |
{% endfor %}
```

---

## Word (.docx) — Without Template

```python
from docx import Document
from docx.shared import Pt

doc = Document()
doc.add_heading("Monthly Report", level=0)
doc.add_paragraph("Date: 2026-03-11")
doc.add_paragraph("Author: Data Team")

doc.add_heading("Executive Summary", level=1)
doc.add_paragraph(
    "This report covers the key metrics for Q1 2026. "
    "Overall performance exceeded expectations."
)

doc.add_heading("Key Metrics", level=1)
table = doc.add_table(rows=1, cols=3)
table.style = "Light Grid Accent 1"
hdr = table.rows[0].cells
hdr[0].text = "Metric"
hdr[1].text = "Value"
hdr[2].text = "Change"

data = [("Revenue", "$1.2M", "+15%"), ("Users", "45,000", "+8%")]
for metric, value, change in data:
    row = table.add_row().cells
    row[0].text = metric
    row[1].text = value
    row[2].text = change

doc.save("report.docx")
print("Generated: report.docx")
```

---

## Word (.docx) — Pandoc Fallback

```bash
# Simple Markdown → DOCX
pandoc report.md -o report.docx

# With reference document for styling
pandoc report.md -o report.docx --reference-doc=company_style.docx

# With table of contents
pandoc report.md -o report.docx --toc --toc-depth=2
```

---

## Excel (.xlsx) — With Template

```python
from openpyxl import load_workbook
import json

wb = load_workbook("template.xlsx")
ws = wb.active

with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

# Assumes template has headers in row 1
# Fill data starting from row 2
sheet_data = data["sheets"]
for sheet_name, sheet_content in sheet_data.items():
    if sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
    else:
        ws = wb.create_sheet(sheet_name)

    # Write headers
    for col, header in enumerate(sheet_content["headers"], 1):
        ws.cell(row=1, column=col, value=header)

    # Write data rows
    for row_idx, row_data in enumerate(sheet_content["rows"], 2):
        for col_idx, value in enumerate(row_data, 1):
            ws.cell(row=row_idx, column=col_idx, value=value)

wb.save("output.xlsx")
print("Generated: output.xlsx")
```

---

## Excel (.xlsx) — From Scratch

```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter
import json

wb = Workbook()

with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

first_sheet = True
for sheet_name, sheet_content in data["sheets"].items():
    if first_sheet:
        ws = wb.active
        ws.title = sheet_name
        first_sheet = False
    else:
        ws = wb.create_sheet(sheet_name)

    headers = sheet_content["headers"]
    rows = sheet_content["rows"]

    # Write headers with bold font
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)

    # Write data rows
    for row_idx, row_data in enumerate(rows, 2):
        for col_idx, value in enumerate(row_data, 1):
            ws.cell(row=row_idx, column=col_idx, value=value)

    # Auto-width columns
    for col_idx in range(1, len(headers) + 1):
        max_len = max(
            len(str(ws.cell(row=r, column=col_idx).value or ""))
            for r in range(1, len(rows) + 2)
        )
        ws.column_dimensions[get_column_letter(col_idx)].width = min(max_len + 2, 50)

wb.save("output.xlsx")
print("Generated: output.xlsx")
```

---

## MS Project (.mspdi) — MPXJ

```python
import jpype
if not jpype.isJVMStarted():
    jpype.startJVM()

from net.sf.mpxj import ProjectFile, Duration, TimeUnit
from net.sf.mpxj.mspdi import MSPDIWriter
from java.text import SimpleDateFormat
import json

with open("tasks.json", encoding="utf-8") as f:
    data = json.load(f)

project = ProjectFile()
date_format = SimpleDateFormat("yyyy-MM-dd")

tasks = []
for task_data in data["tasks"]:
    task = project.addTask()
    task.setName(task_data["name"])

    if task_data.get("start"):
        task.setStart(date_format.parse(task_data["start"]))

    if task_data.get("duration"):
        # Parse "5d" → 5 days
        dur_str = task_data["duration"]
        dur_val = int(dur_str.replace("d", "").replace("h", ""))
        unit = TimeUnit.DAYS if "d" in dur_str else TimeUnit.HOURS
        task.setDuration(Duration.getInstance(dur_val, unit))

    tasks.append(task)

# Set predecessors (1-based index)
for i, task_data in enumerate(data["tasks"]):
    for pred_idx in task_data.get("predecessors", []):
        if 0 < pred_idx <= len(tasks):
            tasks[i].addPredecessor(tasks[pred_idx - 1])

writer = MSPDIWriter()
writer.write(project, "output.xml")
print("Generated: output.xml (MSPDI format)")
```

---

## PDF — With WeasyPrint

```python
import weasyprint
import markdown

md_text = """
# Quarterly Report

## Revenue
Total revenue for Q1 2026 was **$1.2M**, representing a 15% increase.

## Users
| Metric | Value |
|--------|-------|
| Active Users | 45,000 |
| New Users | 5,200 |
| Churn Rate | 2.1% |

## Conclusion
Performance exceeded targets across all metrics.
"""

# Convert Markdown → HTML
html = markdown.markdown(md_text, extensions=["tables", "fenced_code"])

# Wrap in full HTML with basic styling
full_html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body>{html}</body>
</html>
"""

weasyprint.HTML(string=full_html).write_pdf("report.pdf")
print("Generated: report.pdf")
```

---

## PDF — With CSS Template

```python
import weasyprint
import markdown

md_text = open("content.md", encoding="utf-8").read()
html = markdown.markdown(md_text, extensions=["tables", "fenced_code"])

full_html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body>{html}</body>
</html>
"""

weasyprint.HTML(string=full_html).write_pdf(
    "styled_report.pdf",
    stylesheets=[weasyprint.CSS(filename="corporate_style.css")]
)
print("Generated: styled_report.pdf")
```

**Example CSS template (`corporate_style.css`)**:
```css
@page {
    size: A4;
    margin: 2cm;
    @top-center { content: "Company Name — Confidential"; font-size: 9pt; color: #888; }
    @bottom-center { content: "Page " counter(page) " of " counter(pages); font-size: 9pt; }
}

body { font-family: "Segoe UI", Arial, sans-serif; font-size: 11pt; line-height: 1.6; color: #333; }
h1 { color: #1a5276; border-bottom: 2px solid #1a5276; padding-bottom: 0.3em; }
h2 { color: #2e86c1; margin-top: 1.5em; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
th { background-color: #1a5276; color: white; }
tr:nth-child(even) { background-color: #f2f2f2; }
```

---

## PDF — Pandoc Fallback

```bash
# Via WeasyPrint engine
pandoc content.md -o output.pdf --pdf-engine=weasyprint --css=style.css

# Via LaTeX engine (requires texlive)
pandoc content.md -o output.pdf --pdf-engine=xelatex

# With custom margins
pandoc content.md -o output.pdf -V geometry:margin=2cm
```
