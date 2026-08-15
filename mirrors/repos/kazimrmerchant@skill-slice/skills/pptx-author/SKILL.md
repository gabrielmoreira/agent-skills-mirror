---
name: pptx-author
description: "Writes .pptx files headless with python-pptx (pitch decks, IC memos, earnings notes), optionally binding every figure to an Excel model via openpyxl. Use when the deliverable is a .pptx on disk, especially model-backed finance decks paired with excel-author. Not for live PowerPoint/Office MCP sessions or animation-heavy all-hands decks (powerpoint). Never email or upload the file from this skill — write ./out only."
version: 1.0.1
author: Anthropic (adapted by Nous Research)
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [powerpoint, pptx, python-pptx, presentation, finance]
    related_skills: [excel-author, powerpoint]
---

# pptx-author

Produce a `.pptx` file on disk using `python-pptx`. Use when you need to deliver a deck as a file artifact, not drive a live PowerPoint session.

Adapted from Anthropic's `pptx-author` and `pitch-deck` skills in [anthropics/financial-services](https://github.com/anthropics/financial-services). The MCP / Office-JS branches of the originals are dropped — this skill assumes headless Python.

For the broader PowerPoint authoring skill (slides, speaker notes, embeds, media, animations), see the built-in `powerpoint` skill. This skill is a lighter-weight pattern tuned for **model-backed decks** where every number must trace to a source workbook.

## When to Use

- You need a `.pptx` file written to disk as a deliverable artifact.
- Building **pitch decks, IC memos, earnings notes**, or other finance-flavored decks where numbers must trace to an Excel model.
- You are working headless (no live PowerPoint session, no Office MCP).
- You want to pair with `excel-author` so that every figure on a slide is bound to a workbook cell or named range.

### When NOT to use this skill

- The user is in a **live PowerPoint session** with an Office MCP available — drive their live doc instead.
- **Non-financial slideware** (quarterly all-hands, marketing decks) — use the broader `powerpoint` skill.
- Decks with **heavy animation, transitions, or speaker notes** — use the broader `powerpoint` skill.

## Prerequisites

### Python environment

```bash
pip install "python-pptx>=0.6"
pip install openpyxl  # for reading model workbooks
```

On Windows (PowerShell):

```powershell
pip install "python-pptx>=0.6"
pip install openpyxl
```

### Directory expectations

| Path | Purpose |
|------|---------|
| `./out/` | Output directory for `.pptx` files. Create if it does not exist. |
| `./out/model.xlsx` | Source Excel model (produced by `excel-author` or provided by user). |
| `./out/charts/` | PNG charts rendered from the model workbook. |
| `./templates/firm-template.pptx` | Optional firm-branded template. If present, load it to inherit colors, fonts, and master layouts. |

### Output contract

- **Write to `./out/<name>.pptx`**. Create `./out/` if it does not exist.
- **Return the relative path** in your final message.
- **Never email, upload, or post** the file. This skill writes a file only. Orchestration layers handle delivery.

## Procedure

### Step 1 — Install dependencies

```bash
pip install "python-pptx>=0.6" openpyxl
```

### Step 2 — Load the firm template (if mounted)

If `./templates/firm-template.pptx` exists, load it so the deck inherits branded colors, fonts, and master layouts. Otherwise start from a blank presentation.

```python
from pptx import Presentation
from pathlib import Path

template = Path("./templates/firm-template.pptx")
prs = Presentation(str(template)) if template.exists() else Presentation()
```

### Step 3 — Read model values from the source workbook

Every number on a slide must trace to the model. Read named ranges or specific cells from your Excel model so deck numbers never drift.

```python
from openpyxl import load_workbook

wb = load_workbook("./out/model.xlsx", data_only=True)

def nr(name):
    """Resolve a named range to its current computed value."""
    rng = wb.defined_names[name]
    sheet, coord = next(rng.destinations)
    return wb[sheet][coord].value

revenue_fy24 = nr("RevenueFY24")
implied_mid  = nr("ImpliedSharePriceBase")
```

> **Critical:** openpyxl only sees computed values if the workbook has already been calculated. Run the recalc helper in the `excel-author` skill first, or open/save through a real Excel session before reading.

### Step 4 — Build slides (one idea per slide)

**Title states the takeaway; body supports it.** A slide titled "Q3 Revenue" is weak. "Revenue growth accelerated to 14% Y/Y in Q3" is strong.

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pathlib import Path

template = Path("./templates/firm-template.pptx")
prs = Presentation(str(template)) if template.exists() else Presentation()

# Title slide
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "Project Aurora — Strategic Alternatives"
slide.placeholders[1].text = "Preliminary Discussion Materials"

# Valuation summary slide (title-only layout)
slide = prs.slides.add_slide(prs.slide_layouts[5])
slide.shapes.title.text = "Valuation implies $38–$52 per share across methodologies"
```

### Step 5 — Add tables bound to model outputs

```python
rows, cols = 5, 4
tbl_shape = slide.shapes.add_table(rows, cols,
                                   Inches(0.5), Inches(1.5),
                                   Inches(9), Inches(3))
