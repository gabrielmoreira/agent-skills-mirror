---
name: test-writer-vitest-rtl
description: Write unit and component tests using Vitest and React Testing Library, or integration tests for API routes/Server Actions. Use when asked to "write tests", "add test coverage", or "test this function/component".
---

# Test Writer Skill (Vitest + RTL)

## Process

1. Identify what's being tested: pure function → unit test in `src/**/*.test.ts` next to the source file; component → `*.test.tsx` next to the component; API route/Server Action → integration test in `src/**/__tests__/` or co-located.
2. Cover, at minimum: the happy path, one validation/error path, and any edge case explicitly mentioned by the user or visible in the code (empty arrays, null, boundary numbers).
3. For components, query by accessible role/label/text (`getByRole`, `getByLabelText`) — fall back to `data-testid` only when there is no accessible query available.
4. For async behavior, use `findBy*` queries or `waitFor`, never arbitrary `setTimeout`.
5. For Server Actions/API routes, mock the database layer at the module boundary (e.g. `vi.mock('@/server/db')`) rather than hitting a real database.
6. Run `pnpm test <path>` after writing to confirm the test passes (and would have failed before the fix, for regression tests).

## Test skeleton

```ts
import { describe, it, expect, vi } from "vitest";

describe("<unit under test>", () => {
  it("does the expected thing on the happy path", () => {
    // arrange, act, assert
  });

  it("handles the error/edge case", () => {
    // arrange, act, assert
  });
});
```

## Checklist
- [ ] Happy path covered
- [ ] At least one failure/edge case covered
- [ ] No arbitrary `setTimeout`/sleep in async tests
- [ ] Mocks isolated at module boundary, not deep internals
- [ ] `pnpm test` passes locally
