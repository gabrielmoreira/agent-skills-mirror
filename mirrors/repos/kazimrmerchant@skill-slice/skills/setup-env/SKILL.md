---
name: setup-env
version: 2.0.1
description: "Creates isolated Python environments with uv (uv sync, uv run, PEP 723 scripts) from pyproject.toml or requirements.txt. Use when bootstrapping a Python repo so dependencies stay locked and isolated. Not for Node/npm, Vercel env var management (env-vars), or falling back to system pip when uv is missing."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Skill: Manage Python environments with uv

`uv` is a single, fast tool that replaces the `python -m venv` + `pip` + `pip-tools` stack. This skill tells the agent how to pick the right `uv` workflow for a given repository, create an isolated environment, install dependencies reproducibly, and run the project's code. The goal is that the agent never has to "remember" which shell the venv was activated in or whether the lockfile is current — `uv` resolves both for us on every run.

> All commands below were checked against `uv 0.11.19` (released 2026-06-03). If the installed `uv` is older and a flag is rejected, run `uv <command> --help` to see what that version supports rather than guessing.

## When to Use

- The repository is a Python project. `uv` is Python-specific and has no value for other ecosystems.
- You need an isolated environment so the project's dependencies do not collide with the system interpreter or with another project's pins.
- You need reproducibility: a `uv.lock` lets the same versions resolve on every machine and in CI, which is the main reason to prefer `uv sync` over ad-hoc installs.
- You are running a single-file script that declares its own dependencies inline (PEP 723). `uv run` builds a throwaway environment for it automatically.

**Trigger keywords:** Python project, virtual environment, venv, dependencies, uv, pyproject.toml, requirements.txt, uv.lock, PEP 723, uv sync, uv run, uv pip install.

### When NOT to use

- Non-Python projects — there is nothing for `uv` to manage.
- `uv` is not on `PATH`. Detect this first (`uv --version`); if it fails, stop and ask the user to install it rather than falling back to system `pip`, which would defeat the isolation this skill exists to provide.
- The repo has no `pyproject.toml`, no `requirements.txt`, and no PEP 723 markers. There is nothing to resolve, so report that instead of inventing a configuration.
- A legacy `setup.py`-only project that cannot be installed in editable mode. `uv` can often still build it, but if the build back-end is unusual, prefer the project's documented setup steps over forcing a `uv` workflow.

## Prerequisites

1. **`uv` must be installed and on `PATH`.** Verify before doing anything else:
   ```powershell
   uv --version
   ```
   If this fails, stop and ask the user to install `uv` from `https://docs.astral.sh/uv/`. Do **not** fall back to system `pip`.
2. **Windows host is primary (PowerShell).** All commands are tested in PowerShell 5.1+ on Windows. Where Linux/macOS paths differ, they are noted inline.
3. **The repository must contain at least one of:** `pyproject.toml`, `requirements.txt`, or a `.py` file with a PEP 723 `# /// script` block.

## Procedure

### Step 0 — Detect `uv` and confirm version

```powershell
uv --version
```

Expected output (or newer):
```
uv 0.11.19
```

If the command is not found, stop. Do not proceed with system `pip`.

### Step 1 — Select the workflow (decision order)

Detect the configuration in this order and use the first match. The order matters: a `pyproject.toml` is the most declarative source of truth, so it wins over a `requirements.txt` that may only list a subset of dependencies.

| Priority | File present | Workflow | Key commands |
|----------|-------------|----------|--------------|
| 1 | `pyproject.toml` | **Project workflow** | `uv sync`, `uv run` |
| 2 | `requirements.txt` | **Pip workflow** | `uv venv`, `uv pip install -r` |
| 3 | `.py` with PEP 723 block | **Inline workflow** | `uv run script.py` |
| 4 | None of the above | **Stop** | Report: `No supported dependency configuration found` |

---

### Step 2A — Project workflow (`pyproject.toml`)

Run from the directory that contains `pyproject.toml`.

#### Create the environment and install dependencies

```powershell
# If a lockfile already exists, install exactly what it pins and fail on drift.
uv sync --locked

# First run, or when you intend to (re)resolve and write uv.lock:
uv sync
```

**Why two forms:** `uv sync --locked` asserts that `uv.lock` is already up to date with `pyproject.toml` and errors if it is not — ideal in CI and when you must not change versions. Plain `uv sync` resolves dependencies and creates/updates `uv.lock`, which is what you want the first time or after editing dependencies. `uv` creates the environment at `.venv` in the project root (the standard location every editor and tool already understands); it is not a custom path.

#### Run scripts, modules, and tools

Always go through `uv run` so the environment is synced before the command executes:

```powershell
uv run -- python main.py --config config/prod.toml
uv run -- python -m app.cli serve --port 8000
uv run -- pytest -q
```

The `--` separates `uv`'s own flags from the command's flags, so a `--port` meant for your app is never mistaken for a `uv` option.

