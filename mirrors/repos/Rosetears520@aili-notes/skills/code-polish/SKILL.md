---
name: code-polish
description: >
  Engineering Refinement & Standardization Specialist: simplify, standardize, and engineer code into explicit, maintainable structure without changing behavior. Authorized to perform structural refactors inside a logical unit (function/component/module) when needed to enforce project standards and clarity; requires an explicit Plan of intended edits and safety checks.
---

# Engineering Refinement & Standardization (Instruction-Only)

Perform a high-safety refinement pass that **simplifies**, **standardizes**, and **engineers** code into explicit, maintainable structure while preserving **exactly** the same behavior. This is not limited to superficial “polish”: structural simplification is encouraged when it improves clarity and consistency.

Core principle: **Prioritize explicit structure over brevity** (e.g., refactor dense one-liners or ternary chains into clear `if/else` or `switch`).

## Simplification goals (measurable; use in Plan)

When choosing/refusing edits, prefer changes that make one of these measurable improvements within a logical unit:

- Reduce branching paths (fewer distinct condition branches).
- Reduce nesting depth (un-nest / fewer indentation levels).
- Reduce cyclomatic complexity (simpler control flow).
- Reduce duplication (merge repeated expressions/branches into one named path).
- Reduce surface area (smaller function/component via extraction + reuse).

## Output protocol (hard)

To prevent "plan-after-the-fact", separate planning from edits:

- This is a multi-round workflow by default.
- Phase 1 (Plan only): output a **Plan** section and **do not** include any patch/code in the same message.
  - Stop immediately after the Plan (treat it as a stop sequence).
- Phase 2 (Patch only): only after explicit confirmation (or an automated "continue" signal), output **only** a machine-applicable **Unified Diff** patch. No additional prose.

If operating in one-shot/stateless automation where a second turn is impossible, use "atomic mode":
- Output the Plan followed by the patch in the same message.
- The patch must be a Unified Diff and must be strictly derived from the Plan (no extra edits beyond planned actions).

Do not output chain-of-thought or hidden reasoning. The Plan is the only allowed pre-edit content.

## Project Standards Discovery (mandatory)

Before editing anything, do these checks (in this order):

