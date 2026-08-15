---
name: photopea-embedded-editor
description: "Embeds Photopea in a host web app via photopea.js (createEmbed, runScript, saveToOE) for PSD-like layers, text, filters, file I/O, and Photoshop-compatible scripts. Use when integrating an in-page image editor or automating edits from the host. Not for desktop Photoshop plugins, raw postMessage wiring, or server-side image libraries (Sharp/Pillow); never call createEmbed on a zero-size container."
version: 1.0.1
risk: safe
source: community
source_repo: yikuansun/PhotopeaAPI
source_type: community
license: MIT
license_source: "https://github.com/yikuansun/PhotopeaAPI/blob/master/LICENSE"
date_added: 2026-05-20
---

# Photopea Embedded Editor Skill

## When to Use

Use this skill for **every task** that involves:

- Embedding Photopea as an image editor inside a webpage or web app
- Controlling an embedded Photopea instance from your JavaScript code
- Automating image editing workflows from a host page (open files, run scripts, export results)
- Building an image editing feature into your product using Photopea as the engine
- Writing scripts to manipulate documents, layers, text, selections, filters, colors, and paths

**Do NOT** use raw `postMessage` wiring — always use `photopea.js` as the wrapper.

**Trigger keywords:** photopea, embedded editor, image editor, psd editor, photopea.js, runScript, saveToOE, echoToOE, openFromURL, loadAsset, exportImage, createEmbed, Photopea plugin, Photoshop scripting API, batch watermark, layer automation.

---

## Prerequisites

- A modern browser with `postMessage` and `iframe` support
- `photopea@1.1.1` (CDN or npm)
- For self-hosting: download `photopea.min.js` from the npm package `dist/` folder
- For remote URL loading: target servers **must** respond with `Access-Control-Allow-Origin: *` (CORS)
- For React integration: React 18+ with `useRef` and `useEffect`
- For npm/bundler workflows: Node.js installed; install via `npm install photopea`

**Windows host (PowerShell) note:** If you are scaffolding a project on Windows to host the page that embeds Photopea, use PowerShell commands:

```powershell
mkdir photopea-app; cd photopea-app
npm init -y
npm install photopea
```

---

## Procedure

### Step 1 — Install photopea.js

**CDN (no build step):**

```html
<script src="https://cdn.jsdelivr.net/npm/photopea@1.1.1/dist/photopea.min.js"></script>
```

**Self-hosted:**

```html
<script src="./photopea.min.js"></script>
```

**npm (Webpack / Vite / Rollup):**

```bash
npm install photopea
```

```js
import Photopea from "photopea";
```

### Step 2 — Embed Photopea

The container `<div>` **must** have a fixed width and height before calling `createEmbed`. If the container has zero size, `createEmbed` will never resolve.

```html
<div id="editor" style="width:1000px; height:650px;"></div>
<script src="https://cdn.jsdelivr.net/npm/photopea@1.1.1/dist/photopea.min.js"></script>
<script>
  Photopea.createEmbed(document.getElementById("editor")).then(async (pea) => {
    // pea is ready
  });
</script>
```

**React:**

```jsx
import { useEffect, useRef } from "react";
import Photopea from "photopea";

export default function Editor() {
  const containerRef = useRef(null);
  const peaRef       = useRef(null);

  useEffect(() => {
    if (!containerRef.current || peaRef.current) return;
    Photopea.createEmbed(containerRef.current).then((pea) => {
      peaRef.current = pea;
    });
  }, []);

  return <div ref={containerRef} style={{ width: "100%", height: "650px" }} />;
}
```

> **React Strict Mode guard:** In development, `useEffect` fires twice. Always guard with `if (peaRef.current) return;` to prevent double-embedding.

### Step 3 — Open Files

```js
// Remote URL → new document
await pea.openFromURL("https://example.com/design.psd", false);

// Remote URL → smart object layer inside current document
await pea.openFromURL("https://example.com/overlay.png", true);

// Local file (user input → ArrayBuffer → loadAsset)
document.getElementById("fileInput").addEventListener("change", async (e) => {
  const buf = await e.target.files[0].arrayBuffer();
  await pea.loadAsset(buf);
});

// Base64 data URI via runScript
await pea.runScript(`app.open("data:image/png;base64,iVBORw0...");`);
```

### Step 4 — Run Scripts

`runScript` sends a JS string, returns an array of `app.echoToOE(...)` values + `"done"` last.

```js
const result = await pea.runScript(`app.echoToOE("hello");`);
// result → ["hello", "done"]

// Return structured data
const out = await pea.runScript(`
  app.echoToOE(JSON.stringify({
    width:  app.activeDocument.width,
    height: app.activeDocument.height,
    layers: app.activeDocument.layers.length
  }));
