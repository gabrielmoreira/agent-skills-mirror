---
name: web-vitals-analyzer
description: "Diagnoses Core Web Vitals failures (LCP, CLS, INP) from Lighthouse JSON or PageSpeed traces into ranked file-and-line root causes with expected metric deltas. Use when a Lighthouse score, LCP/CLS/INP number, layout shift, laggy click, or bundle-size complaint needs RCA. Not a CI budget gate (frontend-lighthouse) and not the markup-remediation implementer (performance-and-web-vitals)."
version: 1.0.1
---

# Web Vitals Analyzer

Diagnoses Core Web Vitals failures and frontend performance issues by analyzing page structure, resource loading patterns, JavaScript bundle composition, and rendering behavior. Produces prioritized fixes with estimated metric improvements.

## When to Use

- User asks to optimize frontend performance or Core Web Vitals (LCP, CLS, INP).
- User shares a Lighthouse report (JSON or screenshot) and wants root-cause analysis.
- User reports slow page load, layout shift, or laggy interactions.
- User asks to reduce JavaScript bundle size or identify render-blocking resources.
- User mentions specific metrics: "LCP is 5s", "CLS is 0.25", "INP is 600ms".
- User asks for quick wins to improve Lighthouse performance score.

Trigger keywords: Core Web Vitals, LCP, CLS, INP, Lighthouse, PageSpeed, performance score, render-blocking, bundle size, lazy loading, layout shift, main thread, long tasks, code splitting, TTFB, first paint.

## Prerequisites

- A Lighthouse report (JSON preferred), PageSpeed Insights URL, or Chrome DevOps performance trace if available.
- The page URL or source code (HTML, CSS, JS entry points).
- Framework identification (React, Next.js, Vue, Nuxt, SvelteKit, vanilla, etc.).
- Current metric values if known (LCP, CLS, INP, TTFB, total bundle size).

If any of these are missing, ask for them before proceeding. Do not give generic advice without knowing what is actually slow.

## Procedure

### 1. Gather Current State

Ask for or analyze:
- Lighthouse report (JSON or screenshot)
- The page URL or source code (HTML, CSS, JS entry points)
- Framework used (React, Next.js, Vue, vanilla, etc.)
- Current LCP, CLS, and INP values if available

### 2. Analyze Largest Contentful Paint (LCP) — target < 2.5s

Identify the LCP element (usually hero image, heading, or above-fold content), then check each item:

1. **Is the LCP image lazy-loaded?** It should NOT be. Remove `loading="lazy"` from above-fold hero images.
2. **Is there a `<link rel="preload">` for the LCP resource?** If not, add one:
   ```html
   <link rel="preload" as="image" href="/hero.jpg" fetchpriority="high">
   ```
3. **Are render-blocking CSS/JS delaying first paint?** Inline critical CSS; defer non-critical stylesheets.
4. **Server response time (TTFB):** If > 800ms, flag as a server-side issue (CDN, caching, SSR optimization).
5. **Font loading strategy:** Is `font-display: swap` or `optional` used? If not, add it.
6. **Critical CSS:** Is it inlined in `<head>` or loaded as a blocking stylesheet? Inline above-fold critical CSS.

### 3. Analyze Cumulative Layout Shift (CLS) — target < 0.1

Identify elements causing layout shifts (images without dimensions, dynamic content, ads, web fonts), then check:

1. **Do all `<img>` and `<video>` tags have explicit `width` and `height`?** If not, add them.
2. **Is content injected above existing content after load?** Reserve space with fixed-height containers.
3. **Are web fonts causing FOUT/FOIT shifts?** Use `font-display: swap` and `size-adjust` to match fallback metrics.
4. **Are dynamic ads or embeds reserving space?** Use `aspect-ratio` or fixed container dimensions:
   ```css
   .ad-slot { aspect-ratio: 728 / 90; min-height: 90px; }
   ```

### 4. Analyze Interaction to Next Paint (INP) — target < 200ms

Identify heavy JavaScript on the main thread, then check:

