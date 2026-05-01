---
name: markdown-to-document
description: "**WORKFLOW SKILL** — Generate formatted documents from Markdown or structured content. USE FOR: creating PowerPoint presentations, Word documents, Excel spreadsheets, MS Project files, PDFs from Markdown/JSON/chat context using templates. DO NOT USE FOR: converting documents TO Markdown (use doc-to-markdown), general file I/O, web scraping."
argument-hint: Describe what document you need and the target format (pptx, docx, xlsx, mspdi, pdf)
license: MIT
---

# Markdown to Document — Agent Guide

You are helping a developer generate formatted documents from Markdown content, structured JSON data, or chat context. The output can be PowerPoint, Word, Excel, MS Project (MSPDI), or PDF. Templates are the preferred approach for polished output — ask the user for one before generating from scratch.

## Installation

All generation scripts include dependency checks — if a required package is missing, the script auto-installs it in non-interactive environments (LLM agents, CI). In interactive terminals, the user is prompted for confirmation.

| Format | Package | Install |
|--------|---------|--------|
| PowerPoint (.pptx) | python-pptx | `pip install python-pptx` |
| Word (.docx) | docxtpl | `pip install docxtpl` |
| Excel (.xlsx) | openpyxl | `pip install openpyxl` |
| PDF (.pdf) | xhtml2pdf + markdown | `pip install xhtml2pdf markdown` |
| PDF (.pdf) — optional engines | fpdf2, weasyprint | `pip install fpdf2` / `pip install weasyprint` |
| MS Project (.mspdi) | mpxj | `pip install mpxj` (requires Java 11+) |

#### Quick Install (all dependencies)

```bash
pip install python-pptx docxtpl openpyxl xhtml2pdf markdown fpdf2 mpxj jpype1
```

> **Note:** All generation scripts overwrite existing output files without warning.

### Fallback: Pandoc (universal converter)

Pandoc supports PPTX, DOCX, and PDF generation from Markdown with `--reference-doc` for templates.

```bash
# Windows
choco install pandoc
# Linux
apt install pandoc
# macOS
brew install pandoc
```

## Standalone Scripts

This skill includes ready-to-run Python scripts in the `scripts/` directory.

> **⚠️ IMPORTANT: Treat scripts as black boxes.** Run `python scripts/<script>.py --help` to learn usage. Do **NOT** read the source code of these scripts — it will pollute your context window with implementation details you don't need. The scripts are designed to be used via their CLI interface only.

When the user needs document generation, **execute these directly** via `run_in_terminal` instead of generating code from scratch.

| Script | Purpose | Quick Usage |
|--------|---------|-------------|
| `generate_pptx.py` | JSON/MD → PowerPoint | `python scripts/generate_pptx.py input.json -t template.pptx -o output.pptx` |
| `generate_docx.py` | JSON/MD → Word | `python scripts/generate_docx.py input.json -t template.docx -o output.docx` |
| `generate_xlsx.py` | JSON/MD → Excel | `python scripts/generate_xlsx.py input.json -o output.xlsx` |
| `generate_project.py` | JSON → MSPDI XML | `python scripts/generate_project.py input.json -o output.xml` |
| `generate_project.py` (inject) | Inject into MSPDI | `python scripts/generate_project.py input.json -t template.xml -o output.xml --mode inject` |
| `validate_project.py` | Validate MSPDI XML | `python scripts/validate_project.py output.xml` (no Java required) |
| `generate_pdf.py` | MD/HTML → PDF | `python scripts/generate_pdf.py input.md -o output.pdf --css style.css` |
| `analyze_template.py` | Extract style profile | `python scripts/analyze_template.py input.pptx -o profile.json` (also .docx, .xlsx, .mpp, .mspdi, .mpx, .xml) |
| `runtime_resolver.py` | Check runtime deps | `python scripts/runtime_resolver.py java --min-version 11` |
| `audit_overflow.py` | Detect text overflow risks | `python scripts/audit_overflow.py output.pptx` |
| `check_placeholders.py` | Detect leftover placeholders | `python scripts/check_placeholders.py output.pptx --strict` |

