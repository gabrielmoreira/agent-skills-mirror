---
applyTo: "src/app/**/*.tsx,src/app/**/*.ts"
description: "Next.js App Router conventions (routing, data fetching, server actions, metadata)"
---

# Next.js (App Router) Conventions

- Default to React Server Components. Add `"use client"` only at the leaf component that actually needs state/effects/browser APIs.
- Data fetching happens in Server Components or Route Handlers — never fetch in `useEffect` for initial page data.
- Use `app/<route>/page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`, `not-found.tsx` per Next.js file conventions — create the ones that make sense for the route, not all of them by default.
- Mutations go through Server Actions (`"use server"`) with `zod` input validation, not client-side `fetch` to a custom API route, unless the consumer is external (e.g. a webhook or third-party client).
- Use `next/navigation` (`useRouter`, `redirect`, `notFound`) — never `next/router` (Pages Router API).
- Use the built-in `metadata` export or `generateMetadata` for SEO; never hand-roll `<head>` tags.
- Images: always `next/image`, never a raw `<img>`.
- Fonts: `next/font/google` or `next/font/local`, never a `<link>` to Google Fonts.
- Environment variables exposed to the client must be prefixed `NEXT_PUBLIC_` and documented in `.env.example`.
- Route Handlers (`route.ts`) return `NextResponse.json(...)` with explicit status codes; validate `request` body with `zod` before use.
- Caching: be explicit. Use `fetch(url, { cache: 'no-store' })` or `revalidate` rather than relying on implicit defaults — call out the choice in a code comment.
