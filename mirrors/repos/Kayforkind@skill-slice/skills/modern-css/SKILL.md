---
name: modern-css
version: 1.2.1
description: "Writes Baseline 2026 native CSS: Flexbox/Grid/subgrid, logical properties, container queries, @layer/@scope, :has, oklch, nesting, anchor positioning, and fluid type. Use when writing or reviewing stylesheets, layout, dark mode, or cascade without a preprocessor. Not for Tailwind v4 @theme setup (setup-tailwind-typescript), glassmorphism recipes, or Sass/CSS-in-JS. Never default to physical margin-left/width when logical properties apply."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-15
---

# Modern CSS (2026)

Lean on the cascade, logical properties, and intrinsic sizing so layouts adapt without a forest of media queries. All techniques below are Baseline-available in 2026 unless explicitly flagged as newer/uneven.

## When to Use

- Writing component or page styles, design tokens, or a theming layer.
- Refactoring a media-query-heavy stylesheet toward container queries and fluid sizing.
- Reviewing CSS for specificity wars, dark-mode bugs, layout shift, or motion-accessibility.
- Implementing dark-mode strategies, anchor-positioned tooltips, or scroll-snap carousels.
- Animating entry/exit transitions for popovers, dialogs, or accordions without JS measurement.

## Prerequisites

- A modern browser engine (Chromium 120+, Firefox 121+, Safari 17.4+) for Baseline features.
- For newer/uneven features (anchor positioning, `interpolate-size`, `field-sizing`, pure-CSS carousel controls, `text-box-trim`, masonry): check current engine support and gate behind `@supports`.
- No build step required — all features are native CSS. A preprocessor (Sass/Less) is optional and not assumed.

## Procedure

### 1. Choose the right layout axis: Flexbox vs Grid

Use the axis that matches the problem. Both support `gap`.

| Use Flexbox when | Use Grid when |
|------------------|---------------|
| One-dimensional flow (row OR column) | Two-dimensional (rows AND columns) |
| Content size drives layout | Layout structure drives content |
| Toolbars, button groups, tag lists | Page shells, card galleries, forms |

```css
/* Intrinsically responsive grid — no media queries */
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(16rem, 100%), 1fr));
  gap: 1rem;
}
```

**Subgrid** lets nested items align to the parent's tracks — essential for equal-height card sections:

```css
.card { display: grid; grid-template-rows: subgrid; grid-row: span 3; }
```

### 2. Replace physical properties with logical properties

Prefer flow-relative properties so layouts mirror correctly in RTL/vertical writing modes — and so you write less code. `margin-inline`, `padding-block`, `inset`, and `inline-size` follow the text direction; `margin-left`/`top`/`width` do not.

```css
.card {
  margin-inline: auto;          /* left+right in LTR, swaps in RTL */
  padding-block: 1rem;          /* top+bottom */
  inline-size: min(65ch, 100%); /* "width" along the inline axis */
  border-inline-start: 2px solid var(--brand); /* leading edge, dir-aware */
}
.overlay { position: absolute; inset: 0; } /* top/right/bottom/left: 0 */
```

| Physical (avoid) | Logical (prefer) |
|------------------|------------------|
| `width` / `height` | `inline-size` / `block-size` |
| `margin-left` / `-right` | `margin-inline-start` / `-end` (or `margin-inline`) |
| `padding-top` / `-bottom` | `padding-block-start` / `-end` (or `padding-block`) |
| `top/right/bottom/left` | `inset-block-*` / `inset-inline-*` / `inset` |
| `text-align: left` | `text-align: start` |

### 3. Adopt container queries for component-level responsiveness

Style a component by *its own* available size, not the viewport — the key to truly reusable components. Query the container's **size**, or its **style** (custom-property value).

```css
.card-host { container-type: inline-size; container-name: card; }

@container card (width >= 30rem) {
  .card { grid-template-columns: 8rem 1fr; }
}
/* Style query: react to a custom property set on the container */
@container style(--variant: compact) { .card { padding: 0.5rem; } }

/* Container units scale type to the container, not the screen */
.card h2 { font-size: clamp(1rem, 5cqi, 1.75rem); }
```

| Unit | Relative to |
|------|-------------|
| `cqw` / `cqh` | container width / height |
| `cqi` / `cqb` | container inline / block size |
| `cqmin` / `cqmax` | smaller / larger container axis |

> **NOTE:** Size container queries are Baseline; **style queries** are widely available for *custom properties* but querying arbitrary standard properties is still limited — keep style queries to your own `--tokens`.

### 4. Set up custom properties, @property, and color tokens

Use custom properties for tokens; use `@property` to make them *typed* and *animatable*. Derive variants with **relative color syntax** and `color-mix()` instead of hand-picking hex.

