---
name: powerpoint
description: Create designed, editable PowerPoint .pptx presentations with PptxGenJS. Use when the user asks to create, generate, update, or inspect a deck, slide deck, presentation, or .pptx file.
---

# PowerPoint

Use this skill whenever a PowerPoint deck is involved. For new decks, pass a trusted PptxGenJS build script directly to the `pptx_write` tool. For filling or editing an existing template, call `pptx_template_analyze` first and then `pptx_template_fill` with the exact IDs returned by analysis.

## Workflow

1. Decide the deck outline and choose a visual system: palette, typography, repeated motif, and slide rhythm.
2. Write JavaScript module content that exports `default async function build(pptx, ctx)` or named `build(pptx, ctx)`.
3. In the script, add slides directly with PptxGenJS. Do not generate HTML for this workflow.
4. Call `pptx_write` with `path`, `script`, optional `assets_dir`, and optional `data`.
5. Verify the result with `pptx_read`; for visual QA, convert the PPTX to images if the environment has LibreOffice and Poppler.

## Template Workflow

- Use `pptx_template_analyze` when the user provides a `.pptx` template or wants to preserve existing layouts, charts, images, tables, or SmartArt.
- Build a `template_fill_pptx_plan.v1` plan from the returned slide IDs and object IDs, then call `pptx_template_fill`.
- For SmartArt, use `smartarts[*].smartart_id` and `smartarts[*].nodes[*].node_id` in `smartart_edits`. This edits existing node text only; it does not create, delete, or relayout SmartArt nodes.

## Script Creation

- Put the complete JavaScript module in the `script` argument.
- Do not use `local_file_write` or shell commands to create a temporary `.mjs` file for this workflow.
- If revising a deck, update the `script` content and call `pptx_write` again.

## Tool Contract

```json
{
  "tool": "pptx_write",
  "arguments": {
    "path": "deck.pptx",
    "script": "export default async function build(pptx, ctx) {\\n  pptx.layout = \"LAYOUT_WIDE\";\\n}",
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
