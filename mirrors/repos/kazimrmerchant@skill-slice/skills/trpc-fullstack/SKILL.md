---
name: trpc-fullstack
description: "Builds end-to-end type-safe tRPC APIs: routers, Zod procedures, dual Next.js App Router context factories, protected middleware, and subscriptions. Use when scaffolding tRPC in a TypeScript monorepo or migrating REST/GraphQL incrementally inside one repo. Not for OpenAPI/REST-only backends or GraphQL schema-first stacks. Do not share one context factory between fetch Request handlers and RSC callers."
version: 1.0.1
category: framework
risk: none
source: community
date_added: "2026-03-17"
tags: [typescript, trpc, api, fullstack, nextjs, react, type-safety]
tools: [claude, cursor, gemini]
---

# tRPC Full-Stack

## Overview

tRPC lets you build fully type-safe APIs without writing a schema or code-generation step. TypeScript types flow from the server router directly to the client — every API call is autocompleted, validated at compile time, and refactoring-safe. Use this skill when building TypeScript monorepos, Next.js apps, or any project where the server and client share a codebase.

## When to Use

- Building a TypeScript full-stack app (Next.js App Router, Remix, Express + React) where client and server share a single repo
- You want end-to-end type safety on API calls without REST/GraphQL schema overhead
- Adding real-time features (subscriptions) to an existing tRPC setup
- Designing multi-step middleware (auth, rate limiting, tenant scoping) on tRPC procedures
- Migrating an existing REST/GraphQL API to tRPC incrementally

## Prerequisites

- Node.js 18+ and a TypeScript project (Next.js App Router recommended)
- Zod installed for input validation
- A database client (Prisma shown in examples; any ORM works)
- An auth helper that resolves sessions server-side (Next-Auth v5 `auth()` shown)

Install core dependencies:

```bash
npm install @trpc/server @trpc/client @trpc/react-query @tanstack/react-query zod
```

## Procedure

### Step 1: Create the tRPC Instance and Reusable Builders

Create the tRPC instance once. Export `router`, `publicProcedure`, `middleware`, and (later) `protectedProcedure` as reusable builders.

```typescript
// src/server/trpc.ts
import { initTRPC, TRPCError } from '@trpc/server';
import { type Context } from './context';
import { ZodError } from 'zod';

const t = initTRPC.context<Context>().create({
  errorFormatter({ shape, error }) {
    return {
      ...shape,
      data: {
        ...shape.data,
        zodError:
          error.cause instanceof ZodError ? error.cause.flatten() : null,
      },
    };
  },
});

export const router = t.router;
export const publicProcedure = t.procedure;
export const middleware = t.middleware;
```

### Step 2: Define Two Context Factories

**HARD RULE:** Next.js App Router handlers receive a fetch `Request`, not a Node.js `NextApiRequest`. You must define separate context factories — one for the HTTP handler, one for direct server-side callers (Server Components, RSC, cron jobs).

```typescript
// src/server/context.ts
import { type FetchCreateContextFnOptions } from '@trpc/server/adapters/fetch';
import { auth } from '@/server/auth'; // Next-Auth v5 / your auth helper
import { db } from './db';

/**
 * Context for the HTTP handler (App Router Route Handler).
 * opts.req is the fetch Request — auth is resolved server-side via auth().
 */
export async function createTRPCContext(opts: FetchCreateContextFnOptions) {
  const session = await auth();
  return { session, db, headers: opts.req.headers };
}

/**
 * Context for direct server-side callers (Server Components, RSC, cron jobs).
 * No HTTP request is involved — call auth() directly from the server.
 */
export async function createServerContext() {
  const session = await auth();
  return { session, db };
}

export type Context = Awaited<ReturnType<typeof createTRPCContext>>;
```

### Step 3: Build an Auth Middleware and Protected Procedure