```css
@property --angle { syntax: "<angle>"; inherits: false; initial-value: 0deg; }

:root { --space: 1rem; --brand: oklch(0.6 0.2 250); }

.ring { background: conic-gradient(var(--brand) var(--angle), #0000 0); }
.ring:hover { --angle: 360deg; transition: --angle 0.6s; } /* animatable via @property */

/* Relative color syntax: derive a darker hover from one token */
.btn         { background: var(--brand); }
.btn:hover   { background: oklch(from var(--brand) calc(l - 0.08) c h); }
.btn:disabled{ background: oklch(from var(--brand) l calc(c * 0.3) h); }

/* Theme native form controls in one line */
:root { accent-color: var(--brand); }
```

> **TIP:** Prefer `oklch()` for color tokens: perceptually uniform lightness makes accessible hover/active variants trivial (`calc()` the L channel) and gives a wider gamut than hex/rgb. Relative color syntax (`from`) lets every variant track one source token, so re-theming touches a single line.

### 5. Use modern selectors

`:has()` is the parent/relational selector; `:is()`/`:where()` flatten selector lists (`:where()` adds **zero** specificity).

```css
.field:has(:user-invalid) { --border: red; }      /* style parent from child state */
.gallery:has(> :nth-child(6)) { gap: 0.5rem; }     /* respond to child count */
:where(h1, h2, h3) { text-wrap: balance; }         /* low-specificity defaults */
li:nth-child(odd of .visible) { background: #f3f3f3; } /* filtered nth-child */
```

### 6. Nest rules natively

Nest related rules without a preprocessor. The `&` is required when the nested selector starts with an element name or compounds the parent.

```css
.card {
  padding: var(--space);
  & > .title { font-weight: 600; }
  &:hover { background: color-mix(in oklch, canvas, var(--brand) 8%); }
  @media (width >= 48rem) { padding: 2rem; }
}
```

### 7. Manage cascade order with @layer and @scope

`@layer` gives you deterministic source order independent of specificity — declare the order once, stop fighting `!important`. `@scope` bounds styles to a subtree with a lower/upper boundary.

```css
@layer reset, base, components, utilities;
@layer base   { a { color: var(--brand); } }
@layer utilities { .text-center { text-align: center; } } /* always wins over base */

@scope (.card) to (.card__body) {
  img { border-radius: 8px; } /* applies only between the boundaries */
}
```

| Tool | Use it to |
|------|-----------|
| `@layer` | Order whole buckets (reset < framework < app < utilities) |
| `:where()` | Author low-specificity defaults that are easy to override |
| `@scope` | Contain component styles without BEM-style naming |

### 8. Position with anchors (progressive enhancement)

Tether a popover/tooltip/menu to its trigger in CSS — no JS measurement loop. Name the anchor, point the positioned element at it, and declare fallbacks for when it would overflow the viewport.

```css
.trigger { anchor-name: --trigger; }

.tooltip {
  position: absolute;            /* or fixed; pairs well with [popover] */
  position-anchor: --trigger;
  position-area: block-start center;  /* place above, centered */
  margin-block-end: 0.5rem;
  position-try-fallbacks: flip-block, flip-inline; /* reposition if clipped */
}
```

> **WARNING:** Anchor positioning is **newly** available and still uneven across engines in 2026. Gate it behind `@supports (anchor-name: --x){…}` and ensure the element is still usable (e.g. normal-flow or JS-positioned) without it.

### 9. Animate transitions, entry/exit, and intrinsic sizing

Animate entry/exit of elements that toggle `display` (popovers, dialogs) with `@starting-style` + `transition-behavior: allow-discrete`. Animate **to `height: auto`** by opting into `interpolate-size`. Let inputs grow to their content with `field-sizing`. Always honor reduced-motion.

```css
/* Enter/exit animation for a [popover] or <dialog> */
.popover {
  opacity: 0; transition: opacity .3s, display .3s allow-discrete;
}
.popover:popover-open { opacity: 1; }
@starting-style { .popover:popover-open { opacity: 0; } } /* defines the "from" state */

/* Animate an accordion to its natural height (no JS measuring) */
:root { interpolate-size: allow-keywords; }
.panel { block-size: 0; overflow: clip; transition: block-size .3s; }
.panel.open { block-size: auto; }       /* or: calc-size(auto, size) */

/* Auto-grow textareas / size selects to content */
textarea, select { field-sizing: content; }

@media (prefers-reduced-motion: reduce) {
  *, ::before, ::after {
    animation-duration: .01ms !important;
    transition-duration: .01ms !important;
    scroll-behavior: auto !important;
  }
}
```

- **View Transitions:** `@view-transition { navigation: auto; }` for smooth same-document (and cross-document, where supported) page changes.
- **Scroll-driven animations** (`animation-timeline: view()`) are powerful but still uneven across engines — gate behind `@supports` and provide a static fallback.

