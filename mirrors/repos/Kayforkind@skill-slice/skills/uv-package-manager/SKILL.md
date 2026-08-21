---
name: uv-package-manager
version: 1.1.1
description: "Speeds Python packaging with Astral uv: uv init, venvs, lockfiles, interpreter install, pip-compat, workspace monorepos, and Docker/CI installs. Use when setting up Python projects, migrating from pip/poetry/pip-tools, or fixing resolver conflicts. Not for conda channels, non-Python packages, or Python 2.7; never assume uv runs where Rust binaries cannot execute."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-14
---

# UV Package Manager

Comprehensive guide to using **uv**, an extremely fast Python package installer and resolver written in Rust, for modern Python project management and dependency workflows. uv is 10–100x faster than pip, acts as a drop-in pip replacement, manages virtual environments, installs Python interpreters, and produces lockfiles for reproducible builds.

## When to Use

- Setting up new Python projects quickly
- Managing Python dependencies faster than pip
- Creating and managing virtual environments
- Installing and pinning Python interpreters
- Resolving dependency conflicts efficiently
- Migrating from pip / pip-tools / poetry
- Speeding up CI/CD pipelines
- Managing monorepo Python projects with workspaces
- Working with lockfiles for reproducible builds
- Optimizing Docker builds with Python dependencies

**Do NOT use uv when:**

- You require conda-specific packages or environments (use conda/mamba instead)
- You need non-Python language package management
- You need advanced conda features (channels, complex binary dependencies)
- The target environment cannot execute Rust binaries
- Legacy Python 2.7 projects (uv requires Python 3.8+)
- **Deprecation warning:** Avoid using `uv` with Python < 3.8 — no longer supported.
- **Security warning:** Be cautious when using `uv` with untrusted packages.

## Prerequisites

- A supported OS: Linux, macOS, or Windows (Windows PowerShell is the primary host for this skill)
- Python 3.8+ available or installable (uv can bootstrap Python itself)
- Network access for initial install and package downloads (offline mode available after cache populated)
- For Windows PowerShell: execution policy must allow script activation (`.venv\Scripts\Activate.ps1`)

### Install uv

```powershell
# Windows (PowerShell) — primary host
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Using pip (if Python already present)
pip install uv

# Using Homebrew (macOS)
brew install uv

# Using cargo (if Rust available)
cargo install --git https://github.com/astral-sh/uv uv
```

### Verify Installation

```bash
uv --version
# uv 1.1.0
```

## Procedure

### 1. Create a New Project

```bash
# Create new project with virtual environment
uv init my-project
cd my-project

# Or create in current directory
uv init .

# uv init creates:
#   .python-version   (Python version)
#   pyproject.toml    (project config)
#   README.md
#   .gitignore
```

### 2. Install Dependencies

```bash
# Add packages (creates venv if needed)
uv add requests pandas

# Add dev dependencies
uv add --dev pytest black ruff

# Install from requirements.txt (pip-compatible)
uv pip install -r requirements.txt

# Install from pyproject.toml + uv.lock
uv sync
```

### 3. Virtual Environment Management

```bash
# Create virtual environment
uv venv

# Create with specific Python version
uv venv --python 3.12

# Create with custom name
uv venv my-env

# Create with system site packages
uv venv --system-site-packages

# Specify location
uv venv /path/to/venv
```

**Activate the venv:**

```bash
# Linux/macOS
source .venv/bin/activate

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# Windows (PowerShell) — primary host
.venv\Scripts\Activate.ps1
```

**Prefer `uv run` (no activation needed):**

```bash
uv run python script.py
uv run pytest
uv run --python 3.11 python script.py
uv run python script.py --arg value
```

### 4. Adding Dependencies

```bash
# Add package (writes to pyproject.toml)
uv add requests

# Add with version constraint
uv add "django>=4.0,<5.0"

# Add multiple packages
uv add numpy pandas matplotlib

# Add dev dependency
uv add --dev pytest pytest-cov

# Add optional dependency group
uv add --optional docs sphinx

# Add from git
uv add git+https://github.com/user/repo.git

# Add from git with specific ref
uv add git+https://github.com/user/repo.git@v1.0.0

# Add from local path
uv add ./local-package

# Add editable local package
uv add -e ./local-package
```