For reproducible runs that must not trigger a re-resolve, add `--frozen` (use the existing lockfile and environment as-is):

```powershell
uv run --frozen -- pytest -q
```

---

### Step 2B — Pip workflow (`requirements.txt`)

Use this when the project only ships a `requirements.txt` (common in older repos and some deployment setups). It mirrors a classic `pip` flow but keeps the speed and isolation of `uv`.

#### Create the virtual environment

```powershell
uv venv          # creates .venv in the current directory
```

By default this environment is minimal and does **not** include `pip`/`setuptools`. That is fine because `uv pip install` does the installing. Only add `--seed` if some downstream tool shells out to `pip` or `setuptools` inside the venv and therefore needs them present:

```powershell
uv venv --seed   # also installs pip, setuptools, and wheel into .venv
```

#### Install dependencies

`uv pip install` targets the `.venv` it just found in the project, so create the venv first, then install into it:

```powershell
uv pip install -r requirements.txt
```

`uv`'s default resolution already prefers the highest compatible versions. Pass `--resolution` only when you deliberately want different behavior — for example, `--resolution=lowest-direct` to test against the minimum versions your project claims to support:

```powershell
uv pip install --resolution=lowest-direct -r requirements.txt
```

#### Run scripts and modules

Prefer `uv run`, which still works without a `pyproject.toml` and uses the project's `.venv`:

```powershell
uv run -- python main.py
uv run -- python -m app.cli --help
```

If you must call the interpreter directly (for example in a container entrypoint), use the path for the current OS. This is why `uv run` is preferred — it removes the need to branch on platform:

```powershell
# Windows (PowerShell or cmd) — primary host
.venv\Scripts\python.exe main.py

# Linux / macOS
.venv/bin/python main.py
```

---

### Step 2C — Inline workflow (PEP 723 single-file scripts)

A PEP 723 script declares its own dependencies in a comment block, so it needs no `pyproject.toml` and no pre-created venv. `uv run` reads the block, builds an ephemeral environment, and executes the file — ideal for one-off tools and reproducible single-file utilities.

```powershell
uv run analysis/fetch_status.py https://example.com --timeout 5

# Force "treat this path as a script" mode if uv's auto-detection is ambiguous:
uv run --script analysis/fetch_status.py https://example.com
```

#### Example PEP 723 script (modern, fully typed, defensive)

This is a complete, runnable example. It demonstrates the standard every script this skill produces should meet: explicit type annotations on all parameters and returns, strict validation of inputs before use, defensive error handling around I/O, and no `Any` types or bare `except`. Save it as `analysis/fetch_status.py` and run it with the command above.

```python
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "httpx>=0.27",
# ]
# ///
"""Fetch a URL and print its HTTP status, with strict validation and error handling."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class Arguments:
    """Validated command-line arguments."""

    url: str
    timeout: float


def parse_arguments(argv: list[str]) -> Arguments:
    """Parse and validate argv, exiting with a clear message on invalid input."""
    parser = argparse.ArgumentParser(
        description="Fetch a URL and print its HTTP status code.",
    )
    parser.add_argument("url", type=str, help="Absolute http:// or https:// URL.")
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Request timeout in seconds (must be greater than 0).",
    )
    namespace = parser.parse_args(argv)

    url: str = namespace.url
    timeout: float = namespace.timeout

    # Validate at the boundary so the rest of the program can trust its inputs.
    if not url.startswith(("http://", "https://")):
        parser.error("url must start with http:// or https://")
    if timeout <= 0:
        parser.error("--timeout must be greater than 0")

    return Arguments(url=url, timeout=timeout)


def fetch_status(url: str, timeout: float) -> int:
    """Return 0 and print the status on success, or 1 after reporting a request error."""
    try:
        response = httpx.get(url, timeout=timeout, follow_redirects=True)
    except httpx.HTTPError as exc:
        print(f"request failed: {exc}", file=sys.stderr)
        return 1

    print(f"{response.status_code} {url}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Program entry point. Returns a process exit code."""
    args = parse_arguments(sys.argv[1:] if argv is None else argv)
    return fetch_status(args.url, args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
```

---

### Step 3 — Bootstrap an unknown repo end to end

When the agent needs to set up an unknown repo end to end, use one of the scripts below. Both fail fast with a clear message if `uv` is missing and pick the workflow from the files actually present, so they are safe to run unattended.

#### PowerShell (Windows — primary host)

```powershell
#Requires -Version 5.1
$ErrorActionPreference = 'Stop'

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error 'uv is not on PATH. Install it from https://docs.astral.sh/uv/ and retry.'
    exit 127
}

Write-Host "Using $(uv --version)"

if (Test-Path 'pyproject.toml') {
    Write-Host 'Detected pyproject.toml -> project workflow'
    if (Test-Path 'uv.lock') { uv sync --locked } else { uv sync }
}
elseif (Test-Path 'requirements.txt') {
    Write-Host 'Detected requirements.txt -> pip workflow'
    uv venv
    uv pip install -r requirements.txt
}
else {
    Write-Error 'No pyproject.toml or requirements.txt found. For a PEP 723 script run: uv run path\to\script.py'
    exit 1
}

Write-Host 'Environment ready.'
```

