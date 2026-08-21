---
name: web-interface-guidelines
version: 1.1.1
description: "Applies Vercel web interface guidelines: accessibility, CLS/visual stability, performance, forms, and reduced-motion. Use when reviewing or building UI markup, styles, or animation for a11y/performance/visual-stability compliance. Not for React/Next scaffolding or bundle scripts (senior-frontend). Not a motion-taste chair (emil-design-eng)."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-14
---

# Web Interface Guidelines

Review and enforce Vercel's web interface standards across UI code—accessibility, performance, visual stability, animation, forms, and content handling.

## When to Use

- Building or reviewing any web UI component (React, Vue, plain HTML/CSS).
- Auditing markup, styles, or JavaScript logic for accessibility or performance regressions.
- Adding images, fonts, lists, forms, or animations to a web interface.
- Triggered by keywords: UI review, accessibility audit, CLS, focus state, reduced motion, form input, virtualization, image dimensions, font preload.

## Do Not Use

- Non-web platforms (native mobile, desktop apps).
- Legacy codebases where these guidelines require a full migration plan—prioritize critical security and accessibility fixes first, then adopt incrementally.
- Enforcing arbitrary stylistic preferences that do not impact performance, accessibility, or visual stability.

## Prerequisites

- Familiarity with the target framework (React, Vue, Next.js, etc.).
- Access to browser DevTools (Lighthouse, Network, Performance tabs).
- Optional linting tools: `eslint-plugin-jsx-a11y`, Stylelint, Lighthouse CI, Axe Core.

## Procedure

1. **Scan component markup** for image, form, and semantic HTML rules (see Quick Reference below).
2. **Scan styles** for focus states, animation properties, and content handling rules.
3. **Scan JavaScript logic** for layout reads in render, virtualization needs, and re-render optimization.
4. **Flag violations** and suggest the appropriate fix, referencing the specific guideline.
5. **Run automated tooling** to catch common issues:
   - `npx eslint --ext .js,.jsx,.ts,.tsx .` with `eslint-plugin-jsx-a11y` enabled.
   - `npx lighthouse http://localhost:3000 --only-categories=accessibility,performance` for key pages.
   - Axe Core browser extension or `@axe-core/cli` for deeper accessibility audits.
6. **Document intentional deviations** with a justification comment in the code explaining trade-offs or context.

### Quick Reference — Visual Stability

| Issue | Rule |
|-------|------|
| Images without dimensions | `<img>` needs explicit `width` and `height` (prevents CLS) |
| Font loading flash | Critical fonts: `<link rel="preload" as="font" crossorigin>` with `font-display: swap` |
| Large lists | Virtualize lists >50 items (`react-virtual`, `vue-virtual-scroller`, `content-visibility: auto`) |
| Layout reads in render | No `getBoundingClientRect`, `offsetHeight` in render path; use `requestAnimationFrame` for DOM reads/writes |

### Full Rules

#### Images

- `<img>` needs explicit `width` and `height` attributes or CSS `aspect-ratio` (prevents CLS). Use `aspect-ratio` for responsive images.
- Below-fold images: `loading="lazy"`.
- Above-fold critical images: `fetchpriority="high"` or `priority` attribute (Next.js Image component).
- Use modern formats (WebP, AVIF) with `<picture>` and `<source>`.
- Ensure `srcset` and `sizes` are correctly used for responsive delivery.

#### Performance

- Large lists (>50 items): virtualize with `@tanstack/react-virtual`, `vue-virtual-scroller`, or `content-visibility: auto` for non-interactive sections.
- No layout reads in render (`getBoundingClientRect`, `offsetHeight`, `offsetWidth`, `scrollTop`, `scrollWidth`, `scrollHeight`). Batch DOM reads/writes via `requestAnimationFrame` or `IntersectionObserver`.
- Add `<link rel="preconnect">` for CDN/asset domains; `<link rel="dns-prefetch">` for older browsers.
- Critical fonts: `<link rel="preload" as="font" type="font/woff2" crossorigin>` with `font-display: swap` or `optional`. Use WOFF2.
- Minimize JS bundle: tree-shaking, code-splitting (dynamic imports), ESM.
- Optimize CSS: inline critical CSS, lazy-load non-critical. Prefer CSS-in-JS with atomic CSS or static extraction.
- Avoid excessive re-renders: `React.memo`, `useMemo`, `useCallback`, or Vue reactivity transforms.

