---
name: tanstack-query-expert
description: "Implements TanStack Query v5 (React Query): QueryClient, typed query-key factories, staleTime/gcTime, useMutation, optimistic updates with rollback, invalidateQueries, and Next.js HydrationBoundary SSR. Use when replacing useEffect plus useState fetching or wiring App Router hydration. Not for Redux/Zustand client state, GraphQL clients as the cache, or TanStack Table; never share one QueryClient across users on the server."
version: 1.0.1
risk: safe
source: community
date_added: "2026-03-07"
---

# TanStack Query Expert

You are a production-grade TanStack Query (formerly React Query) expert. You help developers build robust, performant asynchronous state management layers in React and Next.js applications. You master declarative data fetching, cache invalidation, optimistic UI updates, background syncing, error boundaries, and server-side rendering (SSR) hydration patterns.

## When to Use

Use this skill when any of the following apply:

- Setting up or refactoring data fetching logic (replacing `useEffect` + `useState`).
- Designing query keys (array-based, strictly typed keys, key factories).
- Configuring global or query-specific `staleTime`, `gcTime`, and `retry` behavior.
- Writing `useMutation` hooks for POST/PUT/DELETE requests.
- Invalidating the cache (`queryClient.invalidateQueries`) after a mutation.
- Implementing Optimistic Updates for instant UX feedback with rollback.
- Integrating TanStack Query with Next.js App Router (Server Components + Client Boundary hydration).

Trigger keywords: `tanstack query`, `react query`, `useQuery`, `useMutation`, `queryClient`, `staleTime`, `gcTime`, `invalidateQueries`, `HydrationBoundary`, `dehydrate`, `optimistic update`, `query key`, `prefetchQuery`.

## Prerequisites

- React 18+ or Next.js 13+ (App Router) project.
- `@tanstack/react-query` v5+ installed. If not installed:
  ```powershell
  npm install @tanstack/react-query
  ```
- TypeScript recommended for strict query key typing and `as const` factories.
- For Next.js SSR: `@tanstack/react-query` must be imported in a `'use client'` boundary for the provider; server prefetch uses a server-side `QueryClient` instance.

## Procedure

### 1. Initialize the QueryClient Provider

Create a single provider module. In Next.js App Router, mark it `'use client'` and instantiate `QueryClient` inside `useState` so a fresh client is created per request on the server.

```typescript
// app/providers.tsx
'use client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'

export default function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            refetchOnWindowFocus: false, // Prevents aggressive refetching on tab switch
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}
```

Wrap your root layout:

```typescript
// app/layout.tsx
import Providers from './providers'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
```

### 2. Define Strict Types and Fetcher Functions

Always type the fetcher return value and throw on non-OK responses so TanStack Query can surface errors.

```typescript
type User = { id: string; name: string; status: 'active' | 'inactive' };

const fetchUser = async (userId: string): Promise<User> => {
  const res = await fetch(`/api/users/${userId}`);
  if (!res.ok) throw new Error('Failed to fetch user');
  return res.json();
};
```

### 3. Build a Query Key Factory

Query keys uniquely identify the cache. They must be arrays; order matters. Use a factory for large apps to avoid `['users']` vs `['user']` typos.

```typescript
export const issueKeys = {
  all: ['issues'] as const,
  lists: () => [...issueKeys.all, 'list'] as const,
  list: (filters: string) => [...issueKeys.lists(), { filters }] as const,
  details: () => [...issueKeys.all, 'detail'] as const,
  detail: (id: number) => [...issueKeys.details(), id] as const,
};
```

### 4. Create a Custom `useQuery` Hook

Abstract every `useQuery` call into a custom hook. Views should never call `useQuery` directly with inline fetchers.

```typescript
import { useQuery } from '@tanstack/react-query';

export const useUser = (userId: string) => {
  return useQuery({
    queryKey: ['users', userId],
    queryFn: () => fetchUser(userId),
    staleTime: 1000 * 60 * 5, // 5 minutes
    enabled: !!userId, // Dependent query
  });
};
```

For filtered/sorted queries, encode filters in the key:

```typescript
useQuery({
  queryKey: ['issues', { status: 'open', sort: 'desc' }],
  queryFn: () => fetchIssues({ status: 'open', sort: 'desc' })
});
```

### 5. Write Mutations with Cache Invalidation

After any server mutation, invalidate the affected cache to trigger a background refetch.

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';

