---
applyTo: "**/*.ts,**/*.tsx"
description: "TypeScript strictness and typing conventions"
---

# TypeScript Conventions

- `strict: true`, `noUncheckedIndexedAccess: true` are assumed in `tsconfig.json` — write code that satisfies them.
- Never use `any`. Use `unknown` + narrowing, or a proper generic.
- Prefer `type` for object shapes/unions, `interface` only when declaration merging is needed.
- Use discriminated unions for state machines (e.g. `{ status: 'idle' } | { status: 'loading' } | { status: 'error'; message: string }`).
- Co-locate types with usage; promote to `src/types/` only when shared across 3+ files.
- Use `satisfies` instead of type assertions (`as`) wherever possible.
- All async functions must have explicit `Promise<T>` return types.
- Use `zod` schemas as the single source of truth, infer TS types via `z.infer<typeof schema>` rather than hand-writing duplicate types.
- Avoid enums; prefer `as const` string unions.
- Path aliases: import via `@/` (mapped to `src/`), never deep relative imports like `../../../`.
