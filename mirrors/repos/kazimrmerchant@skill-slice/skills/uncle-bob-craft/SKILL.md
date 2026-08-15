---
name: uncle-bob-craft
description: "Applies Robert C. Martin craft to review and production code: inward Dependency Rule, SOLID in context, rigidity/fragility smells, and pattern use versus cargo cult. Trigger on code review, refactoring, Clean Architecture, SOLID, or Uncle Bob. Not a linter or formatter substitute and never a Clean Code naming/functions duplicate."
version: 1.0.1
category: code-quality
risk: safe
source: community
date_added: "2026-03-06"
author: antigravity-contributors
tags: [clean-code, clean-architecture, solid, code-review, craftsmanship, uncle-bob]
tools: [claude, cursor, gemini]
---

# Uncle Bob Craft

Apply Robert C. Martin (Uncle Bob) criteria for **code review and production**: Clean Code, Clean Architecture, The Clean Coder, Clean Agile, and design-pattern discipline. This skill is **complementary** to the existing `@clean-code` skill (which focuses on the Clean Code book) and to your project's linter/formatter—it does not replace them.

## Overview

This skill aggregates principles from Uncle Bob's body of work for **reviewing** and **writing** code: naming and functions (via `@clean-code`), architecture and boundaries (Clean Architecture), professionalism and estimation (The Clean Coder), agile values and practices (Clean Agile), and design-pattern use vs misuse. Use it to evaluate structure, dependencies, SOLID in context, code smells, and professional practices. It provides craft and design criteria only—not syntax or style enforcement, which remain the responsibility of your linter and formatter.

### Reference files (load on demand)

| File | When to load |
|------|-------------|
| `./reference.md` | Load first for the full aggregated summary of all sources, including heuristics C1–T9-style and component principles (REP/CCP/CRP, ADP/SDP/SAP). |
| `./references/clean-architecture.md` | Load when reviewing layer boundaries, dependency direction, or separation of concerns. |
| `./references/clean-coder.md` | Load when discussing estimation, saying no, sustainable pace, or professionalism. |
| `./references/clean-agile.md` | Load when discussing Iron Cross, TDD, refactoring, pair programming, or agile process. |
| `./references/design-patterns.md` | Load when assessing whether a design pattern is justified or detecting cargo-cult misuse. |

## When to Use

- **Code review**: Apply Dependency Rule, boundaries, SOLID, and smell heuristics; suggest concrete refactors.
- **Refactoring**: Decide what to extract, where to draw boundaries, and whether a design pattern is justified.
- **Architecture discussion**: Check layer boundaries, dependency direction, and separation of concerns.
- **Design patterns**: Assess correct use vs cargo-cult or overuse before introducing a pattern.
- **Estimation and professionalism**: Apply Clean Coder ideas (saying no, sustainable pace, three-point estimates).
- **Agile practices**: Reference Clean Agile (Iron Cross, TDD, refactoring, pair programming) when discussing process.
- **Do NOT use** to replace or override the project's linter, formatter, or automated tests.

## Prerequisites

- **`@clean-code` skill** should be available for naming, functions, comments, formatting, and test heuristics. This skill references it rather than duplicating that material.
- **Project linter and formatter** must be configured and runnable independently. This skill does not enforce syntax or style.
- **Test suite** should exist or be in progress; this skill reminds you to keep tests green during refactoring but does not generate or run them.
- **Windows host (PowerShell)** is the primary environment. Path examples use Windows conventions where relevant.

## Procedure

### Step 1 — Determine context (review vs writing vs refactoring)

| Context | Apply |
|---------|-------|
| **Code review** | Dependency Rule and boundaries; SOLID in context; list smells; suggest one or two concrete refactors (e.g., extract function, invert dependency); check tests and professionalism. |
| **Writing new code** | Prefer small functions and single responsibility; depend inward (Clean Architecture); write tests first when doing TDD; avoid patterns until duplication or variation justifies them. |
| **Refactoring** | Identify one smell at a time; refactor in small steps with tests green; improve names and structure before adding behavior. |