```typescript
// src/server/trpc.ts (continued)
const enforceAuth = middleware(({ ctx, next }) => {
  if (!ctx.session?.user) {
    throw new TRPCError({ code: 'UNAUTHORIZED' });
  }
  return next({
    ctx: {
      // Narrows type: session is non-null from here downstream
      session: { ...ctx.session, user: ctx.session.user },
    },
  });
});

export const protectedProcedure = t.procedure.use(enforceAuth);
```

### Step 4: Create Domain Routers

Split routers by domain (posts, users, billing) and merge them in `root.ts`.

```typescript
// src/server/routers/post.ts
import { z } from 'zod';
import { router, publicProcedure, protectedProcedure } from '../trpc';
import { TRPCError } from '@trpc/server';

export const postRouter = router({
  list: publicProcedure
    .input(
      z.object({
        limit: z.number().min(1).max(100).default(20),
        cursor: z.string().optional(),
      })
    )
    .query(async ({ ctx, input }) => {
      const posts = await ctx.db.post.findMany({
        take: input.limit + 1,
        cursor: input.cursor ? { id: input.cursor } : undefined,
        orderBy: { createdAt: 'desc' },
      });
      const nextCursor =
        posts.length > input.limit ? posts.pop()!.id : undefined;
      return { posts, nextCursor };
    }),

  byId: publicProcedure
    .input(z.object({ id: z.string() }))
    .query(async ({ ctx, input }) => {
      const post = await ctx.db.post.findUnique({ where: { id: input.id } });
      if (!post) throw new TRPCError({ code: 'NOT_FOUND' });
      return post;
    }),

  create: protectedProcedure
    .input(
      z.object({
        title: z.string().min(1).max(200),
        body: z.string().min(1),
      })
    )
    .mutation(async ({ ctx, input }) => {
      return ctx.db.post.create({
        data: { ...input, authorId: ctx.session.user.id },
      });
    }),

  delete: protectedProcedure
    .input(z.object({ id: z.string() }))
    .mutation(async ({ ctx, input }) => {
      const post = await ctx.db.post.findUnique({ where: { id: input.id } });
      if (!post) throw new TRPCError({ code: 'NOT_FOUND' });
      if (post.authorId !== ctx.session.user.id)
        throw new TRPCError({ code: 'FORBIDDEN' });
      return ctx.db.post.delete({ where: { id: input.id } });
    }),
});
```

### Step 5: Compose the Root Router and Export Types

```typescript
// src/server/root.ts
import { router } from './trpc';
import { postRouter } from './routers/post';
import { userRouter } from './routers/user';

export const appRouter = router({
  post: postRouter,
  user: userRouter,
});

// Export the TYPE for the client — never import appRouter itself on the client
export type AppRouter = typeof appRouter;
```

### Step 6: Mount the API Handler (Next.js App Router)

**HARD RULE:** The App Router handler must use `fetchRequestHandler` from `@trpc/server/adapters/fetch` and the fetch-based context factory. Do NOT use `@trpc/server/adapters/next` — that adapter is for Pages Router only.

```typescript
// src/app/api/trpc/[trpc]/route.ts
import { fetchRequestHandler } from '@trpc/server/adapters/fetch';
import { type FetchCreateContextFnOptions } from '@trpc/server/adapters/fetch';
import { appRouter } from '@/server/root';
import { createTRPCContext } from '@/server/context';

const handler = (req: Request) =>
  fetchRequestHandler({
    endpoint: '/api/trpc',
    req,
    router: appRouter,
    createContext: (opts: FetchCreateContextFnOptions) => createTRPCContext(opts),
  });

export { handler as GET, handler as POST };
```

### Step 7: Set Up the Client (React Query)

```typescript
// src/utils/trpc.ts
import { createTRPCReact } from '@trpc/react-query';
import type { AppRouter } from '@/server/root';

export const trpc = createTRPCReact<AppRouter>();
```

