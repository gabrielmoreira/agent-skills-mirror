---
name: svg-creator
description: "Creates, edits, sanitizes, and packages spec-correct standalone SVG for icons, logos, diagrams, and SMIL animation. Use when generating or fixing .svg markup or converting a visual concept to SVG. Not for corpus quality audits (svg-quality-audit), React/Tailwind UI (design-taste-frontend), or raster PNG illustration."
version: 1.0.1
---

# SVG Creator

Produce SVGs that are spec-correct (W3C SVG 2), **CSS-independent**, accessible when meaningful, safe to render in untrusted contexts, optimized in size, and readable enough to edit.

## When to Use

- User asks to create, edit, review, validate, or package any SVG graphic (icon, logo, illustration, diagram, chart, pattern, animation, or inline SVG code).
- User asks to "make a beautiful SVG", "generate an .svg file", "fix/optimize SVG markup", "convert a visual concept into SVG", or "design an icon set".
- User needs SVG sanitized for untrusted rendering contexts.
- User needs SMIL animation baked into a standalone SVG (no CSS engine dependency).

## Prerequisites

- Python 3 available on PATH for the validation script (optional but recommended when code execution is available).
- Windows host is primary (PowerShell). This folder does not ship a validator script. Apply the Verification checklist in this file. For corpus-level structure scans, use the sibling skill `svg-quality-audit`.

## Procedure

### 1. Identify output type

Determine: icon, logo, illustration, diagram, chart, pattern, animation, or markup repair.

### 2. Resolve brief details

Fill missing brief details with sensible defaults. Do **not** interrogate the user unless brand colors, exact dimensions, or a sensitive logo recreation are involved.

### 3. Plan before drawing

Pick `viewBox`, palette, accessibility mode, and target size.

**Coordinate system defaults:**

| Type | viewBox | Notes |
|---|---|---|
| UI icon | `0 0 24 24` | stroke 1.5–2 |
| Detailed icon | `0 0 64 64` | |
| Illustration | `0 0 512 512` or `0 0 1200 800` | |
| Diagram | grid-aligned (e.g. `0 0 800 500`) | |
| Pattern tile | one tile | document repeat behavior |

Keep all rendered geometry inside the viewBox. Strokes touching an edge are clipped by half their stroke-width unless inset.

### 4. Write the SVG

Write clean, indented standalone markup with stable IDs and meaningful group names. Follow all core rules below.

### 5. Validate

Apply every item in Verification below. Fix markup until those checks pass.

Do not invent a local SVG audit/validator script in this folder. Structural scans of a folder of SVGs belong to `svg-quality-audit`.

### 6. Return output

Return either a complete `.svg` file or a complete inline `<svg>` element. For markup repair, return the full corrected SVG, not a patch.

---

## Core Rules

### CSS independence (default)

The SVG must render identically in any compliant renderer (Chrome, Inkscape, librsvg, CairoSVG, native iOS/Android SVG support, COLR/SVG fonts, design tools, server-side rasterizers) without depending on a CSS engine, an HTML host, or external stylesheets.

- **No `<style>` element.** Use presentation attributes (`fill="..."`, `stroke="..."`, `opacity="..."`).
- **No `style="..."` attribute** on elements.
- **No `currentColor`** unless the user explicitly asks for a CSS-themeable icon. `currentColor` resolves through the CSS cascade; renderers without CSS fall back to black.
- **No CSS variables** (`var(--name)`).
- **No CSS animations** (`@keyframes`, `animation:` shorthand). For motion, use SMIL: `<animate>`, `<animateTransform>`, `<animateMotion>`, `<set>`.
- **No `:hover` / `:focus` rules.**
- **No external resources.** No `@import`, no external fonts, no remote `<image>` hrefs.

**Exception:** When the user explicitly opts in to web-only output ("for an HTML icon system", "themeable via parent color", "use Tailwind classes"), `currentColor` and a minimal `<style>` block are acceptable.

### Root element

