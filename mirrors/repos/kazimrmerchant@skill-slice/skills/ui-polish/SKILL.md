---
name: ui-polish
description: "Audits and refines existing web UI against spacing/type, WCAG 2.2, SEO metadata, and Core Web Vitals (INP, LCP, CLS). Use when polishing a live page or component rather than inventing a new look. Not for original mockups (claude-design, sketch), /better quality loops on arbitrary deliverables, or full-site SEO crawls (seo-audit)."
version: 1.0.1
domain: UI-UX
risk: safe
last_verified: '2026-05-30'
self_updating: true
---

# UI Polish and Quality Gates

## When to Use

- **Use when:** Polishing user interfaces, conducting design audits, checking HTML/CSS responsiveness, tuning transitions, or verifying accessibility and search parameters on web applications.
- **Route elsewhere:** Route to `frontend-design` if creating original mockup layouts or planning custom CSS frameworks from scratch. Route to `seo-audit` if executing full site crawls or deep search index diagnostic tasks.

## Prerequisites

- **Inputs:** Target component or page file path, CSS styling definitions, responsive viewports list, assets list.
- **Environment:** Windows host is primary (PowerShell). Use PowerShell-compatible commands for any local file operations or script executions.

## Procedure

1. **Establish Goals:** Identify visual constraints, target breakpoints, audience profile, and design system constraints.
2. **Context Inspection:** Review existing CSS variables, tailwind configurations, assets, and layouts before proposing structural changes.
3. **Select Focus:** Determine the appropriate polishing boundaries (e.g., responsive adjustments, accessibility fixes, animation enhancements).
4. **Produce Outputs:** Generate refactored markup, style rules, components, or diagnostic checklists.
5. **Verify Outcomes:** Validate visual changes using multiple viewports, verify contrast ratios, and trace interactions against runtime performance thresholds.

### Gate 1: Baseline Visual Review

- [ ] **Consistent Spacing:** Enforce standard utility steps (e.g., Tailwind spacing scale). Do not introduce arbitrary pixel overrides.
- [ ] **Typography Hierarchy:** Verify heading flows (`h1` to `h2` to `h3`) with no skipped heading levels.
- [ ] **Color Contrast:** Verify text elements meet WCAG 2.2 AA requirements (4.5:1 for regular text, 3:1 for large text).
- [ ] **Responsive Validation:** Inspect rendering at 375px (mobile), 768px (tablet), and 1280px (desktop) viewports.
- [ ] **No Horizontal Scroll:** Prevent unexpected layout breakages or horizontal overflows on narrow screens.
- [ ] **Asynchronous States:** Integrate skeletons, loading bars, or spinners for async operations.
- [ ] **Empty States:** Build descriptive illustration or text layouts when target data containers are empty.
- [ ] **Error Boundaries:** Build user-facing error dialogs or layouts when operations fail.
- [ ] **Content Overruns:** Apply CSS truncation tools (`truncate` or `line-clamp`) to prevent text overflowing bounding containers.

### Gate 2: Accessibility (WCAG 2.2)

- [ ] **Keyboard Nav:** Ensure all interactive elements (buttons, inputs, dropdowns) are focusable and operable via Keyboard Tab sequence.
- [ ] **Focus Indicators:** Ensure focus outlines are highly visible and maintain proper contrast when active.
- [ ] **Skip Navigation:** Provide skip-to-content links for users traversing pages using screen readers.
- [ ] **Image Labels:** Add descriptive `alt` tags to images (use `alt=""` explicitly for decorative imagery).
- [ ] **Labeled Controls:** Bind every form field to a visible `<label>` element or assign clear `aria-label` tags (do not rely on placeholder attributes alone).
- [ ] **Correct ARIA:** Utilize semantic HTML first; apply ARIA attributes only where native semantics are unavailable (e.g., `aria-expanded`, `aria-controls`).
- [ ] **Color Independence:** Do not convey status or critical info using color variations alone (combine with icons or text indicators).
- [ ] **Touch Targets:** Maintain a minimum target size of 24x24 CSS pixels for Level AA compliance (44x44 CSS pixels recommended for Level AAA).
- [ ] **Live Regions:** Set `aria-live="polite"` on message banners or dynamically updated page nodes.
- [ ] **Modal Traps:** Trap keyboard focus within active dialog windows and restore focus to the triggering element upon closure.

### Gate 3: Metadata & SEO

