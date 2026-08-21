---
name: test-fixing
version: 1.1.1
description: "Groups failing suite errors by type and root cause, then repairs infrastructure, API drift, and assertion bugs until the project's runner is green. Use when tests fail, CI is red, or a refactor broke the suite. Do not use to author a new pytest or TestNG tree, or to skip or weaken assertions for a pass."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-14
---

# Test Fixing

Systematically identify and fix all failing tests using smart error grouping, root-cause analysis, and iterative validation. Avoid the "whack-a-mole" approach: group failures, fix root causes once, and verify each group before moving on.

## When to Use

- User explicitly asks to fix tests: "fix these tests", "make tests pass", "get the suite green"
- User reports test failures: "tests are failing", "test suite is broken", "CI is red"
- Implementation is complete and the user wants tests passing before commit
- CI/CD pipeline failures caused by test regressions
- After a major refactor where multiple tests are broken simultaneously
- After dependency upgrades that may have introduced breaking changes

## Prerequisites

- The project has an existing test suite (pytest, unittest, jest, etc.)
- A working test runner is available (`make test`, `uv run pytest`, `npm test`, etc.)
- On Windows host (PowerShell), prefer `uv run pytest` or the project's configured runner. If `make` is unavailable, invoke the runner directly.
- Check for a `CLAUDE.md`, `CONTRIBUTING.md`, or project style guide before making edits. Adhere to project-specific coding standards.
- If the project uses `references/` or `scripts/` directories, load them as needed (see Procedure).

## Procedure

### 1. Initial Test Run — Identify Scope

Run the project's primary test command to capture the full failure surface.

**Windows (PowerShell):**
```powershell
uv run pytest --tb=short -q
```

**If a Makefile is present:**
```powershell
make test
```

Analyze the output for:
- Total number of **failures** vs. **errors** (they have different root causes).
- Common error patterns (repeated tracebacks, shared import lines).
- Affected modules, files, and specific test cases.
- Environment-related failures (missing env vars, missing config files, port conflicts).
- Skipped (`SKIPPED`) or expected-fail (`XFAIL`) tests — investigate why before ignoring.

Capture the list of failing test node IDs for targeted re-runs:
```powershell
uv run pytest --tb=line -q 2>&1 | Select-String "FAILED"
```

### 2. Smart Error Grouping

Group failures to solve root causes once rather than fixing symptoms one by one.

**Group by:**
- **Error Type**: `ImportError`, `ModuleNotFoundError`, `AttributeError`, `TypeError`, `AssertionError`, `TimeoutError`.
- **Location**: Failures concentrated in a specific module, directory, or test file.
- **Root Cause**: API breaking changes, dependency updates, configuration drift, fixture issues, environment mismatches.

**Prioritize groups by:**
1. **Impact** — Fix the error causing the most failures first.
2. **Dependency Order** — Fix infrastructure/setup failures before business logic failures. A single `ImportError` can cascade into dozens of downstream failures.

### 3. Fix Order Strategy

Follow this hierarchy to ensure a stable foundation before addressing higher-level logic:

**Level 1 — Infrastructure & Environment**
- `ImportError`, `ModuleNotFoundError`
- Missing dependencies or incorrect `pyproject.toml` / `requirements.txt`
- Environment variable or configuration mismatches
- Fixture setup/teardown failures
- Database or service connection errors

**Level 2 — Interface & API Changes**
- Function signature mismatches (`TypeError`)
- Renamed methods or moved modules (`AttributeError`)
- Updated return types or data structures (e.g., `dict` → dataclass)
- Changed CLI flags or API response shapes

**Level 3 — Logic & Behavioral Issues**
- `AssertionError` (incorrect values)
- Edge case failures (empty input, boundary values, timezone issues)
- Race conditions or timeout issues
- Flaky tests (intermittent failures)

### 4. Systematic Fixing Process (Per Group)

For each group, starting with the highest priority:

#### 4a. Identify Root Cause
- Read the traceback from the **bottom up** — the last frame usually points to the failing line.
- Correlate failures with recent changes:
  ```powershell
  git diff HEAD~5 --name-only
  git log --oneline -10
  ```
- Inspect the failing line of code and the corresponding test assertion side by side.
- If the project has a `references/` directory with architecture or API docs, load the relevant reference file to understand expected behavior before editing.

#### 4b. Implement Fix
- Apply targeted, minimal changes using the Edit tool.
- Adhere to project-specific coding standards (refer to `CLAUDE.md` or equivalent).
- Keep changes minimal to avoid introducing new regressions.
- If a `scripts/` directory contains helper scripts (e.g., lint, format, type-check), run them after each fix to catch side effects early.

