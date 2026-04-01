---
name: md2pdf-export
description: >
  Convert Markdown files to PDF, PNG, or JPEG using headless Chrome (Puppeteer),
  following the same methodology as VS Code's Markdown Preview Enhanced extension.
  Use this skill whenever the user asks to: export/convert/render markdown to PDF or image,
  generate a printable document from .md files, create publication-ready PDFs from markdown,
  set up a markdown-to-PDF pipeline, or install/configure the Node.js + Puppeteer + Chrome
  environment needed for headless rendering. Also trigger when the user mentions "md2pdf",
  "markdown export", "puppeteer PDF", "headless chrome PDF", "crossnote", "mume",
  or wants WYSIWYG-quality PDF output from markdown source files.
  This skill covers both environment setup AND the actual conversion process.
---

# Markdown → PDF/PNG/JPEG Export (Puppeteer Method)

## Architecture Overview

The conversion pipeline mirrors Markdown Preview Enhanced's `chromeExport()`:

```
Markdown (.md)
    │
    ▼  [markdown-it + plugins]
Standalone HTML (with embedded CSS, math, diagrams)
    │
    ▼  [Puppeteer launches headless Chrome]
Chrome loads the HTML via file:// protocol
    │
    ├──▶ page.pdf()        → PDF output
    ├──▶ page.screenshot() → PNG output
    └──▶ page.screenshot() → JPEG output
```

The key insight: Chrome IS the rendering engine. What Chrome renders is what you get — true WYSIWYG.

---

## Step 0: Environment Check & Setup

Before any conversion, verify the environment is ready. Run the setup script:

```bash
bash skills/md2pdf-export/scripts/setup-env.sh
```

This script is idempotent — safe to run multiple times. It handles:
- Detecting OS (macOS / Ubuntu / Debian / Alpine / CentOS)
- Installing Node.js (via nvm, prefers LTS)
- Installing npm packages globally: `puppeteer` (which bundles Chromium)
- Verifying Chrome/Chromium is launchable in headless mode
- Printing a diagnostic summary

If the user's system already has Node.js ≥ 18 and puppeteer installed, the script skips those steps.

### Manual Setup (if the script fails)

For environments where the automated script doesn't work (e.g. restricted Docker containers):

```bash
# 1. Install Node.js >= 18
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc  # or ~/.zshrc
nvm install --lts

# 2. Install puppeteer (bundles Chromium automatically)
npm install -g puppeteer

# 3. For Linux headless environments, install system dependencies
# Ubuntu/Debian:
sudo apt-get update && sudo apt-get install -y \
  ca-certificates fonts-liberation libasound2 libatk-bridge2.0-0 \
  libatk1.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 \
  libnspr4 libnss3 libx11-xcb1 libxcomposite1 libxdamage1 \
  libxfixes3 libxrandr2 xdg-utils wget

# 4. Verify
node -e "const p = require('puppeteer'); p.launch({headless:'new'}).then(b => { console.log('OK'); b.close(); })"
```

### Using an Existing Chrome Installation

If the system already has Chrome/Chromium installed, set the environment variable to skip Chromium download:

```bash
export PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
export PUPPETEER_EXECUTABLE_PATH=/usr/bin/google-chrome  # or /usr/bin/chromium-browser
```

---

## Step 1: Convert Markdown to HTML

Use `markdown-it` with plugins for a feature-rich render. The conversion script at `skills/md2pdf-export/scripts/md2pdf.js` handles this internally, but the logic is:

1. Read the `.md` file
2. Parse YAML front-matter (for puppeteer config overrides)
3. Render Markdown → HTML via `markdown-it` with these plugins:
   - `markdown-it-texmath` + KaTeX for math ($...$, $$...$$)
   - `markdown-it-highlightjs` for syntax highlighting
   - `markdown-it-anchor` + `markdown-it-toc-done-right` for TOC
   - `markdown-it-footnote` for footnotes
4. Wrap in a full HTML document with:
   - A CSS theme (GitHub-light by default, configurable)
   - Embedded styles for print (`@media print` rules)
   - All resources inlined (no external dependencies)

## Step 2: Launch Headless Chrome & Export

The script then:

1. Launches Puppeteer with `headless: 'new'` (new headless mode)
2. Creates a new page, sets viewport (for PNG/JPEG) or paper size (for PDF)
3. Loads the HTML via `page.setContent()` or `page.goto('file://...')`
4. Waits for rendering to complete (`waitUntil: 'networkidle0'`)
5. Calls the appropriate Puppeteer API:
   - **PDF**: `page.pdf({ path, format, printBackground, margin, ... })`
   - **PNG**: `page.screenshot({ path, fullPage: true, type: 'png' })`
   - **JPEG**: `page.screenshot({ path, fullPage: true, type: 'jpeg', quality })`