All scripts accept `--help` for full usage. Paths are passed as parameters — never hardcoded.

> **Working directory:** Run scripts from any directory using absolute paths, or from the skill's root directory using relative paths.

## Format → Tool Mapping

| Format | Extensions | Primary Tool | Fallback | Template Support |
|--------|-----------|-------------|----------|-----------------|
| PowerPoint | .pptx | python-pptx | pandoc `--reference-doc` | Yes — placeholder injection |
| Word | .docx | docxtpl | pandoc `--reference-doc` | Yes — Jinja2 tags |
| Excel | .xlsx | openpyxl | XlsxWriter (from scratch) | Yes — load_workbook |
| PDF | .pdf | xhtml2pdf | fpdf2, WeasyPrint, pandoc | Yes — CSS/HTML templates |
| MS Project | .mspdi (.xml) | MPXJ + Java | — | No — programmatic only |

> **⚠ MS Project trade-off:** The `.mpp` format is proprietary — no open-source library can write it directly. This skill generates **MSPDI XML**, which is the official MS Project interchange format. MS Project opens MSPDI natively with full fidelity (tasks, predecessors, resources, assignments). The user simply opens the `.xml` in Project and can save as `.mpp`. **Always inform the user about this when generating project files.**

## The Template Workflow

This is the core decision flow. Follow it for every document generation request.

```
User request arrives
  │
  ├─ User provides EXAMPLE document (not a template)?
  │   └─ YES → Run analyze_template.py to extract style profile
  │       → Use profile to guide generation (fonts, colors, layouts)
  │       → Ask: "I analyzed your example. Want me to use these patterns?"
  │
  ├─ User provides template file?
  │   ├─ YES → Use template directly
  │   └─ NO → Ask: "Do you have a template (.pptx/.docx/.xlsx) to use as base?"
  │       ├─ YES → User provides path → Use it
  │       └─ NO → Use default generation (no template, clean output)
  │
  ├─ User provides content (MD/JSON)?
  │   ├─ YES → Parse and map to format
  │   └─ NO → Analyze chat context → Structure into JSON intermediate
  │
  └─ Generate document
      ├─ Template path? → Inject content into template
      ├─ Style profile? → Apply extracted patterns to generation
      └─ No template? → Create from scratch with tool defaults
```

### Scenario 1: "Analyze and document"

The user asks to analyze something and produce a document.

1. Perform the requested analysis
2. Structure findings as Markdown or JSON (see Intermediate Representation below)
3. Save intermediate data to a temp JSON file
4. Ask user for template (or proceed without one)
5. Run the appropriate `generate_*.py` script
6. Deliver the generated document

### Scenario 2: "Make a presentation from this chat"

The user asks for a document based on existing chat context.

1. Extract key points from the conversation
2. Structure into the appropriate JSON schema
3. Save to temp JSON file
4. Ask user for template
5. Run the script
6. Deliver

### Scenario 3: "Create using this template"

The user provides a template upfront.

1. Analyze template structure (placeholders, layouts)
2. Gather or generate content to fill placeholders
3. Structure as JSON matching template expectations
4. Run the script with `--template` flag
5. Deliver

### Scenario 4: "Use this existing document as reference"

The user provides an example document and wants new content in the same style.

1. Run `python scripts/analyze_template.py example.pptx` (or .docx / .xlsx / .mpp / .xml)
2. Read the JSON style profile output
3. Use the profile to structure the JSON intermediate:
   - Choose matching slide layouts (most commonly used in the example)
   - Apply font sizes and bullet patterns from the profile
   - Follow the recommendations in the profile output
   - **For MS Project (.mpp/.xml):** Extract WBS structure, resource pool, calendar settings, task duration patterns, and predecessor link types — then generate a new project following the same hierarchy and conventions
4. Generate the new document incorporating those patterns
5. Deliver with a summary of which patterns were applied

> **Tip:** The style profile's `recommendations` field contains ready-to-use guidance. Present these to the user so they can confirm or adjust before generation.

## Intermediate Representation