tbl = tbl_shape.table
headers = ["Methodology", "Low ($)", "Mid ($)", "High ($)"]
for c, h in enumerate(headers):
    tbl.cell(0, c).text = h

# In a real deck, read these from the model workbook with openpyxl
data = [
    ("Trading comps",     "35", "41", "48"),
    ("Precedent M&A",     "39", "45", "52"),
    ("DCF (base)",        "36", "43", "51"),
    ("LBO (10% IRR)",     "33", "38", "44"),
]
for r, row in enumerate(data, start=1):
    for c, val in enumerate(row):
        tbl.cell(r, c).text = val
```

### Step 6 — Embed charts as PNG from the model

When fidelity matters (the model's chart styling must match the deck exactly), render the chart to PNG from the source workbook and embed the image. Native `pptx.chart` charts are fragile and often don't match firm conventions.

```python
slide = prs.slides.add_slide(prs.slide_layouts[5])
slide.shapes.title.text = "Football field — current price $42"
slide.shapes.add_picture("./out/charts/football_field.png",
                         Inches(1), Inches(1.8), width=Inches(8))
```

### Step 7 — Footnote every number with its source

If a figure on a slide came from `./out/model.xlsx`, footnote the sheet and cell:

```
Revenue: $1,250M  (Source: model.xlsx, Inputs!C3)
```

Never transcribe numbers from memory or from a summary — open the workbook, read the named range, and bind the deck value to it programmatically.

### Step 8 — Save to the output directory

```python
Path("./out").mkdir(exist_ok=True)
prs.save("./out/pitch-aurora.pptx")
```

Return the relative path `./out/pitch-aurora.pptx` in your final message.

## Slide-type checklist for pitch decks

A typical banking pitch deck follows this structure. Not prescriptive, but useful as a starting skeleton:

1. Cover / title
2. Disclaimer
3. Table of contents
4. Situation overview
5. Company snapshot (the target)
6. Market / sector context
7. Valuation summary (football field) — the money slide
8. Trading comps detail
9. Precedent transactions detail
10. DCF summary
11. Illustrative LBO / sponsor case
12. Process considerations
13. Appendix

## Pitfalls

- **openpyxl reads stale values.** `load_workbook(..., data_only=True)` only returns cached computed values. If the workbook hasn't been opened/saved in Excel or recalculated via the `excel-author` recalc helper, you will read `None` or outdated numbers. Always recalculate first.
- **Native pptx charts are fragile.** `pptx.chart` charts often don't match firm conventions and break across PowerPoint versions. Prefer embedding PNG charts rendered from the source workbook.
- **Numbers transcribed from memory.** Never type a figure from memory or a summary. Always open the workbook, read the cell or named range, and bind programmatically.
- **Missing `./out/` directory.** `prs.save()` will fail if the directory doesn't exist. Always call `Path("./out").mkdir(exist_ok=True)` before saving.
- **Template not loaded.** If `./templates/firm-template.pptx` exists but you forget to pass it to `Presentation()`, the deck will use default layouts and won't inherit firm branding.
- **Placeholder index errors.** `slide.placeholders[1]` assumes the layout has a subtitle placeholder. Title-only layouts (index 5) may not. Always check `len(slide.placeholders)` before indexing.
- **No external sends.** This skill writes a file only. It must never email, upload, or post the deck. Orchestration layers handle delivery.

## Verification

After generating the deck, verify the output:

```bash
# Confirm the file exists and is non-trivial in size
ls -la ./out/pitch-aurora.pptx
```

On Windows (PowerShell):

```powershell
Get-Item ./out/pitch-aurora.pptx | Select-Object Name, Length, LastWriteTime
```

Verify the file is a valid pptx by reopening it:

```python
from pptx import Presentation
from pathlib import Path

p = Path("./out/pitch-aurora.pptx")
assert p.exists(), f"Output file not found: {p}"
assert p.stat().st_size > 1000, "File is suspiciously small — likely empty or corrupt"

prs = Presentation(str(p))
print(f"Slides: {len(prs.slides)}")
for i, slide in enumerate(prs.slides):
    title = ""
    if slide.shapes.title and slide.shapes.title.has_text_frame:
        title = slide.shapes.title.text
    print(f"  Slide {i+1}: {title}")
```

Expected output (example):

```
Slides: 3
  Slide 1: Project Aurora — Strategic Alternatives
  Slide 2: Valuation implies $38–$52 per share across methodologies
  Slide 3: Football field — current price $42
```

## Related skills

- **excel-author** — Build the source workbook that feeds deck numbers. Run its recalc helper before reading values.
- **powerpoint** — Broader PowerPoint skill for live sessions, speaker notes, animations, transitions, and non-financial slideware.

## Attribution

Conventions adapted from Anthropic's Claude for Financial Services plugin suite, Apache-2.0 licensed. Original: https://github.com/anthropics/financial-services/tree/main/plugins/agent-plugins/pitch-agent/skills/pptx-author