#### 4c. Verify Fix (Iterative Validation)
Run only the affected subset of tests to save time and reduce noise.

```powershell
# Run a specific test file
uv run pytest tests/path/to/test_file.py -v

# Run tests matching a specific keyword/pattern
uv run pytest -k "keyword" -v

# Run only failing tests from the last run
uv run pytest --lf -v

# Run a single test node ID
uv run pytest tests/path/to/test_file.py::TestClass::test_method -v

# Extra verbose output for deep debugging
uv run pytest tests/path/to/test_file.py -vv --tb=long
```

Ensure the current group passes **completely** before moving to the next group.

#### 4d. Move to Next Group
Repeat 4a–4c for the next priority group.

### 5. Final Verification

Once all groups are addressed:

```powershell
# Run the complete test suite
uv run pytest --tb=short

# Or via Makefile
make test
```

- Verify that **no new regressions** were introduced in previously passing modules.
- Check coverage reports if available to ensure no critical paths were accidentally skipped:
  ```powershell
  uv run pytest --cov=src --cov-report=term-missing
  ```
- Remove all temporary debug prints/logs added during investigation.
- Run linters and formatters if configured:
  ```powershell
  uv run ruff check . --fix
  uv run ruff format .
  ```

## Pitfalls

- **Do not** ignore `SKIPPED` or `XFAIL` tests without investigating why they are skipped — they may mask real failures.
- **Do not** modify the test suite to match incorrect behavior in the code. If the test is wrong, confirm the expected behavior first, then update the test with a clear reason.
- **Do not** use `pytest.mark.skip` as a temporary fix without a corresponding `TODO` comment or ticket reference.
- **Do not** perform bulk "find and replace" across the codebase without verifying the impact on all affected tests.
- **Do not** comment out failing tests or weaken assertions just to make the suite pass.
- **Do not** fix symptoms individually ("whack-a-mole") — always group and address root causes.
- **Do not** run the full suite after every single change — use targeted subset runs to maintain a fast feedback loop.
- **Do not** forget to remove debug `print()` statements or temporary logging added during investigation.
- **Do not** commit fixes for multiple unrelated groups in a single atomic commit if the project expects granular history — prefer one commit per root-cause group.
- **Watch for flaky tests**: if a test passes on re-run but failed initially, investigate race conditions, time-dependent logic, or shared mutable state before dismissing it.
- **Watch for environment drift**: failures that only appear in CI but not locally often indicate missing env vars, different Python/Node versions, or OS-specific path handling (especially Windows vs. Linux path separators).

## Verification

Confirm each item before declaring the task complete:

- [ ] All tests in each failing group pass individually.
- [ ] The full test suite runs without errors:
  ```powershell
  uv run pytest --tb=short
  ```
- [ ] No new regressions introduced in previously passing modules.
- [ ] Code adheres to the project's style guide and architecture (`CLAUDE.md` / `CONTRIBUTING.md`).
- [ ] All temporary debug prints/logs have been removed.
- [ ] Linters and formatters pass (if configured).
- [ ] `SKIPPED` and `XFAIL` tests have been investigated and documented if still skipped.
- [ ] Coverage has not dropped on critical paths (if coverage is tracked).

## Examples

**Scenario**: User reports "The tests are failing after my refactor."

1. **Run**: `uv run pytest --tb=short -q` → 15 failures.
2. **Group**:
   - 8 × `ImportError` → Root: `utils.py` moved to `core/utils.py`.
   - 5 × `AttributeError` → Root: `get_user()` now returns a `User` object instead of a `dict`.
   - 2 × `AssertionError` → Root: Logic bug in date calculation.
3. **Fix Group 1** (Infrastructure): Update imports across affected files → Run `uv run pytest tests/test_utils.py -v` → Pass.
4. **Fix Group 2** (Interface): Update call sites to access object attributes (`user.name` instead of `user["name"]`) → Run `uv run pytest tests/test_users.py -v` → Pass.
5. **Fix Group 3** (Logic): Correct date calculation edge case → Run `uv run pytest tests/test_dates.py -v` → Pass.
6. **Final**: Run `uv run pytest --tb=short` → All pass ✓.

## Related Skills

- `debugging` — General debugging workflows for non-test-specific failures.
- `code-review` — Reviewing fixes before commit to ensure minimal, standards-compliant changes.
- `refactoring` — Safe refactoring practices that minimize test breakage.