1. **Are event handlers doing synchronous layout thrashing?** Batch DOM reads and writes separately.
2. **Long tasks (> 50ms) blocking the main thread?** Break them up with `scheduler.yield()` or `setTimeout`.
3. **Unnecessary re-rendering?** For React: check missing `useMemo`, `React.memo()`, excessive state updates. For Vue: check reactive dependencies. For Svelte: check unnecessary store subscriptions.
4. **Third-party scripts blocking interaction?** (analytics, chat widgets, A/B testing). Load with `async`/`defer`; move tracking to `requestIdleCallback`:
   ```javascript
   document.addEventListener('click', (e) => {
     requestIdleCallback(() => trackClick(e));
   });
   ```
5. **Suggest offloading:** `requestIdleCallback`, `scheduler.yield()`, web workers for heavy computation.

### 5. Analyze Bundle and Resource Loading

1. Identify total JS bundle size and largest chunks.
2. Check for unused JavaScript (Chrome DevTools Coverage tab).
3. Suggest code splitting opportunities (route-based, component-based, dynamic `import()`).
4. Check image formats: suggest WebP/AVIF for photos, SVG for icons. Note: AVIF has better compression but slower decode — WebP is the safer default.
5. Identify duplicate dependencies in the bundle (check `package-lock.json` or `npm ls`).
6. Verify text compression (gzip/brotli) is enabled on the server.

### 6. Output Format

Produce a structured diagnosis:

```
Core Web Vitals Diagnosis
==========================
LCP: [current] (target: < 2.5s)
CLS: [current] (target: < 0.1)
INP: [current] (target: < 200ms)

Root Causes (ranked by impact):

1. [SEVERITY]: [Description]
   File: [exact file and line]
   Fix: [specific code change]
   Expected improvement: [-Xs / -Xms]

2. ...

Quick wins (< 15 min each):
- [Actionable item]
- [Actionable item]
```

Severity levels: CRITICAL, HIGH, MODERATE, LOW.

## Examples

### Example 1: Poor LCP on a marketing site

**Input:**
```
Our landing page scores 38 on Lighthouse performance. LCP is 5.2s. Here's the page source.
```

**Output:**
```
Core Web Vitals Diagnosis
==========================
LCP: 5.2s (target: < 2.5s)
CLS: 0.03 (target: < 0.1)
INP: N/A (no interaction data)

Root Causes (ranked by impact):

1. CRITICAL: Hero image (2.4MB JPEG) is lazy-loaded
   File: src/components/Hero.tsx:12
   Fix: Remove loading="lazy" from the above-fold hero image.
   Add: <link rel="preload" as="image" href="/hero.jpg" fetchpriority="high">
   Convert to WebP: reduces 2.4MB → 340KB
   Expected LCP improvement: -2.1s

2. HIGH: 3 render-blocking CSS files (total 180KB uncompressed)
   Files: fonts.css (89KB), animations.css (52KB), above-fold.css (39KB)
   Fix: Inline critical CSS (above-fold.css) in <head>.
   Load fonts.css and animations.css with media="print" onload hack.
   Expected LCP improvement: -0.8s

3. MODERATE: Google Fonts loaded via @import in CSS (parser-blocking)
   Fix: Switch to <link rel="preconnect" href="https://fonts.gstatic.com">
   and <link rel="stylesheet" href="fonts-url"> in HTML <head>
   Expected LCP improvement: -0.3s

Quick wins (< 15 min each):
- Add fetchpriority="high" to hero image tag
- Add width/height to hero image (already good CLS, but defensive)
- Enable text compression (gzip/brotli) on server — saves 60% on CSS
```

### Example 2: High INP on a React dashboard

**Input:**
```
Our dashboard app has INP of 890ms. Users complain clicks feel laggy. It's a React 18 app with Zustand state management.
```