`);
const info = JSON.parse(out[0]);
```

> **HARD RULE:** Always serialize dynamic values with `JSON.stringify` before embedding them in a `runScript` string. Never concatenate user-provided URLs, layer names, or text directly into Photopea script source.

> **HARD RULE:** Always set `app.preferences.rulerUnits = Units.PIXELS` at the start of any script that uses pixel measurements:

```js
var savedUnits = app.preferences.rulerUnits;
app.preferences.rulerUnits = Units.PIXELS;
// ... your code ...
app.preferences.rulerUnits = savedUnits;
```

### Step 5 — Export

```js
// PNG Blob (via exportImage)
const blob = await pea.exportImage("png");
document.getElementById("preview").src = URL.createObjectURL(blob);

// JPEG Blob
const blob = await pea.exportImage("jpg");

// WebP / PSD / quality-controlled JPEG via saveToOE
const result = await pea.runScript(`app.activeDocument.saveToOE("webp:0.85");`);
const webpBlob = new Blob([result[0]], { type: "image/webp" });

const result = await pea.runScript(`app.activeDocument.saveToOE("psd:true");`);
const psdBlob  = new Blob([result[0]], { type: "application/octet-stream" });

// Trigger download
async function download(pea, filename = "export.png") {
  const blob = await pea.exportImage("png");
  const a    = Object.assign(document.createElement("a"), {
    href:     URL.createObjectURL(blob),
    download: filename
  });
  a.click();
}
```

**Export format strings for `saveToOE`:**

| String | Format |
|--------|--------|
| `"png"` | PNG lossless |
| `"jpg"` | JPEG default |
| `"jpg:0.8"` | JPEG quality 0.0–1.0 |
| `"webp:0.7"` | WebP quality 0.0–1.0 |
| `"psd"` | Full PSD |
| `"psd:true"` | Minified PSD |
| `"svg:true"` | SVG |

### Step 6 — Load Assets (Fonts, Brushes, Gradients)

```js
// Font
const buf = await (await fetch("https://example.com/MyFont.otf")).arrayBuffer();
await pea.loadAsset(buf);
// Now usable in textItem.font

// Brush
await pea.loadAsset(await (await fetch("Nature.ABR")).arrayBuffer());

// Gradient
await pea.loadAsset(await (await fetch("Gradients.GRD")).arrayBuffer());
```

### Step 7 — Plugin Mode

When your page is inside Photopea's sidebar iframe:

```js
const pea = new Photopea(window.parent);

const out = await pea.runScript(`app.echoToOE(app.activeDocument.width);`);
console.log("Width:", out[0]);

// Load an asset from your plugin
const buf = await (await fetch("https://my-assets.com/sticker.png")).arrayBuffer();
await pea.loadAsset(buf);
```

Plugin config:

```json
{
  "environment": {
    "plugins": [{
      "name": "My Plugin",
      "url":  "https://my-plugin.example.com",
      "icon": "===https://my-plugin.example.com/icon.png"
    }]
  }
}
```

---

## Core API: The `Photopea` Class

| Method | Description |
|--------|-------------|
| `Photopea.createEmbed(container)` | Creates + injects the iframe, resolves when ready |
| `new Photopea(window.parent)` | Plugin mode: wrap the parent window |
| `pea.runScript(script)` | Run JS string inside Photopea; returns output array |
| `pea.loadAsset(arrayBuffer)` | Load binary file (image, font, brush, etc.) |
| `pea.openFromURL(url, asSmart)` | Open remote URL as new doc or smart object layer |
| `pea.exportImage(type)` | Export current doc; returns `Blob` (`"png"` or `"jpg"`) |

All methods return Promises — always `await` or `.then()`.

---

## Utility Patterns

### addImageAndWait — robust async layer insertion

Use this when `openFromURL(url, true)` creates a smart object layer that isn't immediately ready.

```js
async function addImageAndWait(pea, imgURI) {
  let count = "done";
  while (count === "done")
    count = (await pea.runScript(`app.echoToOE(app.activeDocument.layers.length)`))[0];
  count = parseInt(count);

  const imageUrlLiteral = JSON.stringify(imgURI);
  await pea.runScript(`app.open(${imageUrlLiteral}, null, true);`);

  return new Promise((resolve) => {
    const check = async () => {
      const n = parseInt((await pea.runScript(
        `app.echoToOE(app.activeDocument.layers.length)`
      ))[0]);
      n === count + 1 ? resolve() : setTimeout(check, 50);
    };
    check();
  });
}
```

### getDocumentAsImage — returns `<img>` element

