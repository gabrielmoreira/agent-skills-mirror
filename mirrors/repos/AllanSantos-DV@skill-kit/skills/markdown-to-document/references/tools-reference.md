# Tools Reference — Markdown to Document Generators

Detailed comparison of all tools referenced in the skill. Use this to decide which tool fits a specific scenario.

---

## PowerPoint Tools

### python-pptx

- **Install**: `pip install python-pptx`
- **Type**: Python library
- **License**: MIT
- **Repository**: https://github.com/scanny/python-pptx

| Aspect | Detail |
|--------|--------|
| Strengths | Full control over slides, layouts, placeholders, shapes, images, charts, tables; template support via opening existing .pptx; active maintenance |
| Weaknesses | No Markdown parser — you must structure content programmatically; layout matching can be fragile if template names change; no PDF export |
| Best for | Template-based presentations; programmatic slide generation; inserting charts/images |
| Avoid when | Simple Markdown → PPTX is enough (use pandoc instead) |

**Key API patterns**:
```python
from pptx import Presentation
from pptx.util import Inches, Pt

# From template
prs = Presentation("template.pptx")
layout = prs.slide_layouts[1]  # or .get_by_name("Title and Content")
slide = prs.slides.add_slide(layout)
slide.shapes.title.text = "My Title"
slide.placeholders[1].text = "Body content"

# From scratch
prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "Title"
prs.save("output.pptx")
```

**Template workflow**: Open existing .pptx → iterate slide_layouts → match by name → add_slide with layout → populate placeholders by index or name.

---

## Word Document Tools

### docxtpl

- **Install**: `pip install docxtpl`
- **Type**: Python library (wraps python-docx + Jinja2)
- **License**: MIT
- **Repository**: https://github.com/elapouya/python-docx-template

| Aspect | Detail |
|--------|--------|
| Strengths | Jinja2 template engine inside Word documents; supports loops, conditionals, images, tables, sub-documents; preserves original formatting |
| Weaknesses | Template must be created manually with Jinja2 tags in Word; complex nesting can be tricky; error messages can be opaque |
| Best for | Reports, letters, contracts — any document with a fixed structure and variable data |
| Avoid when | You need to create a document from scratch without a template (use python-docx directly) |

**Key API patterns**:
```python
from docxtpl import DocxTemplate

doc = DocxTemplate("template.docx")
context = {
    "title": "Monthly Report",
    "items": [
        {"name": "Task 1", "status": "Done"},
        {"name": "Task 2", "status": "Pending"},
    ]
}
doc.render(context)
doc.save("output.docx")
```

**Template syntax in Word**: Type `{{ variable }}` directly in the Word document. For loops: `{% for item in items %}...{% endfor %}`. For conditionals: `{% if condition %}...{% endif %}`.

### python-docx

- **Install**: `pip install python-docx`
- **Type**: Python library
- **License**: MIT

| Aspect | Detail |
|--------|--------|
| Strengths | Full programmatic access to create/edit .docx files; paragraphs, tables, images, styles, headers/footers |
| Weaknesses | No template engine — all content must be added via API calls; verbose for complex documents |
| Best for | Creating documents from scratch when no template exists; modifying existing documents programmatically |
| Avoid when | You have a template to fill (use docxtpl instead) |

---

## Excel Tools

### openpyxl

- **Install**: `pip install openpyxl`
- **Type**: Python library
- **License**: MIT
- **Repository**: https://github.com/theorchard/openpyxl

| Aspect | Detail |
|--------|--------|
| Strengths | Read and write .xlsx; template support via load_workbook(); styles, charts, formulas, merged cells, data validation |
| Weaknesses | Only .xlsx (not .xls); can be slow for very large files; chart creation API is complex |
| Best for | Template-based spreadsheets; modifying existing workbooks; detailed cell-level control |
| Avoid when | Creating simple spreadsheets from scratch with no template (XlsxWriter is faster) |

**Key API patterns**:
```python
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font

# From template
wb = load_workbook("template.xlsx")
ws = wb.active
ws["A1"] = "Updated Value"
wb.save("output.xlsx")

# From scratch
wb = Workbook()
ws = wb.active
ws.title = "Data"
ws.append(["Name", "Value"])  # header row
ws.append(["Item 1", 42])
wb.save("output.xlsx")
```

### XlsxWriter

- **Install**: `pip install XlsxWriter`
- **Type**: Python library
- **License**: BSD-2-Clause

| Aspect | Detail |
|--------|--------|
| Strengths | Fast for creating new .xlsx files; excellent chart support; rich formatting options; memory-efficient for large files |
| Weaknesses | **Write-only** — cannot open or modify existing files; no template support |
| Best for | Creating new spreadsheets from scratch with charts and formatting |
| Avoid when | You need to fill an existing template (use openpyxl) |

---

## PDF Tools

### WeasyPrint

