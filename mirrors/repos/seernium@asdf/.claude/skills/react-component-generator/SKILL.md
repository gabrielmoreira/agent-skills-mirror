# Skill: Safe Component Engineering

Generates typed, decoupled UI components bundled with rigorous component spec tests.

## Steps
1. Create component file under `src/components/ui/`
2. Define typed prop structure with explicit defaults
3. Build test spec using Vitest + React Testing Library

## Templates
- See `component-template.tsx` — Typed component with state toggle, aria-label, data-testid
- See `component-test-template.tsx` — Render verification with userEvent callback testing