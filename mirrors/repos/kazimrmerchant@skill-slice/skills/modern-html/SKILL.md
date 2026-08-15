---
name: modern-html
version: 1.2.1
description: "Authors and reviews 2026 Baseline HTML: document head, semantic landmarks, native dialog/popover/invoker commands, web components, forms, WCAG 2.2, JSON-LD, loading/CLS, and HTML security (CSP/SRI). Use when writing or auditing markup rather than CSS or framework state. Not for CSS layout/animation (modern-css), React/Vue architecture, or bundler config."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-15
---

# Modern HTML (2026)

Author HTML that is semantic, accessible, fast, and stable by default. Reach for ARIA, JavaScript widgets, and polyfills only after the native element falls short. Everything below is Baseline-available in 2026 unless explicitly flagged.

## When to Use

- Writing or reviewing markup for any web surface (app shell, marketing page, email-adjacent HTML).
- Setting up a document `<head>` (lang, viewport, metadata, color scheme).
- Auditing an existing page for accessibility (WCAG 2.2), Core Web Vitals (LCP/CLS/INP), or SEO regressions.
- Deciding between a native element/attribute and a JS component.

**Trigger keywords:** HTML, markup, semantic, accessibility, WCAG, ARIA, dialog, popover, web components, shadow DOM, forms, viewport, meta tags, structured data, JSON-LD, srcset, CLS, LCP, CSP, SRI, importmap, speculation rules.

**Do NOT use for:**
- CSS layout/animation work → use `modern-css`.
- Framework component architecture (React/Vue state, routing) → this skill is markup-level only.
- Build tooling / bundler config.

## Prerequisites

- A modern browser engine (Chromium 130+, Firefox 130+, Safari 18+) for full Baseline coverage of popover, invoker commands, and declarative shadow DOM.
- For older-engine support, keep progressive-enhancement fallbacks (`el.showModal()`, `el.showPopover()`) — never make the only path to a destructive action depend on a brand-new attribute.
- No scripts or reference files are required to use this skill. If the agent needs deeper CSS-level detail (layout, `aspect-ratio`, `container-type`), load the `modern-css` skill instead.

## Procedure

### 1. Document setup (the `<head>`)

Get the document scaffold right before anything else — `lang`, encoding, viewport, and color scheme affect rendering, accessibility, and the first paint.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="color-scheme" content="light dark">
  <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#111418" media="(prefers-color-scheme: dark)">
  <title>Page title — Site</title>
</head>
```

| Tag | Why it's required |
|-----|-------------------|
| `<meta charset="utf-8">` | First child of `<head>`, within the first 1024 bytes — stops encoding sniffing |
| `<meta name="viewport" …>` | Responsive scaling; `viewport-fit=cover` enables `env(safe-area-inset-*)` for notches |
| `<html lang>` (+ `dir` per locale) | AT pronunciation, hyphenation, `:lang()`, browser translation |
| `<meta name="color-scheme">` | Themes UA controls + page canvas before CSS paints (kills the dark-mode white flash) |

### 2. Semantic structure & landmarks

One `<main>`, one `<h1>`, a logical heading order with no skipped levels. Provide a skip link as the first focusable element. Use elements for meaning, not styling.

```html
<a class="skip-link" href="#main">Skip to content</a>
<header><nav aria-label="Primary">…</nav></header>
<main id="main">
  <search>
    <form role="search"><input type="search" name="q" aria-label="Search"></form>
  </search>
  <article>
    <h1>Title</h1>
    <section aria-labelledby="details"><h2 id="details">Details</h2>…</section>
    <figure><img …><figcaption>…</figcaption></figure>
    <time datetime="2026-01-15">Jan 15, 2026</time>
  </article>
  <aside aria-label="Related">…</aside>
</main>
<footer>…</footer>
```

| Need | Native element | Avoid |
|------|----------------|-------|
| Modal | `<dialog>` + `showModal()` | `<div role="dialog">` + focus-trap library |
| Disclosure | `<details>`/`<summary>` | `<div>` + click JS |
| Tooltip / menu / non-modal popup | `popover` attribute | hand-rolled show/hide |
| Search region | `<search>` | `<div role="search">` |

### 3. Native interactivity (JS-optional)

Open and close overlays declaratively. **Invoker commands** (`command` + `commandfor`) wire a button to a `<dialog>` or popover with no script; **popovers** get the top layer, light-dismiss, and Esc for free.

```html
<!-- Non-modal popover: top layer, light-dismiss, zero JS -->
<button popovertarget="menu">Options</button>
<div id="menu" popover>
  <ul role="menu">…</ul>
</div>