```js
async function getDocumentAsImage(pea) {
  const result = await pea.runScript(`app.activeDocument.saveToOE('png')`);
  return new Promise((resolve) => {
    const fr = new FileReader();
    fr.addEventListener("load", (e) => {
      const img = new Image(); img.src = e.target.result; resolve(img);
    });
    fr.readAsDataURL(new Blob([result[0]], { type: "image/png" }));
  });
}
```

---

## Real-World Patterns

### Pattern A — Open + Export UI

```html
<input type="file" id="fileInput" accept="image/*,.psd">
<button id="exportBtn">Export PNG</button>
<div id="editor" style="width:100%;height:600px;"></div>
<script src="https://cdn.jsdelivr.net/npm/photopea@1.1.1/dist/photopea.min.js"></script>
<script>
let pea;
Photopea.createEmbed(document.getElementById("editor")).then(p => pea = p);

document.getElementById("fileInput").addEventListener("change", async e => {
  await pea.loadAsset(await e.target.files[0].arrayBuffer());
});
document.getElementById("exportBtn").addEventListener("click", async () => {
  const blob = await pea.exportImage("png");
  const a = Object.assign(document.createElement("a"), {
    href: URL.createObjectURL(blob), download: "export.png"
  });
  a.click();
});
</script>
```

### Pattern B — Template + Text Edit + Export

```js
async function generateCard(pea, name, tagline) {
  await pea.openFromURL("https://example.com/card.psd", false);
  const nameLiteral = JSON.stringify(name);
  const taglineLiteral = JSON.stringify(tagline);
  await pea.runScript(`
    app.activeDocument.layers.getByName("Name").textItem.contents    = ${nameLiteral};
    app.activeDocument.layers.getByName("Tagline").textItem.contents = ${taglineLiteral};
  `);
  return await pea.exportImage("png");
}
```

### Pattern C — Batch Watermark

```js
async function batchWatermark(pea, imageURLs, watermarkURL) {
  const results = [];
  for (const url of imageURLs) {
    await pea.openFromURL(url, false);
    await pea.openFromURL(watermarkURL, true);
    await pea.runScript(`
      var doc = app.activeDocument, wm = doc.activeLayer;
      wm.translate(doc.width - wm.bounds[2] - 20, doc.height - wm.bounds[3] - 20);
      wm.opacity = 70;
    `);
    results.push(await pea.exportImage("png"));
    await pea.runScript(`app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);`);
  }
  return results;
}
```

---

## Full Scripting API Reference

> All code in this section runs **inside `pea.runScript("...")`** strings.
> Photopea implements the Adobe Photoshop CC 2015 JavaScript scripting interface.
> Any Photoshop script targeting that version should work in Photopea.

### `app` — Application Object

#### Properties

| Property | Type | R/W | Description |
|----------|------|-----|-------------|
| `app.activeDocument` | Document | R/W | The currently active document |
| `app.documents` | Documents | R | Collection of all open documents |
| `app.documents.length` | number | R | Count of open documents |
| `app.documents[i]` | Document | R | Access by zero-based index |
| `app.foregroundColor` | SolidColor | R/W | Current foreground color |
| `app.backgroundColor` | SolidColor | R/W | Current background color |
| `app.preferences.rulerUnits` | Units | R/W | `Units.PIXELS`, `Units.CM`, `Units.INCHES`, `Units.MM`, `Units.PICAS`, `Units.POINTS`, `Units.PERCENT` |
| `app.preferences.typeUnits` | TypeUnits | R/W | `TypeUnits.PIXELS`, `TypeUnits.MM`, `TypeUnits.POINTS` |
| `app.displayDialogs` | DialogModes | R/W | `DialogModes.NO`, `DialogModes.ALL`, `DialogModes.ERROR` |

#### Methods

| Method | Description |
|--------|-------------|
| `app.open(url)` | Open URL as new document |
| `app.open(url, null, true)` | Open URL as smart object layer in active document |
| `app.echoToOE(string)` | **Photopea extension** — send string to host page (captured by `runScript`) |
| `app.showWindow("magiccut")` | **Photopea extension** — open Magic Cut panel |
| `app.showWindow("vbitmap")` | **Photopea extension** — open Vectorize Bitmap panel |
| `app.UI.zoomIn()` | Zoom in |
| `app.UI.zoomOut()` | Zoom out |
| `app.UI.fitTheArea()` | Fit canvas to viewport |
| `app.UI.pixelToPixel()` | 100% zoom |
| `app.UI.switchFullscreen()` | Toggle fullscreen |
| `app.UI.scroll(dx, dy)` | Scroll by delta |
| `app.UI.scrollTo(x, y)` | Scroll to absolute position |

### `Document` — Document Object

Access via `app.activeDocument` or `app.documents[i]`.

#### Properties

