---
type: skill
inheritance: inheritable
lifecycle: stable
name: "book-publishing"
description: "Markdown-to-PDF pipeline via Pandoc and LuaLaTeX with emoji rendering, dual output, and print-ready formatting"
tier: extended
applyTo: '**/*book*,**/*publish*,**/*pdf*,**/*pandoc*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Book Publishing

> End-to-end book production pipeline: Markdown → Pandoc → LuaLaTeX → dual PDF (print + digital).

> **Staleness Watch**: See [EXTERNAL-API-REGISTRY.md](../../../EXTERNAL-API-REGISTRY.md) for source URLs and recheck cadence

**Scope**: Inheritable skill. Covers the complete pipeline for producing professional-quality PDF books from Markdown source, including emoji handling, dual format output, and print-ready configuration.

## Pipeline Architecture

```
Markdown Source
    ↓
Pandoc (--pdf-engine=lualatex)
    ↓
LuaLaTeX Engine
    ↓
├── Print PDF (twoside, crop marks, ISBN)
└── Digital PDF (oneside, hyperlinks, bookmarks)
```

### Key Dependencies

| Tool | Version | Purpose |
|------|---------|---------|
| Pandoc | 3.x+ | Markdown → LaTeX conversion |
| LuaLaTeX | TeX Live 2024+ | PDF rendering (Unicode-native) |
| Twemoji | Latest | Cross-platform emoji rendering |
| `needspace` package | LaTeX | Orphan/widow prevention |

**Why LuaLaTeX**: Native Unicode support (XeLaTeX works but LuaLaTeX handles emoji processing more reliably with Lua filters).

## Emoji Handling (Critical)

### The ZWJ Problem

Zero Width Joiner (ZWJ) sequences combine multiple emoji into one glyph. **Sort order is critical**:

| Emoji | Codepoints | Length |
|-------|-----------|--------|
| 👨‍👩‍👧‍👦 | U+1F468 U+200D U+1F469 U+200D U+1F467 U+200D U+1F466 | 7 |
| 👨‍👩‍👧 | U+1F468 U+200D U+1F469 U+200D U+1F467 | 5 |
| 👨‍👩 | U+1F468 U+200D U+1F469 | 3 |
| 👨 | U+1F468 | 1 |

**CRITICAL RULE**: The emoji replacement map MUST be sorted by **length descending** (longest sequences first). If you process `👨` before `👨‍👩‍👧‍👦`, the family emoji gets partially replaced and corrupts the output.

### Emoji Map File

Create an explicit `emoji-map.json` that controls all replacements:

```json
{
  "metadata": {
    "version": "1.0",
    "source": "Twemoji",
    "sortOrder": "length-descending"
  },
  "emojis": [
    {
      "sequence": "👨‍👩‍👧‍👦",
      "codepoints": "1f468-200d-1f469-200d-1f467-200d-1f466",
      "image": "1f468-200d-1f469-200d-1f467-200d-1f466.png",
      "length": 7
    }
  ]
}
```

**Rule**: Never rely on automatic emoji detection. Use an explicit map file that you control and sort.

### Twemoji Base64 Embedding

Embed Twemoji images directly as base64 in the LaTeX output to avoid external file dependencies:

```lua
-- Pandoc Lua filter for emoji replacement
function Str(elem)
  -- Process emoji map (length-descending order)
  for _, entry in ipairs(emoji_map) do
    if elem.text:find(entry.sequence) then
      local img = pandoc.Image("", entry.base64_data_uri)
      -- Set size to match surrounding text
      img.attributes.height = "1em"
      return img
    end
  end
end
```

### Windows Emoji Limitation

Windows cannot natively render flag emoji (🇺🇸, 🇬🇧, etc.) in many contexts. Solutions:

| Approach | Result |
|----------|--------|
| Twemoji replacement in PDF | Full flag rendering |
| HTML output with Twemoji CSS | Full flag rendering |
| Windows terminal/editor | Broken or missing flags |

**Rule**: Always preview emoji-heavy content in the PDF output, not in the editor.

## Dual PDF Configuration

### Print Edition

```yaml
# pandoc-print.yaml
pdf-engine: lualatex
variables:
  documentclass: book
  classoption:
    - twoside            # Different left/right margins
    - openright           # Chapters start on right pages
  geometry:
    - inner=2.5cm        # Binding side (wider)
    - outer=2cm
    - top=2.5cm
    - bottom=2.5cm
  fontsize: 11pt
  mainfont: "Linux Libertine O"
  monofont: "Fira Code"
  linestretch: 1.15
```

### Digital Edition