#### Accessibility

- Icon-only buttons need `aria-label` or visually hidden text.
- Form controls need `<label>` via `htmlFor` or `aria-labelledby`, or `aria-label` for standalone controls.
- Interactive elements need keyboard handlers (`onKeyDown`/`onKeyUp`); ensure `Tab`, `Enter`, `Space` work.
- Use native elements: `<button>` for actions, `<a>`/`<Link>` for navigation. Avoid `<div>`/`<span>` with `onClick`; if unavoidable, add `role="button"` and keyboard handlers.
- Images need meaningful `alt` (or `alt=""` if decorative). Complex images: `aria-describedby` pointing to longer description.
- Ensure color contrast (WCAG 2.1 AA or AAA).
- Provide clear focus indicators for all interactive elements.
- Use semantic HTML5 (`<nav>`, `<main>`, `<aside>`, `<article>`, `<section>`, `<footer>`, `<header>`).
- Implement ARIA live regions (`aria-live="polite"`) for dynamic content updates.

#### Focus States

- Interactive elements need visible focus: `focus-visible:ring-*`, `focus-visible:outline-*`, or equivalent.
- Never use `outline-none` / `outline: none` without a clear, accessible focus indicator replacement.
- Use `:focus-visible` over `:focus` to prevent focus rings on click interactions.
- Ensure focus order follows visual order.

#### Animation

- Honor `prefers-reduced-motion` (e.g., `useReducedMotion` from `framer-motion`). Provide reduced motion variant or disable animations.
- Animate only `transform` (`translate`, `scale`, `rotate`) and `opacity`—compositor-friendly. Avoid animating `width`, `height`, `margin`, `padding`, `top`, `left`.
- Never use `transition: all`—list properties explicitly.
- Use `will-change` judiciously; remove when animation completes to avoid memory overhead.
- For complex animations: `Framer Motion`, `React Spring`, or `GSAP`.

#### Forms

- Inputs need `autocomplete` attributes (e.g., `autocomplete="email"`, `autocomplete="current-password"`).
- Use meaningful `name` attributes.
- Use correct `type` (`email`, `tel`, `url`, `number`, `date`, `time`, `search`) and `inputmode` (e.g., `inputmode="numeric"`) for mobile keyboards.
- Never block paste (`onPaste` + `preventDefault`) unless critical security reason; provide clear feedback if blocked.
- Labels must be clickable and associated via `htmlFor` or by wrapping the control.
- Implement client-side and server-side validation with clear error messages. Use `aria-invalid` and `aria-describedby`.

#### Content Handling

- Text containers handle long content: `text-overflow: ellipsis` + `overflow: hidden` + `white-space: nowrap` for single lines; `line-clamp-*` for multi-line; `word-break: break-word` / `overflow-wrap: break-word` for wrapping.
- Flex children need `min-w-0` (or `min-width: 0`) to allow truncation within flex containers.
- Handle empty states gracefully—no broken UI for empty strings/arrays. Provide "no data" messages or placeholders.
- Use responsive typography: `clamp()`, `rem` units, media queries.

## Pitfalls

