---
name: ui-ux-pro-max
description: UI/UX design intelligence for web and mobile. Includes 50+ styles, 161 color palettes, 57 font pairings, 161 product types with reasoning rules, 99 UX guidelines, and 25 chart types across 10 technology stacks. Use when designing UI, choosing palettes, typography, or component architecture.
---

<!--
  Source: nextlevelbuilder/ui-ux-pro-max-skill
  File:   https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/.claude/skills/ui-ux-pro-max/SKILL.md
  Install: npx uipro init --ai claude
  Used by: ui-agent
-->

# UI/UX Pro Max

## When to trigger
- User requests UI/UX design
- Keywords: "component", "layout", "design system", "color palette", "landing page", "dashboard"
- Any new visual surface

## Reference files

This skill's folder contains searchable databases (loaded on demand):

- `styles.md` — 50+ styles (glassmorphism, brutalism, neumorphism, bento grid, ...)
- `palettes.md` — 161 color palettes with HEX codes
- `fonts.md` — 57 font pairings (heading + body combos)
- `products.md` — 161 product types with reasoning rules
- `guidelines.md` — 99 UX guidelines
- `charts.md` — 25 chart types across stacks

*(Stub files will be created as needed — see `styles.md` for example)*

## Supported stacks

React · Next.js · Astro · Vue · Nuxt · Svelte · SwiftUI · React Native · Flutter · HTML+Tailwind (default)

## Design process

### 1. Understand the need
- What product type? (SaaS landing, dashboard, portfolio, ...)
- What audience?
- What tone? (serious / playful / technical / luxury)

### 2. Pick a style
Look up `styles.md` — pick one matching the product type + tone.

### 3. Pick a palette
Look up `palettes.md` — match brand identity. Pay attention to contrast for accessibility.

### 4. Pick typography
Look up `fonts.md` — pick a heading + body pair. Web-safe or Google Fonts preferred.

### 5. Component plan
- Layout (grid system, hero, sections)
- Components (reuse shadcn/ui where possible)
- Interaction states (hover, focus, loading, error)

### 6. Accessibility check
- Contrast ratio WCAG AA min
- Aria labels on interactive elements
- Keyboard navigation order
- Focus indicators visible

## Output format

```markdown
## Design Summary

**Product type:** <type>
**Style:** <name> — *reason for choice*
**Palette:**
  - Primary: #HEX
  - Secondary: #HEX
  - Accent: #HEX
  - Text: #HEX
  - Background: #HEX

**Typography:**
  - Heading: <font>
  - Body: <font>
  - Mono: <font>

**Layout:**
<grid/structure description or ASCII sketch>

**Key components:**
- <Component> — <purpose>

**Accessibility:**
- <aria notes>
- <keyboard nav>
- <contrast verified>

**Responsive breakpoints:**
- Mobile: <behavior>
- Tablet: <behavior>
- Desktop: <behavior>
```

## Rules

- Default stack: Tailwind v4 + shadcn/ui.
- Never introduce new design dependencies silently — flag as a decision.
- Reuse existing components before creating new ones.
- Dark mode + responsive by default.
- Accessibility is mandatory — every component gets aria + keyboard nav.
- Never write implementation code — produce a brief, builder codes from it.