**Output:**
```
INP Diagnosis: 890ms (target: < 200ms)

Root Causes:

1. CRITICAL: Filter dropdown triggers full data grid re-render (45,000 rows)
   File: src/components/DataGrid.tsx
   The grid component re-renders on every filter change because the parent
   passes a new array reference each time.
   Fix: Memoize the filtered data with useMemo:
     const filteredData = useMemo(() => data.filter(filterFn), [data, filters]);
   Wrap DataGrid in React.memo().
   Expected INP improvement: -500ms

2. HIGH: Analytics script (third-party) runs 180ms synchronous task on click
   Source: analytics.min.js:1 event listener on document.body
   Fix: Load analytics with async/defer. Move tracking to requestIdleCallback:
     document.addEventListener('click', (e) => {
       requestIdleCallback(() => trackClick(e));
     });
   Expected INP improvement: -180ms

3. MODERATE: Date formatting in table cells using Intl.DateTimeFormat per-render
   Fix: Create formatter once outside component:
     const fmt = new Intl.DateTimeFormat('en-US', { dateStyle: 'medium' });
   Expected INP improvement: -80ms
```

## Pitfalls

- **Never give generic advice without identifying the specific LCP element.** Always pinpoint what is actually slow.
- **CLS fixes must include explicit code changes** — dimensions, `aspect-ratio` values, container styles. Do not say "add dimensions" without specifying the values.
- **For INP, focus on the main thread.** Network latency does not directly affect INP.
- **Recommend `fetchpriority="high"` only for the single most important above-fold resource.** Adding it to multiple elements defeats the purpose.
- **AVIF has better compression but slower decode.** WebP is the safer default for broad compatibility.
- **Do not recommend service workers for performance** unless the use case specifically involves repeat visits.
- **Account for framework-specific patterns:** Next.js Image component, Nuxt's `useAsyncData`, SvelteKit's load functions. Do not give vanilla JS advice for a framework app.
- **Do not remove `loading="lazy"` from below-fold images** — only the LCP element and above-fold content.
- **`font-display: optional` causes fonts to not render at all on slow connections.** Use `swap` for body text, `optional` only for non-critical decorative fonts.
- **`media="print" onload` CSS hack can cause FOUC.** Test visually after applying.

## Verification

After implementing fixes, verify with:

1. **Re-run Lighthouse** and confirm the performance score improved:
   ```bash
   npx lighthouse https://your-site.com --output=json --output-path=./lighthouse-after.json --preset=desktop
   ```
   Compare `lighthouse-after.json` to the before report.

2. **Check Core Web Vitals field data** via PageSpeed Insights:
   ```
   https://pagespeed.web.dev/analysis?url=https://your-site.com
   ```

3. **Verify LCP element changed** in Chrome DevTools:
   - Open DevTools → Performance tab
   - Record a page load
   - Check "Largest Contentful Paint" marker identifies the correct (optimized) element

4. **Verify no new layout shifts:**
   - Open DevTools → Performance → Record page load
   - Check "Layout Shift" entries — CLS should be < 0.1

5. **Verify INP improvement:**
   - Open DevTools → Performance → Record interaction
   - Check total blocking time and long tasks (> 50ms) are reduced

6. **Verify bundle size reduction:**
   ```bash
   # Next.js
   npx @next/bundle-analyzer

   # Webpack
   npx webpack-bundle-analyzer dist/stats.json

   # Vite
   npx vite-bundle-visualizer
   ```

7. **Verify image format conversion:**
   ```bash
   # Check file sizes
   ls -lh public/images/hero.webp public/images/hero.jpg
   ```

## Related Skills

- **frontend-design-system**: For component-level accessibility, design tokens, and UI state coverage.
- **accessibility-audit**: For WCAG 2.2 compliance checks that overlap with performance (focus management, reduced motion).

## References

- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- W3C Understanding WCAG 2.2: https://www.w3.org/WAI/WCAG22/Understanding/intro
- Apple Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines
- Material accessibility guidance: https://m2.material.io/design/usability/accessibility.html
- Google Search Central documentation: https://developers.google.com/search/docs

Re-check official/current docs before relying on provider-specific APIs, policy, pricing, security behavior, or platform rules.