| Property | Type | R/W | Description |
|----------|------|-----|-------------|
| `width` | number | R | Document width in current ruler units |
| `height` | number | R | Document height in current ruler units |
| `resolution` | number | R | DPI (pixels per inch) |
| `name` | string | **R/W** | **Photopea extension** — display label (no history step) |
| `source` | string | **R/W** | **Photopea extension** — file origin URL or `"local,X,NAME"` |
| `mode` | DocumentMode | R | `DocumentMode.RGB`, `GRAYSCALE`, `CMYK`, `LAB`, `BITMAP`, `INDEXEDCOLOR`, `MULTICHANNEL` |
| `bitsPerChannel` | BitsPerChannelType | R | `BitsPerChannelType.EIGHT`, `SIXTEEN`, `THIRTYTWO` |
| `colorProfileName` | string | R | Name of embedded color profile |
| `activeLayer` | Layer/ArtLayer/LayerSet | R/W | Set to activate a layer |
| `currentLayer` | ArtLayer | R/W | Alias for `activeLayer` |
| `layers` | Layers | R | All top-level layers (both art + group) |
| `artLayers` | ArtLayers | R | All top-level art layers only |
| `layerSets` | LayerSets | R | All top-level group layers only |
| `selection` | Selection | R | The current selection |
| `channels` | Channels | R | All channels |
| `historyStates` | HistoryStates | R | Undo history |
| `activeHistoryState` | HistoryState | R/W | Current history position |
| `layerComps` | LayerComps | R | Layer comps collection |
| `guides` | Guides | R | Guides collection |
| `pathItems` | PathItems | R | Vector paths |
| `id` | number | R | Unique document ID |
| `saved` | boolean | R | Whether document has unsaved changes |
| `quickMaskMode` | boolean | R | Whether in Quick Mask mode |
| `backgroundLayer` | ArtLayer | R | The background layer |
| `pixelAspectRatio` | number | R | Custom pixel aspect ratio (0.1–10.0) |
| `histogram` | array | R | 256-element histogram array |

#### Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `resizeImage` | `(w, h, res, resampleMethod)` | Resize image pixels. ResampleMethod: `BICUBIC`, `BILINEAR`, `NEARESTNEIGHBOR`, `NONE`, `BICUBICSHARPER`, `BICUBICSMOOTHER` |
| `resizeCanvas` | `(w, h, anchor)` | Resize canvas without scaling. AnchorPosition: `TOPLEFT`, `TOPCENTER`, `TOPRIGHT`, `MIDDLELEFT`, `MIDDLECENTER`, `MIDDLERIGHT`, `BOTTOMLEFT`, `BOTTOMCENTER`, `BOTTOMRIGHT` |
| `rotateCanvas` | `(degrees)` | Rotate entire canvas. Positive = clockwise |
| `flipCanvas` | `(direction)` | `Direction.HORIZONTAL` or `Direction.VERTICAL` |
| `crop` | `([x1,y1,x2,y2], angle, w, h)` | Crop canvas. Angle and dimensions are optional |
| `trim` | `(trimType, top, left, bottom, right)` | Trim transparent/background-color borders. TrimType: `TRANSPARENT`, `TOPLEFT`, `BOTTOMRIGHT` |
| `revealAll` | `()` | Expand canvas to show clipped content |
| `flatten` | `()` | Merge all layers into one |
| `mergeVisibleLayers` | `()` | Merge all visible layers |
| `rasterizeAllLayers` | `()` | Rasterize all vector/text layers |
| `changeMode` | `(mode, options)` | Convert color mode (e.g., `ChangeMode.GRAYSCALE`) |
| `convertProfile` | `(profileName, renderingIntent, blackPointCompensation, dither)` | Convert color profile |
| `duplicate` | `(name, mergedLayers)` | Duplicate the document |
| `close` | `(saveOptions)` | Close document. SaveOptions: `DONOTSAVECHANGES`, `SAVECHANGES`, `PROMPTTOSAVECHANGES` |
| `save` | `()` | Save (requires server config in embed) |
| `saveToOE` | `(format)` | **Photopea extension** — send binary to host. Formats: `"png"`, `"jpg:0.8"`, `"webp:0.7"`, `"psd:true"`, `"svg:true"` |
| `clearHistory` | `()` | **Photopea extension** — clear undo history to free RAM |
| `exportDocument` | `(file, exportType, options)` | Export to filesystem (triggers ZIP). ExportType: `SAVEFORWEB` |
| `paste` | `(intoSelection)` | Paste clipboard into document |
| `suspendHistory` | `(historyName, callback)` | Wrap multiple ops in one history state |

#### Document examples

