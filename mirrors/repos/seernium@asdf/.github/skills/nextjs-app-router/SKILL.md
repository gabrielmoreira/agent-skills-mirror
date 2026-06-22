---
name: nextjs-app-router
description: Scaffold a new Next.js App Router route segment (page, layout, loading, error states, and optional Server Action) following this repo's conventions. Use when asked to "add a page", "create a route", "add a new screen", or "scaffold a feature route".
---

# Next.js App Router Scaffolding

Use this skill whenever the user asks to add a new route/page/screen to the Next.js app.

## Process

1. **Determine the route segment** from the request (e.g. "settings page" → `src/app/settings/`).
2. **Check for route groups / parallel routes** — if the feature needs auth gating, place it under the existing `(authenticated)` route group if one exists; check `src/app/` first.
3. **Create the minimal necessary files** — do not generate `loading.tsx`/`error.tsx`/`not-found.tsx` unless the route does data fetching that can meaningfully be slow or fail:
   - `page.tsx` — always
   - `layout.tsx` — only if the segment needs shared chrome distinct from its parent
   - `loading.tsx` — only if `page.tsx` awaits a data fetch
   - `error.tsx` — only if `page.tsx` awaits a data fetch that can throw
4. **Default to a Server Component** for `page.tsx`. Fetch data directly in the component with `async function Page()`.
5. **If the page needs a form/mutation**, create a co-located `actions.ts` with a `"use server"` function, validated with `zod`, referenced via [the node skill](../node-api-builder/SKILL.md) conventions for error shape.
6. **Add `generateMetadata`** with at least `title` and `description`.
7. **Wire up navigation** — check `src/components/layout/Sidebar.tsx` or `Nav.tsx` (if present) and add a link to the new route.

## Reference template

See [page-template.tsx](./page-template.tsx) for the canonical starting structure and [actions-template.ts](./actions-template.ts) for the Server Action pattern.

## Checklist before finishing
- [ ] Route follows existing folder/route-group conventions in `src/app/`
- [ ] Server Component by default, `"use client"` only where required
- [ ] `generateMetadata` present
- [ ] Server Actions validate input with `zod`
- [ ] New route linked from navigation if it's a primary feature
- [ ] Test added if the route contains non-trivial logic
