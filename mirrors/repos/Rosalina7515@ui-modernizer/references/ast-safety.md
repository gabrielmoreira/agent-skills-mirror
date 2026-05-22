# AST safety net (v0.7+)

Before v0.7, ui-modernizer relied on regex to find Tailwind class strings inside source files. That worked for ~95% of cases but had three honest weaknesses:

1. A class string inside a JS comment or markdown code block could be falsely "modernized".
2. A `cn("base", isActive && "active")` call needed Claude to be very careful about which string was an argument vs. a variable.
3. Vue's `:class="[...]"` array bindings were brittle.

v0.7 introduces **AST-backed extraction** for `.jsx` / `.tsx` files, plus a tightened best-effort scanner for `.vue` / `.svelte` files (full AST for those is a v0.8 stretch goal).

## 1 · The contract

`scripts/ast-extract.mjs <file>` returns every class string in a file together with:
- **Where** it lives (line, column, attribute name).
- **What kind** of position (`jsx-attr`, `template-quasi`, `cn-arg`, etc.).
- **Whether** it's safe to mechanically substitute classes inside it (`editable: true | false`).

Editable = `true` means: this string is a known-static container, and replacing class names inside it cannot accidentally break logic. Editable = `false` means: the string is conditional / dynamic / a directive key — leave it alone unless you're certain.

## 2 · What gets extracted (JSX / TSX, via `@babel/parser`)

| Position | `editable` | Example |
|---|---|---|
| `<div className="...">` | ✅ true | `<div className="bg-zinc-50">` |
| `<div className={"..."}>` | ✅ true | `<div className={"bg-zinc-50"}>` |
| Template literal quasi | ✅ true | `` className={`bg-zinc-50 ${size}`} `` — the `"bg-zinc-50 "` part |
| `cn("..." , ...)` argument | ✅ true | `cn("bg-zinc-50", isActive && "ring-2")` |
| Conditional consequent / alternate | ✅ true | `className={ok ? "text-emerald-600" : "text-rose-600"}` |
| Object property key (in `cn({...})`) | ✅ true | `cn({ "bg-zinc-50": always })` |
| Identifier / variable reference | ❌ false | `className={dynamicClasses}` — opaque, skipped |
| Unknown function call | ❌ false | `className={mySpecialFn(x)}` — skipped |

Recognized class-merger calls: `cn`, `clsx`, `classNames`, `twMerge`, `twJoin`, `cva`. Add more by editing `CN_CALLS` in `ast-extract.mjs`.

## 3 · What gets extracted (Vue, best-effort)

Until v0.8 adds full Vue AST:
- Only `<template>` block is scanned (script/style ignored).
- `class="..."` → editable.
- `:class="[...]"` / `:class="{...}"` — string literals inside are editable; variables are skipped.

This catches the common cases. It misses: classes computed in `<script setup>` and bound dynamically.

## 4 · What gets extracted (Svelte, best-effort)

Until v0.8:
- `<script>` and `<style>` blocks are masked out.
- `class="..."` → editable.
- `class:foo={bool}` directives → flagged but **not editable** (the key is tied to component state).

## 5 · How the Skill uses this

The SKILL.md Step 5 (APPLY) now recommends:

```
1. Run ast-extract for each file in the plan: node scripts/ast-extract.mjs <file>
2. For each editable string in the output:
   a. Match its content against modernization rules.
   b. Apply the rule using Edit tool, scoped to that line/column.
3. Never touch strings with editable=false.
```

This makes the "we don't touch business logic" promise *mechanically verifiable* — Claude only edits strings the AST has identified as static class containers.

## 6 · Graceful degradation

`ast-extract.mjs` is **optional safety**. If `@babel/parser` isn't installed:
- Script exits with `{ ok: false, reason: 'parser-missing', installHint: ... }`.
- The Skill falls back to v0.6-style regex extraction.
- Modernization still works, just without the AST guarantee.

To enable: `npm install --save-dev @babel/parser @babel/traverse` (already in `optionalDependencies`, so `npm install --include=optional` will pick them up).

## 7 · Known limitations (will improve in v0.8+)

- Vue and Svelte still use a (tightened) scanner, not a full parser.
- `.mdx` files are not handled (Markdown + JSX) — they fall back to regex.
- Source maps from build outputs (`.next/`) are out of scope.
- Inline `<style>` attributes are not parsed (they're CSS-in-attr, separate problem).

## 8 · Try it

```bash
# Single file
node scripts/ast-extract.mjs app/page.tsx --pretty

# Multiple files, JSON output
node scripts/ast-extract.mjs app/page.tsx components/Card.tsx
```

Example pretty output:
```
app/page.tsx  [.tsx]  via babel
  12 class string(s):
    L 14:  4  ✓  jsx-attr            "relative"
    L 21: 17  ✓  jsx-attr            "sticky top-0 z-40 backdrop-blur-md bg-white/70 dark:bg-zinc-..."
    L 36: 14  ✓  jsx-attr            "mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10"
    ...
```