When Markdown structure isn't sufficient, produce JSON matching these schemas. Save the JSON to a file, then pass it to the generation script.

### PPTX Schema

```json
{
  "slides": [
    {
      "layout": "Title Slide",
      "title": "Presentation Title",
      "body": "Subtitle or description",
      "notes": "Speaker notes for this slide"
    },
    {
      "layout": "Title and Content",
      "title": "Slide Title",
      "body": "- Bullet point 1\n- Bullet point 2\n  - Sub-bullet (level 1)\n    - Deep sub-bullet (level 2)\n- Bullet point 3",
      "notes": "Additional context",
      "image_path": "path/to/image.png"
    }
  ]
}
```

> **Bullet formatting:** Bullet markers (`•`, `-`, `*`) and indentation (2 spaces per level, max level 2) in the `body` field are converted to native PowerPoint bullet formatting with proper paragraph levels. Numbered lists (`1.`, `2.`, etc.) are preserved as text with bullet-level indentation. Lines without markers are rendered as plain paragraphs. Speaker notes are always plain text.

### PPTX Inject Schema

Used with `--mode inject`. Each entry targets an existing slide by index (0-based). If `slide_index` is omitted, slides are matched sequentially.

```json
{
  "slides": [
    {
      "slide_index": 0,
      "title": "New Title for Slide 1",
      "body": "Replaced body content",
      "notes": "Optional new speaker notes"
    },
    {
      "slide_index": 2,
      "title": "Updated Third Slide",
      "body": "- Bullet 1\n- Bullet 2\n- Bullet 3"
    }
  ]
}
```

> **Inject rules:** Only slides referenced in the JSON are modified — others stay untouched. The `title` replaces the title placeholder text. The `body` replaces the first non-title text placeholder. Multi-line body text is split by `\n` and distributed across existing paragraphs; if there are more lines than paragraphs, new ones are cloned from the last paragraph's format. `layout` and `image_path` are ignored in inject mode.

### DOCX Schema

**Without template** (from-scratch generation using built-in structure):

```json
{
  "data": {
    "title": "Document Title",
    "subtitle": "Optional subtitle",
    "author": "Author Name",
    "date": "2026-03-11",
    "sections": [
      {
        "heading": "Section 1",
        "body": "Paragraph text for section 1."
      },
      {
        "heading": "Section 2",
        "body": "Paragraph text for section 2."
      }
    ],
    "items": [
      {"name": "Item 1", "description": "Details about item 1", "status": "Complete"},
      {"name": "Item 2", "description": "Details about item 2", "status": "In Progress"}
    ],
    "summary": "Closing summary paragraph."
  }
}
```

Supported fields: `title`, `subtitle`, `author`, `date`, `sections` (array of `{heading, body}`), `items` (array of objects → rendered as table, or array of strings → rendered as bullet list), `summary`.

**With template** (Jinja2 via docxtpl): Provide fields matching the template's `{{ variable }}` placeholders. Any JSON structure is supported — the data is passed directly to docxtpl's `render()`.

### XLSX Schema

```json
{
  "sheets": {
    "Summary": {
      "headers": ["Metric", "Value", "Change"],
      "rows": [
        ["Revenue", "$1.2M", "+15%"],
        ["Users", "45,000", "+8%"]
      ]
    },
    "Details": {
      "headers": ["Date", "Category", "Amount"],
      "rows": [
        ["2026-01-15", "Sales", "$50,000"],
        ["2026-01-16", "Marketing", "$12,000"]
      ]
    }
  }
}
```

### XLSX Inject Schema

Used with `--mode inject`. Each sheet entry targets an existing sheet by name. Only sheets present in the JSON are modified — others stay untouched.

```json
{
  "sheets": {
    "Summary": {
      "start_row": 2,
      "start_col": 1,
      "headers": ["Metric", "Value", "Change"],
      "rows": [
        ["Revenue", "$2.5M", "+22%"],
        ["Users", "80,000", "+12%"]
      ]
    }
  }
}
```