1) Discover project-provided standards (do not guess)
- Search for and follow the most authoritative and closest-in-scope guidance available in the target repository, such as:
  - `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `README.md`
  - `.editorconfig`, Prettier/ESLint/ruff configs, `pyproject.toml`, `tsconfig.json`
  - “rules” files (e.g., `.cursorrules`, `.windsurfrules`) if present
- Scope rule: nearest-file-wins for nested instructions; if multiple documents conflict, follow the more specific scope, then the more recent/explicit constraint.
- If no standards are provided by the project, fall back to the default manifesto below.

### Standards summary template (required in Plan phase)

In the Plan phase, include a short standards summary using this template:

- Standards sources found:
  - `<path>`: `<1-line summary of rules applied>`
  - `<path>`: `<1-line summary of rules applied>`
- Conflicts resolved:
  - `<rule A>` vs `<rule B>` -> `<decision + why>`
- Defaults used (only if none found):
  - `<which Default Project Manifesto bullets were applied>`

2) Detect language(s)
- Identify which language(s) are involved in the current change footprint (may be multi-language).
- For each detected language, apply the corresponding language-specific high-risk rules by reading only the relevant reference file(s) under `references/`:
  - Python: `references/python.md`
  - Go: `references/go.md`
  - C/C++: `references/c-cpp.md`
  - JS/TS: `references/js-ts.md`
- If language is unclear or mixed in a way you cannot confidently reason about, default to **high risk** and strongly prefer a no-op.

## Default Project Manifesto (fallback; enforce unless overridden)

If the project does not provide explicit standards, enforce these defaults:

### Cross-language

- Prefer explicit structure over brevity; refactor clever one-liners into clear blocks.
- No nested ternaries; refactor into `if/else` or `switch`.
- Prefer clearly named intermediate variables over repeated/compound expressions.
- Prefer early returns/guard clauses when they clarify intent.
- Tooling precedence: if the repo uses canonical formatters/linters/type-checkers (e.g., Prettier/ESLint, ruff/mypy), treat their configs and outputs as authoritative. Do not fight the tool; avoid “hand-formatting” or style conversions that the tool will revert.

### TS/JS (including React)

- Prefer `function` declarations over arrow functions by default, unless the project’s lint/formatter rules (or framework conventions) prefer arrow functions.
- Prefer explicit return types for exported/public functions and non-trivial locals; avoid `any`/implicit widening in typed codebases.
- Prefer explicit, stable React props shapes: define `Props` as an interface/type and keep props destructuring straightforward.
- See `references/js-ts.md` for language-specific high-risk rules.

### Python

- If the file/module already uses typing, add/keep explicit return types for non-trivial functions; avoid half-typed churn.
- Prefer straightforward `if/elif/else` over dense comprehensions when complexity grows.
- See `references/python.md` for language-specific high-risk rules.

### Go

- Prefer explicit control flow and error handling; reduce nesting with early returns.
- Keep public API surfaces stable; do not rename exported identifiers.
- See `references/go.md` for language-specific high-risk rules.

## Non-negotiables (zero behavior change)

Preserve exactly:
- Outputs and serialized formats
- Side effects (I/O, logs that users/tests rely on)
- Error types and messages; throw-vs-return behavior
- Public APIs (function names/signatures, CLI flags, config keys)
- Short-circuit/evaluation order and edge-case semantics
- Observable performance characteristics (avoid new/extra I/O)

If equivalence cannot be confidently proven, **skip the change**.

## Safety gates (hard)

- One intent per change: each change should do only one kind of improvement (e.g., control-flow clarity OR naming OR dead-code cleanup), not a bundle.
- Reversibility: if proving equivalence would take a long explanation, undo/skip that change.
- Negation blindness defense: if inverting control flow or conditions (e.g., guard clauses), explicitly verify De Morgan's laws and double-check compound boolean negations.
- Prefer “structural subtraction” over micro-style churn: extract functions, merge repeated paths, and remove dead branches before considering stylistic rewrites.
- Do not extract helpers or verify logic into new functions if the resulting abstraction is used only once and creates more cognitive load (jumping between functions) than the original inline logic. Simplification should aid reading, not just satisfy metrics.
  
## Scope (Logical Unit Context)

- Primary constraint: keep changes within the user's requested area and/or the provided change footprint.
- Authorized expansion: if you modify any line inside a function/component/class/module, you are authorized and encouraged to refactor the **entire containing logical unit** to enforce consistency, explicit structure, and the project standards.
- Still forbidden: drive-by refactors in unrelated files, repo-wide formatting, mass renames, or dependency/tooling changes not required by the local refactor.

## Mandatory plan (before editing)

Before writing a patch, produce a short **Plan** in this structure (repeat per action):

- File:
- Region:
- Action:
- Reason:
- Goal metric:
- Invariants:
- Safety check:
- Risk skipped:

If all candidates are risky, do a no-op and state: "No safe finishing changes identified; preserving current behavior and diff cleanliness."

## Allowed edits (Structural Simplification)

- Remove unused imports/locals, unreachable code, commented-out dead blocks.
- Structural simplification inside a logical unit, while preserving exact semantics:
  - Un-nesting ("de-tangle") deeply nested blocks.
  - Consolidate conditionals and clarify branching.
  - Extract clearly named variables to explain complex expressions.
  - Refactor complex one-liners (especially ternary chains) into explicit `if/else` or `switch` blocks.
  - Merge repeated branches/returns by extracting a helper or consolidating a shared path.
- Improve local naming for **private/local** variables/helpers (do not rename exported/public symbols).
- Extract file-local constants for magic literals when purely mechanical.
- Update docstrings/comments in the touched region to match current code.

## Avoid by default (high risk)

- Regex/parsing/date-time/float logic rewrites
- Concurrency/async scheduling changes
- Loop/comprehension rewrites that alter evaluation timing/memory use (language-sensitive)
- Any change that would require updating tests' expected outputs

## Formatting & linter policy (scope-safe)

- Do not try to "be" a formatter or linter. Do not guess Black/Prettier/gofmt output.
- Align code with discovered project standards (or the default manifesto), refactoring surrounding legacy patterns if necessary within the same logical unit.
- If the repo clearly uses a canonical formatter, avoid manual formatting churn; let real tooling apply canonical formatting.
- If tool configs exist (e.g., ESLint/Prettier, ruff/mypy), treat them as the source of truth for style constraints; do not perform style conversions that the tool would reject or immediately revert.
- Tool-driven simplification: if static analysis rules exist that *directly* reduce complexity/duplication (e.g., no nested ternaries, complexity limits, duplicate branch detection, unused), prefer refactors that satisfy those rules while keeping behavior identical. Do not invent tool commands; follow repo docs/instructions.

## Validation rules

- Finish-stage default: do not modify tests.
  - Only exception: tests already in scope for this task/run and the edit is purely mechanical synchronization (e.g., renaming a private helper used only inside tests) with no expectation meaning change.
- If a refactor would require changing test expectations, revert/refuse the refactor.
- Any change that alters assertions' meaning/scope or golden outputs is an immediate rollback trigger.
- If you did not run tests, but you discover that you would need to change tests just to compile/run (beyond purely mechanical sync within scope), treat that as an immediate rollback trigger.
- Prefer the fastest relevant checks in the repo and follow the repo's documented execution rules (do not invent commands).
- Report commands run and observed results; if none were run, say so.

## Semantic equivalence checklist (required for structural edits)

For any structural simplification (un-nesting, merging branches, extracting helpers, consolidating conditionals), explicitly verify:

- Inputs/outputs unchanged (including returned shapes and serialization).
- Side effects preserved (I/O, logging, mutations) and still occur under the same conditions.
- Evaluation order and short-circuiting preserved where it can affect behavior.
- Exceptions and error messages preserved (type, message, and when they trigger).
- Boundary cases preserved (null/empty/zero, missing keys, off-by-one, default branches).

If any item cannot be confidently verified, skip or reduce the refactor.

## Domain-rule sanity (required when logic looks “businessy”)

When conditionals encode business rules or invariants, do not “simplify by assumption”:

- Confirm which branches/states are actually possible; if unknown, preserve the explicitness.
- Prefer naming + extraction (make rules explicit) over collapsing rules into fewer lines.

## Reporting requirements (end of run)

Include:
- Concrete edits made (fact-based)
- High-risk candidates skipped + rationale
- Checks run (commands + observed result) or a clear statement that none were run
- If no-op: explicitly state "No changes made" and include the Plan with all candidates marked as skipped.

## Few-shot examples (short)

### Allowed (control-flow clarity, same order)

Original:
```py
if x is not None:
    if x > 0:
        return f(x)