```typescript
// src/app/providers.tsx
'use client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { httpBatchLink } from '@trpc/client';
import { useState } from 'react';
import { trpc } from '@/utils/trpc';

export function TRPCProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());
  const [trpcClient] = useState(() =>
    trpc.createClient({
      links: [
        httpBatchLink({
          url: '/api/trpc',
          headers: () => ({ 'x-trpc-source': 'react' }),
        }),
      ],
    })
  );

  return (
    <trpc.Provider client={trpcClient} queryClient={queryClient}>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </trpc.Provider>
  );
}
```

### Step 8: Use Procedures in Components

**Query (read):**

```typescript
// components/PostList.tsx
'use client';
import { trpc } from '@/utils/trpc';

export function PostList() {
  const { data, isLoading, error } = trpc.post.list.useQuery({ limit: 10 });

  if (isLoading) return <p>Loading…</p>;
  if (error) return <p>Error: {error.message}</p>;

  return (
    <ul>
      {data?.posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

**Mutation with cache invalidation:**

```typescript
'use client';
import { trpc } from '@/utils/trpc';

export function CreatePost() {
  const utils = trpc.useUtils();

  const createPost = trpc.post.create.useMutation({
    onSuccess: () => {
      utils.post.list.invalidate();
    },
  });

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const data = new FormData(form);
    createPost.mutate({
      title: data.get('title') as string,
      body: data.get('body') as string,
    });
    form.reset();
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="title" placeholder="Title" required />
      <textarea name="body" placeholder="Body" required />
      <button type="submit" disabled={createPost.isPending}>
        {createPost.isPending ? 'Creating…' : 'Create Post'}
      </button>
      {createPost.error && <p>{createPost.error.message}</p>}
    </form>
  );
}
```

### Step 9: Server-Side Caller (Server Components / SSR)

Use `createServerContext` — the dedicated server-side factory — so `auth()` is called correctly without a synthetic request object.

```typescript
// app/posts/page.tsx (Next.js Server Component)
import { appRouter } from '@/server/root';
import { createCallerFactory } from '@trpc/server';
import { createServerContext } from '@/server/context';

const createCaller = createCallerFactory(appRouter);