<!-- Modal dialog opened by an invoker command (no JS) -->
<button commandfor="confirm" command="show-modal">Delete…</button>
<dialog id="confirm" aria-labelledby="ct">
  <h2 id="ct">Delete?</h2>
  <form method="dialog">
    <button value="cancel">Cancel</button>
    <button value="ok" autofocus>Delete</button>
  </form>
</dialog>
```

| Pattern | Markup | Modality |
|---------|--------|----------|
| Menu / tooltip / non-modal | `popover` + `popovertarget` | non-modal, does **not** trap focus |
| Confirm / blocking | `<dialog>` + `command="show-modal"` | modal, traps focus, has backdrop |
| Disclosure | `<details>`/`<summary>` | inline, no top layer |

> **WARNING:** Invoker commands (`command`/`commandfor`) are newly Baseline (2025). If you must support older engines, keep a tiny progressive-enhancement fallback (`el.showModal()` / `el.showPopover()`); never make the only path to a destructive action depend on a brand-new attribute.

### 4. Web components

Use declarative shadow DOM so components render server-side without a JS round-trip. Use the `slot` for projected content.

```html
<user-card>
  <template shadowrootmode="open">
    <style>:host { display:block; container-type:inline-size; }</style>
    <slot name="name"></slot>
    <slot></slot>
  </template>
  <span slot="name">Ada</span>
  <p>Bio…</p>
</user-card>
```

- **Form participation:** attach inputs to forms via `ElementInternals` (`static formAssociated = true; this.attachInternals()`), not a hidden `<input>` hack.
- **Scoped registries** avoid global custom-element name collisions in micro-frontends.
- Always provide light-DOM fallback content for no-JS and SEO crawlers.

### 5. Modern forms

Let the browser do autofill, keyboard, and validation work. Set the autofill + keyboard hints on every text field, and group related controls with `<fieldset>`/`<legend>`.

```html
<input id="email" name="email" type="email"
       autocomplete="email" inputmode="email"
       enterkeyhint="next" autocapitalize="off"
       spellcheck="false" required>

<input id="otp" name="otp"
       autocomplete="one-time-code" inputmode="numeric"
       pattern="\d{6}" maxlength="6" required>

<fieldset>
  <legend>Notification method</legend>
  <label><input type="radio" name="notify" value="email" checked> Email</label>
  <label><input type="radio" name="notify" value="sms"> SMS</label>
</fieldset>

<label for="city">City</label>
<input id="city" name="city" list="cities" autocomplete="address-level2">
<datalist id="cities"><option value="Austin"></option><option value="Boston"></option></datalist>
```

| Attribute | Purpose | Example value |
|-----------|---------|---------------|
| `autocomplete` | Browser/password-manager autofill | `email`, `new-password`, `cc-number`, `one-time-code` |
| `inputmode` | On-screen keyboard layout | `numeric`, `decimal`, `tel`, `url` |
| `enterkeyhint` | Soft-keyboard Enter label | `next`, `done`, `search`, `send` |
| `pattern` | Client-side format validation | `\d{6}` |

- A `<legend>` is the accessible name of its `<fieldset>` — use it to label radio/checkbox groups, not a bare `<p>`.
- Use `<output>` for computed results so AT announces live changes.
- Use `:user-valid` / `:user-invalid` (CSS) so error styling appears only *after* interaction — never red-flag an untouched field.

### 6. Accessibility (WCAG 2.2 / ARIA)

First rule of ARIA: don't use ARIA when a native element exists. Manage focus on route changes and dialog open/close; use the `inert` attribute to remove background content from tab + AT order. For collapsed content you still want discoverable, prefer `hidden="until-found"` (it fires `beforematch` and auto-expands on browser find-in-page) over `display:none`.

| WCAG 2.2 SC | What it requires | Markup/CSS hook |
|-------------|------------------|-----------------|
| 2.5.8 Target Size (Min) | Interactive targets ≥ 24×24 CSS px | adequate padding / `min-height` |
| 2.4.11 Focus Not Obscured | Focused element not fully hidden by sticky UI | `scroll-margin`, layout audit |
| 2.5.7 Dragging Movements | A non-drag alternative for any drag action | add buttons/inputs |
| 3.3.8 Accessible Authentication | No cognitive test (e.g. transcription puzzle) | passkeys, `autocomplete="one-time-code"` |
| 1.4.13 Content on Hover/Focus | Dismissible, hoverable, persistent | prefer `popover` |

```html
<dialog id="settings" aria-labelledby="st">
  <h2 id="st">Settings</h2>
  …
</dialog>
<main inert><!-- inert while a modal dialog is open --></main>

<!-- Find-in-page–discoverable FAQ answer -->
<details>
  <summary>Refund policy</summary>
  <p hidden="until-found">Full refunds within 30 days…</p>
