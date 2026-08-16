---
name: safe-refactoring
description: Execute behavior-preserving or intentionally scoped refactors safely. Use this for multi-file renames, component/service extraction, state-management changes, API migrations, concurrency refactors, or any request where unrelated user work and subtle contracts must be preserved.
---

# Safe refactoring

Change structure without losing behavior, protocol validity, or concurrent user edits.

## Before mutation

1. Establish the exact behavior to preserve and the intentional behavior change, if any.
2. Locate callers, implementations, serialized forms, tests, configuration, and external protocol names.
3. Check the working tree and treat unrelated modifications as user-owned.
4. Define mechanical acceptance checks: compile, focused tests, type checks, contract tests, and diff inspection.
5. Split the work into dependency-ordered increments when a single atomic patch would be hard to verify.

## Mutation rules

- Use expected content hashes for existing files; a mismatch means reload and reconcile instead of overwriting.
- Prefer narrow edits and stable compatibility adapters while consumers migrate.
- Keep persisted schema and event changes versioned; tolerate additive fields where forward compatibility is intended.
- Preserve tool-call/result adjacency, event IDs, resource ownership, cancellation, and error semantics during agent-runtime refactors.
- Do not mix broad formatting or unrelated cleanup into the functional diff.
- If a generated artifact should change, update its source and regenerate it with the documented command.

## Verification loop

1. Inspect the resulting diff for accidental deletion, path drift, stale names, and expanded authority.
2. Run the smallest fast check that catches syntax/type errors, then the focused behavior tests.
3. Run broader integration checks when the changed boundary has multiple consumers.
4. Treat warnings or skipped tests relevant to the change as evidence to explain, not automatic success.
5. If verification fails, retain the diagnostic evidence, correct the implementation, and repeat.

## Completion report

Report the behavioral outcome, compatibility decisions, important changed paths, and checks actually executed. Call out anything not verified. Do not describe a refactor as behavior-preserving without evidence.