```js
var doc = app.activeDocument;

// Resize image to 1920×1080 at 72dpi bicubic
doc.resizeImage(1920, 1080, 72, ResampleMethod.BICUBIC);

// Expand canvas to 2000px wide, keeping content centered
doc.resizeCanvas(2000, doc.height, AnchorPosition.MIDDLECENTER);

// Crop to a region
doc.crop([100, 100, 900, 600]);

// Trim transparent edges
doc.trim(TrimType.TRANSPARENT, true, true, true, true);

// Flip horizontal
doc.flipCanvas(Direction.HORIZONTAL);

// Change to grayscale
doc.changeMode(ChangeMode.GRAYSCALE);

// Export PNG to filesystem (triggers ZIP download)
var opts = new ExportOptionsSaveForWeb();
opts.format  = SaveDocumentType.PNG;
opts.PNG8    = false;
opts.quality = 100;
doc.exportDocument(new File("/output.png"), ExportType.SAVEFORWEB, opts);

// Close without saving
doc.close(SaveOptions.DONOTSAVECHANGES);
```

### `Layers` / `ArtLayers` / `LayerSets` Collections

```js
var doc = app.activeDocument;

// Access
doc.layers          // all top-level (art + groups)
doc.artLayers       // top-level art layers only
doc.layerSets       // top-level group layers only

// By index (0 = topmost)
doc.layers[0]
doc.layers[doc.layers.length - 1]  // bottommost

// By name (throws if not found)
doc.layers.getByName("Background")
doc.artLayers.getByName("Logo")
doc.layerSets.getByName("Header Group")

// Add
var newLayer  = doc.artLayers.add();         // new blank art layer
var newGroup  = doc.layerSets.add();         // new group
var innerLayer = newGroup.artLayers.add();   // layer inside a group

// Remove
doc.artLayers.getByName("Temp").remove();

// Iterate all layers recursively
function walkLayers(parent) {
  for (var i = 0; i < parent.layers.length; i++) {
    var l = parent.layers[i];
    if (l.typename === "LayerSet") walkLayers(l);
    else /* ArtLayer */ processLayer(l);
  }
}
walkLayers(doc);
```

### `ArtLayer` — Individual Layer

#### Properties

| Property | Type | R/W | Description |
|----------|------|-----|-------------|
| `name` | string | R/W | Layer name |
| `visible` | boolean | R/W | Layer visibility |
| `opacity` | number | R/W | Layer opacity 0–100 |
| `fillOpacity` | number | R | Fill opacity 0–100 |
| `blendMode` | BlendMode | R/W | Blend mode |
| `kind` | LayerKind | R/W | Layer type (can set to `LayerKind.TEXT` on empty layer) |
| `textItem` | TextItem | R | Text object (only when `kind === LayerKind.TEXT`) |
| `bounds` | array | R | `[left, top, right, bottom]` in current ruler units |
| `parent` | Document/LayerSet | R | Containing object |
| `typename` | string | R | Always `"ArtLayer"` |
| `selected` | boolean | R | **Photopea extension** — is layer highlighted in panel |
| `isBackgroundLayer` | boolean | R | Is this the locked background layer |
| `grouped` | boolean | R | Is clipping mask applied |
| `pixelsLocked` | boolean | R | Pixels locked |
| `positionLocked` | boolean | R | Position locked |
| `transparentPixelsLocked` | boolean | R | Transparent pixels locked |
| `layerMaskDensity` | number | R | Layer mask density 0–100 |
| `layerMaskFeather` | number | R | Layer mask feather 0–250 |
| `vectorMaskDensity` | number | R | Vector mask density 0–100 |
| `vectorMaskFeather` | number | R | Vector mask feather 0–250 |

#### Transform Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `translate` | `(deltaX, deltaY)` | Move layer by offset |
| `rotate` | `(angle, anchor)` | Rotate by degrees. AnchorPosition optional (default center) |
| `resize` | `(widthPct, heightPct, anchor)` | Scale as percentage of current size |
| `rasterize` | `(target)` | Rasterize. RasterizeType: `ENTIRE`, `FILLCONTENT`, `LAYERCLIPPINGMASK`, `LINKEDLAYERS`, `SHAPE`, `TEXTCONTENTS`, `VECTORMASK` |

#### Layer Management Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `duplicate` | `()` | Duplicate to same document, returns new layer |
| `duplicate` | `(doc, placement)` | Duplicate to another document |
| `remove` | `()` | Delete the layer |
| `merge` | `()` | Merge down; returns the merged ArtLayer |
| `move` | `(target, location)` | Move layer. ElementPlacement: `PLACEBEFORE`, `PLACEAFTER`, `PLACEATBEGINNING`, `PLACEATEND`, `PLACEINSIDE` |
| `link` | `(targetLayer)` | Link with another layer |
| `unlink` | `()` | Remove all links |
| `adjustCurves` | `(curveShape)` | Apply curves adjustment |
| `adjustLevels` | `(inputRangeStart, inputRangeEnd, inputRangeGamma, outputRangeStart, outputRangeEnd)` | Apply levels adjustment |
| `adjustBrightnessContrast` | `(brightness, contrast)` | Apply brightness/contrast |
| `applyDespeckle` | `()` | Apply despeckle filter |
| `applyGaussianBlur` | `(radius)` | Apply Gaussian blur |
| `applySharpen` | `()` | Apply sharpen filter |
| `applyUnSharpMask` | `(amount, radius, threshold)` | Apply unsharp mask |
| `applyAddNoise` | `(amount, distribution, monochromatic)` | Apply noise. NoiseDistribution: `GAUSSIAN`, `UNIFORM` |

