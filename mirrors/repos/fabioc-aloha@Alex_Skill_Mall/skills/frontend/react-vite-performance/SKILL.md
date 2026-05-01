---
type: skill
lifecycle: stable
inheritance: inheritable
name: react-vite-performance
description: React + Vite performance optimization — code splitting, lazy loading, bundle analysis, Web Vitals, and modern React patterns for fast web applications
tier: standard
applyTo: '**/*react*,**/*vite*,**/*performance*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# React + Vite Performance Optimization


> Fast by default, optimized by design — sub-300KB bundles and sub-2s load times.
>
> **Targets**: React 19+ / Vite 6+ | **Last validated**: April 2026

## Performance Targets

| Metric | Target | Tool |
|--------|--------|------|
| Initial JS (gzipped) | < 300 KB | `rollup-plugin-visualizer` |
| First Contentful Paint | < 1.5s | Lighthouse |
| Time to Interactive | < 3s | Lighthouse |
| Largest Contentful Paint | < 2.5s | Web Vitals |
| Cumulative Layout Shift | < 0.1 | Web Vitals |

## Vite Build Configuration

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    target: 'esnext',
    minify: 'esbuild',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui': ['@headlessui/react', '@heroicons/react'],
          // Group large dependencies into separate chunks
        },
      },
    },
    chunkSizeWarningLimit: 500,
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom'],
  },
});
```

### Bundle Analysis

```bash
npm install -D rollup-plugin-visualizer
```

```typescript
// vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer';

plugins: [
  react(),
  visualizer({ filename: 'dist/stats.html', gzipSize: true }),
]
```

## Code Splitting

### Route-Based Splitting

```typescript
import { lazy, Suspense } from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { path: 'dashboard', element: <Dashboard /> },
      { path: 'settings', element: <Settings /> },
    ],
  },
]);

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <RouterProvider router={router} />
    </Suspense>
  );
}
```

### Component-Based Splitting

```typescript
const Chart = lazy(() => import('./components/Chart'));

function Dashboard() {
  return (
    <Suspense fallback={<ChartSkeleton />}>
      <Chart data={data} />
    </Suspense>
  );
}
```

### Preloading on Hover

```typescript
function NavLink({ to, loader, children }) {
  const preload = () => loader(); // e.g., () => import('./pages/Settings')

  return (
    <Link to={to} onMouseEnter={preload} onFocus={preload}>
      {children}
    </Link>
  );
}
```

## Modern React Patterns

### Compiler-Friendly Code (React 19+)

React 19's compiler auto-memoizes. Write straightforward components:

```typescript
// ✅ Let the compiler optimize
function UserCard({ user }: { user: User }) {
  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
}

// ❌ Avoid manual memoization the compiler handles
const UserCard = React.memo(({ user }) => { ... });
```

**Vite setup** — install `babel-plugin-react-compiler` and add to `vite.config.ts`:

```typescript
// vite.config.ts
import react from '@vitejs/plugin-react';
export default defineConfig({
  plugins: [
    react({ babel: { plugins: ['babel-plugin-react-compiler'] } }),
  ],
});
```

### use() Hook for Data Loading

```typescript
import { use, Suspense } from 'react';

function UserProfile({ userPromise }: { userPromise: Promise<User> }) {
  const user = use(userPromise);
  return <div>{user.name}</div>;
}

function App() {
  const userPromise = fetchUser(userId);
  return (
    <Suspense fallback={<UserSkeleton />}>
      <UserProfile userPromise={userPromise} />
    </Suspense>
  );
}
```

### useTransition for Non-Urgent Updates

```typescript
import { useState, useTransition } from 'react';

function SearchableList({ items }: { items: Item[] }) {
  const [query, setQuery] = useState('');
  const [filtered, setFiltered] = useState(items);
  const [isPending, startTransition] = useTransition();

  const handleSearch = (value: string) => {
    setQuery(value); // Urgent: update input immediately
    startTransition(() => {
      setFiltered(items.filter(item =>
        item.name.toLowerCase().includes(value.toLowerCase())
      ));
    });
  };

  return (
    <>
      <input value={query} onChange={e => handleSearch(e.target.value)} />
      {isPending && <Spinner />}
      <List items={filtered} />
    </>
  );
}
```

## TanStack Query Optimization

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,    // 5 minutes
      gcTime: 30 * 60 * 1000,      // 30 minutes
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});
```

### Optimistic Updates

```typescript
const updateUser = useMutation({
  mutationFn: (data: UserUpdate) => api.updateUser(data),
  onMutate: async (newData) => {
    await queryClient.cancelQueries({ queryKey: ['user'] });
    const previous = queryClient.getQueryData(['user']);
    queryClient.setQueryData(['user'], old => ({ ...old, ...newData }));
    return { previous };
  },
  onError: (_err, _new, context) => {
    queryClient.setQueryData(['user'], context?.previous);
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['user'] });
  },
});
```

## Asset Optimization

### Images

```typescript
// Non-critical images: lazy load
<img src={src} alt={alt} loading="lazy" decoding="async" fetchpriority="low" />

// LCP image: load immediately
<img src={src} alt={alt} fetchpriority="high" />
```

### Fonts

```css
@font-face {
  font-family: 'Inter';
  src: url('/fonts/Inter-var.woff2') format('woff2-variations');
  font-display: swap;
  font-weight: 100 900;
}
```

```html
<link rel="preload" href="/fonts/Inter-var.woff2" as="font" type="font/woff2" crossorigin>
```

## Web Vitals Monitoring

> **INP replaced FID** as a Core Web Vital in March 2024. INP measures overall responsiveness (all interactions), not just the first one.

```typescript
import { onCLS, onINP, onLCP, onFCP, onTTFB } from 'web-vitals';

function reportMetric(metric: Metric) {
  analytics.track('web-vitals', {
    name: metric.name,
    value: metric.value,
    rating: metric.rating,
  });
}

onCLS(reportMetric);
onINP(reportMetric);   // Interaction to Next Paint (replaced FID)
onLCP(reportMetric);
onFCP(reportMetric);
onTTFB(reportMetric);
```

## Performance Checklist

### Build

- [ ] Manual chunks for large vendor libs
- [ ] Tree shaking enabled (ESM imports)
- [ ] Dependency pre-bundling configured
- [ ] Bundle size tracked in CI

### Runtime

- [ ] Routes lazy-loaded with Suspense
- [ ] Heavy components split into separate chunks
- [ ] `useTransition` for non-urgent state updates
- [ ] Virtual scrolling for long lists
- [ ] Debounce expensive operations

### Assets

- [ ] Images: WebP, lazy loading, responsive sizes
- [ ] Fonts: `font-display: swap`, preload critical
- [ ] Brotli/gzip compression enabled
- [ ] Critical CSS inlined