> **Inject rules:** Only sheets referenced in the JSON are modified — others stay untouched. `start_row` (default: 2) is the first row for data injection. `start_col` (default: 1) is the first column. If `headers` is present, they are injected in the row before `start_row` (preserving formatting). If the template has more data rows than the JSON, leftover cells are cleared (`value=None`) but formatting is preserved. Merged cells, charts, formulas, and conditional formatting are not disturbed.

### MSPDI (Project) Schema

```json
{
  "tasks": [
    {
      "name": "Project Phase 1",
      "start": "2026-04-01",
      "duration": "30d",
      "predecessors": [],
      "resources": ["PM"],
      "outline_level": 1,
      "summary": true,
      "children": [
        {
          "name": "Design",
          "start": "2026-04-01",
          "duration": "10d",
          "predecessors": [],
          "resources": ["Designer"],
          "notes": "Include mockups",
          "percent_complete": 50,
          "constraint_type": "SNET",
          "constraint_date": "2026-04-01",
          "priority": 500,
          "custom_fields": {
            "text1": "Category A",
            "number1": 42,
            "flag1": true
          }
        },
        {
          "name": "Development",
          "duration": "15d",
          "predecessors": [
            {"task": 2, "type": "FS", "lag": "2d"},
            {"task": 3, "type": "SS"}
          ],
          "resources": ["Dev Team"]
        }
      ]
    }
  ],
  "resources": [
    {"name": "PM", "type": "work", "group": "Management", "standard_rate": 100, "max_units": 100},
    {"name": "Designer", "type": "work", "group": "Design"},
    {"name": "Dev Team", "type": "work"}
  ],
  "calendar": {
    "name": "Standard",
    "working_days": ["MON", "TUE", "WED", "THU", "FRI"],
    "hours": {"start": "08:00", "end": "17:00"}
  }
}
```

**New fields (all optional — simple JSON still works):**
- `children` — nested subtasks (WBS hierarchy)
- `outline_level` — explicit WBS level (1-based)
- `summary` — mark as summary/group task
- `predecessors` — integers (backward compat) OR `{"task": id, "type": "FS"|"SS"|"FF"|"SF", "lag": "2d"}`
- `notes` — task notes text
- `percent_complete` — integer 0-100
- `constraint_type` — ASAP, ALAP, SNET, SNLT, FNET, FNLT, MSO, MFO
- `constraint_date` — date for the constraint
- `priority` — integer (0-1000, default 500)
- `custom_fields` — `text1`-`text5`, `number1`-`number5`, `flag1`-`flag5`
- `resources` (top-level) — enriched resource definitions with `type`, `group`, `standard_rate`, `max_units`
- `calendar` — project calendar with working days and hours

### MSPDI Inject Schema

Used with `--mode inject`. Each entry targets an existing task by UID, name, or adds a new task.

```json
{
  "tasks": [
    {"task_uid": 5, "name": "Updated Name", "duration": "8d", "percent_complete": 75},
    {"task_name": "Design Phase", "notes": "Updated notes", "custom_fields": {"text1": "Modified"}},
    {"name": "Brand New Task", "duration": "3d", "start": "2026-05-01", "resources": ["New Resource"]}
  ]
}
```

> **Inject rules:** `task_uid` matches by UID (most precise). `task_name` matches by name (first match). Neither → task is appended as new. Fields not mentioned in the JSON stay untouched. If Java/MPXJ fails, an XML fallback using `xml.etree` handles `.xml`/`.mspdi` files (not `.mpp`).

## Runtime Dependency Discovery

Some tools require external runtimes (Java for MPXJ, LibreOffice for PDF via Carbone). Use the `runtime_resolver.py` script to check availability before running generation.

1. Run `python scripts/runtime_resolver.py <runtime> --min-version <ver>`
2. The script checks: env vars → PATH → known OS paths → reports findings
3. If found: proceed normally
4. If not found: tell the user what's needed and how to install it
5. User can provide custom paths via `--extra-paths PATH1 PATH2`
6. Output is JSON — discovered paths can be stored for future use

