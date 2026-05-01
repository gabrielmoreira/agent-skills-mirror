---
name: tailwind-design-system
description: Build, audit, and refactor Tailwind CSS interfaces and design systems. Use when Codex is asked about Tailwind classes, component variants, utility consistency, tokens, theme variables, responsive patterns, class detection, dynamic class issues, production CSS size, design-system enforcement, or Tailwind UI polish.
license: MIT
---

# Tailwind Design System

## Core Workflow

1. Identify Tailwind version, framework, styling architecture, component library, token source, and build setup.
2. Inspect existing patterns before adding new utilities, colors, spacing, shadows, or radii.
3. Define design tokens and component variants before one-off class strings multiply.
4. Use complete static class names where Tailwind must detect utilities. Avoid dynamic string construction that the compiler cannot see.
5. Keep responsive, state, dark-mode, and data/ARIA variants predictable.
6. Verify production CSS generation and visual output in the browser.

## Design System Priorities

- Tokens: colors, typography, spacing, radius, shadows, borders, z-index, motion, and breakpoints should be deliberate.
- Components: define variants for buttons, inputs, cards, nav, modals, tables, badges, alerts, and menus.
- Consistency: prefer shared component APIs or variant helpers over repeated ad hoc class clusters.
- Responsiveness: design mobile, tablet, and desktop behavior explicitly.
- Accessibility: preserve focus styles, contrast, hit targets, disabled states, and semantic HTML.
- Production: make sure Tailwind can detect classes and avoid shipping accidental unused CSS.

## Freshness Rule

Tailwind CSS source detection and configuration changed significantly across versions. Verify current official Tailwind docs before giving version-sensitive guidance about config files, `@source`, content detection, plugins, or production CSS behavior.

## Deliverable Shape

For Tailwind work, provide:

- Tailwind version and integration assumptions
- Token/component patterns found
- Source detection or build risks
- Refactor or design-system recommendations
- Accessibility and responsive-state checks
- Production CSS verification steps

## References

- Read `references/tailwind-system-checklist.md` when auditing or refactoring Tailwind UI.
