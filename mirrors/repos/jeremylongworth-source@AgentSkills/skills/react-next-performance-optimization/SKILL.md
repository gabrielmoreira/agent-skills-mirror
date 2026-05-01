---
name: react-next-performance-optimization
description: Audit, diagnose, and optimize React and Next.js application performance. Use when Codex is asked about Core Web Vitals, slow interactions, bundle size, caching, Server Components, Client Component boundaries, re-renders, memoization, image/font/script optimization, lazy loading, route performance, production readiness, or React/Next.js performance regressions.
license: MIT
---

# React Next Performance Optimization

## Core Workflow

1. Identify framework version, router mode, rendering strategy, deployment target, slow user flow, and target metric.
2. Measure before changing: build output, bundle analyzer, browser performance traces, React Profiler, Lighthouse/Web Vitals, server logs, or user-reported reproduction.
3. Classify bottlenecks by layer: network, server/rendering, data fetching/cache, JavaScript bundle, hydration, re-rendering, layout/paint, images/fonts/scripts, third-party code, or backend.
4. Fix highest-impact verified issues first. Avoid speculative memoization and broad rewrites.
5. Re-measure after each meaningful change and record the before/after evidence.
6. Leave a prevention note: what pattern caused the issue, how to avoid it, and what metric/test should catch recurrence.

## Optimization Priorities

- Next.js: prefer Server Components by default, keep `"use client"` boundaries narrow, use framework image/font/script/lazy-loading tools, and understand caching/revalidation before changing data flow.
- React: reduce unnecessary state lifting, unstable props, expensive renders, effect loops, and avoidable context churn; use `memo`, `useMemo`, and `useCallback` only when they solve a measured problem or preserve stable references intentionally.
- Bundles: inspect large dependencies, duplicate packages, client-only imports, heavy charts/editors/maps, and dynamic imports.
- Runtime: inspect long tasks, hydration cost, layout shifts, input delay, memory churn, and repeated network work.
- Core Web Vitals: optimize LCP, INP, and CLS with user-flow evidence, not only lab scores.

## Freshness Rule

Verify current official React, Next.js, and web.dev guidance before making version-sensitive recommendations about React Compiler, Server Components, caching APIs, Turbopack, bundle analysis, or Web Vitals thresholds.

## Deliverable Shape

For performance work, provide:

- Baseline evidence collected or missing
- Bottleneck classification
- Prioritized findings
- Recommended changes with expected impact
- Changes made, if editing
- Before/after verification
- Prevention notes and remaining risks

## References

- Read `references/performance-audit-checklist.md` when auditing or optimizing a React/Next.js app.
