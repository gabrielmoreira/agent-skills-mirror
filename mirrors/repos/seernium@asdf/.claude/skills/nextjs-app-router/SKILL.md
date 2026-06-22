# Skill: Next.js App Router Structure Generation

Synthesizes App Router nodes with corresponding server/client component boundaries.

## Steps
1. Create route directory (`src/app/<route-path>`)
2. Build async `page.tsx` with server-level data fetching using Suspense
3. Implement `loading.tsx` skeleton layout
4. Isolate client mutations in Server Action modules (`actions.ts`)

## Output Files
- `page.tsx` — Async server component with Suspense boundaries, notFound handling, and cached fetch
- `loading.tsx` — Loading skeleton for Suspense fallback
- `actions.ts` — Server Actions with Zod validation and revalidateTag

## Templates
- See `page-template.tsx` for route page structure
- See `actions-template.ts` for Server Action pattern