</details>
```

### 7. SEO & metadata

Unique `<title>` + meta description per page, one canonical, Open Graph for sharing, and JSON-LD structured data for rich results.

```html
<link rel="canonical" href="https://example.com/article/x">
<meta name="description" content="…">
<meta property="og:title" content="…">
<meta property="og:image" content="https://example.com/og.png">
<script type="application/ld+json">
{ "@context":"https://schema.org","@type":"Article",
  "headline":"…","datePublished":"2026-01-15",
  "author":{"@type":"Person","name":"…"} }
</script>
```

### 8. Loading performance

Prioritize the LCP image; defer everything below the fold. `fetchpriority` ranks competing resources; `loading="lazy"` defers offscreen images and iframes. Serve the right pixels with `srcset` width descriptors + `sizes`.

```html
<link rel="preconnect" href="https://cdn.example.com" crossorigin>
<link rel="preload" as="image" href="/hero.avif" fetchpriority="high">

<!-- LCP image: eager + high priority, never lazy -->
<img src="/hero.avif" alt="" width="1280" height="720"
     fetchpriority="high" decoding="async">

<!-- Below the fold: responsive widths + lazy -->
<img src="/feature-800.avif" alt="…"
     srcset="/feature-400.avif 400w, /feature-800.avif 800w, /feature-1600.avif 1600w"
     sizes="(width >= 48rem) 50vw, 100vw"
     width="800" height="600" loading="lazy" decoding="async">

<picture>
  <source type="image/avif" srcset="/p.avif">
  <source type="image/webp" srcset="/p.webp">
  <img src="/p.jpg" alt="…" width="640" height="480"
       loading="lazy" decoding="async">
</picture>

<!-- Prerender likely-next pages (progressive enhancement) -->
<script type="speculationrules">
{ "prerender": [{ "where": { "href_matches": "/article/*" }, "eagerness": "moderate" }] }
</script>
```

> **HARD RULE:** Never set `loading="lazy"` on the LCP/hero image — it delays the paint the metric measures and *hurts* LCP. Lazy-load only below-the-fold media.

> **NOTE:** Speculation Rules (prerender/prefetch) are Chromium-only as of 2026. Treat them as an enhancement — pages must work identically without them, and over-eager prerendering wastes bandwidth and can fire analytics early.

### 9. Visual stability (CLS)

Always declare intrinsic `width`/`height` (or `aspect-ratio`) so the browser reserves space before the asset loads. Reserve space for ads, embeds, and async-injected banners; avoid inserting content above existing content.

```html
<img src="/thumb.avif" alt="" width="400" height="225"> <!-- 16:9 reserved -->
<div class="ad-slot" style="aspect-ratio:300/250"></div> <!-- reserved before fill -->
```

Use `font-display: swap` with a metric-matched fallback to avoid layout shift on web-font load.

### 10. Security baseline

Markup-level safety that belongs in the HTML itself, not only in server config.

| Risk | HTML mitigation |
|------|-----------------|
| Reverse tabnabbing / referrer leak | `rel="noopener noreferrer"` on `target="_blank"` links |
| Tampered third-party script/style | Subresource Integrity: `integrity="sha384-…" crossorigin="anonymous"` |
| Inline-script injection (XSS) | Ship a CSP — prefer an HTTP header; `<meta http-equiv="Content-Security-Policy">` as a fallback |
| Bare-specifier hijack | Pin exact versions in `<script type="importmap">` |
| Clickjacking | `frame-ancestors` in CSP (a `<meta>` CSP **cannot** set this) |

```html
<a href="https://other.example" target="_blank" rel="noopener noreferrer">Docs</a>

<script src="https://cdn.example.com/lib.js"
        integrity="sha384-…" crossorigin="anonymous"></script>