> **NOTE:** `interpolate-size: allow-keywords`, `calc-size()`, and `field-sizing` are 2024–2025 additions and not universal in 2026. They degrade gracefully (no animation / fixed size), so use them as progressive enhancement, never load-bearing.

### 10. Build scroll-snap carousels

Build sliders with native scroll snap — accessible, keyboard-friendly, no library.

```css
.carousel {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scroll-behavior: smooth;
  overscroll-behavior-x: contain;
}
.carousel > * { flex: 0 0 100%; scroll-snap-align: start; }
```

> **NOTE:** Pure-CSS carousel controls — `::scroll-button()`, `::scroll-marker` / `scroll-marker-group` (dots/prev-next with zero JS) — are **Chromium-only as of 2026**. Treat them as enhancement on top of the scroll-snap baseline above.

### 11. Set up fluid responsive typography

Fluid type with `clamp()` removes most breakpoint juggling; use `rem` for accessibility (respects user font scale). Use **dynamic viewport units** (`dvh`/`svh`/`lvh`) for full-height layouts so mobile browser chrome doesn't clip content. Improve line breaks with `text-wrap`.

```css
:root { --step-0: clamp(1rem, 0.92rem + 0.4vw, 1.25rem); }
h1 { font-size: clamp(2rem, 1.4rem + 3vw, 4rem); text-wrap: balance; }
p  { font-size: var(--step-0); text-wrap: pretty; max-inline-size: 65ch; }

.hero { min-block-size: 100dvh; }  /* not 100vh — accounts for mobile toolbars */
```

| Token | Use | Avoid |
|-------|-----|-------|
| `rem` | font sizes, spacing scale | `px` for type (ignores user zoom prefs) |
| `clamp()` | fluid type/space (min, preferred, max) | stacks of width media queries |
| `ch` | readable measure (`max-inline-size`) | fixed `px` widths for text |
| `dvh`/`svh`/`lvh` | full-height sections on mobile | `100vh` (clipped by browser UI) |

### 12. Implement dark mode

Declare `color-scheme` so form controls/scrollbars theme correctly, then pick colors with `light-dark()` — no duplicate `prefers-color-scheme` block needed for simple cases.

```css
:root { color-scheme: light dark; }
body {
  background: light-dark(#ffffff, #111418);
  color:      light-dark(#111418, #e7e9ea);
}
/* User override: a [data-theme] attr forces one scheme */
[data-theme="dark"]  { color-scheme: dark;  }
[data-theme="light"] { color-scheme: light; }
```

> **WARNING:** `light-dark()` only resolves when `color-scheme` includes both keywords on that element (or an ancestor). Forgetting `color-scheme: light dark` makes every `light-dark()` value silently render its light branch.

### 13. Apply performance and containment

Skip rendering work for offscreen content and stop scrollbars from shifting layout.

```css
/* Skip layout/paint for far-offscreen list items; reserve their space */
.feed > article {
  content-visibility: auto;
  contain-intrinsic-size: auto 16rem; /* estimated height → no CLS on reveal */
}

/* Reserve the scrollbar track so toggling overflow doesn't shift the page */
:root { scrollbar-gutter: stable both-edges; }
```

- Use `contain: layout paint` on independent widgets to wall off their reflow from the rest of the page.
- Reach for `will-change` only right before an animation and remove it after — leaving it on permanently wastes GPU memory.

### 14. Honor accessibility and user preferences

Style keyboard focus only (not mouse clicks), respect high-contrast and contrast/transparency preferences, and never strip focus outlines without a replacement.

```css
:focus-visible { outline: 2px solid var(--brand); outline-offset: 2px; }
:focus:not(:focus-visible) { outline: none; } /* hide ring for pointer users only */

/* Windows High Contrast / forced colors: use system colors, don't fight them */
@media (forced-colors: active) {
  .btn { border: 1px solid ButtonText; background: ButtonFace; color: ButtonText; }
  /* forced-color-adjust: none; ONLY when you must preserve a meaningful color */
}

@media (prefers-contrast: more) { :root { --border: CanvasText; } }
@media (prefers-reduced-transparency: reduce) {
  .glass { backdrop-filter: none; background: Canvas; } /* drop blur, stay legible */
}
```

## Pitfalls