- Always include `xmlns="https://www.w3.org/2000/svg"` on the root `<svg>`. Required for standalone SVG, `<img src>`, and copy-paste portability.
- Always include a `viewBox`. Attribute name is camelCase (`viewBox`, not `viewbox`).
- Format: `min-x min-y width height` — four finite numbers, width and height positive.
- Default `preserveAspectRatio` is `xMidYMid meet`. Set explicitly only when you need cropping (`slice`) or non-uniform stretch (`none`).
- Never emit retired `version` or `baseProfile` attributes.
- Never emit `<!DOCTYPE>`, `<!ENTITY>`, or `<?xml-stylesheet?>`. Plain `<?xml ?>` declaration is allowed but unnecessary inside HTML.

### Path data

- Start every visible path with `M` or `m`. After `M`, extra coordinate pairs are implicit `L`/`l`; after `m`, implicit `l`.
- Smooth curves (`S`/`s`, `T`/`t`) reflect the previous control point **only** if the previous command was the matching curve type (`C`/`c` for `S`; `Q`/`q` for `T`). Otherwise the inferred control point collapses to the current point and produces a degenerate curve. **Never emit `S` after `L`.**
- Arc command takes exactly seven values: `rx ry x-axis-rotation large-arc-flag sweep-flag x y`. Flags must be `0` or `1`. The parser treats arc flags as a single digit each; do not write `10` thinking it means "1, 0".
- Avoid negative arc radii (spec normalizes via absolute value but explicit positive values are clearer for tooling).
- Cap path-data decimals at 2–3 places for icons, 3–4 for illustrations.

### Color and paint

- `fill` defaults to **black**, `stroke` defaults to **none**. A bare `<path d="..."/>` renders solid black. For stroke-only icons, set `fill="none"` and a stroke explicitly.
- Set explicit colors as presentation attributes: `fill="#3b82f6"`, `stroke="#0f172a"`.
- Set `stroke-linecap="round"` and `stroke-linejoin="round"` for friendly UI icons and organic line art. Use `miter` only for sharp technical/geometric styles, and set `stroke-miterlimit` to avoid spikes.
- For diagrams that may be scaled non-uniformly, use `vector-effect="non-scaling-stroke"`.
- `paint-order` defaults to `fill stroke markers`. To outline text without eating into letterforms, set `paint-order="stroke"` on `<text>`.
- `fill-rule` defaults to `nonzero`. For nested sub-paths where direction matters, consider `fill-rule="evenodd"`.

### Identifiers and references

- Every `id` must be unique. Prefix with the subject (`mountain-gradient-a`, `chart-clip`, `arrow-marker`).
- Every `url(#id)` and `href="#id"` must resolve.
- Sanitize both `href` and `xlink:href`; earlier-generation `xlink:href` still resolves if `href` is absent.
- Avoid `xlink:href` in new output. SVG 2 supports plain `href` everywhere.

### Gradients

