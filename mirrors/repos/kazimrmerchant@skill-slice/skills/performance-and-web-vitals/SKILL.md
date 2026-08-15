---
name: performance-and-web-vitals
description: "Remediates Core Web Vitals in page assets and markup: LCP preload and fetchpriority, CLS width/height, INP main-thread splits, WebP/AVIF, and font-display. Use for LCP above 2.5s, CLS above 0.1, or INP above 200ms in the site itself. Never substitute web-vitals-analyzer (report RCA) or frontend-lighthouse (CI budget gates)."
version: 1.0.1
---

# Performance and Web Vitals

## When to Use

Use this skill when:
- Auditing UI performance with Lighthouse (CLI or DevTools)
- Fixing Core Web Vitals: LCP > 2.5s, CLS > 0.1, INP > 200ms
- Optimising page load, images, fonts, or render-blocking resources
- Setting up Lighthouse CI to catch performance regressions
- Reviewing frontend code for main-thread blocking, layout shift, or slow interactions

Trigger keywords: Lighthouse, LCP, CLS, INP, Core Web Vitals, page speed, performance audit, layout shift, input delay, render-blocking, preload, lazy load, font-display, WebP, AVIF.

## Prerequisites

- Node.js 18+ and npm available on PATH
- Chrome/Chromium installed (Lighthouse launches it automatically)
- PowerShell as primary shell on Windows host
- Project must be servable via a URL (local dev server or deployed site)

## Procedure

### 1. Run a Lighthouse Audit

```powershell
# CLI audit outputs HTML report
npx lighthouse https://example.com --output html --output-path ./lighthouse-report.html

# Headless, useful in CI
npx lighthouse https://example.com --chrome-flags="--headless" --output json --output-path ./report.json

# Audit specific categories only
npx lighthouse https://example.com --only-categories=performance,accessibility,seo
```

Alternatively, open Chrome DevTools > Lighthouse tab > Analyse page load.

**Target scores:**

| Category | Target |
|---|---|
| Performance | 90+ |
| Accessibility | 100 |
| Best Practices | 95+ |
| SEO | 95+ |

### 2. Fix LCP (Largest Contentful Paint) — Target: 2.5s

LCP measures when the largest visible element (hero image, heading, video poster) renders. This is the user's perception of "did the page load?"

| Cause | Fix |
|---|---|
| Unoptimised hero image | Use WebP/AVIF, correct size, `fetchpriority="high"` |
| Image not preloaded | `<link rel="preload" as="image" href="hero.webp">` |
| Render-blocking CSS/JS | Defer non-critical JS, inline critical CSS |
| Slow server response | CDN, caching headers, edge delivery |
| Web font blocking render | `font-display: swap` or `optional` |

```html
<!-- Preload LCP image -->
<link rel="preload" as="image" href="hero.webp" fetchpriority="high">

<!-- LCP image: no lazy loading -->
<img src="hero.webp" alt="..." fetchpriority="high" width="1200" height="600">
```

**HARD RULE:** Never use `loading="lazy"` on the LCP image — it delays the most important render.

### 3. Fix CLS (Cumulative Layout Shift) — Target: 0.1

CLS measures unexpected layout shifts — content moving after it has rendered.

| Cause | Fix |
|---|---|
| Images without width/height | Always set `width` and `height` on `<img>` |
| Web font swap | Use `font-display: optional` or preload fonts |
| Dynamic content above fold | Reserve space with `min-height` on containers |
| Late-loading ads or embeds | Reserve fixed dimensions for ad slots |
| Animations that shift layout | Animate `transform` only, never `top/left/width/height` |

```html
<!-- Always include dimensions -->
<img src="product.jpg" width="400" height="300" alt="...">
```

```css
/* Reserve space for dynamic content */
.ad-slot { min-height: 250px; }

/* Animate transform, not layout properties */
.slide-in { transform: translateY(0); transition: transform 300ms; }
```

### 4. Fix INP (Interaction to Next Paint) — Target: 200ms

INP measures the delay between a user interaction (click, tap, keyboard) and the next visual update. High INP makes the UI feel sluggish.

| Cause | Fix |
|---|---|
| Heavy JS on main thread | Break into smaller tasks, use `requestIdleCallback` |
| Large event handlers | Debounce/throttle scroll and resize handlers |
| Synchronous DOM updates | Batch DOM writes with `requestAnimationFrame` |
| Third-party scripts blocking | Load third-party scripts with `async` or `defer` |
| React re-renders | Memoize with `useMemo`, `useCallback`, `React.memo` |

### 5. Optimise Images

Images are the single biggest performance lever on most pages.

```html
<!-- Modern formats with fallback -->
<picture>
  <source srcset="image.avif" type="image/avif">
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" width="800" height="600" alt="..." loading="lazy">
</picture>

<!-- Responsive images -->
<img
  srcset="image-400.webp 400w, image-800.webp 800w, image-1200.webp 1200w"
  sizes="(max-width: 600px) 100vw, 50vw"
  src="image-800.webp"
  alt="..."
  width="800"
  height="600"
  loading="lazy"
>
```

