# Performance Audit Checklist

## Evidence

- Reproduction flow is clear.
- Baseline metrics are captured before edits.
- Build output or bundle analysis is inspected.
- Browser performance trace or React Profiler is used for interaction/render problems.
- Server logs or data-fetch traces are checked for backend/cache issues.

## Common Checks

- Client components are not broader than needed.
- Heavy dependencies are not pulled into initial route bundles unnecessarily.
- Images reserve space, use responsive sizes, and avoid unoptimized large sources.
- Fonts avoid layout shift and excessive variants.
- Third-party scripts are delayed, scoped, or removed when not essential.
- Lists, tables, charts, editors, maps, and canvases avoid unnecessary re-renders.
- Context providers do not force large subtree updates.
- Data fetching and caching behavior is explicit.

## Verification

- Before/after metric is recorded.
- User-facing flow feels faster, not just cleaner in code.
- No correctness, accessibility, SEO, or loading-state regression is introduced.
- Prevention note or test is added for recurring patterns.