- **Install**: `pip install weasyprint`
- **Type**: Python library
- **License**: BSD-3-Clause
- **Repository**: https://github.com/Kozea/WeasyPrint

| Aspect | Detail |
|--------|--------|
| Strengths | CSS-based styling; excellent typography; supports @page rules for headers/footers/margins; pure Python (no external services); PDF/A support |
| Weaknesses | Requires system-level dependencies on some OSes (GTK/Pango); CSS Flexbox/Grid not fully supported; no JavaScript rendering |
| Best for | Professional PDF generation from HTML+CSS; reports, invoices, contracts |
| Avoid when | You need to render JavaScript-heavy pages (use Playwright/Puppeteer instead) |

**Key API patterns**:
```python
import weasyprint

# From HTML string
html = "<h1>Title</h1><p>Content</p>"
weasyprint.HTML(string=html).write_pdf("output.pdf")

# From HTML file with CSS
weasyprint.HTML(filename="page.html").write_pdf(
    "output.pdf",
    stylesheets=[weasyprint.CSS(filename="style.css")]
)

# From Markdown (convert first)
import markdown
html = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
weasyprint.HTML(string=html).write_pdf("output.pdf")
```

**CSS template features**: Use `@page { margin: 2cm; @top-center { content: "Header"; } }` for page headers/footers. Use `page-break-before: always;` for manual page breaks.

---

## MS Project Tools

### MPXJ

- **Install**: `pip install mpxj`
- **Type**: Python wrapper over Java library
- **License**: LGPL-2.1
- **Repository**: https://github.com/joniles/mpxj

| Aspect | Detail |
|--------|--------|
| Strengths | Reads/writes 20+ project file formats including MSPDI, MPP, Primavera; comprehensive project data model; active maintenance |
| Weaknesses | **Requires Java 11+** — must be installed separately; startup is slower due to JVM initialization; error messages can reference Java internals |
| Best for | Creating MSPDI XML files importable by MS Project; interoperability between project management tools |
| Avoid when | Java is not available and can't be installed; only simple task lists are needed (CSV may suffice) |

**Key API patterns**:
```python
import jpype
import mpxj

# Read
from net.sf.mpxj.reader import UniversalProjectReader
reader = UniversalProjectReader()
project = reader.read("input.mpp")

# Write MSPDI
from net.sf.mpxj.writer import UniversalProjectWriter
from net.sf.mpxj import ProjectFile, Task
from net.sf.mpxj.mspdi import MSPDIWriter

project = ProjectFile()
task = project.addTask()
task.setName("Task 1")
writer = MSPDIWriter()
writer.write(project, "output.xml")
```

**Java dependency**: Always verify Java availability before using MPXJ. Use `runtime_resolver.py java --min-version 11`.

---

## Universal Tools

### Pandoc

- **Install**: System package (`apt install pandoc`, `brew install pandoc`, `choco install pandoc`)
- **Type**: Universal CLI tool (Haskell)
- **License**: GPL-2.0

| Aspect | Detail |
|--------|--------|
| Strengths | Markdown → PPTX/DOCX/PDF in one command; `--reference-doc` for templates; mature and well-documented; supports many Markdown flavors |
| Weaknesses | System dependency (not pip-installable); limited control over slide layouts; template customization is limited to styles, not structure |
| Best for | Quick Markdown → document conversion; when python-pptx/docxtpl is overkill; CI/CD pipelines |
| Avoid when | You need fine-grained control over placeholders, layouts, or programmatic content injection |

**Key patterns**:
```bash
# Markdown → PPTX with template
pandoc input.md -o output.pptx --reference-doc=template.pptx

# Markdown → DOCX with template
pandoc input.md -o output.docx --reference-doc=template.docx

# Markdown → PDF via WeasyPrint
pandoc input.md -o output.pdf --pdf-engine=weasyprint --css=style.css

# Markdown → PDF via LaTeX
pandoc input.md -o output.pdf --pdf-engine=xelatex
```

**`--reference-doc` behavior**: Pandoc copies styles (fonts, colors, layouts) from the reference document and applies them to the output. It does **not** inject content into template placeholders — for that, use docxtpl or python-pptx.

### Carbone (Node.js alternative)

- **Install**: `npm install carbone`
- **Type**: Node.js library
- **License**: Community Edition (free) / Enterprise (paid)

| Aspect | Detail |
|--------|--------|
| Strengths | Template-based generation for DOCX, XLSX, PPTX, ODS, ODT, PDF (via LibreOffice); simple `{d.field}` syntax in templates |
| Weaknesses | Node.js dependency; PDF requires LibreOffice; enterprise features behind paywall |
| Best for | When the team already uses Node.js; multi-format template rendering from a single tool |
| Avoid when | Python-only toolchain; no Node.js available |

Mentioned for awareness — the primary skill workflow uses Python tools.