<script type="importmap">
{ "imports": { "lit": "https://cdn.example.com/lit@3.2.1/index.js" } }
</script>
```

> **HARD RULE:** A `<meta>` CSP is strictly weaker than the header form: `frame-ancestors`, `report-to`/`report-uri`, and sandbox directives only work as a real HTTP response header. Use meta CSP only as a defense-in-depth fallback.

## Pitfalls

### Anti-patterns to reject on review

| Anti-pattern | Why it hurts | Do instead |
|--------------|--------------|------------|
| `<div onclick>` as a button | No keyboard, no role, no focus | `<button>` |
| Image with no `width`/`height` | Layout shift → CLS spike | declare dimensions / `aspect-ratio` |
| `loading="lazy"` on hero | Delays LCP | eager + `fetchpriority="high"` |
| `role="button"` on a `<button>` | Redundant ARIA | drop it |
| Multiple `<h1>` / skipped levels | Breaks AT outline + SEO | one `<h1>`, ordered headings |
| Placeholder used as label | Vanishes on input, low contrast | real `<label for>` |
| `target="_blank"` with no `rel` | Reverse-tabnabbing + referrer leak | `rel="noopener noreferrer"` |
| Missing `<html lang>` | Wrong AT pronunciation/hyphenation | set `lang` (and `dir`) |
| JS-toggled FAQ/accordion | Not find-in-page discoverable | `<details>` or `hidden="until-found"` |

### Gotchas

1. **Declarative shadow DOM is parser-only:** `innerHTML` won't process `shadowrootmode`; use `setHTMLUnsafe()` for runtime injection.
2. **`<dialog>` needs `showModal()`** (or `command="show-modal"`), not `show()`/`open`, to get the backdrop, focus trap, and Esc-to-close.
3. **`popover` ≠ `dialog`:** popovers are non-modal and don't trap focus — wrong choice for destructive confirmations.
4. **`autocomplete="off"` is widely ignored** by password managers; use a specific token instead of fighting them.
5. **`hidden="until-found"` won't be found if CSS also sets `display:none`** — let the UA manage its content-visibility; only the `until-found` value is find-in-page-discoverable.
6. **`alt=""` is correct for decorative images** — an empty alt removes it from the AT tree; omitting `alt` entirely makes screen readers announce the filename.
7. **Customizable `<select>`** (`appearance: base-select` + `<selectedcontent>` and rich `<option>` markup) is rolling out but **not universal in 2026** — it degrades to a native select, so treat content projection inside options as progressive enhancement, never a hard dependency.
8. **`<meta>` CSP is limited:** `frame-ancestors`, reporting, and sandbox directives require a real HTTP header — don't assume meta-only CSP is equivalent.

## Verification

When reviewing or auditing HTML output, check each item below:

### Document scaffold
- [ ] `<meta charset="utf-8">` is the first child of `<head>` and within the first 1024 bytes.
- [ ] `<html lang>` is set (and `dir` for RTL locales).
- [ ] `viewport-fit=cover` is present in the viewport meta.
- [ ] `color-scheme` meta is set to `light dark` or a single scheme.

### Semantics & accessibility
- [ ] Exactly one `<main>`, one `<h1>`, no skipped heading levels.
- [ ] Skip link is the first focusable element and targets `#main`.
- [ ] Every interactive element is a native `<button>`, `<a>`, or `<input>` — no `<div onclick>`.
- [ ] `aria-labelledby` or `aria-label` is used only where a native label is impossible.
- [ ] `inert` is applied to background content when a modal `<dialog>` is open.
- [ ] All form fields have a `<label for>` (or `<legend>` inside `<fieldset>`); no placeholder-as-label.
- [ ] Interactive targets meet ≥ 24×24 CSS px (WCAG 2.2 SC 2.5.8).

### Performance & stability
- [ ] LCP/hero image has `fetchpriority="high"` and is **not** lazy-loaded.
- [ ] All `<img>` tags declare `width` and `height` (or `aspect-ratio` via CSS).
- [ ] Below-the-fold images use `loading="lazy"` and `decoding="async"`.
- [ ] `srcset` uses width descriptors with a matching `sizes` attribute.
- [ ] Ad slots and async-injected containers have reserved dimensions.

### Security
- [ ] Every `target="_blank"` link has `rel="noopener noreferrer"`.
- [ ] Third-party `<script>`/`<link>` tags have `integrity` and `crossorigin="anonymous"`.
- [ ] `importmap` pins exact versions (no bare specifiers without a mapping).
- [ ] CSP is delivered via HTTP header (not meta-only) if `frame-ancestors` or reporting is needed.

### Quick automated checks (PowerShell on Windows host)

```powershell
# Check for lazy-loaded hero images (should return nothing)
Select-String -Path .\index.html -Pattern '<img[^>]*loading="lazy"[^>]*(hero|banner)' -AllMatches

# Check for target=_blank without rel=noopener
Select-String -Path .\index.html -Pattern 'target="_blank"(?!.*rel="noopener)' -AllMatches

# Check for images missing width/height
Select-String -Path .\index.html -Pattern '<img(?![^>]*(width|height))[^>]*>' -AllMatches

# Check for missing html lang
Select-String -Path .\index.html -Pattern '<html(?!.*lang=)' -AllMatches

# Check for div onclick (should use <button>)
Select-String -Path .\index.html -Pattern '<div[^>]*onclick=' -AllMatches
```

Each command should return no matches on clean HTML. If matches appear, fix the markup before shipping.

## Related skills

- `modern-css` — styling, layouts, and visual design
- `web-interface-guidelines` — general UI checklists and visual stability reference
- `development` — frontend/backend workflows
- `security-audit` — checking for XSS and HTML injections
