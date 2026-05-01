---
applyTo: "src/components/**,src/pages/**,src/app/**,src/features/**/*.tsx"
---
# Frontend Development Standards

## Component Architecture
- Default to React Server Components unless interactivity is needed
- Client components: add `'use client'` directive and name files `*.client.tsx`
- Co-locate component logic: `MyComponent.tsx`, `MyComponent.test.tsx`, `MyComponent.module.css`

## UI Components
- **Always** use components from `@/components/ui/*` — never raw HTML div/span for UI elements
- Never write inline styles; use CSS modules or the design system tokens
- All interactive elements must have `aria-label` or meaningful visible text

## State Management
- Local state: `useState`, `useReducer`
- Server state / caching: React Query (`@tanstack/react-query`)
- Global client state: [your state library, e.g., Zustand]
- Form state: `react-hook-form` with `zod` validation schemas

## Forms
- All forms use `react-hook-form`
- Validation schemas in separate `schemas/[form-name].schema.ts` files
- Use `defaultValues` to prevent unnecessary re-renders
- Show inline field errors, not just top-level form errors

## Data Fetching
- Use React Query hooks for all server data
- Handle loading, error, and empty states explicitly — never assume data exists
- Use optimistic updates for mutations that affect visible UI

## Naming Conventions
- Components: `PascalCase` (e.g., `UserProfileCard`)
- Hooks: `camelCase` starting with `use` (e.g., `useUserProfile`)
- Event handlers: `handleXxx` (e.g., `handleSubmit`, `handleClose`)
- Boolean props: `is`, `has`, `can` prefix (e.g., `isLoading`, `hasError`)
