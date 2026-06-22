---
applyTo: "**/*.tsx,**/*.css"
description: "Tailwind CSS styling and design-token conventions"
---

# Tailwind CSS Conventions

- Utility classes only — no inline `style={{}}` unless the value is truly dynamic/runtime-computed (e.g. a chart's calculated width).
- No custom CSS files except `src/app/globals.css` for `@tailwind` directives, font-face, and CSS variable definitions.
- Use design tokens defined in `tailwind.config.ts` (`theme.extend.colors`, `spacing`, `fontFamily`) instead of arbitrary values like `bg-[#1a1a1a]` — only use arbitrary values when no token fits, and prefer adding the token instead.
- Class ordering: layout → box model → typography → visual → state. Let Prettier's `prettier-plugin-tailwindcss` auto-sort; don't hand-order.
- Use `clsx` (or `cn()` helper combining `clsx` + `tailwind-merge`) for conditional classes — never string concatenation.
- Responsive design is mobile-first: unprefixed classes are the base/mobile style, then layer `sm:` `md:` `lg:` `xl:` up.
- Dark mode via the `dark:` variant driven by the `class` strategy, not OS-only `media`.
- Avoid `@apply` except for genuinely repeated multi-class patterns (e.g. a `.btn-base` used in 5+ places) — prefer a React component over a CSS abstraction.
- Animations: use Tailwind's built-in `animate-*` utilities or `tailwindcss-animate` plugin classes before reaching for a JS animation library.