### `TextItem` — Text Layer Content

| Property | Type | R/W | Description |
|----------|------|-----|-------------|
| `contents` | string | R/W | The text content |
| `font` | string | R/W | Font family name (must be loaded or built-in) |
| `size` | number | R/W | Font size in type units |
| `color` | SolidColor | R/W | Text color |
| `justification` | Justification | R/W | `LEFT`, `CENTER`, `RIGHT` |
| `position` | array | R/W | `[x, y]` anchor position |
| `orientation` | Orientation | R/W | `HORIZONTAL`, `VERTICAL` |
| `capitalization` | TextCase | R/W | `NORMAL`, `ALLCAPS`, `SMALLCAPS` |
| `tracking` | number | R/W | Letter tracking |
| `leading` | number | R/W | Line spacing |
| `autoLeading` | boolean | R/W | Auto line spacing |
| `horizontalScale` | number | R/W | Horizontal scale 0–1000 |
| `verticalScale` | number | R/W | Vertical scale 0–1000 |
| `baselineShift` | number | R/W | Baseline offset |
| `underline` | UnderlineType | R/W | `NONE`, `SINGLE`, `DOUBLE` |
| `strikeThru` | StrikeThruType | R/W | `NONE`, `SINGLE`, `DOUBLE` |

### `Selection` — Active Selection

| Method | Signature | Description |
|--------|-----------|-------------|
| `select` | `(region, type, feather, antiAlias)` | Select a rectangular/polygonal region |
| `selectAll` | `()` | Select entire canvas |
| `selectNone` | `()` | Deselect |
| `invert` | `()` | Invert selection |
| `fill` | `(fillType, mode, opacity, preserveTransparency)` | Fill selection. FillType: `FOREGROUND`, `BACKGROUND`, `COLOR`, `WHITE`, `BLACK`, `GRAY` |
| `stroke` | `(strokeColor, width, location, opacity, mode)` | Stroke selection border |
| `clear` | `()` | Delete selection content |
| `copy` | `()` | Copy to clipboard |
| `paste` | `()` | Paste from clipboard |
| `contract` | `(amount)` | Contract selection by pixels |
| `expand` | `(amount)` | Expand selection by pixels |
| `feather` | `(amount)` | Feather selection edges |
| `grow` | `(tolerance, antiAlias)` | Grow selection by color tolerance |
| `similar` | `(tolerance, antiAlias)` | Select similar colors |
| `transformSelection` | `(rotation)` | Rotate selection |
| `resizeBoundary` | `(widthPct, heightPct, anchor)` | Resize selection boundary |
| `store` | `(pathItem)` | Save selection as path |
| `load` | `(pathItem)` | Load selection from path |

### `SolidColor` — Color Object

```js
var c = new SolidColor();
c.rgb.red   = 255;
c.rgb.green = 128;
c.rgb.blue  = 0;

// Other color models
c.hsb.hue        = 30;
c.hsb.saturation = 100;
c.hsb.brightness = 50;

c.cmyk.cyan    = 0;
c.cmyk.magenta = 50;
c.cmyk.yellow  = 100;
c.cmyk.black   = 0;

c.lab.l = 75;
c.lab.a = 40;
c.lab.b = 60;

// Grayscale
c.gray.gray = 128;
```

### `ActionDescriptor` / `ActionReference` — Action Manager (AM)

For operations not covered by the DOM API, use Action Manager:

