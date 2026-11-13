# Formats

Use these when the project has no format of its own. When it does (a plans or specs folder, an issue template, a README style), follow its location and template instead.

## Plan: `docs/design-system/plan.md`

```md
# Design system plan

## Summary
What the module is, where it lives, and what changes for people building UI, in three or four sentences.

## What exists
The stack and UI libraries, the current module or its absence, and the spec files, with paths.

## Critique
Each finding about the current module: the problem, its evidence (`file:line`), and the change.

## Direction
Only when the look was open: the pick, its references, and what it sets.

## Spec
The `DESIGN.md` path and the approved spec changes. Changes the user declined, and why.

## Module
Location, the flat layout, how tokens flow from `DESIGN.md` into code, and the dependency rule.

## Catalog
| Component | Tier | Props and variants | Tokens | Absorbs | Composes |
| --- | --- | --- | --- | --- | --- |
| Button | atom | `variant: primary \| secondary \| ghost`, `size: sm \| md`, `loading` | `primary`, `rounded.md`, `label-md` | 2 duplicates, 14 inline buttons | — |

## Opportunities
Every opportunity by kind, each occurrence as `file:line`, and the component or token that absorbs it.
Opportunities left out, with the reason.

## README outline
The module README's sections, per the README format below.

## Slices
In build order. Each: the components it delivers, the call sites it migrates, its acceptance checks,
and what it depends on.

## Open questions
Ideally none. Anything here blocks the slice that needs it.
```

## Component header

Mark each component's tier where a reader of the code sees it, in the language's doc comment, with one line on what it is for:

```tsx
/**
 * Molecule: a labeled text input with its hint and error.
 */
export function TextField(props: TextFieldProps) {
```

```rust
/// Organism: a dialog with a title, body, and footer actions.
pub struct ConfirmDialog { /* … */ }
```

## README

The module's `README.md`, written for people:

- **What it is**: one paragraph, and a link to `DESIGN.md` as the source of truth for the look.
- **Explore**: how to see the components (the catalog command, when the project has one; otherwise the catalog table and the tests), and where each file lives.
- **Catalog**: one table per tier (atoms, molecules, organisms), each row the component, what it is for, and its main props.
- **Tokens**: where they come from, how to change one (`DESIGN.md` first, then regenerate or update the token file), and how components read them.
- **Rules**: plain props in, no app imports, no raw values, the allowed dependencies, a tier on every component.
- **Add or change a component**: check the catalog for an existing one, pick its tier, write it with its test, add it to the catalog, and lint `DESIGN.md` when tokens changed.
- **Test**: the command and what every component's test covers (renders, variants, states, keyboard, labels).

## Issue

```md
## What
The slice in two or three sentences: the components it delivers and the call sites it migrates.

## Components
- `Button` (atom): `variant`, `size`, `loading`. Tokens: `primary`, `rounded.md`, `label-md`.

## Call sites
- `src/features/billing/PayButton.tsx:12`: replace with `Button variant="primary"`.

## Acceptance
- [ ] Each component renders and is tested in isolation, covering its variants and states.
- [ ] Every listed call site uses the module, and no raw value remains at those sites.
- [ ] The module README's catalog lists the new components.

## Context
Plan: docs/design-system/plan.md#slices · Spec: DESIGN.md
Blocked by: #12
```

Title each issue with the outcome ("Buttons come from the design system"), not the layer. When the user picked Issues without a plan, put each issue's component details and call sites in full, so it stands without the plan, and link `DESIGN.md` for the tokens.
