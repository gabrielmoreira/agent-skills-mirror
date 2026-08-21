---
name: pytest-skill
description: "Authors pytest modules with conftest fixtures, parametrize, markers, pytest-mock, asyncio, and coverage or xdist runners. Trigger on pytest, conftest, @pytest.fixture, or parametrize. Not for unittest.TestCase-first trees, Jest/Vitest, or coverage-gate configuration alone."
version: 1.0.1
risk: unknown
source: https://github.com/LambdaTest/agent-skills/tree/main/pytest-skill
source_repo: LambdaTest/agent-skills
source_type: community
date_added: 2026-07-01
license: MIT
license_source: https://github.com/LambdaTest/agent-skills/blob/main/LICENSE
---

# Pytest Testing Skill

## Overview

This skill provides production-grade pytest test generation patterns covering fixtures, parametrize, markers, mocking, conftest, async testing, and CI/CD integration. It targets Python projects using pytest as the primary test runner on Windows (PowerShell) hosts.

## When to Use

Use this skill when the user needs to generate, refactor, or debug pytest tests. Trigger keywords and phrases:

- `pytest`
- `conftest`
- `@pytest.fixture`
- `@pytest.mark`
- `Python test`
- `parametrize`
- `pytest-asyncio`
- `pytest-mock`
- `pytest-cov`
- `pytest-xdist`

Do **not** use this skill for `unittest`-only projects or non-Python testing frameworks. If the project uses `unittest.TestCase` classes, prefer plain `assert` patterns but note that `setUp`/`tearDown` methods still work under pytest.

## Prerequisites

1. Python 3.8+ installed and on `PATH`.
2. pytest installed in the active environment:
   ```powershell
   pip install pytest
   ```
3. Recommended plugins (install only what the project needs):
   ```powershell
   pip install pytest-mock pytest-cov pytest-xdist pytest-asyncio
   ```
4. On Windows, confirm the executable is available:
   ```powershell
   python --version
   pytest --version
   ```
5. If the project uses `pyproject.toml` or `pytest.ini`, ensure test paths and markers are declared there before running marker-filtered commands.

## Procedure

### 1. Identify the test scope

Determine what needs testing: a function, class, module, API endpoint, or integration flow. Check for an existing `conftest.py` and `tests/` directory structure.

### 2. Create or update conftest.py

Place shared fixtures in `tests/conftest.py` (or project-root `conftest.py` for top-level fixtures).

```python
# tests/conftest.py
import pytest
from myapp.calculator import Calculator
from myapp.database import Database

@pytest.fixture
def calculator():
    return Calculator()

@pytest.fixture
def db_connection():
    conn = Database.connect("test_db")
    yield conn  # teardown after yield
    conn.rollback()
    conn.close()

@pytest.fixture(scope="module")
def api_client():
    from myapp.client import APIClient
    client = APIClient(base_url="http://localhost:8000")
    yield client
    client.logout()

@pytest.fixture(autouse=True)
def reset_state():
    from myapp.state import State
    State.reset()
    yield
    State.cleanup()
```

### 3. Write the test file

Use plain `assert` statements — pytest's assertion rewriting gives richer failure messages than `self.assertEqual`.

```python
# tests/test_calculator.py
import pytest

def test_addition():
    assert 2 + 3 == 5

def test_exception():
    with pytest.raises(ValueError, match="invalid"):
        int("not_a_number")

class TestCalculator:
    def test_add(self, calculator):
        assert calculator.add(2, 3) == 5

    def test_divide_by_zero(self, calculator):
        with pytest.raises(ZeroDivisionError):
            calculator.divide(10, 0)
```

### 4. Add parametrized tests

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", 5), ("", 0), ("pytest", 6),
])
def test_string_length(input, expected):
    assert len(input) == expected

@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5), (-1, 1, 0), (0, 0, 0),
])
def test_add_parametrized(calculator, a, b, expected):
    assert calculator.add(a, b) == expected
