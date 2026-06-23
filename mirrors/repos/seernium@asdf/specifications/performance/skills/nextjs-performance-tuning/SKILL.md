---
name: nextjs-performance-tuning
description: Steps and audit checklists for Next.js rendering optimizations, layout shift prevention, and static bundle chunking.
---

# Skill: Next.js Performance Auditing & Tuning

This skill defines workflows and checklists to optimize page load speeds, reduce bundle sizes, and eliminate Cumulative Layout Shift (CLS).

## Auditing & Implementation Steps

### 1. Bundle Chunking & Lazy Loading
- **Audit**: Scan page layout files for large third-party libraries (e.g. rich charts, editor frameworks) or heavy dynamic elements.
- **Fix**: Load components lazily using standard dynamic imports:
  ```typescript
  import dynamic from 'next/dynamic';
  const HeavyChart = dynamic(() => import('@/components/HeavyChart'), {
    loading: () => <SkeletonPlaceholder />,
    ssr: false // Set to false if it relies on browser-only API
  });
  ```

### 2. Cumulative Layout Shift (CLS) Mitigation
- **Audit**: Identify images or layout boxes that shift during page rendering.
- **Fix**: 
  - Always use Next.js `Image` components (`next/image`) with explicit `width` and `height` dimensions or layout configurations.
  - Use placeholder aspect ratio CSS rules (`aspect-square`, `aspect-video`) on containers hosting dynamic content loads.
  - Specify fallback skeleton dimensions matching target layout sizes.

### 3. Server-Side Data Fetching & Streaming
- **Audit**: Scan for slow API fetches that block layout rendering.
- **Fix**:
  - Fetch data as close to the leaf components as possible.
  - Wrap components carrying asynchronous calls in React `Suspense` boundaries to enable streaming:
    ```tsx
    import { Suspense } from 'react';
    // Inside page render:
    <Suspense fallback={<CardSkeleton />}>
      <AsyncDataComponent />
    </Suspense>
    ```

### 4. Static vs Dynamic Route Selection
- **Audit**: Check if page routes are dynamic when they could be static.
- **Fix**:
  - Optimize pages with static content using `generateStaticParams`.
  - Use appropriate cache revalidation windows (`revalidate = 3600`) where data updates frequently but doesn't require real-time client syncs.