Example:
```bash
python scripts/runtime_resolver.py java --min-version 11
# → {"found": true, "version": "17.0.2", "path": "C:\\Program Files\\Java\\jdk-17\\bin\\java.exe", ...}
```

## Per-Format Generation Guide

### PowerPoint (.pptx)

**With template (generate mode — default):**
1. Prepare JSON matching the PPTX schema
2. Run: `python scripts/generate_pptx.py slides.json -t corporate_template.pptx -o output.pptx`
3. The script opens the template, matches slide layouts by name, and populates placeholders

**Without template:**
1. Prepare JSON or pass Markdown directly
2. Run: `python scripts/generate_pptx.py slides.json -o output.pptx`
3. Creates a blank presentation with default slide layouts

**From Markdown:**
- Headings (`##`) become slide titles
- Bullet lists become slide body content
- Content between headings becomes one slide

**Inject mode (mail-merge from corporate templates):**

Use `--mode inject` when you have a fully-designed corporate template and want to replace only the text content while preserving **100% of the visual formatting** (fonts, colors, animations, backgrounds, shapes).

1. Prepare JSON matching the PPTX Inject Schema (see below)
2. Run: `python scripts/generate_pptx.py input.json -t corporate_template.pptx -o output.pptx --mode inject`
3. The script walks existing slides and replaces text in-place via XML manipulation — no slides are added or removed

Key differences from generate mode:
- Does NOT add new slides — works with existing template slides only
- Preserves all `<a:rPr>` (run properties: font, size, color, bold, italic)
- Preserves all `<a:pPr>` (paragraph properties: alignment, spacing, bullets)
- Multi-line body text is distributed across existing paragraphs; excess paragraphs are cloned from the last one
- Slides not referenced in the JSON input remain untouched

**Pandoc fallback:**
```bash
pandoc input.md -o output.pptx --reference-doc=template.pptx
```

### Word (.docx)

**With Jinja2 template:**
1. The template file (.docx) contains Jinja2 tags: `{{ title }}`, `{% for item in items %}`, etc.
2. Prepare JSON matching the template variables
3. Run: `python scripts/generate_docx.py data.json -t report_template.docx -o report.docx`
4. docxtpl renders the template with the JSON data

**Without template:**
1. Pass Markdown or JSON
2. Run: `python scripts/generate_docx.py content.md -o report.docx`
3. Creates a clean document from the Markdown structure

**Pandoc fallback:**
```bash
pandoc input.md -o output.docx --reference-doc=template.docx
```

### Excel (.xlsx)

**With template (generate mode — default):**
1. Prepare JSON matching the XLSX schema
2. Run: `python scripts/generate_xlsx.py data.json -t template.xlsx -o output.xlsx`
3. The script opens the template and fills cells starting from specified positions

**Without template:**
1. Run: `python scripts/generate_xlsx.py data.json -o output.xlsx`
2. Creates a new workbook with one sheet per key in the JSON

**Features:** Bold headers, auto-width columns, basic number formatting.

**Inject mode (preserve formatting from corporate templates):**

Use `--mode inject` when you have a fully-designed XLSX template and want to replace only cell values while preserving **100% of the visual formatting** (fonts, fills, borders, number formats, alignment, merged cells, charts).

1. Prepare JSON matching the XLSX Inject Schema (see above)
2. Run: `python scripts/generate_xlsx.py data.json -t template.xlsx -o output.xlsx --mode inject`
3. The script captures each cell's formatting before writing, then restores it after — no styles are lost

Key differences from generate mode:
- Preserves all cell formatting: font, fill, border, number_format, alignment, protection
- Merged cells are never broken or displaced
- Charts and formulas referencing data cells are not disturbed
- Sheets not referenced in the JSON remain untouched
- Leftover data rows (template has more rows than JSON data) are cleared but keep their formatting

### MS Project (.mspdi)

**Requires Java 11+.** The script checks automatically via `runtime_resolver.py`.