```js
// Select a layer by name using AM
function selectLayerByName(name) {
  var desc = new ActionDescriptor();
  var ref  = new ActionReference();
  ref.putName(charIDToTypeID("Lyr "), name);
  desc.putReference(charIDToTypeID("null"), ref);
  desc.putBoolean(charIDToTypeID("MkVs"), false);
  executeAction(charIDToTypeID("slct"), desc, DialogModes.NO);
}

// Open Smart Object for editing
var l = doc.layers.getByName("SmartObj");
doc.activeLayer = l;
executeAction(stringIDToTypeID("placedLayerEditContents"));
// Smart Object is now the active document
doc.activeLayer.rotate(90);
doc.save();
doc.close();

// Apply Hue/Saturation as destructive adjustment
var desc = new ActionDescriptor();
var list = new ActionList();
var channel = new ActionDescriptor();
channel.putEnumerated(stringIDToTypeID("presetKind"), stringIDToTypeID("presetKindType"), stringIDToTypeID("presetKindDefault"));
channel.putInteger(stringIDToTypeID("hue"),        20);
channel.putInteger(stringIDToTypeID("saturation"), 30);
channel.putInteger(stringIDToTypeID("lightness"),  0);
list.putObject(stringIDToTypeID("hueSaturationAdjustmentV2Layer"), channel);
desc.putList(stringIDToTypeID("adjustment"), list);
executeAction(stringIDToTypeID("hueSaturation"), desc, DialogModes.NO);
```

> **HARD RULE:** When editing Smart Objects via AM, always call `doc.save(); doc.close();` when done. Failing to do so leaves the SO open and hangs subsequent operations.

---

## Complete Practical Script Examples

### 1. Rename all text layers based on their contents

```js
app.preferences.rulerUnits = Units.PIXELS;
var doc = app.activeDocument;

function processLayers(parent) {
  for (var i = 0; i < parent.layers.length; i++) {
    var l = parent.layers[i];
    if (l.typename === "LayerSet") processLayers(l);
    else if (l.kind === LayerKind.TEXT) {
      l.name = l.textItem.contents.substring(0, 30);
    }
  }
}
processLayers(doc);
app.echoToOE("done");
```

### 2. Export each layer as a separate PNG

```js
app.preferences.rulerUnits = Units.PIXELS;
var doc = app.activeDocument;

for (var i = 0; i < doc.layers.length; i++) {
  for (var j = 0; j < doc.layers.length; j++) doc.layers[j].visible = false;
  doc.layers[i].visible = true;
  var opts = new ExportOptionsSaveForWeb();
  opts.format  = SaveDocumentType.PNG;
  opts.PNG8    = false;
  opts.quality = 100;
  doc.exportDocument(
    new File("/" + doc.layers[i].name + ".png"),
    ExportType.SAVEFORWEB, opts
  );
}

for (var i = 0; i < doc.layers.length; i++) doc.layers[i].visible = true;
```

### 3. Find and replace text across all text layers

```js
var searchText   = "2024";
var replaceText  = "2025";

function findReplaceText(parent) {
  for (var i = 0; i < parent.layers.length; i++) {
    var l = parent.layers[i];
    if (l.typename === "LayerSet") findReplaceText(l);
    else if (l.kind === LayerKind.TEXT) {
      var t = l.textItem;
      if (t.contents.indexOf(searchText) !== -1) {
        t.contents = t.contents.split(searchText).join(replaceText);
      }
    }
  }
}
findReplaceText(app.activeDocument);
app.echoToOE("Find & Replace complete");
```

### 4. Grid of duplicate layers

```js
app.preferences.rulerUnits = Units.PIXELS;
var doc   = app.activeDocument;
var layer = doc.activeLayer;
var cols  = 4, rows = 3;
var padX  = 20, padY = 20;
var w = layer.bounds[2] - layer.bounds[0];
var h = layer.bounds[3] - layer.bounds[1];

for (var r = 0; r < rows; r++) {
  for (var c = 0; c < cols; c++) {
    if (r === 0 && c === 0) continue;
    var copy = layer.duplicate();
    var targetX = layer.bounds[0] + c * (w + padX);
    var targetY = layer.bounds[1] + r * (h + padY);
    copy.translate(targetX - copy.bounds[0], targetY - copy.bounds[1]);
    copy.opacity = 100 - (r * cols + c) * 5;
  }
}
```

### 5. Apply watermark from URL

```js
app.preferences.rulerUnits = Units.PIXELS;
var doc = app.activeDocument;

app.open("https://example.com/watermark.png", null, true);
var wm = doc.activeLayer;

var wmW = wm.bounds[2] - wm.bounds[0];
var targetW = doc.width * 0.2;
var scalePct = (targetW / wmW) * 100;
wm.resize(scalePct, scalePct, AnchorPosition.TOPLEFT);

var wmNewW = wm.bounds[2] - wm.bounds[0];
var wmNewH = wm.bounds[3] - wm.bounds[1];
wm.translate(
  doc.width  - wmNewW - 20 - wm.bounds[0],
  doc.height - wmNewH - 20 - wm.bounds[1]
);
wm.opacity = 60;
app.echoToOE("watermark applied");
```

### 6. Get all layer info as JSON