### 5. Removing Dependencies

```bash
uv remove requests
uv remove --dev pytest
uv remove numpy pandas matplotlib
```

### 6. Upgrading Dependencies

```bash
# Upgrade specific package
uv add --upgrade requests

# Upgrade all packages
uv sync --upgrade

# Show what would be upgraded
uv tree --outdated
```

### 7. Locking Dependencies

```bash
# Generate uv.lock
uv lock

# Update lock file
uv lock --upgrade

# Lock without installing
uv lock --no-install

# Lock specific package
uv lock --upgrade-package requests
```

### 8. Python Version Management

```bash
# Install Python version
uv python install 3.12

# Install multiple versions
uv python install 3.11 3.12 3.13

# Install latest
uv python install

# List installed versions
uv python list

# List all available versions
uv python list --all-versions

# Pin Python version for project (creates/updates .python-version)
uv python pin 3.12

# Use specific Python version for a command
uv --python 3.11 run python script.py

# Create venv with specific version
uv venv --python 3.12
```

### 9. pyproject.toml Configuration

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "My awesome project"
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "requests>=2.31.0",
    "pydantic>=2.0.0",
    "click>=8.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]
docs = [
    "sphinx>=7.0.0",
    "sphinx-rtd-theme>=1.3.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    # Additional dev dependencies managed by uv
]

[tool.uv.sources]
# Custom package sources
my-package = { git = "https://github.com/user/repo.git" }
```

### 10. Migrating from Other Tools

```bash
# From requirements.txt
uv add -r requirements.txt

# From poetry (keep existing pyproject.toml)
uv sync

# Export to requirements.txt
uv pip freeze > requirements.txt

# Export with hashes
uv pip freeze --require-hashes > requirements.txt
```

### 11. Monorepo / Workspace Support

```bash
# Project structure:
# monorepo/
#   packages/
#     package-a/
#       pyproject.toml
#     package-b/
#       pyproject.toml
#   pyproject.toml (root)
```

```toml
# Root pyproject.toml
[tool.uv.workspace]
members = ["packages/*"]
```

```bash
# Install all workspace packages
uv sync

# Add workspace dependency
uv add --path ./packages/package-a
```

### 12. CI/CD Integration (GitHub Actions)

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v2
        with:
          enable-cache: true

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --all-extras --dev

      - name: Run tests
        run: uv run pytest

      - name: Run linting
        run: |
          uv run ruff check .
          uv run black --check .
```

### 13. Docker Integration

**Single-stage:**

```dockerfile
FROM python:3.12-slim

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first for cache efficiency
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .
CMD ["uv", "run", "python", "app.py"]
```

**Multi-stage (optimized):**

```dockerfile
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable

# Runtime stage
FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /app/.venv .venv
COPY . .

ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "app.py"]
```

### 14. Lockfile Workflows

```bash
# Create lockfile
uv lock

# Install from lockfile (exact versions)
uv sync --frozen

# Update lockfile without installing
uv lock --no-install

# Upgrade specific package in lock
uv lock --upgrade-package requests

# Check if lockfile is up to date
uv lock --check

# Export lockfile to requirements.txt
uv export --format requirements-txt > requirements.txt

# Export with hashes for security
uv export --format requirements-txt --hash > requirements.txt
```

### 15. Performance Optimization

```bash
# Global cache locations:
#   Linux:   ~/.cache/uv
#   macOS:   ~/Library/Caches/uv
#   Windows: %LOCALAPPDATA%\uv\cache

# Clear cache
uv cache clean

# Show cache directory
uv cache dir

# Control parallelism (uv parallelizes by default)
uv pip install --jobs 4 package1 package2

# Sequential install
uv pip install --jobs 1 package

# Offline mode (cache only, no network)
uv pip install --offline package
uv sync --frozen --offline
```