### Step 2 — Check boundaries and Dependency Rule

1. Identify the layers in the changed code (entities, use cases, interface adapters, frameworks/drivers).
2. Verify that **dependencies point inward**: use cases do not import from UI, web framework, or DB client packages.
3. Flag any outward-pointing dependency with file path and import statement.

> For detailed layer definitions and boundary patterns, load `./references/clean-architecture.md`.

### Step 3 — Evaluate SOLID in context

Check each principle where it applies to the touched code:

- **SRP**: Does the function/class have one reason to change? If it parses AND persists, split.
- **OCP**: Can you add new behavior without modifying existing code? If not, consider a strategy or interface.
- **LSP**: Do subclasses preserve the contract of their base? Flag any override that breaks expectations.
- **ISP**: Are consumers forced to depend on methods they don't use? Split the interface.
- **DIP**: Do high-level modules depend on abstractions, not concretions? Introduce an interface if a use case imports a concrete DB client.

### Step 4 — Scan for smells

| Smell | Meaning |
|-------|---------|
| **Rigidity** | Small change forces many edits. |
| **Fragility** | Changes break unrelated areas. |
| **Immobility** | Hard to reuse in another context. |
| **Viscosity** | Easy to hack, hard to do the right thing. |
| **Needless complexity** | Speculative or unused abstraction. |
| **Needless repetition** | DRY violated; same idea in multiple places. |
| **Opacity** | Code is hard to understand. |

List each smell with the file/function/area where it appears. Full heuristic lists (C1–T9-style) are in `./reference.md`—load it when you need the complete checklist.

### Step 5 — Propose concrete refactors

For each review, suggest **at least one** concrete refactor:

- "Extract this into a function named `apply_discount`."
- "Introduce an `OrderRepository` interface so the use case does not depend on the concrete DB client."
- "Split `process` into `parse` and `persist` to satisfy SRP."

### Step 6 — Assess design patterns (if relevant)

- **Use patterns** when they solve a real design problem (variation in behavior, lifecycle, or cross-cutting concern).
- **Avoid cargo cult**: Do not add Factory/Strategy/Repository just because the codebase "should" have them.
- **Rule of thumb**: Introduce a pattern when you feel the third duplication or the second reason to change; name the pattern in code or docs so intent is clear.
- **Signs of misuse**: Pattern name in every class name, layers that only delegate without logic, patterns that make simple code harder to follow.

> Load `./references/design-patterns.md` for detailed use-vs-misuse criteria.

### Step 7 — Check tests and professionalism

- Note if tests exist for the changed code.
- Flag obvious "we'll fix it later" comments that violate professionalism (Clean Coder).
- If discussing process, reference Clean Agile: Iron Cross (cost/quality/features/schedule), TDD, refactoring, pair programming.

> Load `./references/clean-coder.md` for estimation and professionalism detail.
> Load `./references/clean-agile.md` for agile values and practices.

### Step 8 — Run linter and formatter separately

This skill does NOT replace lint or format. After applying craft criteria, run the project's own tooling:

```powershell
# Example: run project linter (use your project's actual command)
npm run lint

# Example: run formatter
npm run format
```

## Examples

### Example 1: Code review prompt (copy-pasteable)

```markdown
Please review this change using Uncle Bob craft criteria (@uncle-bob-craft):
1. Dependency Rule and boundaries — do dependencies point inward?
2. SOLID in context — any violations in the touched code?
3. Smells — list rigidity, fragility, immobility, viscosity, needless complexity/repetition, or opacity.
4. Suggest one or two concrete refactors (e.g., extract function, invert dependency).
Do not duplicate lint/format; focus on structure and design.
```

### Example 2: Before/after (extract and name)

**Before (opacity, does more than one thing):**