return g()
```

Polish (same checks, same order, no side effects moved):
```py
if x is None:
    return g()
if x <= 0:
    return g()
return f(x)
```

### Forbidden (parsing rewrite)

- Rewriting regex/date parsing/float rounding logic "for readability" is high risk; refuse and prefer no-op.

## Comments policy (conservative)

- Only remove obviously dead/incorrect comments in the touched region.
- Do not add new comments unless they explain a non-obvious invariant, workaround, or hazard that must not be broken.

## Patch format policy (robustness)

- Default: output a **Unified Diff** that is compatible with `git apply` / `patch` tooling.
- If the environment/tooling requires a different patch protocol, follow that protocol, but keep it tool-agnostic when possible.
- If patch application is fragile (unknown file versions, high churn), fall back to explicit `SEARCH_BLOCK` / `REPLACE_BLOCK` pairs with exact string matching.
- Keep copied context minimal (at most 2-3 surrounding lines) to reduce transcription errors and unintended whitespace churn.

## Clarity vs preference (subjectivity defense)

- Do not rewrite code purely due to style preference (e.g., changing `x = x + 1` to `x += 1`) unless it is required as part of a larger planned refactor in the same local region.
- Exception: if a Project Standard (discovered rules) or the Default Project Manifesto explicitly requires a pattern, that standard overrides “don’t churn”; apply the standard only within the authorized scope (Logical Unit Context) and only when behavior equivalence is preserved.
- Rename locals only when names are clearly unclear or misleading (e.g., `tmp`, `data`, `obj`, `foo`).
- Do not perform "synonym churn" renames (e.g., `user_list` -> `users`) when the original name is already specific and readable.

## Docstrings/comments sync (minimal adjustment)

- If updating docstrings/comments is necessary, make the smallest possible edit to remove contradiction with code.
- Preserve existing tone, formatting, indentation, and parameter description structure; do not rewrite wholesale.
