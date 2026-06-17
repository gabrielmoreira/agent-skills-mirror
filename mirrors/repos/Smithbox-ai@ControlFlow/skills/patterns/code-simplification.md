# Code Simplification

## Purpose

Use this skill when working code needs to become easier to understand, review, or maintain without changing observable behavior. Simplification is not a license to rewrite; it is a disciplined refactor with a narrow boundary and proof that behavior stayed the same.

## Minimum Viable Change Ladder

Before adding code, layers, dependencies, or configuration, stop at the first rung that satisfies the current acceptance criteria:

1. **Does this need to exist?** If no current requirement, test, or operational constraint needs it, skip it and record the future option outside the implementation.
2. **Can existing project behavior cover it?** Prefer current helpers, schemas, templates, documentation, or process over a new surface.
3. **Can the standard library or native platform cover it?** Prefer language/runtime APIs, browser features, database constraints, shell built-ins, or CI primitives over custom code.
4. **Can an already-installed dependency cover it?** Reuse a dependency already present in the repo before adding another package.
5. **Can one localized line or existing helper cover it?** Prefer the smallest scoped edit that remains readable and testable.
6. **Only then write the minimum new code that works.**

Do not use the ladder to remove safety. Input validation at trust boundaries, error handling that prevents data loss, security controls, accessibility requirements, rollback guidance, and explicitly requested behavior stay in scope. If a deliberate shortcut has a known ceiling, record the ceiling and the upgrade trigger in the execution report or a short code comment when future maintainers need it.

## Chesterton's Fence

Do not remove or rewrite code you cannot explain. Before touching a suspicious branch, helper, abstraction, or guard, establish why it exists and whether that reason still applies.

Minimum understanding checklist:

- What behavior does this code protect or provide?
- Who calls it, and what depends on its current side effects or errors?
- Which tests, fixtures, schemas, docs, or historical commits explain its purpose?
- Is it compensating for a platform, data, migration, or compatibility constraint?
- What would fail if it were removed?

If the answer is unknown, gather more context or stop. Deleting a fence without understanding it is not simplification; it is guesswork.

## Rule Of 500

Keep simplification reviewable. If the expected refactor would touch more than about 500 changed lines, more than a small set of closely related files, or more than one reviewable concern, split it into smaller phases or use a mechanical transformation with separate validation.

Use these bounds:

- One behavioral surface or simplification theme per change.
- Prefer small file sets with obvious ownership and dependency boundaries.
- Keep mechanical renames, formatting, and behavior-preserving refactors separate from feature or bug work.
- If the diff grows past the original intent, stop and report the new scope instead of quietly expanding it.

## Behavior Preservation

Simplification must not change observable behavior unless a separate requirement says so. Inputs, outputs, side effects, error behavior, ordering, persistence, generated artifacts, and public contracts must remain equivalent.

Before editing, identify the baseline checks that describe current behavior. Run the same checks after the edit. For risky code, add characterization coverage before refactoring so the intended preservation is explicit.

## Refactor Heuristics

| Signal | Prefer |
| ------ | ------ |
| Deep nesting or repeated negative conditions | Guard clauses or named predicates that keep the main path readable. |
| A helper with a useful domain name | Keep it, even if inlining would reduce line count. |
| A wrapper that adds no policy, naming, validation, or abstraction value | Inline it after confirming callers do not rely on it as a boundary. |
| Duplicated logic across nearby code | Extract only when the shared behavior is truly the same concept. |
| Comments explaining what obvious code does | Remove or replace with clearer code. Keep comments that explain why. |

## Anti-Rationalization Deltas

Apply the canonical Anti-Rationalization Table in `skills/patterns/llm-behavior-guidelines.md` for scope drift, adjacent cleanup, verification skips, and speculative abstractions. For simplification work, also enforce these local deltas:

| Pattern | Required Action |
| ------- | --------------- |
| "It's just dead code" | Prove it is unreachable with search, tests, or ownership evidence before removal. |
| "A quick rewrite is faster than understanding" | Explain the current contract, then make the smallest behavior-preserving change. |
| "Fewer lines means simpler" | Optimize for comprehension and reviewability, not line count. |
| "A new abstraction or dependency is cleaner" | Walk the Minimum Viable Change Ladder first; use existing behavior, standard library, native platform, or already-installed dependency when it satisfies the acceptance criteria. |

## Stop Conditions

Abandon or re-scope the simplification attempt when:

- You cannot explain why the current code exists.
- Behavior changes are required to make the simplification work.
- Tests are absent and the risk is too high to characterize quickly.
- The diff exceeds the Rule of 500 boundary or crosses unrelated ownership areas.
- The simplified version is harder to read, harder to review, or inconsistent with local conventions.
- A new dependency, schema change, or migration would be needed to complete the refactor.

When a stop condition triggers, leave the working behavior intact and report the blocker, evidence gathered, and a narrower follow-up option.
