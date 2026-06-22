---
mode: agent
description: Perform a safe, test-backed code refactoring with before/after verification.
---

Execute a safe refactoring following this protocol:
1. Run `pnpm test` on the target module — tests must pass before any changes.
2. Invoke `@implementer` to make the refactoring (structure/naming/clarity only — no behavior changes).
3. Run `pnpm test` again — all tests must still pass. If any fail, the refactoring changed behavior and must be reviewed.
4. Run `pnpm tsc --noEmit` and `pnpm lint`.
5. Invoke `@code-reviewer` to verify external behavior is unchanged and type safety is maintained.

The refactoring target: ${input}
