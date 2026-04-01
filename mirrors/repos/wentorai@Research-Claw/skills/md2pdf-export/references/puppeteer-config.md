# Puppeteer Configuration Reference

## page.pdf() Options

These options map directly to Puppeteer's `page.pdf()` API and can be set via:
- CLI flags (e.g. `--format A4`)
- YAML front-matter in the .md file (under `puppeteer:`)
- Programmatic `puppeteerConfig` object

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `path` | string | auto | Output file path |
| `format` | string | `"A4"` | Paper format. Values: `Letter`, `Legal`, `Tabloid`, `Ledger`, `A0`-`A6` |
| `width` | string/number | — | Paper width (overrides format). E.g. `"8.5in"`, `"210mm"` |
| `height` | string/number | — | Paper height (overrides format) |
| `landscape` | boolean | `false` | Paper orientation |
| `scale` | number | `1` | Scale of the webpage rendering. Range: 0.1 to 2 |
| `printBackground` | boolean | `true` | Print background graphics (colors, images) |
| `displayHeaderFooter` | boolean | `false` | Display header and footer |
| `headerTemplate` | string | — | HTML template for header. Can use classes: `date`, `title`, `url`, `pageNumber`, `totalPages` |
| `footerTemplate` | string | — | HTML template for footer (same classes as header) |
| `margin.top` | string | `"10mm"` | Top margin. Accepts CSS units: `px`, `in`, `cm`, `mm` |
| `margin.right` | string | `"10mm"` | Right margin |
| `margin.bottom` | string | `"10mm"` | Bottom margin |
| `margin.left` | string | `"10mm"` | Left margin |
| `preferCSSPageSize` | boolean | `false` | Give CSS `@page` size priority over `format` |
| `pageRanges` | string | `""` | Paper ranges to print, e.g. `"1-5, 8, 11-13"` |
| `omitBackground` | boolean | `false` | Hides default white background for transparent PDFs |
| `timeout` | number | `30000` | Maximum time in ms to wait for PDF generation |

### Header/Footer Template Variables

Inside `headerTemplate` and `footerTemplate`, these CSS classes are auto-populated:

- `.date` — formatted print date
- `.title` — document title
- `.url` — document URL
- `.pageNumber` — current page number
- `.totalPages` — total number of pages

Example footer:
```html
<div style="font-size:8px; width:100%; text-align:center; color:#888;">
  <span class="title"></span> — Page <span class="pageNumber"></span> of <span class="totalPages"></span>
</div>
```

Note: Header/footer templates must use inline styles. Font size must be explicitly set.

---

## page.screenshot() Options

Used when exporting to PNG or JPEG.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `path` | string | auto | Output file path |
| `type` | string | `"png"` | `"png"` or `"jpeg"` |
| `quality` | number | — | JPEG quality (1-100). Only for JPEG type |
| `fullPage` | boolean | `true` | Capture full scrollable page vs. viewport only |
| `clip` | object | — | Clip region: `{ x, y, width, height }` |
| `omitBackground` | boolean | `false` | Transparent background (PNG only) |
| `encoding` | string | `"binary"` | `"binary"` or `"base64"` |

### Viewport Settings for Screenshots

Set viewport before screenshot to control output dimensions:

```javascript
await page.setViewport({
  width: 1200,           // Viewport width in px
  height: 800,           // Viewport height (only matters if fullPage=false)
  deviceScaleFactor: 2,  // 2x for Retina-quality output
});
```

---

## Front-Matter Configuration

All Puppeteer options can be set in the Markdown file's YAML front-matter:

```yaml
---
title: "My Document"
puppeteer:
  format: A4
  landscape: false
  printBackground: true
  displayHeaderFooter: true
  margin:
    top: "25mm"
    bottom: "25mm"
    left: "15mm"
    right: "15mm"
  headerTemplate: '<span style="font-size:8px;"></span>'
  footerTemplate: >
    <div style="font-size:8px;width:100%;text-align:center;">
      <span class="pageNumber"></span> / <span class="totalPages"></span>
    </div>
  timeout: 3000
  args:
    - "--no-sandbox"
screenshot:
  fullPage: true
  width: 1440
  deviceScaleFactor: 2
  quality: 90
export_on_save:
  puppeteer: true
  puppeteer: ["pdf", "png"]
---
```

Front-matter values take precedence over CLI flags, which take precedence over defaults.

---

## Chrome Launch Options

| Option | Environment Variable | Description |
|--------|---------------------|-------------|
| Executable path | `PUPPETEER_EXECUTABLE_PATH` | Path to Chrome/Chromium binary |
| Skip download | `PUPPETEER_SKIP_CHROMIUM_DOWNLOAD` | Don't download bundled Chromium |
| Cache dir | `PUPPETEER_CACHE_DIR` | Where to store downloaded browsers |
| `--no-sandbox` | — | Required in Docker/rootless environments |
| `--disable-setuid-sandbox` | — | Required alongside `--no-sandbox` |
| `--disable-dev-shm-usage` | — | Use `/tmp` instead of `/dev/shm` (Docker) |
| `--disable-gpu` | — | Disable GPU hardware acceleration |
| `--font-render-hinting=none` | — | Better font rendering on Linux |