#### Bash (Linux / macOS)

```bash
#!/usr/bin/env bash
# Bootstrap a Python project's environment with uv, choosing the right workflow.
set -euo pipefail

# Fail fast and explain how to recover if uv is unavailable.
if ! command -v uv >/dev/null 2>&1; then
  echo "error: uv is not on PATH. Install it from https://docs.astral.sh/uv/ and retry." >&2
  exit 127
fi

echo "Using $(uv --version)"

if [[ -f pyproject.toml ]]; then
  echo "Detected pyproject.toml -> project workflow"
  if [[ -f uv.lock ]]; then
    uv sync --locked          # reproducible: error if the lockfile is stale
  else
    uv sync                   # first run: resolve and write uv.lock
  fi
elif [[ -f requirements.txt ]]; then
  echo "Detected requirements.txt -> pip workflow"
  uv venv                     # creates .venv in the project root
  uv pip install -r requirements.txt
else
  echo "error: no pyproject.toml or requirements.txt found." >&2
  echo "For a single-file PEP 723 script, run it directly: uv run path/to/script.py" >&2
  exit 1
fi

echo "Environment ready."
```

## Pitfalls

1. **`uv` not on `PATH`.** Always check `uv --version` first. If it fails, stop and ask the user to install it. Never fall back to system `pip` — that defeats the isolation this skill exists to provide.
2. **Manual venv activation is stateful and shell-specific.** It is the usual source of "works in my terminal, fails in the agent's." Always prefer `uv run` over `.\.venv\Scripts\Activate.ps1` or `source .venv/bin/activate`. `uv run` re-syncs the project environment and executes the command inside it every time, with no activation step.
3. **`uv sync --locked` vs plain `uv sync` confusion.** `--locked` errors if `uv.lock` is stale relative to `pyproject.toml` — use it in CI or when you must not change versions. Plain `uv sync` resolves and writes `uv.lock` — use it on first run or after editing dependencies. Using `--locked` on a first run (no lockfile) will fail.
4. **Missing `--` separator.** Without `--`, a flag like `--port` meant for your app can be mistaken for a `uv` option. Always use `uv run -- <command>`.
5. **`uv venv` without `--seed` breaks downstream tools that shell out to `pip`.** The default venv is minimal (no `pip`/`setuptools`). Only add `--seed` if a downstream tool requires `pip` or `setuptools` inside the venv.
6. **Windows path separators.** On Windows, use backslashes: `.venv\Scripts\python.exe`. On Linux/macOS, use forward slashes: `.venv/bin/python`. `uv run` avoids this branching entirely.
7. **No supported configuration found.** If the repo has no `pyproject.toml`, no `requirements.txt`, and no PEP 723 markers, do not invent a configuration. Report: `No supported dependency configuration found (expected pyproject.toml, requirements.txt, or a PEP 723 script).`
8. **Legacy `setup.py`-only projects.** `uv` can often still build these, but if the build back-end is unusual, prefer the project's documented setup steps over forcing a `uv` workflow.
9. **Older `uv` versions rejecting flags.** If a flag is rejected, run `uv <command> --help` to see what that version supports rather than guessing.

## Verification

Confirm the environment is healthy before declaring the setup complete. Each check below maps to a real `uv 0.11.x` command:

1. **`uv` is installed and recent:**
   ```powershell
   uv --version
   ```
   Expected: prints a version string (e.g., `uv 0.11.19` or newer).

2. **The chosen configuration file exists** — i.e., the workflow selection was correct:
   ```powershell
   Test-Path pyproject.toml    # or requirements.txt, or PEP 723 block in .py
   ```

3. **Tests pass (skip if the project has no tests, and say so):**
   ```powershell
   uv run -- pytest -q
   ```

4. **Expected packages are installed:**
   ```powershell
   uv pip list
   ```

5. **No broken or incompatible dependencies:**
   ```powershell
   uv pip check
   ```
   Expected: `No issues found` or equivalent clean output.

6. **Resolved dependency graph has no unexpected conflicts:**
   ```powershell
   uv tree
   ```

7. **Review outdated packages (informational — outdated is not a failure):**
   ```powershell
   uv pip list --outdated
   ```

## Related skills

- Python project setup and packaging (`pyproject.toml`, build back-ends).
- Reproducible dependency management with `uv.lock` (`uv sync --locked` / `--frozen`).
- Writing PEP 723 self-contained scripts.
- CI configuration for Python (cache `.venv` / `uv` cache, run `uv sync --locked`).