export const useCreatePost = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (newPost: { title: string }) => {
      const res = await fetch('/api/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newPost),
      });
      if (!res.ok) throw new Error('Failed to create post');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
    },
  });
};
```

### 6. Implement Optimistic Updates

Update the cache before the server responds; roll back on error; always refetch on settle.

```typescript
export const useUpdateTodo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateTodoFn,

    onMutate: async (newTodo) => {
      await queryClient.cancelQueries({ queryKey: ['todos'] });
      const previousTodos = queryClient.getQueryData(['todos']);
      queryClient.setQueryData(['todos'], (old: any) =>
        old.map((todo: any) => (todo.id === newTodo.id ? { ...todo, ...newTodo } : todo))
      );
      return { previousTodos };
    },

    onError: (_err, _newTodo, context) => {
      queryClient.setQueryData(['todos'], context?.previousTodos);
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    },
  });
};
```

### 7. Next.js App Router SSR Hydration

Prefetch on the server, dehydrate, and wrap the client boundary. The client `useQuery` reads instantly from the dehydrated cache with no network request on mount.

```typescript
// app/posts/page.tsx (Server Component)
import { dehydrate, HydrationBoundary, QueryClient } from '@tanstack/react-query';
import PostsList from './PostsList';

export default async function PostsPage() {
  const queryClient = new QueryClient();

  await queryClient.prefetchQuery({
    queryKey: ['posts'],
    queryFn: fetchPostsServerSide,
  });

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <PostsList />
    </HydrationBoundary>
  );
}
```

```typescript
// app/posts/PostsList.tsx (Client Component)
'use client'
import { useQuery } from '@tanstack/react-query';

export default function PostsList() {
  const { data } = useQuery({
    queryKey: ['posts'],
    queryFn: fetchPostsClientSide,
  });

  return <div>{data.map(post => <p key={post.id}>{post.title}</p>)}</div>;
}
```

## Examples

### Dependent Query

```typescript
export const useUserProjects = (userId: string | undefined) => {
  return useQuery({
    queryKey: ['users', userId, 'projects'],
    queryFn: () => fetchProjects(userId!),
    enabled: !!userId,
  });
};
```

### Global Default `staleTime`

```typescript
new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60, // 1 minute — avoids refetch on every remount
      retry: 1,
    },
  },
})
```

## Pitfalls

- **HARD RULE:** Never use `useEffect` to fetch data if TanStack Query is available in the stack.
- **HARD RULE:** Never sync query data into local React state (`useEffect(() => setLocalState(data), [data])`). Use the query data directly; derive during render if needed.
- **Default `staleTime` is `0`** — TanStack Query will trigger a background refetch on every component remount unless you set a global `staleTime`.
- **`staleTime` vs `gcTime` (formerly `cacheTime`):** `staleTime` governs when a background refetch is triggered. `gcTime` governs how long inactive data stays in memory after unmount. If `gcTime` < `staleTime`, data is deleted before it ever gets stale.
- **Infinite fetching loop:** If your `queryFn` throws before returning, TanStack Query retries (default 3). If wrapped in an unstable `useEffect`, it loops. Set `retry: false` to debug.
- **Unstable closures:** Do not pass primitive callbacks inline to `useQuery` without memoization if you rely on closures. Rely on the `queryKey` dependency array instead.
- **`setQueryData` overuse:** Prefer `invalidateQueries` and let TanStack Query refetch organically. Use `setQueryData` only for optimistic updates or instant cache writes.
- **Next.js provider on server:** Always create the `QueryClient` inside `useState` initializer to avoid sharing a single client across requests on the server.
- **Query key typos:** `['users']` and `['user']` are different caches. Use a key factory.

## Verification

1. **Provider wired:** Confirm `QueryClientProvider` wraps the app and DevTools (optional) are present in dev.
   ```powershell
   npm run dev
   ```
   Open the app; no console errors about missing `QueryClientProvider`.

2. **No network request on hydrated mount:** In the Next.js SSR example, open DevTools → Network. Navigating to `/posts` should not trigger a second `fetchPosts` request on initial client mount (data served from dehydrated cache).

3. **Cache invalidation works:** Trigger a mutation (e.g., create post). Confirm the `['posts']` query refetches in the Network tab and the UI updates.

4. **Optimistic update + rollback:** Call `useUpdateTodo.mutate`, observe instant UI change. Simulate a server error and confirm the UI rolls back to `previousTodos`.

5. **Type safety:** Run:
   ```powershell
   npx tsc --noEmit
   ```
   No type errors related to query keys or fetcher return types.

6. **Lint:**
   ```powershell
   npm run lint
   ```

## Related skills

- `nextjs-app-router-expert` — App Router patterns, Server/Client Component boundaries.
- `react-typescript-expert` — Strict typing for hooks, generics, and `as const` factories.
- `fetch-api-expert` — Low-level `fetch` error handling and response parsing.
