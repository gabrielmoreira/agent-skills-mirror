---
name: implementation-engineering
description: Generates typed, production-grade technical and numerical Python implementations from Mapping Documents with strict type hints, precondition assertions, and literature/specification citations. Use when implementing quantitative or technical algorithms in Python.
license: Apache-2.0
user-invocable: false
---

# Technical Implementation Engineering Skill

## Purpose
This skill generates clean, typed, high-performance numerical and technical code modules from an approved `Mapping Document`.

## Required Context
* The approved `Mapping Document` (`mapping.json`).
* Target destination file (e.g. `algorithm.py`).
* Strict linting and typing rules defined in [lint_rules.json](./lint_rules.json).

## Coding Standards & Invariants
0. **Environment & Dependency Ownership (`requirements.txt` + `./.venv`):**
   * Author/update `requirements.txt` (pinning runtime packages plus `pytest` and `hypothesis`) via `create(path="<absolute_cwd>/requirements.txt", file_text="...")` and install into `./.venv/bin/pip`. During Stage 4 Reflexion repair, update `requirements.txt` and re-install on the fly whenever `@Auditor` feedback requires additional or alternative libraries.
1. **Public Interface Conformance & Zero-Loop Editing:**
   * Implement the exact module and function signatures declared under `public_interface` in `mapping.json`.
   * Always pass `"path"` (full absolute path) as the **first** argument in `create`, `edit`, and `view`.
   * For modules `<= 300` lines or multi-function refactors, prefer atomic `create(path="<absolute_path>", file_text="<complete_module>")` (backed by `.rollback_<module>.py` staging on `SyntaxError` and automatic `ruff format`). For large files (`> 300` lines), use `edit` (enhanced by 4-stage `preToolUse` `old_str` auto-snap) or [code_patch.py](./scripts/code_patch.py) (`inspect`, `replace-symbol`, `replace-lines`).
2. **Strict Type Annotations:**
   * Comply with the rules in [lint_rules.json](./lint_rules.json).
   * Annotate every parameter and return value using standard `typing`, `numpy.typing` (`NDArray[np.float64]`), dataclasses, or Pydantic.
   * Never use bare untyped variables or implicit `Any`.
3. **Precondition Assertions:**
   * At the start of each public function, insert executable assertions for dimensions, non-negativity, finite checks, or valid ranges based on the `precondition_assertions` in the mapping document.
4. **Anchor Smoke-Testing:**
   * Before handing off to `@Auditor`, smoke-test the implementation against the `anchor_test_cases` declared in `mapping.json` to catch trivial edge cases and base-case regressions early.
5. **Traceability Invariant (Citation Contract):**
   * The module docstring must cite the paper, book, or specification title, authors, and DOI/URL.
   * Every function docstring must explicitly state: `Implements Eq. (X.Y), Page Z` or `Section X.Y of [Specification]`.
   * Complex mathematical steps or state transitions must include inline comments quoting the original formula or rule (e.g. `# Eq. (2.5): y = A x + b`).
6. **Reflexion Bounded Repair:**
   * If Stage 4 verification discovers counter-examples, read `AUDIT_FEEDBACK.json` to inspect the exact failed obligation, minimal counter-example, and diagnosis. Make surgical code repairs without tampering with upstream specifications or weakening tolerances.
7. **Active Compilation & AST Guard:**
   * Every file edit is automatically verified by the `postToolUse` compilation and AST hook (`python3 -m py_compile` + `validate_python_ast()`), and [code_patch.py](./scripts/code_patch.py) also enforces workspace containment and reports `ast_warnings`. Fix any reported syntax or contract errors immediately.

## Success Criteria
* A standalone, clean Python module implementing the algorithm.
* 100% type-annotated public interface.
* Explicit assertions guarding domain preconditions.
* Direct citations embedded in docstrings and inline comments.