### 16. Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: uv-lock
        name: uv lock
        entry: uv lock
        language: system
        pass_filenames: false

      - id: ruff
        name: ruff
        entry: uv run ruff check --fix
        language: system
        types: [python]

      - id: black
        name: black
        entry: uv run black
        language: system
        types: [python]
```

### 17. VS Code Integration

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["-v"],
  "python.linting.enabled": true,
  "python.formatting.provider": "black",
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true
  }
}
```

> **Windows note:** On Windows the interpreter path is `${workspaceFolder}/.venv/Scripts/python.exe`.

## Examples

### Complete New Project Workflow

```bash
uv init my-project
cd my-project

uv python pin 3.12

uv add fastapi uvicorn pydantic
uv add --dev pytest black ruff mypy

mkdir -p src/my_project tests

uv run pytest
uv run black .
uv run ruff check .
```

### Maintaining an Existing Project

```bash
git clone https://github.com/user/project.git
cd project

# Install dependencies (creates venv automatically)
uv sync

# Install with all extras + dev
uv sync --all-extras

# Update dependencies
uv lock --upgrade

# Run application
uv run python app.py

# Run tests
uv run pytest

# Add new dependency
uv add new-package

# Commit updated files
git add pyproject.toml uv.lock
git commit -m "Add new-package dependency"
```

### Migration Cheatsheet

| From | Before | After |
|------|--------|-------|
| pip + requirements.txt | `python -m venv .venv && pip install -r requirements.txt` | `uv venv && uv pip install -r requirements.txt` (or `uv init && uv add -r requirements.txt`) |
| poetry | `poetry install && poetry add requests` | `uv sync && uv add requests` |
| pip-tools | `pip-compile requirements.in && pip-sync requirements.txt` | `uv lock && uv sync --frozen` |

## Pitfalls

- **uv not found after install:** Ensure uv binary is on PATH. On Windows, the installer updates PATH for new shells; restart your terminal. On Linux/macOS add `export PATH="$HOME/.cargo/bin:$PATH"` to your shell rc.
- **Wrong Python version selected:** Always pin explicitly with `uv python pin 3.12` and create venv with `uv venv --python 3.12`.
- **Dependency conflict unresolved:** Run `uv lock --verbose` to inspect resolution steps.
- **Cache corruption or stale cache:** Run `uv cache clean` then re-sync.
- **Lockfile out of sync with pyproject.toml:** Regenerate with `uv lock --upgrade`; never manually edit `uv.lock`.
- **Windows PowerShell activation blocked:** If `Activate.ps1` fails, set execution policy for the current user: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`. Alternatively, use `uv run` to avoid activation entirely.
- **Docker image bloat:** Use multi-stage builds and `--no-dev --no-editable --frozen` to keep runtime image small.
- **CI flakiness from floating versions:** Always commit `uv.lock` and use `uv sync --frozen` in CI.
- **Untrusted packages:** Be cautious installing untrusted packages; they may pose security risks.
- **Python < 3.8 unsupported:** uv requires Python 3.8+; do not attempt to use with Python 2.7.

## Verification

```bash
# 1. Confirm uv is installed and on PATH
uv --version
# Expected: uv 1.1.0 (or newer)

# 2. Confirm project venv exists
uv venv
# Expected: "Using Python <version>" / "Creating virtual environment at: .venv"

# 3. Confirm dependencies installed
uv pip list
# Expected: list including requests, pandas, etc.

# 4. Confirm lockfile is current
uv lock --check
# Expected: exit code 0, no diff output

# 5. Confirm Python pin
cat .python-version
# Expected: 3.12 (or chosen version)

# 6. Confirm cache directory
uv cache dir
# Expected: platform-specific path (e.g., %LOCALAPPDATA%\uv\cache on Windows)

# 7. Run a command in the venv without activation
uv run python -c "import requests; print(requests.__version__)"
# Expected: prints installed requests version
```

## Related Skills

- **python-project-setup** — scaffolding Python project structure
- **ruff-linter** — fast Python linting with ruff
- **black-formatter** — Python code formatting
- **pytest-testing** — Python test workflows
- **docker-python** — containerizing Python applications