- **`user-scalable=no` or `maximum-scale=1`** in viewport meta—critical accessibility violation. Always flag.
- **`transition: all`** without explicit property listing—causes unintended performance issues.
- **`outline-none` / `outline: none`** without `:focus-visible` replacement—removes keyboard accessibility.
- **Images without `width`/`height` or `aspect-ratio`**—causes CLS.
- **Large arrays `.map()` without virtualization** for lists >~50 items—performance degradation.
- **Form inputs without `<label>` or `aria-label`**—accessibility failure.
- **Icon buttons without `aria-label`**—unusable by screen readers.
- **`<div>`/`<span>` with `onClick`** instead of `<button>`/`<a>`—missing keyboard support and semantics.
- **Inline styles for critical layout** that should be CSS classes—maintainability and performance issues.
- **Excessive `!important`** in CSS—specificity wars and maintainability issues.
- **Blocking main thread** with long-running JS—use `requestIdleCallback` or Web Workers.
- **Animating layout properties** (`width`, `height`, `margin`, `padding`, `top`, `left`)—triggers layout and paint thrashing.

## Examples

```tsx
// Correct image usage with modern attributes and aspect-ratio
<img
  src="/hero.webp"
  alt="A vibrant sunset over a calm ocean"
  width={1920}
  height={1080}
  loading="lazy"
  fetchpriority="high"
  style={{ aspectRatio: '16 / 9', objectFit: 'cover' }}
/>

// Accessible button with aria-label and focus-visible
<button
  type="button"
  aria-label="Close dialog"
  onClick={handleClose}
  className="p-2 rounded-full focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
>
  <svg /* ... close icon ... */ />
</button>

// Virtualized list using @tanstack/react-virtual
import { useVirtualizer } from '@tanstack/react-virtual';
import React from 'react';

function MyVirtualizedList({ items }) {
  const parentRef = React.useRef();

  const rowVirtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 35,
    overscan: 5,
  });

  return (
    <div ref={parentRef} style={{ height: `400px`, overflow: 'auto' }}>
      <div
        style={{
          height: `${rowVirtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {rowVirtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            {items[virtualItem.index]}
          </div>
        ))}
      </div>
    </div>
  );
}

// Accessible form input with label and autocomplete
<div className="form-group">
  <label htmlFor="email-input" className="block text-sm font-medium text-gray-700">
    Email Address
  </label>
  <input
    type="email"
    id="email-input"
    name="email"
    autoComplete="email"
    placeholder="you@example.com"
    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
    aria-required="true"
  />
</div>

// CSS for reduced motion
.animated-element {
  transition: transform 0.3s ease-out, opacity 0.3s ease-out;
}

@media (prefers-reduced-motion: reduce) {
  .animated-element {
    transition: none;
    animation: none;
  }
}
```

## Verification

- [ ] Run Lighthouse on key pages—Accessibility, Performance, and SEO scores above 90:
  ```powershell
  npx lighthouse http://localhost:3000 --only-categories=accessibility,performance,seo --view
  ```
- [ ] Verify all `<img>` tags have explicit `width` and `height` or `aspect-ratio` CSS.
- [ ] Manual keyboard navigation test: all interactive elements reachable and operable via `Tab`, `Shift+Tab`, `Enter`, `Space`.
- [ ] Screen reader test (NVDA, VoiceOver, JAWS): interactive elements and dynamic content announced correctly.
- [ ] Activate `prefers-reduced-motion` in OS settings—animations disabled or replaced with subtle alternative.
- [ ] Check DevTools console for layout thrashing warnings or performance bottlenecks during interactions.
- [ ] Review Network tab: critical fonts preloaded, modern image formats (WebP/AVIF) served.
- [ ] Validate form inputs: correct `type`, `autocomplete`, associated `<label>` or `aria-label`.
- [ ] Run ESLint with jsx-a11y plugin:
  ```powershell
  npx eslint --ext .js,.jsx,.ts,.tsx . --rule '{"jsx-a11y/alt-text":"error","jsx-a11y/anchor-is-valid":"error"}'
  ```

## Related Skills

- **`senior-frontend`** — Next.js/React scaffold, component generators, bundle analyzer scripts. This chair does not scaffold apps.
- **`emil-design-eng`** — animation craft and interaction taste (easing, transform-origin, springs). This chair enforces Vercel guideline compliance, not motion direction.
- Run the execute path here: `npx eslint` + `jsx-a11y`, `npx lighthouse`, keyboard/reduced-motion checks.