| Anti-pattern | Why it hurts | Do instead |
|--------------|--------------|------------|
| Viewport media queries for component layout | Breaks when component is reused at other widths | `@container` |
| Deeply chained selectors for specificity | Specificity wars, `!important` creep | `@layer` + `:where()` |
| `px` font sizes | Ignores user zoom / a11y prefs | `rem` + `clamp()` |
| `100vh` for full-height sections | Clipped by mobile browser chrome | `100dvh` / `svh` / `lvh` |
| Physical props (`margin-left`, `width`) in i18n UI | Breaks in RTL/vertical writing modes | logical props (`margin-inline`, `inline-size`) |
| Duplicate light/dark color blocks | Drift between the two themes | `light-dark()` |
| Animating `width`/`height`/`top` | Triggers layout, janky INP | animate `transform`/`opacity`; for size use `interpolate-size` |
| Hard-coded hex everywhere | No theming, no contrast math | `oklch()` tokens + relative color + `color-mix()` |
| `outline: none` with no replacement | Kills keyboard focus visibility (WCAG 2.4.7) | style `:focus-visible` instead |
| JS to measure & animate `auto` height | Fragile, reflow-heavy | `interpolate-size: allow-keywords` + `calc-size()` |

### Critical gotchas

1. **`:has()` is unforgiving** — an invalid selector inside invalidates the whole list (unlike `:is()`/`:where()`, which are forgiving).
2. **Nesting needs `&` before element/type selectors:** `div { p {…} }` is fine, but `div { & p {…} }` is clearer and `div { &.active {…} }` is required to compound.
3. **`container-type: inline-size` establishes containment** — descendants can no longer size the container by their height; watch for collapsed containers.
4. **`@layer` beats specificity, not `!important`:** an `!important` in an *earlier* layer still wins, because important declarations reverse layer order.
5. **`text-wrap: balance` is capped** (browsers stop balancing past ~6 lines) — it's for headings, not body copy; use `pretty` for paragraphs.
6. **`gap` on Flexbox** is fully supported now — stop using margin hacks and `:last-child` margin resets.
7. **`interpolate-size: allow-keywords` is opt-in and not universal** — it unlocks animating to `auto`/`min-content`, but without it the transition simply snaps. Keep the layout correct in the un-animated state.
8. **Anchor positioning fallbacks matter:** without `position-try-fallbacks` an anchored element can render off-screen; always test against viewport edges and `@supports`-gate it.
9. **`content-visibility: auto` needs `contain-intrinsic-size`** — omitting the size estimate causes scrollbar jumps and CLS as items render on scroll.
10. **`forced-colors` overrides your palette by design** — don't `forced-color-adjust: none` to "fix" it except for color-critical UI (e.g. a chart legend); doing so breaks High Contrast Mode.
11. **`text-box-trim`/`text-box`** (leading-trim for tight optical alignment) is rolling out unevenly in 2026 — use it to remove half-leading on headings, but don't rely on it for layout math.
12. **Masonry item layout** (`grid-template-rows: masonry` / `item-pack`) is still being standardized and is not Baseline — use a JS/columns fallback until it lands.

## Verification

1. **Logical properties / RTL check:** Temporarily set `dir="rtl"` on `<html>` and confirm margins/padding/inset mirror correctly. If any physical property was used, the layout will not flip.
2. **Container query check:** Resize the component's parent (not the browser window) and confirm styles respond. If styles only change on viewport resize, you are using `@media` instead of `@container`.
3. **Dark mode check:** Set `color-scheme: light dark` on `:root`, then toggle OS/browser dark mode. Confirm `light-dark()` values switch. If the light branch always renders, `color-scheme` is missing both keywords.
4. **Reduced-motion check:** Enable `prefers-reduced-motion: reduce` in DevTools (Rendering tab → Emulate CSS media feature). Confirm all animations and transitions are effectively instant.
5. **Focus-visible check:** Tab through the page with keyboard only — confirm visible focus rings. Click elements with mouse — confirm no focus ring appears. If rings show on click, `:focus:not(:focus-visible)` override is missing.
6. **`@layer` order check:** Inspect computed styles in DevTools. Confirm that a utility-layer rule wins over a base-layer rule even when the base rule has higher specificity. If not, the layer order declaration is missing or misordered.
7. **`content-visibility` CLS check:** Scroll a long list with `content-visibility: auto`. If scrollbar jumps or content shifts on reveal, `contain-intrinsic-size` is missing or inaccurate.
8. **Anchor positioning check:** Open the anchored element near a viewport edge. If it renders off-screen, `position-try-fallbacks` is missing. Confirm the element is still positioned (even if imperfectly) with `@supports (anchor-name: --x)` disabled.
9. **`interpolate-size` check:** Toggle a panel between `block-size: 0` and `block-size: auto`. If it snaps without animating, confirm `:root { interpolate-size: allow-keywords; }` is set and the browser supports it.
10. **Forced-colors check:** Enable Windows High Contrast Mode (Settings → Accessibility → Contrast themes). Confirm form controls and text are legible using system colors. If custom colors persist and are illegible, remove `forced-color-adjust: none` or add explicit system-color fallbacks.

## Related skills

- `modern-html` — markup semantics, forms, and accessibility landmarks
- `web-interface-guidelines` — UI checklists and visual stability reference
- `development` — frontend/backend workflows
