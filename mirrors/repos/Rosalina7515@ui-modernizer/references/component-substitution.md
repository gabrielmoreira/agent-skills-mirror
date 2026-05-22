# Component substitution (shadcn primitives)

When the user opts in (says **"modernize this UI **and use shadcn components**"** / **"...with shadcn primitives"** / **"...and substitute components"**), ui-modernizer goes one step further: after rewriting `className` strings, it **replaces hand-rolled native elements with shadcn/ui primitives**.

A hand-rolled `<button class="bg-indigo-600 px-4 py-2 rounded-md text-white ...">` becomes `<Button>` — same look, but now you get keyboard semantics, asChild composition, and a single source of truth.

## 1 · Why opt-in

Substitution is **off by default**:
- It modifies more than `className` (touches imports, may add new files via `npx shadcn add`).
- It only makes sense if the project is OK adopting shadcn/ui as its component library.
- The `npx shadcn add` command modifies `components/ui/` and `tailwind.config` / `components.json`.

The user must explicitly say *"and use shadcn"* (or similar). If they don't, skip Step 6b entirely.

## 2 · Workflow (inserted between APPLY and SCREENSHOT-AFTER)

### Step 6a — DETECT SUBSTITUTIONS

```
node scripts/detect-substitutions.mjs
```

Outputs JSON listing every candidate in the project:

```json
{
  "totalCandidates": 12,
  "byComponent": { "button": 7, "input": 3, "badge": 2 },
  "installNeeded": ["button", "input", "badge"],
  "perFile": [
    { "file": "app/page.tsx", "line": 42, "match": "<button ...>",
      "suggestedComponent": "Button", "suggestedVariant": "default",
      "confidence": "high" }
  ]
}
```

### Step 6b — SHOW PLAN

Show the user the table:
- N candidates across M files
- Which shadcn components will be installed
- Approximate import statements that will be added

Ask: **"Run `npx shadcn add button input badge`? (y/n/pick)"**

### Step 6c — INSTALL

If shadcn was never set up here, run `npx shadcn init` first. The user must answer its prompts (style, base color, CSS variables, etc.) interactively.

Then `npx shadcn@latest add <component1> <component2> ...` in one command.

If any install fails (network, version mismatch, etc.): STOP and surface the error. Don't proceed with rewrites — leaving the code in a half-installed state would be worse than not running.

### Step 6d — REWRITE

For each entry in `perFile`:
1. Open the file.
2. Replace the candidate JSX with the shadcn equivalent (see `references/shadcn-component-map.md` for the per-pattern mapping).
3. Add the import at the top of the file (deduplicate against existing imports).
4. Preserve all event handlers, refs, and dynamic props.

### Step 6e — VERIFY

Run the project's type-check (`npm run typecheck` or `tsc --noEmit`) if TypeScript is configured. If errors appear:
- Roll back the substitution edits (the backup from Step 3 covers this).
- Note the failure in the report.
- Continue with screenshot + report — the className modernization still stands.

## 3 · Safety rules

| Rule | Why |
|---|---|
| Substitution requires explicit opt-in | Adds runtime deps + new files |
| Never substitute if `shadcn add` install fails | Half-state worse than no-state |
| Type-check is mandatory if TS configured | Catches missing props |
| Preserve every event handler / ref / data-* attribute | Same hard rule as v0.1 modernization |
| Keep the original JSX wrapping (parent `<div>` etc.) | Wrapper styles often matter — don't collapse them |
| Skip files outside the `uiFiles[]` list from detect-stack | Same scope discipline |

## 4 · Confidence levels

- **high** — Obvious match. The element name + class signature is unambiguous (`<button>` with primary CTA classes).
- **medium** — Likely match. Element type matches a target but classes are unusual (custom palette). Show but ask.
- **low** — Speculative. (Currently excluded from output by default; the script doesn't surface these in MVP.)

## 5 · Per-framework notes

| Runtime | Element source | Import target |
|---|---|---|
| React + Next | `<button>`, `<input>`, `<span>` | `@/components/ui/<component>` |
| Vue + Nuxt | `<button>`, `<input>`, etc. inside `<template>` | Use **shadcn-vue** equivalents — `import { Button } from '@/components/ui/button'`. If shadcn-vue isn't set up, skip substitution and tell the user. |
| Svelte + SvelteKit | `<button>` etc. | Use **shadcn-svelte** equivalents. If not set up, skip and tell the user. |

If the project's `package.json` does not show `shadcn` / `shadcn-vue` / `shadcn-svelte` (or `components.json` is missing), the modernizer must run init first or refuse substitution gracefully.

## 6 · What this does NOT replace

These are intentionally **not** substituted in v0.5 — too much state / accessibility nuance:
- `<dialog>` / modal patterns → would need Dialog with focus traps
- `<select>` → shadcn Select needs different markup (Radix-based)
- Dropdown / menu patterns → state-heavy
- Custom toast / alert systems → require provider setup
- Anything inside `<form>` with custom validation logic — risky

These may be in `v0.6+`.
