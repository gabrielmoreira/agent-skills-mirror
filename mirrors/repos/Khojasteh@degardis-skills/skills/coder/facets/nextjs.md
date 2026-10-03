---
title: Next.js
category: Framework and library
x-claim-provenance:
- claim: Next.js 15 changed fetch requests, GET Route Handlers, and client navigations from cached by default to uncached by default; GET Route Handlers had been cached in Next.js 14 unless they used a dynamic function or option, and the Client Router Cache staleTime for page segments became 0.
  source: https://nextjs.org/blog/next-15
  scope: Next.js 15 release announcement, 2024-10-21.
- claim: Next.js 16 introduced Cache Components, an entirely opt-in caching model built around the "use cache" directive in which dynamic code runs at request time by default, and replaced middleware.ts with proxy.ts, which runs on the Node.js runtime, deprecating middleware.ts while keeping it for Edge runtime use.
  source: https://nextjs.org/blog/next-16
  scope: Next.js 16 release announcement, 2025-10-21.
- claim: NEXT_PUBLIC_ variables are inlined into the JavaScript sent to the browser at next build, so the built app no longer responds to changes in them.
  source: https://nextjs.org/docs/app/guides/environment-variables
  scope: Next.js 16.3 documentation, updated 2026-08-25.
---

The configured Next.js and React versions, router generation, rendering modes, runtime targets, bundler, cache settings, middleware, and deployment adapter decide which APIs apply, and only APIs supported by the configured router and version apply. The version decides even what is cached. Next.js 15 stopped caching `fetch` requests, `GET` route handlers, and client navigations to page segments by default, where Next.js 14 had cached them, and Next.js 16 added Cache Components, an opt-in model in which caching is declared with `"use cache"`, and replaced `middleware.ts` with `proxy.ts`, which runs on Node.js, deprecating `middleware.ts` while keeping it for the Edge runtime. The same source can therefore serve cached data under one version and fresh data under another.

The server/client component boundary, route ownership, data loading and mutation, cache and revalidation semantics, dynamic versus static rendering, authentication, error and loading states, and environment exposure are behavioral contracts, as are public URLs, generated parameters, metadata, redirects, cookies, headers, server actions, API routes, and deployment-runtime limits. Environment exposure is decided at build time: the `NEXT_PUBLIC_` prefix marks the variables that are inlined into the client bundle when `next build` runs, so which variables reach the browser follows from that rule as the resolved version applies it, and a built image promoted to another environment keeps the values it was built with.

Behavior runs through layouts and nested routes, server/client imports, streaming and suspense, fetch caching, revalidation tags or paths, request memoization, middleware matching, cookies and headers, server actions, route handlers, image and asset behavior, and adapter output. Behavior is also referenced indirectly, through:

- file-based route conventions, dynamic segments, and parallel or intercepted routes
- environment variable exposure and edge or runtime declarations
- generated manifests and static params
- code moved into the client bundle

Characteristic failure modes are cached personalized data, server-only secrets crossing client imports, hydration mismatch, redirect loops, middleware trust, mutation paths that omit revalidation, and features unsupported by the target adapter.

Behavioral evidence comes from production builds and the configured deployment adapter, because development routing and cache behavior are not evidence for production output. It covers route generation and precedence, server/client serialization, authentication, cookies and headers, caching and invalidation, static and dynamic rendering, streaming, errors, redirects, middleware, actions or handlers, and hydration. Performance evidence includes rendered and client payloads, server latency, cache hit behavior, and revalidation under the deployed runtime, and an optimization must preserve React lifecycle and accessibility.