- [ ] **Unique Page Titles:** Assign distinct `<title>` strings reflecting current page context.
- [ ] **Meta Descriptions:** Provide short page descriptions under 160 characters.
- [ ] **Open Graph (OG):** Configure OG tags (`og:title`, `og:description`, `og:image`, `og:url`, `og:type`) for social link rendering.
- [ ] **Structured Metadata:** Implement JSON-LD objects to define search engine entities.
- [ ] **Canonicalization:** Declare absolute `<link rel="canonical">` locations on all page routes.
- [ ] **Icon Manifest:** Supply standard favicons in 16x16, 32x32, 180x180 (Apple touch icon), and web app manifest configurations.
- [ ] **Robots & Sitemap:** Ensure `robots.txt` is configured and points to a validated `sitemap.xml`.
- [ ] **Document Language:** Always set the `lang` attribute on the root `<html>` element.

### Gate 4: Motion & Performance (Core Web Vitals)

- [ ] **GPU Acceleration:** Implement CSS transitions and keyframes using `transform` and `opacity` properties to prevent CPU-bound layout repaints.
- [ ] **Cumulative Layout Shift (CLS):** Set explicit dimensions (`width` and `height` or `aspect-ratio` wrappers) on images and video nodes to maintain CLS < 0.1.
- [ ] **Interaction to Next Paint (INP):** Break up long-running tasks (>50ms) using `requestIdleCallback` or Web Workers to maintain interactive latency INP < 200ms.
- [ ] **Largest Contentful Paint (LCP):** Preload primary hero assets and set lazy-loading (`loading="lazy"`) for elements below the fold to ensure LCP < 2.5s.
- [ ] **Reduced Motion:** Wrap decorative visual transitions in `@media (prefers-reduced-motion: no-preference)` styles.
- [ ] **Transition Timing:** Cap operational animation feedback durations below 300ms to preserve UI responsiveness.
- [ ] **Resource Optimization:** Verify bundle assets, compress media to modern formats (e.g., WebP, AVIF), and eliminate unused CSS or script packages.

## Pitfalls

- **High Interaction Delay (INP):** Track blocking JavaScript tasks using browser profiling tools. Refactor long event handler scripts to run asynchronously by splitting executions with `setTimeout` or `requestAnimationFrame`.
- **Layout Jumps (CLS):** Audit layout modifications dynamically using Chrome User Experience Report metrics. Inject CSS `contain-intrinsic-size` rules to reserve block areas before slow media payloads load.
- **Legacy Browser Viewports:** Deprecate standard viewport height units (`vh`) on interactive containers to prevent mobile address bar overlap bugs. Standardize on dynamic viewport height (`dvh`) or small viewport height (`svh`) rules.
- **Accessibility Non-Negotiables:** Treat Accessibility (Gate 2) compliance as non-negotiable. Correct touch targets and tab-index flows before testing other parameters.
- **Motion Sickness:** Verify custom transitions against user system settings (`prefers-reduced-motion`) to avoid causing motion sickness.
- **Raw Pixel Overrides:** Avoid `any` styles or styling rules containing raw pixel overrides inside Tailwind projects. Do not use inline style declarations in JSX/HTML layouts unless programmatically calculated.
- **Hidden Focus:** Outlines are never hidden on `:focus` selectors without providing an alternate focus visual style.

## Verification

Execute all 4 quality gates before merging code contributions into production branches. Generate validation records in the following format before concluding visual reviews:

```markdown
| Quality Gate | Checked Criteria | Total Criteria | Compliance Status | Notes / Fixes |
|---|---|---|---|---|
| **Visual Review** | 9 | 9 | PASS | No overflows found |
| **Accessibility (WCAG 2.2)** | 9 | 10 | WARNING | Spacing workaround applied on small close button |
| **Metadata & SEO** | 8 | 9 | WARNING | Canonical URL needs dynamic hostname binding |
| **Motion & Performance** | 8 | 9 | PASS | INP clocked at 145ms; lazy loading active |
```

### Output Audit Structure

```json
{
  "visual_audit": { "responsive_ok": true, "no_overflow": true },
  "accessibility_audit": { "wcag_aa_compliant": true, "focus_traps_handled": true },
  "seo_audit": { "canonical_meta_ok": true, "structured_data_present": true },
  "performance_audit": { "inp_ms": 150, "cls_ratio": 0.05 }
}
```

## Related skills

- `frontend-design`: Use for creating original mockup layouts or planning custom CSS frameworks from scratch.
- `seo-audit`: Use for executing full site crawls or deep search index diagnostic tasks.

## References

Load the following references if deeper context is needed during the procedure:
- [W3C WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/) (Load when verifying Gate 2 accessibility criteria)
- [web.dev Core Web Vitals (INP)](https://web.dev/articles/inp) (Load when diagnosing Gate 4 performance issues)
- [Tailwind CSS v4 Documentation](https://tailwindcss.com/docs/v4-beta) (Load when applying Gate 1 visual review in Tailwind projects)