```js
function getLayerInfo(parent, depth) {
  depth = depth || 0;
  var result = [];
  for (var i = 0; i < parent.layers.length; i++) {
    var l = parent.layers[i];
    var info = {
      name:    l.name,
      type:    l.typename,
      visible: l.visible,
      opacity: l.opacity,
      depth:   depth
    };
    if (l.typename === "ArtLayer") {
      info.kind   = l.kind.toString();
      info.bounds = [l.bounds[0], l.bounds[1], l.bounds[2], l.bounds[3]];
      if (l.kind === LayerKind.TEXT) {
        info.text = l.textItem.contents;
        info.font = l.textItem.font;
        info.size = l.textItem.size;
      }
    } else if (l.typename === "LayerSet") {
      info.children = getLayerInfo(l, depth + 1);
    }
    result.push(info);
  }
  return result;
}
app.echoToOE(JSON.stringify(getLayerInfo(app.activeDocument)));
```

---

## Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| `createEmbed` never resolves | Container has no size | Add `width` + `height` CSS to the container `<div>` |
| `runScript` returns `["done"]` with no data | No `echoToOE` in script | Add `app.echoToOE(value)` for anything you want back |
| `result[0]` is `"done"`, not the expected value | `echoToOE` not reached | Check script logic for early exit or errors |
| Images won't load (network error) | CORS | Server must respond with `Access-Control-Allow-Origin: *` |
| `openFromURL(url, true)` layer not ready | Async loading lag | Use `addImageAndWait` utility |
| `exportImage` only PNG/JPG | `exportImage` limitation | Use `runScript("saveToOE('webp:0.85')")` for other formats |
| Pixel coordinates behave unexpectedly | Wrong ruler units | Always set `app.preferences.rulerUnits = Units.PIXELS` first |
| Text `size` set but looks different | Wrong type units | Set `app.preferences.typeUnits = TypeUnits.PIXELS` |
| Layer not found by name | Wrong layer level | Layers are scoped; use recursive search for nested layers |
| `layer.bounds[0]` returns a UnitValue, not number | Ruler units issue | Force `Units.PIXELS` before reading bounds |
| Smart Object edit hangs | Missing `doc.save(); doc.close()` | Always save + close when done editing SO |
| React double-mount in dev | Strict Mode | Use `if (peaRef.current) return` guard in `useEffect` |
| Script injection via user input | Direct string concatenation | Always serialize dynamic values with `JSON.stringify` before embedding in `runScript` strings |

---

## Verification

1. **Embed loads:** Open your page in a browser. The Photopea iframe should render inside the container `<div>` with the Photopea UI visible.

2. **Script round-trip works:**

```js
const result = await pea.runScript(`app.echoToOE("hello");`);
console.log(result); // → ["hello", "done"]
```

Expected output: `["hello", "done"]`

3. **File open works:**

```js
await pea.openFromURL("https://example.com/test.png", false);
const info = await pea.runScript(`
  app.echoToOE(JSON.stringify({
    width: app.activeDocument.width,
    height: app.activeDocument.height
  }));
`);
console.log(JSON.parse(info[0]));
```

Expected: JSON object with `width` and `height` matching the image.

4. **Export works:**

```js
const blob = await pea.exportImage("png");
console.log(blob.type, blob.size);
```

Expected: `image/png` with a non-zero `size`.

5. **saveToOE format works:**

```js
const result = await pea.runScript(`app.activeDocument.saveToOE("webp:0.85");`);
const webpBlob = new Blob([result[0]], { type: "image/webp" });
console.log(webpBlob.size);
```

Expected: non-zero `size`.

6. **React guard check:** In React 18 dev mode with Strict Mode, verify only one iframe is created by inspecting the DOM — there should be exactly one `iframe` inside the container.

---

## Limitations

- This skill covers host-page integration patterns; it does not replace Photopea's own terms, API documentation, or licensing guidance.
- Remote URL loading depends on browser CORS behavior, network availability, and the user's Photopea account/session state.
- `runScript` executes scripts inside the embedded Photopea document context. Only run scripts you understand and only with user-approved files.
- Serialize dynamic values with `JSON.stringify` before embedding them in a `runScript` string. Never concatenate user-provided URLs, layer names, or text directly into Photopea script source.
- Export behavior can vary by document size, browser memory limits, and the formats supported by the active Photopea runtime.

---

## Sources

- photopea.js: https://github.com/yikuansun/PhotopeaAPI
- npm: https://www.npmjs.com/package/photopea
- Photopea Live Messaging API: https://www.photopea.com/api/live
- Photopea Script reference: https://www.photopea.com/learn/scripts
- Photoshop JS Scripting reference (compatible): https://theiviaxx.github.io/photoshop-docs/Photoshop/index.html
- Plugin dev gists (addImageAndWait, getDocumentAsImage): https://gist.github.com/yikuansun/c0f1a602b4e9d4e344a41c4f49ded3bf