> **Inform the user:** This skill generates MSPDI XML (`.xml`), not `.mpp` directly. The `.mpp` format is proprietary and cannot be written by open-source tools. However, **MS Project imports MSPDI XML natively with full fidelity** — all tasks, durations, predecessors, resources, and assignments are preserved. The user opens the `.xml` in Project and saves as `.mpp` if needed. If the user has MS Project installed and wants direct `.mpp` output, COM Automation (`win32com`) is an alternative path but requires the application installed locally.

**Generate mode (default):**
1. Prepare JSON matching the MSPDI schema (supports WBS hierarchy, custom fields, constraints, enriched resources, calendar)
2. Run: `python scripts/generate_project.py tasks.json -o project.xml`
3. Output is MSPDI XML — open directly in MS Project, Project Professional, or ProjectLibre
4. Save as `.mpp` from within the application if the binary format is needed

**Inject mode (modify existing projects):**

Use `--mode inject` to modify tasks in an existing MSPDI XML file while preserving all other data.

1. Prepare JSON matching the MSPDI Inject Schema (`task_uid`, `task_name`, or new tasks)
2. Run: `python scripts/generate_project.py inject.json -t existing.xml -o output.xml --mode inject`
3. Tasks matched by UID or name are updated; unmatched entries are added as new tasks
4. Fields not mentioned in the JSON stay untouched (full preservation)

> If Java/MPXJ is unavailable, inject falls back to `xml.etree` for `.xml`/`.mspdi` files (not `.mpp`).

**Validate output:**

After generating or injecting, validate the result:
```bash
python scripts/validate_project.py output.xml
python scripts/validate_project.py output.xml --json    # JSON output
python scripts/validate_project.py output.xml --strict   # warnings = errors
```

If Java is not found, the generate script prints installation instructions and exits.

### PDF (.pdf)

The script auto-detects the best available engine: **xhtml2pdf** → **fpdf2** → **WeasyPrint**. You can force one with `--engine`.

**Dependencies:**
```bash
pip install xhtml2pdf markdown  # primary engine
pip install fpdf2               # fallback engine (optional)
pip install weasyprint           # tertiary engine (optional, requires GTK3/Pango)
```

**From Markdown:**
1. Run: `python scripts/generate_pdf.py content.md -o output.pdf`
2. Markdown is converted to HTML internally, then rendered to PDF

**With CSS template (xhtml2pdf or WeasyPrint):**
1. Run: `python scripts/generate_pdf.py content.md -o output.pdf --css corporate_style.css`
2. CSS controls fonts, margins, headers/footers, page breaks

**Force a specific engine:**
```bash
python scripts/generate_pdf.py content.md -o output.pdf --engine xhtml2pdf
python scripts/generate_pdf.py content.md -o output.pdf --engine fpdf2
python scripts/generate_pdf.py content.md -o output.pdf --engine weasyprint
```

**Pandoc fallback:**
```bash
pandoc input.md -o output.pdf --pdf-engine=weasyprint --css=style.css
```

## When the User Asks for Help

- **"Create a presentation from this content"** → Structure content into PPTX JSON schema. Ask for template. Run `python scripts/generate_pptx.py`. Verify python-pptx is installed first.

- **"Generate a report as Word document"** → Ask if they have a .docx template with Jinja2 tags. Structure data as JSON. Run `python scripts/generate_docx.py`. Verify docxtpl is installed.

- **"Make a spreadsheet from this data"** → Structure data into XLSX JSON schema (sheets → headers + rows). Run `python scripts/generate_xlsx.py`. Verify openpyxl is installed.

- **"Export this as a project plan"** → Check Java: `python scripts/runtime_resolver.py java --min-version 11`. Structure as MSPDI JSON schema. Run `python scripts/generate_project.py`.

- **"Generate a PDF from this"** → Determine if input is Markdown or HTML. Ask if they have CSS styles. Run `python scripts/generate_pdf.py`. Requires xhtml2pdf or fpdf2 (`pip install xhtml2pdf markdown`).

- **"I have a template I want to use"** → Identify the template format (.pptx/.docx/.xlsx). Analyze what placeholders/variables it expects. Structure content to match. Run the corresponding script with `-t`.

