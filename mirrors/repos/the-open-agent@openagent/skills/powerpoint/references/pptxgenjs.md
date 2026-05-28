# PptxGenJS Reference

Use this reference when writing the `.mjs` build script for the `pptx_write` tool.

## Script File Creation

Use `local_file_write` to write the `.mjs` script in one complete operation whenever that tool is available. Avoid repeated `shell` commands like `echo ... >> build.mjs`; they are brittle for JavaScript, especially on Windows. If you need to inspect the script, prefer `local_file_read`; if shell is the only option, use `type C:\path\build.mjs` on Windows or `cat /path/build.mjs` on Linux/macOS. Empty shell output from `echo ... >> file` is normal and should not trigger another rewrite by itself.

## Basic Structure

```javascript
export default async function build(pptx, ctx) {
  pptx.layout = "LAYOUT_WIDE";
  pptx.title = ctx.data?.title || "Presentation";

  const slide = pptx.addSlide();
  slide.background = { color: "FFFFFF" };
  slide.addText("Hello", { x: 0.6, y: 0.5, w: 8, h: 0.6, fontSize: 36 });
}
```

Useful layouts:

- `LAYOUT_WIDE`: 13.333 x 7.5 in.
- `LAYOUT_16X9`: 10 x 5.625 in.
- `LAYOUT_4X3`: 10 x 7.5 in.

Use inches for all `x`, `y`, `w`, and `h` values.

## Text

```javascript
slide.addText("Main title", {
  x: 0.6, y: 0.4, w: 8.5, h: 0.6,
  fontFace: "Aptos Display",
  fontSize: 38,
  bold: true,
  color: "111827",
  margin: 0,
});

slide.addText([
  { text: "First point", options: { bullet: true, breakLine: true } },
  { text: "Second point", options: { bullet: true } },
], {
  x: 0.8, y: 1.4, w: 5.4, h: 1.2,
  fontSize: 17,
  color: "374151",
  breakLine: false,
  paraSpaceAfterPt: 8,
});
```

Rules:

- Use `margin: 0` when aligning text with shapes or icons.
- Use PptxGenJS bullets; do not type bullet glyphs into strings.
- Use `breakLine: true` in rich text arrays when items must appear on separate lines.
- Avoid tiny body text; most slide body copy should stay at or above 14 pt.

## Shapes

```javascript
slide.addShape(pptx.ShapeType.rect, {
  x: 0, y: 0, w: 13.333, h: 7.5,
  fill: { color: "F8FAFC" },
  line: { color: "F8FAFC" },
});

slide.addShape(pptx.ShapeType.roundRect, {
  x: 0.7, y: 1.2, w: 3.5, h: 1.2,
  rectRadius: 0.08,
  fill: { color: "FFFFFF" },
  line: { color: "E5E7EB", width: 1 },
  shadow: { type: "outer", color: "000000", opacity: 0.12, blur: 2, angle: 45, distance: 1 },
});

slide.addShape(pptx.ShapeType.line, {
  x: 0.7, y: 6.8, w: 11.8, h: 0,
  line: { color: "CBD5E1", width: 1 },
});
```

Color rules:

- Hex colors must not include `#`.
- Do not use 8-character hex for transparency. Use `transparency` or `opacity`.
- Use a fresh options object for each shape; PptxGenJS mutates some option values internally.

## Images and Icons

```javascript
slide.addImage({
  data: ctx.imageData("photo.png"),
  x: 7.1, y: 1.0, w: 5.4, h: 3.4,
  sizing: { type: "cover", x: 7.1, y: 1.0, w: 5.4, h: 3.4 },
});

slide.addImage({
  data: ctx.iconSvgData("chart-line", "2563EB"),
  x: 0.8, y: 1.2, w: 0.35, h: 0.35,
});
```

Use `ctx.resolveAsset()` when a PptxGenJS API needs a file path. Use `ctx.imageData()` when embedding local PNG/JPG/GIF/SVG assets. Use `ctx.iconSvgData()` for Font Awesome solid icons by names such as `check`, `chart-line`, `shield-halved`, or `circle-info`.

## Tables and Charts

```javascript
slide.addTable([
  ["Metric", "Current", "Target"],
  ["Activation", "42%", "55%"],
  ["Retention", "68%", "74%"],
], {
  x: 0.7, y: 1.5, w: 6.0, h: 1.2,
  border: { pt: 1, color: "E5E7EB" },
  fill: { color: "FFFFFF" },
  color: "111827",
  fontSize: 12,
});

slide.addChart(pptx.ChartType.bar, [{
  name: "Revenue",
  labels: ["Q1", "Q2", "Q3", "Q4"],
  values: [12, 16, 21, 28],
}], {
  x: 0.7, y: 1.2, w: 6.2, h: 3.8,
  barDir: "col",
  chartColors: ["2563EB"],
  showLegend: false,
  showValue: true,
  valGridLine: { color: "E2E8F0", size: 0.5 },
});
```

Prefer a small set of chart colors from the deck palette. Hide legends when there is only one series.

## Layout Ideas

- Cover: full color block or image area with large title and short subtitle.
- Agenda: strong sidebar plus numbered sections.
- Two-column: explanatory text on one side, image/chart/diagram on the other.
- Card grid: 2x2 or 3x2 cards with icon, header, and one-sentence body.
- Timeline/process: numbered steps connected by lines or arrows.
- Data slide: one large chart plus two or three stat callouts.
- Closing: strong statement, next action, or summary trio.

## QA Checklist

- Slide order and text match the requested content.
- Text does not collide with shapes, images, footers, or other text.
- Long labels fit in their boxes and do not clip.
- Contrast is readable on every background.
- Margins are at least 0.5 in unless intentionally full bleed.
- Layouts vary; the deck does not read as repeated title-plus-bullets.
- Generated file opens and `pptx_read` returns the expected text.
