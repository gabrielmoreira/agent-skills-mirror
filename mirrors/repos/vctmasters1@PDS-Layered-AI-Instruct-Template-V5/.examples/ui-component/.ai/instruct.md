# ui-component — Module AI Instructions (Example)

**Scope**: Authoritative for everything inside `.examples/ui-component/`
**Last Updated**: 2026-05-25

> Example module. See [`.examples/README.md`](../../README.md) for context.

---

## Contents

| Section | What's here |
|---|-------------|
| [Module Overview](#module-overview) | What this component library is for |
| [Directory Structure](#directory-structure) | Per-component co-location |
| [Component Rules](#component-rules) | Composition, props, state |
| [Styling Rules](#styling-rules) | Tailwind discipline, no inline styles |
| [Accessibility Rules](#accessibility-rules) | What must be true of every component |
| [Storybook & Testing](#storybook--testing) | Required stories and tests |
| [Global Rules Reference](#global-rules-reference) | Cross-references |

---

## Module Overview

`ui-component` is the **shared React component library**. Every cross-app primitive (`Button`, `Modal`, `Form`, `Table`) lives here. App-specific composites do **not** — they live in the consuming app's `features/` directory.

- **Stack**: React 18, TypeScript, Tailwind CSS, Radix primitives, Storybook 8
- **Public entry**: `src/index.ts` (curated re-exports)
- **Distribution**: consumed as a workspace package; **never** publish secrets or undocumented exports
- **Browser support**: last 2 versions of evergreen browsers; no IE11

---

## Directory Structure

```
ui-component/
├── .ai/instruct.md
├── .dev-docs/index.md
├── src/
│   ├── index.ts                 ← curated re-exports only
│   └── components/
│       └── Button/              ← one folder per component
│           ├── Button.tsx
│           ├── Button.types.ts
│           ├── Button.stories.tsx
│           ├── Button.test.tsx
│           └── index.ts         ← re-export only
├── tailwind.preset.js
└── tsconfig.json
```

---

## Component Rules

1. **One component per folder**, folder name = component name in `PascalCase`. Component-folder casing is the **only** PascalCase directory in the repo and is an explicit exception to [Directory Naming](../../../.ai/conventions.md#directory-naming) (kebab-case elsewhere).
2. **Props are typed in a sibling `*.types.ts`** file. Inline `Props` interfaces are forbidden — they show up duplicated in Storybook controls and tests.
3. **Functional components only.** No class components, no `forwardRef` unless a parent needs a DOM handle (document why in a one-line comment).
4. **No local fetching.** Components are presentational. Data comes in via props. Data fetching belongs in the consuming app.
5. **No `any`**, no `as unknown as`. If a type genuinely can't be expressed, file a TODO and ping in the PR.
6. **Default exports are forbidden.** Named exports only — they survive renames in IDE refactors.

---

## Styling Rules

1. **Tailwind utility classes only.** No CSS files, no `styled-components`, no inline `style={{}}` props.
2. **Use the shared design tokens** in `tailwind.preset.js`. Adding an ad-hoc color in a component is a blocker — extend the preset instead.
3. **Compose class strings with `cn()`** from `src/lib/cn.ts`. Manual string concatenation of conditional classes leaks duplicate utilities into the bundle.
4. **Dark mode**: every color utility has a `dark:` counterpart. The AI must add both or neither.

---

## Accessibility Rules

These are non-negotiable; PRs that violate them must not merge.

1. Every interactive element is reachable by keyboard and visible focus is preserved.
2. Every icon-only button has an `aria-label`.
3. Form inputs have an associated `<label>` (visual or `sr-only`). Placeholders are not labels.
4. Color contrast meets WCAG AA. The AI must run `tailwind-merge` + the design-token palette only — those tokens have been pre-verified.
5. Components built on Radix primitives keep the Radix props untouched unless there's a documented reason — Radix already solves the a11y for them.

---

## Storybook & Testing

1. Every component has at least one `.stories.tsx` covering: default, all variants, all interactive states (hover/focus/disabled/loading).
2. Every component has a `.test.tsx` using Testing Library that covers: renders, primary user interaction, accessibility role queries.
3. **Snapshot tests are not accepted** — they encode nothing meaningful and rot quickly.
4. Visual regression is run in CI via Chromatic; locally optional.

---

## Global Rules Reference

> **→ [No-Duplication Rule](../../../.ai/conventions.md#no-duplication-rule)** — instructions live in one place.
> **→ [File Naming](../../../.ai/conventions.md#file-naming)** — TS/TSX naming. Component folders are the documented PascalCase exception.
> **→ [Never Delete Rule](../../../.ai/maintenance.md#never-delete-rule)** — archive deprecated components instead of removing.