**Rules:**
- Always set `width` and `height` — prevents CLS
- Use `loading="lazy"` below the fold, **never** on LCP image
- Serve WebP or AVIF — typically 30–50% smaller than JPEG
- Size images to their display size — do not serve a 2000px image for a 400px slot
- Use a CDN with automatic format conversion where possible

### 6. Optimise Fonts

Web fonts block rendering if not handled correctly.

```html
<!-- Preconnect to font origin -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<!-- Preload critical font file -->
<link rel="preload" href="/fonts/brand.woff2" as="font" type="font/woff2" crossorigin>
```

```css
@font-face {
  font-family: 'Brand';
  src: url('/fonts/brand.woff2') format('woff2');
  font-display: swap; /* show fallback immediately, swap when loaded */
  /* font-display: optional; never swap, use fallback if not cached */
}
```

- `font-display: swap` — good for headings, acceptable CLS
- `font-display: optional` — zero CLS, font only used if cached (best for body text)
- Subset fonts to the characters actually used — reduces file size by 60–80%

### 7. Optimise JavaScript Loading

```html
<!-- Defer non-critical scripts -->
<script src="analytics.js" defer></script>
<script src="chat-widget.js" async></script>

<!-- Module scripts are deferred by default -->
<script type="module" src="app.js"></script>
```

- `defer`: executes after HTML parsed, in order — use for most scripts
- `async`: executes as soon as downloaded, out of order — use for independent scripts (analytics)
- **Never** block the main thread with synchronous `<script>` in `<head>`

### 8. Set Up Lighthouse CI for Automated Audits

```powershell
# Install
npm install -g @lhci/cli

# Run
lhci autorun --upload.target=temporary-public-storage
```

```json
// .lighthouserc.json
{
  "ci": {
    "assert": {
      "assertions": {
        "categories:performance": ["warn", { "minScore": 0.9 }],
        "categories:accessibility": ["error", { "minScore": 1.0 }],
        "categories:seo": ["warn", { "minScore": 0.95 }]
      }
    }
  }
}
```

## Pitfalls

- **LCP image with `loading="lazy"`**: This is the most common LCP regression. Never lazy-load the hero or largest visible element.
- **Missing `width`/`height` on images**: Browser cannot reserve space, causing CLS spikes even with fast-loading images.
- **Animating layout properties**: Animating `top`, `left`, `width`, or `height` triggers reflow and layout shift. Always animate `transform` and `opacity` instead.
- **Synchronous `<script>` in `<head>`**: Blocks HTML parsing and delays first paint entirely.
- **`font-display: swap` on body text**: Causes visible CLS from font metric differences. Use `font-display: optional` for body text where zero shift matters.
- **Serving oversized images**: A 2000px image in a 400px slot wastes bandwidth and decode time. Always match display size.
- **Third-party scripts without `async`/`defer`**: Analytics, chat widgets, and ad scripts can block the main thread and inflate INP.
- **Heavy scroll/resize handlers without throttling**: Fire on every frame, blocking the main thread and degrading INP.
- **React re-renders from unstable references**: Missing `useMemo`/`useCallback`/`React.memo` causes unnecessary re-renders on every interaction.

## Verification

Run through this checklist after applying fixes:

- [ ] Lighthouse performance score ≥ 90
- [ ] Lighthouse accessibility score = 100
- [ ] LCP ≤ 2.5s — LCP image preloaded, no `loading="lazy"` on it
- [ ] CLS ≤ 0.1 — all images have `width` and `height`, no layout-shifting animations
- [ ] INP ≤ 200ms — no heavy synchronous JS on main thread
- [ ] Images served as WebP or AVIF with correct dimensions
- [ ] `loading="lazy"` on all below-fold images
- [ ] Web fonts use `font-display: swap` or `optional`
- [ ] Non-critical JS loaded with `defer` or `async`
- [ ] Lighthouse CI configured to catch regressions in deployment pipeline

**Re-run the audit to confirm:**

```powershell
npx lighthouse https://example.com --only-categories=performance --output json --output-path ./verify-report.json
```

Check that `categories.performance.score` in the JSON output is ≥ 0.9 and that LCP, CLS, and INP metrics in `audits` meet their targets.

## Related Skills

- **ui-ux-design**: For interface design, accessibility, responsive layouts, and design-system work
- **accessibility-wcag**: For WCAG 2.2 compliance checks and semantic structure

## References

- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- W3C Understanding WCAG 2.2: https://www.w3.org/WAI/WCAG22/Understanding/intro
- Apple Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines
- Material Design: https://m3.material.io/
- Material accessibility guidance: https://m2.material.io/design/usability/accessibility.html
- Lighthouse CI documentation: https://github.com/GoogleChrome/lighthouse-ci