export default async function PostsPage() {
  const caller = createCaller(await createServerContext());
  const { posts } = await caller.post.list({ limit: 20 });

  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

### Step 10: Real-Time Subscriptions (WebSocket)

Server-side subscription using `observable`:

```typescript
// server/routers/notifications.ts
import { observable } from '@trpc/server/observable';
import { EventEmitter } from 'events';

const ee = new EventEmitter();

export const notificationRouter = router({
  onNew: protectedProcedure.subscription(({ ctx }) => {
    return observable<{ message: string; at: Date }>((emit) => {
      const onNotification = (data: { message: string }) => {
        emit.next({ message: data.message, at: new Date() });
      };

      const channel = `user:${ctx.session.user.id}`;
      ee.on(channel, onNotification);
      return () => ee.off(channel, onNotification);
    });
  }),
});
```

Client usage — requires `wsLink` and `splitLink` in the client config:

```typescript
trpc.notification.onNew.useSubscription(undefined, {
  onData(data) {
    toast(data.message);
  },
});
```

## Examples

### Mutation with Optimistic Update

```typescript
'use client';
import { trpc } from '@/utils/trpc';

export function TogglePublish({ id, published }: { id: string; published: boolean }) {
  const utils = trpc.useUtils();
  const toggle = trpc.post.togglePublish.useMutation({
    onMutate: async () => {
      await utils.post.byId.cancel({ id });
      const prev = utils.post.byId.getData({ id });
      if (prev) {
        utils.post.byId.setData({ id }, { ...prev, published: !published });
      }
      return { prev };
    },
    onError: (_err, _vars, ctx) => {
      if (ctx?.prev) utils.post.byId.setData({ id }, ctx.prev);
    },
    onSettled: () => {
      utils.post.byId.invalidate({ id });
    },
  });

  return <button onClick={() => toggle.mutate({ id })}>Toggle</button>;
}
```

### Testing Procedures with createCallerFactory

```typescript
// tests/post.test.ts
import { createCallerFactory } from '@trpc/server';
import { postRouter } from '@/server/routers/post';
import { createServerContext } from '@/server/context';

const createCaller = createCallerFactory(postRouter);

test('list returns posts', async () => {
  const caller = createCaller(await createServerContext());
  const result = await caller.list({ limit: 5 });
  expect(result.posts.length).toBeLessThanOrEqual(5);
});
```

## Pitfalls

- **Auth session is `null` in protected procedures even when the user is logged in.** Ensure `createTRPCContext` uses the correct server-side auth call (e.g. `auth()` from Next-Auth v5) and is not receiving a Pages Router `req/res` cast via `as any` in an App Router handler.

- **Server Component caller fails for auth-dependent queries.** Use `createServerContext()` (the dedicated server-side factory) instead of passing an empty or synthetic object to `createContext`. **Never** use `createContext({} as any)`.

- **"Type error: AppRouter is not assignable to AnyRouter".** Import `AppRouter` as a `type` import (`import type { AppRouter }`) on the client, not the full module.

- **Mutations not reflecting in the UI after success.** Call `utils.<router>.<procedure>.invalidate()` in `onSuccess` to trigger a refetch via React Query.

- **"Cannot find module '@trpc/server/adapters/next'" with App Router.** Use `@trpc/server/adapters/fetch` and `fetchRequestHandler` for the App Router. The `nextjs` adapter is for Pages Router only.

- **Subscriptions not connecting.** Subscriptions require `splitLink` — route subscriptions to `wsLink` and queries/mutations to `httpBatchLink`. Without `splitLink`, the client will attempt HTTP for subscription calls and fail silently.

- **Don't cast context with `as any`** to silence type errors — the mismatch will surface as a runtime failure when auth or session lookups return undefined.

- **Don't share the tRPC client instance globally** — create it per-provider to avoid stale closures and stale auth headers.

- **Don't put business logic in the route handler** — keep it in the procedure or a service layer.

- **Always validate all input shapes with Zod**, including pagination cursors and IDs, to prevent injection via malformed inputs.

- **Always enforce authorization in `protectedProcedure`** — never rely on client-side checks alone.

- **Avoid exposing internal error details to clients** — use `TRPCError` with a public-safe `message` and keep stack traces server-side only.

## Verification

1. **Type-check the server and client share the same router type:**

```bash
npx tsc --noEmit
```

Expected: no errors. If you see "AppRouter is not assignable to AnyRouter," switch the client import to `import type { AppRouter }`.

2. **Verify the API handler responds:**

```bash
curl -X POST http://localhost:3000/api/trpc/post.list -H "content-type: application/json" -d '{"json":{"limit":5}}'
```

Expected: a JSON response with a `result` object containing `posts` and `nextCursor`.

3. **Verify protected procedures reject unauthenticated requests:**

```bash
curl -X POST http://localhost:3000/api/trpc/post.create -H "content-type: application/json" -d '{"json":{"title":"test","body":"test"}}'
```

Expected: an error response with `code: 'UNAUTHORIZED'`.

4. **Verify the client type-safety in the editor:** In a client component, type `trpc.post.` and confirm autocomplete shows `list`, `byId`, `create`, `delete`. If autocomplete is empty, the `AppRouter` type import is missing or wrong.

5. **Verify server-side caller works in a Server Component:** Navigate to the `/posts` route and confirm posts render without a `UNAUTHORIZED` or context error.

## Related Skills

- `typescript-expert` — Deep TypeScript patterns used inside tRPC routers and generic utilities
- `react-patterns` — React hooks patterns that pair with `trpc.*.useQuery` and `useMutation`
- `test-driven-development` — Write procedure unit tests using `createCallerFactory` without an HTTP server
- `security-auditor` — Review tRPC middleware chains for auth bypass and input validation gaps

## Additional Resources

- [tRPC Official Docs](https://trpc.io/docs)
- [create-t3-app](https://create.t3.gg) — Production Next.js starter with tRPC wired in
- [tRPC GitHub](https://github.com/trpc/trpc)
- [TanStack Query Docs](https://tanstack.com/query/latest)

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