```

### 5. Apply markers

Register custom markers in `pyproject.toml` or `pytest.ini` before using them:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "slow: slow tests",
    "integration: integration tests",
]
addopts = "-v --tb=short"
```

Then use in tests:

```python
import sys
import pytest

@pytest.mark.slow
def test_large_dataset(): ...

@pytest.mark.skip(reason="Not implemented")
def test_future_feature(): ...

@pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
def test_unix_permissions(): ...

@pytest.mark.xfail(reason="Known bug #123")
def test_known_bug(): ...
```

### 6. Add mocking where needed

Prefer `pytest-mock`'s `mocker` fixture for ergonomics. Fall back to `unittest.mock` if the plugin is not installed.

```python
from unittest.mock import patch, MagicMock

# pytest-mock style
def test_send_email(mocker):
    mock_smtp = mocker.patch("myapp.email.smtplib.SMTP")
    send_welcome_email("user@test.com")
    mock_smtp.return_value.sendmail.assert_called_once()

def test_api_call(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"users": [{"name": "Alice"}]}
    mocker.patch("myapp.service.requests.get", return_value=mock_response)
    users = get_users()
    assert len(users) == 1

# unittest.mock style (no pytest-mock dependency)
@patch("myapp.service.database")
def test_save_user(mock_db):
    mock_db.save.return_value = True
    assert save_user({"name": "Alice"}) is True
    mock_db.save.assert_called_once()
```

### 7. Run tests

Quick reference table (PowerShell-compatible commands):

| Task | Command |
|------|---------|
| Run all | `pytest` |
| Run file | `pytest tests/test_login.py` |
| Run specific | `pytest tests/test_login.py::test_login_success` |
| By marker | `pytest -m slow` |
| By keyword | `pytest -k "login and not invalid"` |
| Verbose | `pytest -v` |
| Stop first fail | `pytest -x` |
| Last failed | `pytest --lf` |
| Coverage | `pytest --cov=myapp --cov-report=html` |
| Parallel | `pytest -n auto` (requires pytest-xdist) |

### 8. Load the deep reference playbook

For advanced production patterns, load `reference/playbook.md` from this skill directory. Consult it when the user needs any of the following:

| Section | When to load |
|---------|-------------|
| §1 Config | Setting up `pytest.ini` or `pyproject.toml` with markers and coverage |
| §2 Fixtures | Scoping, factories, teardown, autouse, `tmp_path` |
| §3 Parametrize | IDs, cartesian product, indirect parametrization |
| §4 Mocking | `pytest-mock`, `monkeypatch`, spies, environment variables |
| §5 Async | `pytest-asyncio`, async fixtures, async test client |
| §6 Exceptions | `pytest.raises(match=)`, warning capture |
| §7 Markers & Plugins | Custom markers, collection hooks, plugin development |
| §8 Class-Based | Nested classes, autouse setup in class context |
| §9 CI/CD | GitHub Actions matrix, coverage gates |
| §10 Debugging Table | 10 common problems with fixes |
| §11 Best Practices | 15-item production checklist |

Load the file at the start of step 8 or whenever the user's request goes beyond the core patterns above.

## Examples

### Minimal test file

```python
import pytest

def test_addition():
    assert 2 + 3 == 5

def test_exception():
    with pytest.raises(ValueError, match="invalid"):
        int("not_a_number")
```

### Fixture with teardown

```python
@pytest.fixture
def db_connection():
    conn = Database.connect("test_db")
    yield conn
    conn.rollback()
    conn.close()

def test_query(db_connection):
    assert db_connection.execute("SELECT 1") == 1
```

### Floating-point assertion

```python
assert 0.1 + 0.2 == pytest.approx(0.3)
```

### Anti-patterns to avoid

| Bad | Good | Why |
|-----|------|-----|
| `self.assertEqual()` | `assert x == y` | pytest rewrites give better output |
| Setup in `__init__` | `@pytest.fixture` | Lifecycle management |
| Global mutable state | Fixture with `yield` | Proper cleanup |
| Huge test functions | Small focused tests | Easier debugging |
| Hardcoded paths | `tmp_path` fixture | Portable, auto-cleaned temp dirs |

