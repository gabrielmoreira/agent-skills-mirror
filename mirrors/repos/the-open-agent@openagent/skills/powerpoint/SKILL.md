---
name: powerpoint
description: Create designed, editable PowerPoint .pptx presentations with PptxGenJS. Use when the user asks to create, generate, update, or inspect a deck, slide deck, presentation, or .pptx file.
---

# PowerPoint

Use this skill whenever a PowerPoint deck is involved. For new decks, write a trusted local PptxGenJS `.mjs` build script and run it with the `pptx_write` tool.

## Workflow

1. Decide the deck outline and choose a visual system: palette, typography, repeated motif, and slide rhythm.
2. Create a local `.mjs` script that exports `default async function build(pptx, ctx)` or named `build(pptx, ctx)`.
3. In the script, add slides directly with PptxGenJS. Do not generate HTML for this workflow.
4. Call `pptx_write` with `path`, `script_path`, optional `assets_dir`, and optional `data`.
5. Verify the result with `pptx_read`; for visual QA, convert the PPTX to images if the environment has LibreOffice and Poppler.

## Script File Creation

- Prefer `local_file_write` to create the `.mjs` script in one complete write. Use `overwrite: true` when revising a script.
- Do not build long JavaScript files with repeated `shell` commands such as `echo ... >> build.mjs`, especially on Windows. Shell escaping for `{}`, `()`, `>`, `&`, `|`, `%`, quotes, and newlines is fragile.
- After the `.mjs` script is written, call `pptx_write` directly. Do not keep appending, rewriting, or checking the script with shell unless there is a concrete error.
- To inspect a script, prefer `local_file_read`. If only shell is available, use `type C:\path\build.mjs` on Windows or `cat /path/build.mjs` on Linux/macOS.
- `echo ... >> file` commonly returns no stdout on success. A `(no output)` shell result is not evidence that the write failed; do not retry only because output is empty.

## Tool Contract

```json
{
  "tool": "pptx_write",
  "arguments": {
    "path": "deck.pptx",
    "script_path": "/absolute/path/to/build_deck.mjs",
    "assets_dir": "/absolute/path/to/assets",
    "data": {"title": "Quarterly Review"}
  }
}
```

The worker creates the PptxGenJS instance and writes the output file. The script only adds slides and content.

```javascript
export default async function build(pptx, ctx) {
  pptx.layout = "LAYOUT_WIDE";
  pptx.author = "OpenAgent";

  const slide = pptx.addSlide();
  slide.background = { color: "FFFFFF" };
  slide.addText("Title", {
    x: 0.6, y: 0.4, w: 8, h: 0.6,
    fontSize: 36, bold: true, color: "1F2937",
    margin: 0,
  });
  slide.addNotes("speaker notes");
}
```

`ctx` includes:

- `ctx.data`: JSON data passed from the tool call.
- `ctx.assetsDir`: resolved asset directory.
- `ctx.outPath`: final PPTX path.
- `ctx.resolveAsset("image.png")`: absolute path under `assets_dir`.
- `ctx.imageData("image.png")`: base64 image data URL.
- `ctx.iconSvgData("check", "16A34A")`: Font Awesome solid icon as SVG data.

## Design Rules

- Avoid plain white bullet decks. Every slide should have a visual element: shape, image, chart, icon, timeline, stat callout, or diagram.
- Vary layouts across the deck: title, divider, two-column, card grid, process flow, quote/callout, and conclusion.
- Pick topic-specific colors. Use one dominant color, one or two supporting tones, and one accent.
- Use strong hierarchy: titles around 36-44 pt, section labels around 20-24 pt, body text around 14-18 pt.
- Keep at least 0.5 inch margins and consistent gaps around 0.3-0.5 inch.
- Use editable text wherever practical; use images for photos, screenshots, logos, or complex visual backgrounds.
- Add speaker notes when useful; `pptx_read` can surface them later.

## PptxGenJS Reference

For API patterns, chart examples, bullets, image sizing, icons, and common file-corruption pitfalls, load `pptxgenjs.md`.

## Required QA

- Run `pptx_read` on the generated file and check slide order, missing text, typo risk, and notes.
- Inspect generated XML or render slides when visual precision matters.
- Watch for overlap, text overflow, low contrast, cramped spacing, repeated layouts, and leftover placeholder text.
- If a visual issue is found, edit the `.mjs` script and rewrite the PPTX.
