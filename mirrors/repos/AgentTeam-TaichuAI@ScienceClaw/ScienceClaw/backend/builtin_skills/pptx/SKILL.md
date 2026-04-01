---
name: pptx
description: "Use this skill any time a .pptx file is involved — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading or extracting text from .pptx files; editing or updating existing presentations; combining or splitting slide files; working with templates, layouts, speaker notes, or comments. Trigger whenever the user mentions 'deck', 'slides', 'presentation', or references a .pptx filename. If a .pptx file needs to be opened, created, or touched, use this skill."
license: Proprietary. LICENSE.txt has complete terms
---

# PPTX Skill

## Quick Reference

| Task | Approach |
|------|----------|
| Read/analyze content | `python3 -m markitdown presentation.pptx` |
| **Generate structured presentation** | **Use `generate_report.js` — see below** |
| Create custom from scratch | Use pptxgenjs directly (see pptxgenjs section) |

---

## Generating Presentations (Recommended)

For structured presentations with cover slide, auto-generated TOC, content slides, and closing, use the pre-built template:

### Step 1: Copy the generator script

```bash
cp /builtin-skills/pptx/scripts/generate_report.js ./generate_pptx.js
```

### Step 2: Build `slides_data.json` via Python script

**Two phases: write slide content files, then assemble into JSON.**

**CRITICAL**: NEVER write or edit `.json` files directly. Use a Python script with `json.dump()` to guarantee valid JSON output.

**Phase 1 — Write each slide's content as a plain text file** using `write_file`:

For each major topic, `read_file` the relevant research data, then `write_file` the slide content directly:
```
read_file("research_data/literature.md")           # refresh data in context
write_file("slides/slide_01_intro.txt", "...")      # write slide body
write_file("slides/slide_02_analysis.txt", "...")   # next slide
...
```
Each content slide body should be concise but substantive (3-6 bullet points or 2-4 sentences with specific data and citations).

**NEVER write a Python script that contains slide text as string literals.** The slide content goes directly into .txt files via `write_file`, not into Python code.

**Language (CRITICAL):**
- All presentation content (title, subtitle, slide headings, body text, chart labels, speaker notes) MUST be written in the **user's configured language** as specified in the system prompt's `## Language` section.
- If the user's language is Chinese (`zh`), write the entire presentation in Chinese; if English (`en`), write in English. Do NOT mix languages unless quoting a proper noun or technical term that has no standard translation.

**Phase 2 — Assemble into JSON** using a standard assembler script:

```python
import json, glob, os

SLIDES_DIR = "slides"
TITLE = "Presentation Title"
SUBTITLE = "Subtitle or tagline"

# Slide config: (file_pattern, type, title, extra_fields_or_None)
SLIDE_MAP = [
    ("slide_01_*.txt", "section", "Introduction", None),
    ("slide_02_*.txt", "bullets", "Key Findings", None),
    ("slide_03_*.txt", "content", "Market Overview", {"layout": "text-image", "image": "chart.png"}),
    ("slide_04_*.txt", "stat", "Key Metrics", {
        "stats": [
            {"value": "25%", "label": "Revenue Growth"},
            {"value": "15%", "label": "Cost Reduction"},
            {"value": "32%", "label": "Market Share"},
        ]
    }),
    ("slide_05_*.txt", "content", "Trend Analysis", None),
    (None, "chart_pie", "Distribution", {
        "labels": ["Type A", "Type B", "Type C", "Other"],
        "values": [35, 30, 20, 15],
    }),
    (None, "chart_line", "Yearly Trends", {
        "x_labels": ["2020", "2021", "2022", "2023", "2024"],
        "series": [{"name": "Metric", "values": [40, 55, 62, 70, 78]}],
    }),
]

data = {
    "title": TITLE, "subtitle": SUBTITLE,
    "author": "ScienceClaw", "date": "2026-03-09",
    "theme": "midnight", "toc": True, "slides": [],
}

for entry in SLIDE_MAP:
    pattern, stype, title, extra = entry
    slide = {"type": stype, "title": title}

    if pattern:
        matches = sorted(glob.glob(os.path.join(SLIDES_DIR, pattern)))
        if matches:
            body = open(matches[0], encoding="utf-8").read().strip()
            if stype == "bullets":
                slide["items"] = [line.strip() for line in body.split("\n") if line.strip()]
            else:
                slide["body"] = body

    if extra:
        slide.update(extra)
    data["slides"].append(slide)

# Closing slide
data["slides"].append({"type": "closing", "title": "Thank You", "subtitle": "Questions?"})

with open("slides_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"Generated slides_data.json ({len(data['slides'])} slides)")
```

### Step 3: Generate the PPTX

```bash
python3 build_slides_data.py   # outputs slides_data.json
node generate_pptx.js slides_data.json output.pptx
```

### Supported slide types