- `gradientUnits` default is `objectBoundingBox` (x1/y1/x2/y2 are 0–1 fractions of the filled element's bounding box). Use `userSpaceOnUse` for absolute placement.
- Default linearGradient vector is horizontal: `x1=0% y1=0% x2=100% y2=0%`. Set vectors explicitly for diagonal or vertical gradients.
- `spreadMethod` defaults to `pad`. Use `reflect` or `repeat` only intentionally.
- Stop offsets must be monotonically non-decreasing. Out-of-range values are clamped to `[0, 1]`.

### Masks vs clipPath

- `clipPath` is **binary** (in or out, no soft edge). `mask` is **alpha or luminance**, allowing soft edges and gradients.
- `clipPathUnits` defaults to `userSpaceOnUse`. **`maskUnits` defaults to `objectBoundingBox`.** They are opposite — set explicitly when in doubt.
- `mask` defaults to `mask-type="luminance"`: white pixels show, black pixels hide. Naive masks drawn with default colors render as invisible. Either set `mask-type="alpha"` or use white fills.

### Filters

- Filter region defaults are `x="-10%" y="-10%" width="120%" height="120%"`. **Effects extending further (drop shadows, glows, large blurs) get clipped.** For a shadow with `dy=8 stdDeviation=10`, expand to e.g. `x="-25%" y="-25%" width="150%" height="150%"`.
- `feDropShadow` is the safest way to draw a shadow (consolidates blur + offset + flood + composite + merge).
- `feMerge` stacks `<feMergeNode>` children bottom-to-top in document order.
- `color-interpolation-filters` defaults to `linearRGB` (not sRGB). For color-accurate blending, set `color-interpolation-filters="sRGB"` on the `<filter>`.
- Avoid expensive primitives in animations: `feTurbulence`, `feMorphology`, `feDisplacementMap`, `feConvolveMatrix` rasterize per frame. Cache or pre-render.

### Markers

- `markerUnits` defaults to `strokeWidth`: marker dimensions scale with host stroke. Use `userSpaceOnUse` to fix marker size.
- `orient="auto"` rotates the marker to match path direction; `auto-start-reverse` lets one arrowhead serve both ends.
- Use `fill="context-stroke"` on the marker's geometry so the arrowhead inherits the line's color.

### Accessibility

**For meaningful SVGs** (illustrations, charts, diagrams, meaningful logos):

- Set `role="img"` on the root for atomic graphics. Use `role="graphics-document"` for charts/maps/diagrams whose layout conveys meaning. Use `role="graphics-symbol"` for atomic glyphs whose meaning matters more than visual detail.
- Place `<title>` and `<desc>` as the **first** direct children of the root.
- Reference them with `aria-labelledby="<title-id> <desc-id>"`.
- Provide one `<title>` and at most one `<desc>` per element.

**For decorative SVGs** (next to visible text, button icons with labels, ambient marks):

- Set `aria-hidden="true"` and `focusable="false"`.
- Do **not** include `role="img"` simultaneously with `aria-hidden="true"`.

### Security (always strip in untrusted SVG)

- `<script>` element.
- Any attribute whose lowercased name starts with `on` (event handlers: `onclick`, `onload`, `onerror`, `onbegin`, `onend`, `onrepeat`, `onzoom`).
- `javascript:` URLs in `href`, `xlink:href`, or any URL-bearing attribute.
- `<foreignObject>` (full HTML inside SVG — highest-risk element).
- External resource references in `<image>`, `<use>`, `feImage`, `<a>`, CSS `url(...)`, `@import`, `@font-face`. Allow only fragment refs (`#id`).
- `data:` URLs limited to `image/png`, `image/jpeg`, `image/gif`, `image/webp` in `<image href>`. **Never `data:image/svg+xml`** (equivalent to inline SVG).
- XML constructs: `<!DOCTYPE>`, `<!ENTITY>` (XXE), `<?xml-stylesheet?>` PI.
- SMIL animations whose `to`/`from`/`values` change `href`/`xlink:href` to `javascript:` or `data:image/svg+xml`.

For output that may end up in untrusted hands, recommend the consumer pass it through DOMPurify with `USE_PROFILES: { svg: true, svgFilters: true }`, and parse server-side with external entity resolution disabled (`defusedxml` in Python, `disallow-doctype-decl` feature in Java).

### Animation (SMIL only)

For CSS-independent SVG, animation is **always** SMIL declarative animation elements baked into the SVG document.

- Use `<animate>` for scalar attributes (`cx`, `r`, `opacity`, `fill`, `stroke-width`, etc.).
- Use `<animateTransform>` for transform animation. The `type` attribute is required: `translate`, `scale`, `rotate`, `skewX`, `skewY`. **Never use `<animate attributeName="transform">`** — it does not work.
- Use `<animateMotion>` for path-following motion. Provide a `path` attribute or a child `<mpath href="#path-id"/>`. Optional `rotate="auto"` aligns the moved element to the path tangent.
- Use `<set>` for instantaneous attribute changes at a `begin` time (no interpolation).
- Required attributes: `attributeName` (case-sensitive, kebab-case e.g. `stroke-width`), one of `from`+`to` / `by` / `values`, and `dur`.
- Default `repeatCount` is 1. Use `repeatCount="indefinite"` to loop. `fill="freeze"` keeps the end state; `fill="remove"` (default) reverts.
- For multi-step animation: `values="a;b;c;d"` with optional `keyTimes="0;0.25;0.5;1"` (lengths must match) and `calcMode` of `linear` (default), `discrete`, `paced`, or `spline` (with `keySplines`).
- For complex sequencing: `begin="otherAnim.end"` and `begin="elementId.click"` to chain animations declaratively.
- SMIL ignores `prefers-reduced-motion` automatically. Keep motion subtle, brief, looping, and never essential to comprehension. Always provide a static equivalent.

### Performance

- Element count: under 500 is fast everywhere; 500–5,000 is fine on desktop, slow on mobile zoom; over 10,000 needs reconsideration.
- One complex path is cheaper than many simple paths. Use SVGO-style `mergePaths` mentally when authoring.
- Filters force an offscreen rasterization pass. Combine effects in a single `<filter>` chain rather than nesting filters across groups.
- Gradient stop count: keep ≤8 in animated gradients.

## Reference Loading

This folder ships only `SKILL.md`. Use Core Rules, Pitfalls, and Verification in this file. For folder-level structure scans, load the sibling skill `svg-quality-audit` — do not add an audit script here.

## Output Contract

For new SVGs, produce one of:

- A complete standalone `.svg` file with valid XML and resolved references.
- A complete inline `<svg>` element suitable for HTML.
- A short explanation plus the SVG, only when the user asks for explanation or the design has non-obvious choices.

For SVG repair, return the corrected complete SVG. For sets (icon families, multi-state graphics), use a consistent coordinate system, stroke language, ID prefix, and palette across all members.

## Pitfalls

- **`<style>` and `style="..."` break portability.** A renderer without a CSS engine ignores them. Use presentation attributes.
- **`currentColor` defaults to black** in non-CSS renderers. Use explicit colors unless the user asks for CSS theming.
- **`viewBox` is camelCase.** `viewbox` silently fails in strict XML parsing.
- **`fill` default is black.** Forgetting `fill="none"` on a stroked outline produces a solid black blob.
- **`mask-type` default is `luminance`.** White-on-black masks reveal; alpha-style masks need `mask-type="alpha"`.
- **Filter region defaults clip shadows.** Expand explicitly.
- **Arc flags are single-digit.** Compact `A 25,25 0 016,3` parses as flags `0`, `1` then number `6`.
- **`S`/`T` after a non-matching curve degenerate.** Always pair `C`→`S` and `Q`→`T`.
- **Both `href` and `xlink:href` must be sanitized;** the retired form still resolves.
- **`<animate attributeName="transform">` does not work;** use `<animateTransform type="...">`.
- **`data:image/svg+xml` URLs are equivalent to inline SVG** and unsafe in `<image href>`.

## Verification

1. Apply the manual spot-checks below to the SVG you just wrote. This folder does not ship a validator; do not invent one. For scanning a directory of SVGs, use `svg-quality-audit`.

2. Manual spot-checks:
- `xmlns` present on root `<svg>`.
- `viewBox` is camelCase and contains four finite numbers with positive width/height.
- No `<style>`, no `style="..."`, no `currentColor` (unless explicitly requested), no CSS variables.
- No `<script>`, no `on*` attributes, no `javascript:` URLs, no `<foreignObject>`.
- Every `url(#id)` and `href="#id"` resolves to an existing `id`.
- `fill="none"` set on all stroke-only paths.
- Filter regions expanded for any shadow/blur with offset or large `stdDeviation`.
- Arc flags are single digits (`0` or `1`).
- No `S`/`s` or `T`/`t` commands preceded by non-matching curve commands.
- `<title>` and `<desc>` are first children of root for meaningful SVGs; `aria-hidden="true"` on decorative SVGs.
- Animation uses `<animateTransform type="...">`, not `<animate attributeName="transform">`.

3. Render test: open the `.svg` file directly in a browser (no HTML host) to confirm it renders without CSS dependency.

## Related Skills

- UI/UX design skills — for interface design, accessibility review, responsive layouts, and design system guidance.
- Animation/motion skills — for Lottie/Rive/Canvas/WebGL animation pipelines when SVG SMIL is insufficient.