## Pitfalls

1. **Unregistered markers cause warnings.** Always declare custom markers in `pyproject.toml` under `[tool.pytest.ini_options]` markers list or in `pytest.ini`. Unregistered markers trigger `PytestUnknownMarkWarning` and may be treated as errors with `-W error`.
2. **`assertEqual` instead of `assert`.** When using `unittest.TestCase` subclasses, `self.assertEqual` works but loses pytest's assertion rewriting. Prefer plain `assert` in non-`TestCase` test classes.
3. **Forgetting teardown.** A fixture without `yield` or a `try/finally` block leaks resources. Always use `yield` followed by teardown code.
4. **`scope="session"` fixtures with mutable state.** Session-scoped fixtures persist across the entire run. If tests mutate session-scoped data, later tests may see stale state. Use `scope="function"` or add a reset fixture.
5. **`mocker` fixture not available.** `mocker` comes from `pytest-mock`. If the plugin is not installed, `mocker` will raise a fixture-not-found error. Fall back to `unittest.mock.patch` as a decorator or context manager.
6. **Windows path issues.** Use `pathlib.Path` or `os.path.join` instead of hardcoded forward slashes. The `tmp_path` fixture returns a `Path` object that works cross-platform.
7. **`pytest-xdist` and session-scoped fixtures.** With `-n auto`, session-scoped fixtures may be instantiated per-worker. Use `scope="session"` carefully and consider `pytest-xdist`'s `--dist=loadscope` to group tests sharing expensive fixtures.
8. **Async tests without `pytest-asyncio`.** A bare `async def test_...` will be skipped or error. Install `pytest-asyncio` and either mark the test with `@pytest.mark.asyncio` or set `asyncio_mode = "auto"` in config.
9. **Coverage not collected.** `pytest --cov=myapp` requires `pytest-cov` and the `coverage` package. Ensure the import path matches the package directory, not the test directory.
10. **Import errors from `conftest.py`.** A `conftest.py` at the project root that imports application code will fail if the package is not installed in editable mode. Run `pip install -e .` or ensure `PYTHONPATH` includes the project root.

## Verification

After generating or modifying tests, verify with these checkable commands:

1. **Confirm pytest is installed and collects tests:**
   ```powershell
   pytest --collect-only
   ```
   Expected: a list of collected test items with no errors.

2. **Run the full suite verbosely:**
   ```powershell
   pytest -v
   ```
   Expected: each test name printed with `PASSED`, `FAILED`, `SKIPPED`, or `XFAIL`.

3. **Check for marker warnings:**
   ```powershell
   pytest -W error::pytest.PytestUnknownMarkWarning
   ```
   Expected: no errors if all markers are registered.

4. **Run with coverage (if configured):**
   ```powershell
   pytest --cov=myapp --cov-report=term-missing
   ```
   Expected: a coverage summary table showing per-file line coverage and missing line numbers.

5. **Run only the new or modified test file:**
   ```powershell
   pytest tests/test_your_file.py -v
   ```
   Expected: all tests in that file pass (or show expected `xfail`/`skip`).

6. **Verify no fixture leaks (quick smoke):**
   ```powershell
   pytest --lf -v
   ```
   Expected: previously failed tests re-run; if they now pass, the fix is confirmed.

## Related skills

- **unittest-skill** — for projects using `unittest.TestCase` as the primary framework.
- **coverage-skill** — for advanced coverage configuration and gate enforcement.
- **github-actions-skill** — for CI matrix setup referenced in `reference/playbook.md` §9.

## Limitations

- Use this skill only when the task clearly matches its upstream source and local project context.
- Verify commands, generated code, dependencies, credentials, and external service behavior before applying changes.
- Do not treat examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
- Windows (PowerShell) is the primary host. Commands are tested on PowerShell; adjust quoting for bash/zsh if running on WSL or Linux.
