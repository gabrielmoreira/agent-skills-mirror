# Tailwind CSS v4 — modernization guide

Tailwind v4 changed enough that the v3 modernization playbook needs adjustments. This file is loaded when `detect-stack.mjs` reports `tailwind.flavor === 'v4'`.

## 1 · What changed in v4

| | v3 | v4 |
|---|---|---|
| Config | `tailwind.config.js` (JS) | CSS-first via `@theme` (optional JS config) |
| Directives | `@tailwind base; @tailwind components; @tailwind utilities;` | `@import "tailwindcss";` |
| Content paths | `content: [...]` in config | Auto-discovered; or `@source` directives |
| PostCSS plugin | `tailwindcss` | `@tailwindcss/postcss` |
| Theme tokens | `theme.extend.colors.brand` | `@theme { --color-brand-600: oklch(...); }` |
| Default colors | RGB-ish, fixed scale | OKLCH, perceptually uniform |
| `tailwindcss-animate` | Installed plugin | Built-in (`animate-in`, `fade-in`, etc.) |

## 2 · Detection sanity

If detect-stack says v4 but you see `@tailwind base;` in globals.css → conflict. Report it; don't proceed automatically. Likely the project is mid-migration.

## 3 · Globals.css template (v4)

Use this shape instead of the v3 globals.css template:

```css
@import "tailwindcss";

@theme {
  --font-sans: "Inter", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;

  --radius: 0.5rem;

  /* Accent — overwrite or extend if a brand color is detected */
  --color-primary-500: oklch(0.62 0.22 270);
  --color-primary-600: oklch(0.55 0.24 270);
  --color-primary-700: oklch(0.47 0.22 270);
}

/* dark mode opt-in via class */
@custom-variant dark (&:where(.dark, .dark *));

@layer base {
  body {
    @apply min-h-screen bg-white dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100 antialiased;
    font-feature-settings: "rlig" 1, "calt" 1;
  }
  ::selection { @apply bg-indigo-500/20; }
  :focus-visible {
    @apply outline-none ring-2 ring-indigo-500 ring-offset-2 ring-offset-white dark:ring-offset-zinc-950;
  }
}
```

## 4 · Class-mapping differences from v3

Most v3 class names still work — but a few have changed:

| v3 class | v4 class |
|---|---|
| `bg-opacity-50` | `bg-black/50` (already preferred in v3; mandatory in v4) |
| `ring-opacity-*` | `ring-color/opacity` syntax |
| `flex-shrink-0` | `shrink-0` |
| `flex-grow-0` | `grow-0` |
| `overflow-ellipsis` | `text-ellipsis` |

The exhaustive v3 → v4 list is in Tailwind's upgrade guide. Modernizer should leave any unknown class alone (white-list policy from `tailwind-modernization.md` still applies).

## 5 · Don'ts in v4

- **Don't write `tailwind.config.js`** for a v4 project unless one already exists. CSS-first config is the idiomatic choice.
- **Don't install `tailwindcss-animate`** — `animate-in`, `fade-in`, etc. are built-in in v4.
- **Don't replace `oklch(...)` values** with hex. The OKLCH defaults exist because they're perceptually superior in dark mode.

## 6 · Brand color injection (v4)

When `detect-brand.mjs` finds a brand color in v4, the modernizer should **add or extend `@theme` block** rather than touching a JS config:

```css
@theme {
  --color-brand-50:  ...;
  --color-brand-100: ...;
  ...
  --color-brand-950: ...;
}
```

Then `bg-brand-600` etc. work automatically. If only a single value is detected, generate a 9-step scale from it using a simple OKLCH lightness ramp.
