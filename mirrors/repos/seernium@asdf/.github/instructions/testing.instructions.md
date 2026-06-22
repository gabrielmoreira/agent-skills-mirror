---
applyTo: "**/*.test.ts,**/*.test.tsx,**/*.spec.ts,**/*.spec.tsx"
description: "Testing conventions across the stack (Vitest, React Testing Library, Playwright)"
---

# Testing Conventions

- Unit/component tests: Vitest + React Testing Library. Query by role/label/text, never by CSS class or `data-testid` unless there's no accessible alternative.
- One `describe` block per unit, `it`/`test` names read as a sentence: `it('shows a validation error when email is invalid')`.
- Mock at the network boundary (`msw`) instead of mocking internal modules where possible.
- E2E tests (Playwright) live in `e2e/`, target user flows, not implementation details.
- Every bug fix gets a regression test that fails before the fix and passes after.
- No `test.skip` / `it.todo` left in committed code without a linked issue reference in a comment.
- Snapshot tests are discouraged for components with logic; acceptable only for stable, presentational markup.