```yaml
# pandoc-digital.yaml
pdf-engine: lualatex
variables:
  documentclass: book
  classoption:
    - oneside            # Symmetric margins
  geometry:
    - margin=2cm
  fontsize: 11pt
  colorlinks: true
  linkcolor: blue
  urlcolor: blue
  toccolor: blue
```

### Key Differences

| Feature | Print | Digital |
|---------|-------|---------|
| Page layout | `twoside` (inner/outer margins) | `oneside` (symmetric) |
| Chapters | `openright` (start on right page) | No forced page side |
| Links | Black text (no hyperlinks on paper) | Blue, clickable |
| Crop marks | Yes (for professional printing) | No |
| Blank pages | Inserted for chapter openings | None |

## Page Numbering

### Front Matter vs. Body

| Section | Numbering | Style |
|---------|-----------|-------|
| Title page | None | — |
| Copyright, dedication | None | — |
| Table of Contents | Roman (i, ii, iii) | `\pagenumbering{roman}` |
| Foreword, preface | Roman (continues) | — |
| Chapter 1+ | Arabic (1, 2, 3) | `\pagenumbering{arabic}` |
| Appendices | Arabic (continues) or lettered | `\appendix` |
| Index | Arabic (continues) | — |

**Rule**: The transition from Roman to Arabic numbering resets at page 1 for the first chapter.

## Table of Contents

LaTeX auto-generates TOC from headings. Configure depth:

```latex
\setcounter{tocdepth}{2}    % Include down to subsections
\setcounter{secnumdepth}{2} % Number down to subsections
```

### Heading Lint Before Build

Run a heading validation pass before PDF generation:

| Check | Rule | Why |
|-------|------|-----|
| No skipped levels | H1 → H2 → H3 (not H1 → H3) | TOC structure breaks |
| Unique within chapter | No duplicate H2 headings in same chapter | Anchor collisions |
| No trailing punctuation | "Getting Started" not "Getting Started." | TOC formatting |
| Consistent casing | Title Case or Sentence case, not mixed | Professional appearance |

## Orphan/Widow Prevention

### The `needspace` Package

Prevents headings from appearing at the bottom of a page with no following content:

```latex
\usepackage{needspace}
\needspace{4\baselineskip}  % Ensure 4 lines available before heading
```

### Configuration

| Element | Minimum Space |
|---------|--------------|
| Chapter title | New page (automatic in `book` class) |
| Section heading | 4 `\baselineskip` |
| Subsection heading | 3 `\baselineskip` |
| Code block | 5 `\baselineskip` |
| Figure/table | Full figure height + caption |

## Build Pipeline

### Complete Build Script

```bash
#!/bin/bash
# build-book.sh — Dual PDF build

set -e

# Step 1: Lint headings
echo "Linting headings..."
python scripts/lint-headings.py chapters/*.md

# Step 2: Generate emoji map (sorted by length descending)
echo "Generating emoji map..."
python scripts/build-emoji-map.py --sort-by-length-desc

# Step 3: Build print edition
echo "Building print PDF..."
pandoc chapters/*.md \
  --defaults=pandoc-print.yaml \
  --lua-filter=filters/emoji.lua \
  --lua-filter=filters/needspace.lua \
  --toc \
  --output=output/book-print.pdf

# Step 4: Build digital edition
echo "Building digital PDF..."
pandoc chapters/*.md \
  --defaults=pandoc-digital.yaml \
  --lua-filter=filters/emoji.lua \
  --toc \
  --output=output/book-digital.pdf

echo "Build complete: output/book-print.pdf, output/book-digital.pdf"
```

### Build Validation

After building, verify:

| Check | How |
|-------|-----|
| Page count reasonable | Compare to previous build |
| TOC links work | Click in PDF reader |
| Emoji render correctly | Visual spot-check family/flag emoji |
| No orphan headings | Scan for headings at page bottom |
| Front matter numbering | Roman numerals before Chapter 1 |
| Chapter openings (print) | Always on right-hand page |

## Project Structure

```
book/
├── chapters/
│   ├── 00-frontmatter.md
│   ├── 01-introduction.md
│   ├── 02-foundations.md
│   └── ...
├── filters/
│   ├── emoji.lua
│   └── needspace.lua
├── scripts/
│   ├── build-emoji-map.py
│   └── lint-headings.py
├── assets/
│   ├── emoji/              # Twemoji PNGs
│   └── images/             # Book images
├── output/                 # Generated PDFs (gitignored)
├── emoji-map.json          # Explicit emoji map
├── pandoc-print.yaml       # Print edition config
├── pandoc-digital.yaml     # Digital edition config
└── build-book.sh           # Build script
```