6. Closes the browser

---

## Running the Conversion

### Basic Usage

```bash
# PDF (default)
node skills/md2pdf-export/scripts/md2pdf.js input.md

# PNG
node skills/md2pdf-export/scripts/md2pdf.js input.md --type png

# JPEG with quality
node skills/md2pdf-export/scripts/md2pdf.js input.md --type jpeg --quality 90

# Custom output path
node skills/md2pdf-export/scripts/md2pdf.js input.md -o output.pdf

# A3 landscape
node skills/md2pdf-export/scripts/md2pdf.js input.md --format A3 --landscape
```

### Front-Matter Configuration

Users can embed Puppeteer config directly in the Markdown file's YAML front-matter:

```yaml
---
puppeteer:
  format: A4
  landscape: false
  margin:
    top: "20mm"
    right: "20mm"
    bottom: "20mm"
    left: "20mm"
  printBackground: true
  displayHeaderFooter: true
  headerTemplate: '<span style="font-size:8px;width:100%;text-align:center;"><span class="title"></span></span>'
  footerTemplate: '<span style="font-size:8px;width:100%;text-align:center;"><span class="pageNumber"></span> / <span class="totalPages"></span></span>'
screenshot:
  fullPage: true
  width: 1200
  deviceScaleFactor: 2
export_on_save:
  puppeteer: true
---
```

### CLI Options Reference

| Option | Default | Description |
|--------|---------|-------------|
| `--type` | `pdf` | Output type: `pdf`, `png`, `jpeg` |
| `-o, --output` | `<input>.pdf` | Output file path |
| `--format` | `A4` | Paper format (A3, A4, A5, Letter, Legal, Tabloid) |
| `--landscape` | `false` | Landscape orientation |
| `--no-background` | | Disable printing background graphics |
| `--margin` | `10mm` | Uniform margin (or use --margin-top etc.) |
| `--quality` | `80` | JPEG quality (1-100) |
| `--scale` | `1` | Device scale factor for screenshots |
| `--width` | `1200` | Viewport width for screenshots |
| `--theme` | `github` | CSS theme: github, github-dark, minimal |
| `--chrome-path` | auto | Path to Chrome/Chromium executable |
| `--wait` | `0` | Extra wait time in ms after page load |
| `--toc` | `false` | Generate table of contents |

---

## Programmatic Usage (Node.js)

For integration into agent pipelines:

```javascript
const { convertMarkdown } = require('skills/md2pdf-export/scripts/md2pdf.js');

const result = await convertMarkdown({
  inputPath: './paper.md',
  outputPath: './paper.pdf',
  type: 'pdf',               // 'pdf' | 'png' | 'jpeg'
  puppeteerConfig: {
    format: 'A4',
    printBackground: true,
    margin: { top: '20mm', bottom: '20mm', left: '15mm', right: '15mm' },
  },
  theme: 'github',
  chromePath: null,           // auto-detect
  waitTimeout: 1000,
  toc: true,
});

console.log(`Exported to: ${result.outputPath}`);
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Chromium revision is not downloaded" | Puppeteer can't find Chrome | Run `npx puppeteer browsers install chrome` or set `PUPPETEER_EXECUTABLE_PATH` |
| Blank PDF | Page not fully rendered before export | Increase `--wait` timeout, or check for async content |
| Missing fonts (CJK, etc.) | System fonts not installed | Install `fonts-noto-cjk` (Ubuntu) or `noto-fonts-cjk` (Arch) |
| "No usable sandbox" on Linux | Chrome sandboxing in Docker | Add `--no-sandbox` arg (already handled by the script in Docker detection) |
| Math not rendering | KaTeX CSS not loaded | Ensure `markdown-it-texmath` + KaTeX are in dependencies |
| Mermaid diagrams missing | Client-side JS not executed | Use `--wait 2000` to give Mermaid time to render |

---

## Advanced: Batch Conversion

For converting an entire directory of Markdown files:

```bash
# Convert all .md files in a directory to PDF
for f in docs/*.md; do
  node skills/md2pdf-export/scripts/md2pdf.js "$f" -o "output/$(basename "${f%.md}.pdf")"
done
```

---

## Reference Files

- `references/puppeteer-config.md` — Full Puppeteer `page.pdf()` and `page.screenshot()` API options
- `references/themes.md` — Available CSS themes and how to create custom ones