- **"Convert this chat into a document"** → Extract key content from conversation. Ask target format. Structure into appropriate JSON schema. Generate.

## Quick Reference

| I need to... | Format | Tool | Template? |
|---|---|---|---|
| Create a presentation | PPTX | python-pptx | Recommended |
| Write a report | DOCX | docxtpl | Recommended |
| Build a spreadsheet | XLSX | openpyxl | Optional |
| Export a project plan | MSPDI | MPXJ + Java | N/A |
| Generate a PDF | PDF | xhtml2pdf / fpdf2 | CSS optional |
| Quick convert (any) | PPTX/DOCX/PDF | Pandoc | `--reference-doc` |
| Analyze a template | PPTX/DOCX/XLSX/MPP | analyze_template.py | N/A — reads existing docs |

## QA Pipeline

After generating a PPTX, XLSX, or MSPDI (especially in inject mode), run the QA scripts to catch issues before delivery:

```bash
# PPTX pipeline
python scripts/generate_pptx.py input.json -t template.pptx -o output.pptx --mode inject
python scripts/audit_overflow.py output.pptx
python scripts/check_placeholders.py output.pptx --strict

# MSPDI pipeline
python scripts/generate_project.py tasks.json -o project.xml
python scripts/validate_project.py project.xml
```

| Script | What it checks | Exit code |
|--------|---------------|----------|
| `audit_overflow.py` | Text boxes where content exceeds estimated capacity | 1 if any OVERFLOW, 0 otherwise |
| `check_placeholders.py` | Leftover template text ("Click to add", "Lorem ipsum", demo names) | 1 if any found, 0 if clean |
| `validate_project.py` | MSPDI XML: predecessors, cycles, durations, WBS, assignments | 1 if errors, 0 if warnings/info only |

**`audit_overflow.py` flags:**
- `--budget 0.8` — capacity threshold for "AT RISK" warning (default: 80%)
- `--json` — output as JSON for programmatic use

**`check_placeholders.py` flags:**
- `--strict` — also detect demo company names (Contoso, Fabrikam) and example URLs
- `--json` — output as JSON
- `--patterns file.txt` — additional regex patterns (one per line)

**CI integration:** Both scripts return exit code 1 on failure, making them suitable for CI pipelines:
```bash
python scripts/audit_overflow.py output.pptx && python scripts/check_placeholders.py output.pptx --strict
```

## Common Pitfalls

❌ Generating a PPTX by writing raw XML — use python-pptx, it handles the complexity.
✅ Use `Presentation()` from python-pptx to create or open templates.

❌ Hardcoding slide layout indices — layout names differ between templates.
✅ Match layouts by name: `prs.slide_layouts.get_by_name("Title and Content")` with fallback to index.

❌ Installing MPXJ without checking for Java first.
✅ Always run `runtime_resolver.py java --min-version 11` before using MPXJ.

❌ Using `python-docx` for template rendering — it has no template engine.
✅ Use `docxtpl` which wraps python-docx and adds Jinja2 template support.

❌ Generating PDF from Markdown using raw `markdown` library — styling is minimal.
✅ Use xhtml2pdf (CSS support) or fpdf2 (lightweight) via `generate_pdf.py`. WeasyPrint is optional for best quality but requires GTK3 on Windows.

❌ Passing Markdown with `---` frontmatter to generation scripts — it will be treated as content.
✅ Strip YAML frontmatter before passing to scripts, or use JSON input instead.

❌ Creating Excel files with XlsxWriter when you need to fill a template — XlsxWriter only creates new files.
✅ Use openpyxl's `load_workbook()` to open and modify existing templates.

For detailed tool comparisons, see [tools-reference.md](./references/tools-reference.md).
For code examples by format, see [examples.md](./references/examples.md).
For troubleshooting common issues, see [troubleshooting.md](./references/troubleshooting.md).
For template creation guidance, see [templates-guide.md](./references/templates-guide.md).

## Companion Skills

- For **the reverse direction** (documents → Markdown): use **doc-to-markdown**
- For **understanding intent** before generating documents: use **task-intent**
