---
name: tailwind-design-system
description: Apply or extend the project's Tailwind design tokens (colors, spacing, typography) consistently, and audit existing markup for hardcoded/arbitrary values that should use tokens instead. Use when asked to "fix styling", "make this consistent with the design system", "add a new color/theme token", or "convert this to Tailwind".
---

# Tailwind Design System Skill

## When extending the design system

1. Open `tailwind.config.ts` and add the new token under `theme.extend` — never replace `theme` wholesale.
2. For colors, use CSS variables defined in `src/app/globals.css` (`--color-*`) and reference them in the Tailwind config so dark mode "just works" via variable swapping:
   ```ts
   colors: {
     primary: "hsl(var(--primary) / <alpha-value>)",
   }
   ```
3. Re-export new tokens' usage examples in [tokens-reference.md](./tokens-reference.md) so future requests can discover them.

## When auditing/fixing existing markup

1. Search for arbitrary value syntax: `\[#`, `\[rgb`, `\[hsl`, inline `style=`.
2. For each hit, find the closest existing token in `tailwind.config.ts`. If none fits well, propose a new token rather than leaving an arbitrary value or picking an ill-fitting one.
3. Replace inline `style={{...}}` with Tailwind classes unless the value is genuinely computed at runtime (animation progress, chart dimensions) — in that case keep `style` but isolate it to only the dynamic property.
4. Run class sorting via Prettier (`prettier-plugin-tailwindcss` is configured) — don't hand-order utility classes.

## Checklist
- [ ] No new hardcoded hex/rgb/hsl values outside `globals.css`
- [ ] New tokens added to `theme.extend`, not overriding base theme
- [ ] Dark mode variant (`dark:`) considered for any new color usage
- [ ] Responsive variants applied mobile-first