| Type | Required Fields | Optional Fields |
|------|----------------|-----------------|
| `title` | (auto from top-level) | `title`, `subtitle`, `author`, `date` |
| `agenda` | `items` (string array) | `title` (default: "Agenda") |
| `section` | `title` | `subtitle` |
| `content` | `title` | `body`, `layout`, `image` |
| `bullets` | `title`, `items` | `subtitle` |
| `two_column` | `title`, `left`, `right` | each column: `{heading, body}` or `{heading, items}` |
| `table` | `title`, `headers`, `rows` | `caption` |
| `stat` | `title`, `stats` | stats: `[{value, label}]` (2-4 items) |
| `image` | `title`, `image` | `caption` |
| `chart_bar` | `title`, `categories`, `series` | series: `[{name, values}]` |
| `chart_pie` | `title`, `labels`, `values` | — |
| `chart_line` | `title`, `x_labels`, `series` | series: `[{name, values}]` |
| `quote` | `text` | `author`, `title` |
| `closing` | `title` | `subtitle`, `contact` |

**Chart types for data visualization (use 2-4 per presentation, mix types):**
- `chart_bar` — for comparisons, rankings (e.g. drug efficacy scores)
- `chart_pie` — for proportions, distributions (e.g. mutation type breakdown)
- `chart_line` — for trends over time (e.g. yearly incidence rates)

### Top-level JSON keys

| Key | Required | Description |
|-----|----------|-------------|
| `title` | Yes | Presentation title (cover slide) |
| `subtitle` | No | Subtitle on cover slide |
| `author` | No | Author name |
| `date` | No | Date string |
| `theme` | No | Color theme (see below) |
| `toc` | No | Auto-generate Table of Contents slide (default: true) |
| `slides` | Yes | Array of slide objects |

### Available themes

| Theme | Primary | Secondary | Accent | Style |
|-------|---------|-----------|--------|-------|
| `midnight` | `1E2761` | `CADCFC` | `408EC6` | Dark navy, professional |
| `forest` | `2C5F2D` | `97BC62` | `F5F5F5` | Green, nature |
| `coral` | `F96167` | `F9E795` | `2F3C7E` | Warm, energetic |
| `ocean` | `065A82` | `1C7293` | `21295C` | Deep blue, calm |
| `charcoal` | `36454F` | `F2F2F2` | `212121` | Minimal, modern |
| `teal` | `028090` | `00A896` | `02C39A` | Fresh, trustworthy |
| `berry` | `6D2E46` | `A26769` | `ECE2D0` | Elegant, warm |

### Design guidelines

- **Every slide needs a visual element** — avoid text-only slides
- **Vary layouts** — don't repeat the same layout across slides
- **Use section slides** to separate major topics — these also populate the auto-generated TOC
- **Use stat slides** for key numbers (big number + label format)
- **Mix chart types** — aim for 2-4 charts per presentation (bar for comparisons, pie for distributions, line for trends)
- **Keep bullet points concise** — 3-6 items per slide, 1-2 lines each
- **Content quality**: Each slide body should contain specific data, not vague summaries. Include numbers, percentages, dates, and source references where possible.

### Writing guidelines for long presentations

1. **Use the two-phase workflow**: Write slide content as separate text files first, then assemble into JSON. This avoids context loss and allows iterative refinement.
2. **Be specific**: Slide bodies should contain concrete data, not generic statements. "Revenue grew 25% to $4.2B in Q3 2025" beats "Revenue increased significantly".
3. **Use section slides as dividers**: They auto-populate the TOC and give the audience clear navigation.
4. **Balance text and visuals**: For every 2-3 text/bullet slides, include a chart, stat, or image slide.
5. **End with a closing slide**: Include contact info or next steps.
6. **No page/slide count on cover**: Do NOT include total page count or slide count on the cover slide or subtitle — the count is unknown at assembly time and produces inaccurate information.

---

## Reading Content

```bash
python3 -m markitdown presentation.pptx
```

---

## Creating Custom Presentations (pptxgenjs)

For fully custom presentations beyond the template's capabilities, use pptxgenjs directly:

```javascript
const pptxgen = require("pptxgenjs");
let pres = new pptxgen();
pres.layout = "LAYOUT_16x9";

let slide = pres.addSlide();
slide.addText("Hello World!", { x: 0.5, y: 0.5, fontSize: 36, color: "363636" });

pres.writeFile({ fileName: "output.pptx" });
```

### Key rules for pptxgenjs

- **NEVER use "#" with hex colors** — `color: "FF0000"` not `color: "#FF0000"`
- **Use `bullet: true`** — NEVER unicode symbols like "•"
- **Use `breakLine: true`** between array items for multi-line text
- **NEVER reuse option objects** — pptxgenjs mutates them in-place; create fresh objects each time
- Coordinates are in inches; `LAYOUT_16x9` = 10" × 5.625"

---

## Converting to Images (for QA)

```bash
python3 /builtin-skills/pptx/scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

---

## Dependencies

- `npm install -g pptxgenjs` — creating presentations
- `pip install "markitdown[pptx]"` — text extraction
- `pip install Pillow` — image processing
- LibreOffice (`soffice`) — PDF conversion
- Poppler (`pdftoppm`) — PDF to images
