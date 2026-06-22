---
applyTo: "src/components/**/*.tsx,src/app/**/*.tsx"
description: "React component structure, hooks, and state conventions"
---

# React Conventions

- Functional components only. No class components.
- One component per file; file name matches component name in PascalCase (`UserCard.tsx` exports `UserCard`).
- Props are typed with an explicit `interface <Component>Props`, never inline object types for anything beyond 1-2 props.
- Destructure props in the function signature.
- Custom hooks live in `src/hooks/`, named `use<Thing>.ts`, and must follow the Rules of Hooks (no conditional calls).
- Co-locate component-specific subcomponents/styles/tests in the same folder:
  ```
  components/UserCard/
    UserCard.tsx
    UserCard.test.tsx
    index.ts
  ```
- Lift state up only as far as necessary; prefer composition over prop drilling beyond 2 levels — use context or a small store (e.g. Zustand) instead.
- Memoize (`useMemo`/`useCallback`/`React.memo`) only when there's a measured perf reason — do not reflexively wrap everything.
- Forms use `react-hook-form` + `zod` resolver, not manually managed `useState` per field.
- Accessibility: every interactive element must be keyboard-operable; every `<img>` needs `alt`; every form input needs an associated `<label>`.