```python
def process(d):
    if d.get("t") == 1:
        d["x"] = d["a"] * 1.1
    elif d.get("t") == 2:
        d["x"] = d["a"] * 1.2
    return d
```

**After (clear intent, single level of abstraction):**

```python
def apply_discount(amount: float, discount_type: int) -> float:
    if discount_type == 1:
        return amount * 1.1
    if discount_type == 2:
        return amount * 1.2
    return amount

def process(order: dict) -> dict:
    order["x"] = apply_discount(order["a"], order.get("t", 0))
    return order
```

## Pitfalls

- **Treating every class as needing a Factory or Strategy.**
  *Fix*: Introduce patterns only when you have a real design need (third duplication, second axis of change). Load `./references/design-patterns.md` for criteria.

- **Review only listing "violates SOLID" without saying where or how.**
  *Fix*: Point to the file/function and name the specific principle (e.g., "SRP: this function parses and persists; split into `parse` and `persist`").

- **Skipping the project linter because "we applied Uncle Bob."**
  *Fix*: This skill is about craft and design; always run the project's lint and format separately. This skill does NOT enforce syntax or style.

- **Adding design patterns without a clear duplication or variation reason.**
  *Fix*: Wait for the third duplication or second reason to change before introducing a pattern. Name the pattern in code or docs so intent is clear.

- **Overwriting `@clean-code` material.**
  *Fix*: Use `@clean-code` for naming, functions, comments, formatting, and test heuristics. Use this skill for architecture, boundaries, SOLID, smells, and process.

- **Generating tests instead of reminding to write them.**
  *Fix*: This skill does not replace automated tests. It can remind you to write tests (Clean Coder, Clean Agile) but does not run or generate them.

## Verification

After applying this skill, verify the following:

1. **Dependency direction check**: Confirm no use-case or entity imports from UI, web framework, or DB client packages.
   ```powershell
   # Example: search for outward-pointing imports in use-case layer
   Select-String -Path .\src\use_cases\*.py -Pattern "import.*framework|import.*db_client|import.*ui"
   ```
   Expected: no matches (or only matches through interfaces/abstractions).

2. **Smell list completeness**: Confirm each identified smell includes file path and function/area.

3. **Concrete refactor proposed**: Confirm at least one specific refactor suggestion exists (not just "violates SOLID").

4. **Linter and formatter run independently**: Confirm the project's lint and format commands were executed separately from this skill's review.
   ```powershell
   npm run lint
   npm run format
   ```

5. **No syntax/style enforcement from this skill**: Confirm this skill did not override or replace linter/formatter output.

## Related Skills

- **`@clean-code`** — Detailed Clean Code book material (names, functions, comments, formatting, tests, classes, smells). Use for day-to-day code quality; use `uncle-bob-craft` for architecture and cross-book criteria.
- **`@architecture`** — General architecture decisions and trade-offs. Use when choosing high-level structure; use `uncle-bob-craft` for Dependency Rule and boundaries.
- **`@code-review-excellence`** — Code review practices. Combine with `uncle-bob-craft` for principle-based review.
- **`@refactor-clean-code`** — Refactoring toward clean code. Use with `uncle-bob-craft` when refactoring for boundaries and SOLID.
- **`@test-driven-development`** — TDD workflow. Aligns with Clean Agile and Clean Coder (tests as requirement, sustainable pace).

## Limitations

- **Does not replace the project linter or formatter.** Run lint and format separately; this skill gives design and craft criteria only.
- **Does not replace automated tests.** It can remind you to write tests but does not run or generate them.
- **Complementary to tooling.** Use it alongside existing CI, lint, and test suites.
- **No syntax or style enforcement.** Focuses on structure, dependencies, smells, and professional practice—not brace style or line length.
- **Summaries, not the books.** Full Clean Code heuristics, component principles (REP/CCP/CRP, ADP/SDP/SAP), and detailed stories are in the books; we reference the most used parts. See `./reference.md` "Scope and attribution."
