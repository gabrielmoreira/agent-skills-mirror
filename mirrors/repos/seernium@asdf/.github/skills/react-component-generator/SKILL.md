---
name: react-component-generator
description: Generate a new React component with the repo's standard folder structure (component, types, test, barrel export). Use when asked to "create a component", "build a UI piece", or "add a new <X>" that is a reusable UI element.
---

# React Component Generator

## Process

1. Confirm whether the component is **presentational** (no data fetching) or **container** (fetches/owns data). Presentational components are strongly preferred — push data fetching to the Server Component parent and pass props down.
2. Create the folder structure:
   ```
   src/components/<ComponentName>/
     <ComponentName>.tsx
     <ComponentName>.test.tsx
     index.ts
   ```
3. Use [component-template.tsx](./component-template.tsx) as the starting point.
4. Define `<ComponentName>Props` as an exported interface so it can be reused/extended by consumers.
5. Style exclusively with Tailwind utility classes; use the `cn()` helper from `src/lib/utils.ts` for conditional classes.
6. Add a basic render + interaction test using React Testing Library — see [component-test-template.tsx](./component-test-template.tsx).
7. Export the component from the folder's `index.ts` so consumers import `from '@/components/ComponentName'`, not deep paths.

## Decision: client or server?
Default: no `"use client"` directive. Add it only if the component uses:
- `useState`, `useEffect`, `useReducer`, or any other hook with browser/runtime behavior
- Event handlers (`onClick`, `onChange`, etc.)
- Browser-only APIs (`window`, `localStorage`)

## Checklist
- [ ] Props interface exported
- [ ] No `"use client"` unless actually needed
- [ ] Tailwind only, no inline styles
- [ ] Accessible (labels, roles, keyboard support)
- [ ] Test file created
- [ ] Exported via `index.ts`
