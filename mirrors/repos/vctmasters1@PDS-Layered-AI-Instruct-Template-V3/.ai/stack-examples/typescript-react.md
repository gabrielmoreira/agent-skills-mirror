# Stack Example — TypeScript + React + Vite

> Reference snippet. Copy into a real module's `.ai/instruct.md` and tune.

## Contents

| Section | What's here |
|---|-------------|
| [Code Organization](#code-organization) | Feature folders, routing, state |
| [Imports](#imports) | Path aliases and cross-feature rules |
| [TypeScript](#typescript) | Compiler flags and `any` policy |
| [React](#react) | Components, hooks, effects |
| [Testing](#testing) | Vitest, Testing Library, Playwright |

## Code Organization

- **Feature-first folders** under `src/features/<feature-name>/` — each feature owns its routes, components, hooks, services. No `src/components/` dumping ground.
- **Cross-feature reuse** goes in `src/shared/` (utilities, hooks) or the workspace's `ui-component/` package (presentational components). Never import from another feature's internals.
- **Routing**: a single `src/router.tsx` declares all routes; features export a `routes` array, not raw `<Route>` JSX scattered across files.
- **State**: server state via TanStack Query, UI state via component-local `useState`/`useReducer`. Redux/Zustand only with a documented reason in the module's `.ai/instruct.md`.
- **No barrel files** (`index.ts` re-exports) except at the public boundary of a package — they kill Vite tree-shaking inside an app.

## Imports

- Path aliases only for `@/` → `src/`. No deep relative imports (`../../../`).
- A feature **must not** import from `src/features/<other-feature>/`. Cross-feature communication goes through `shared/` or a route-level page.
- Test files import from the same paths as production code; no `__mocks__` shadowing without a comment explaining why.

## TypeScript

- `strict: true`, `noUncheckedIndexedAccess: true`, `exactOptionalPropertyTypes: true` in `tsconfig.json`.
- No `any`. If you must escape, use `unknown` and narrow; add a `// TODO(types):` comment.
- Prefer `type` over `interface` for component props (cleaner unions); use `interface` for class-shaped objects.

## React

- Functional components only. Named exports only.
- One component per file. Filename is `PascalCase.tsx` for components, `camelCase.ts` for hooks/utilities.
- Effects: minimize. If a `useEffect` is doing data fetching, replace with TanStack Query.
- Suspense boundaries are explicit and live at route level — not inside leaf components.

## Testing

- Vitest + Testing Library for unit/integration.
- One `*.test.tsx` per non-trivial component. Tests query by role/label, not by test-id (test-ids only when there is no accessible alternative).
- Playwright for end-to-end. E2E specs live in the app root `e2e/` directory, never inside `src/`.
