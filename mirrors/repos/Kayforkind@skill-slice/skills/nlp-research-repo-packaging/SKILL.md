---
name: nlp-research-repo-packaging
version: 1.1.1
description: "Aligns Python interpreter and pinned deps before installing NLP research repos from requirements.txt or environment.yml. Use when cloning or reproducing NLP papers, debugging torch/transformers conflicts, or setting up research envs. Not for greenfield app packaging, unbounded pip upgrade, or overwriting system Python."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# NLP Research Repo Package Installation

When reproducing an NLP research repo, align the environment to the repo's **declared** dependencies *before* installing anything. Most reproduction failures are not subtle bugs — they are environment drift. Two causes dominate:

1. **Python version mismatch.** Research code is usually validated against one interpreter (e.g., 3.11). A newer interpreter can change standard-library behavior, drop removed APIs, or ship wheels that pinned libraries were never built against.
2. **Installing packages without following `requirements.txt` / `environment.yml`.** Newer releases of `torch`, `transformers`, `numpy`, etc. routinely change APIs *and* numerical behavior. A repo that "ran fine for the authors" can silently produce different results — or fail to import — on `latest`.

The goal is not "install the newest, most secure stack." It is "recreate the stack the authors actually tested," then change it deliberately and minimally if you must.

## When to Use

Use this skill when:

- Reproducing or running NLP research code from a repository, where matching the authors' results depends on matching their environment.
- Setting up a development environment for an NLP research project from scratch.
- Debugging dependency conflicts or Python version mismatches in an NLP project — these symptoms usually trace back to skipping the alignment step.
- About to install packages in a freshly cloned research repo. Doing the alignment check *before* the first `pip install` is far cheaper than unwinding a half-installed, mismatched environment afterward.

**Trigger keywords:** `reproduce`, `NLP research repo`, `requirements.txt`, `environment.yml`, `dependency conflict`, `Python version mismatch`, `pip install`, `conda env create`, `torch`, `transformers`, `reproduction`.

### When NOT to Use

- **General-purpose, non-research package installation.** If you just need a library in your own project, the reproduction-grade ceremony here (snapshotting the interpreter, pinning to the authors' versions) is overhead with no payoff. Use normal packaging tooling instead.
- **Installing directly without the alignment step.** Skipping straight to `pip install` is what produces the mismatched environments this skill exists to prevent. Read the dependency files first so you install into the *right* interpreter.
- **Assuming the system Python matches the repo.** Containers and CI images ship whatever Python the base image happened to include; that is rarely the version the repo expects. Verify with `python -VV` rather than assuming.
- **Reflexively chasing "latest stable" versions.** For ordinary application code, newer is often better. For *reproduction* it is usually the opposite: the pins in `requirements.txt` are the contract that makes the results comparable. Upgrading "to be safe" is the single most common way to break a repo. Respect the pins by default.
- **Blanket `pip install --upgrade` without a target version.** An unbounded upgrade can pull a major release that changes APIs and invalidates the reproduction. If you genuinely need to patch one dependency (e.g., a known CVE in a transitive package), bump *that* dependency to a specific known-good version and then re-run the smoke test — don't upgrade everything at once.
- **Treating deprecation warnings as noise.** They often flag exactly the API the repo relies on. Read them; they tell you whether a version bump is safe or whether it will break the code you are trying to run.

## Prerequisites

- **Python** installed and accessible on `PATH` (verify with `python -VV`).
- **pip** matching the target interpreter (verify with `python -m pip --version`).
- **conda** (Miniconda or Mamba) if the repo ships `environment.yml` — verify with `conda --version`.
- **uv** (optional but recommended) for fast, reproducible interpreter installation — install via `curl -LsSf https://astral.sh/uv/install.sh | sh` (Linux/macOS) or `irm https://astral.sh/uv/install.ps1 | iex` (PowerShell).
- **Windows host (primary):** PowerShell is the default shell. Use `python -m pip` (not bare `pip`) to ensure installs target the correct interpreter. On Windows, `venv` activation uses `.\.venv\Scripts\Activate.ps1` (PowerShell) or `.\.venv\Scripts\activate.bat` (cmd). If execution policies block activation, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`.
- **Linux/WSL:** Bash scripts below are verified for Debian/Ubuntu bases. On Windows, run them inside WSL or translate to PowerShell equivalents (provided where critical).

## Procedure

### Step 1 — Read the repo's dependency files (order matters)

Knowing which file is authoritative prevents you from installing a half-right environment:

1. **Prefer `environment.yml` / `environment.yaml`.** Conda environment files frequently pin **Python itself**, plus channels and non-pip (C/CUDA) dependencies that `pip` cannot install. That makes them the most complete description of the environment.
2. **Otherwise use `requirements.txt`** (pip-only dependencies).
3. **If both exist,** treat `environment.yml` as the base layer and `requirements.txt` as a supplement applied *inside* the created conda env — unless the README says otherwise. **The README wins** because authors sometimes document a non-obvious install order.

A typical `environment.yml` that pins Python:

```yaml
name: nlp-research
channels:
  - conda-forge
  - pytorch
dependencies:
  - python=3.11
  - pip
  - pytorch=2.1.*
  - pip:
      - transformers==4.38.2
      - datasets==2.18.0
```

The `- python=3.11` line is the one you most need to honor.

### Step 2 — Snapshot the current environment before changing it

Write a snapshot file *before* you install or modify anything. This is a debuggable "before" picture: if the reproduction later misbehaves, this file tells you exactly which interpreter and which packages you started from.

**HARD RULE:** Always snapshot before any `pip install` or `conda env create`. No exceptions.

Capture, in order:

1. `python -VV` — full version banner (build, compiler). The Python version is the single most common root cause, so it leads.
2. `python -m pip --version` — confirms which pip maps to which interpreter (they can disagree).
3. `python -m pip freeze` — the exact pre-existing package set.

**PowerShell (Windows host):**

```powershell
$logFile = "~\python_int.txt"
python -VV              | Out-File -FilePath $logFile -Encoding utf8
python -m pip --version | Out-File -FilePath $logFile -Encoding utf8 -Append
python -m pip freeze    | Out-File -FilePath $logFile -Encoding utf8 -Append
```

**Bash (Linux/WSL):**

```bash
set -euo pipefail
LOG_FILE="/root/python_int.txt"
mkdir -p "$(dirname "$LOG_FILE")"
python -VV              >  "$LOG_FILE"
python -m pip --version >> "$LOG_FILE"
python -m pip freeze    >> "$LOG_FILE"
```

### Step 3 — Compare the repo's required Python against the running interpreter

Compare the repo's required Python major/minor against the running interpreter.

- **If they match:** install straight from the repo's dependency files (no ad-hoc upgrades), then run an import/smoke test.
- **If they differ:** build a matching interpreter in an *isolated* location first. **HARD RULE: Never overwrite the system Python.** OS tooling and other projects depend on it; replacing it in place can break the whole image. A fresh, isolated `venv` keeps the change contained.

You can detect mismatches programmatically before running any shell flow. The typed helper below parses `environment.yml`, compares only major/minor (research repos rarely need an exact patch), and returns a process exit code so a calling script can branch on it:

```python
#!/usr/bin/env python3
"""Decide whether the running interpreter satisfies a repo's Python pin.

Exit codes:
    0  match, or no explicit pin found
    1  the dependency file could not be read/parsed
    2  wrong command-line usage
    3  mismatch -- build a matching interpreter before installing
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Optional

_PYTHON_PIN: Final[re.Pattern[str]] = re.compile(
    r"^\s*-\s*python\s*(?P<op>>=|<=|==|~=|=|>|<)?\s*(?P<version>\d+(?:\.\d+){0,2})"
)


class DependencyFileError(RuntimeError):
    """Raised when a dependency file is missing, unreadable, or malformed."""


@dataclass(frozen=True)
class PythonRequirement:
    major: int
    minor: Optional[int]
    patch: Optional[int]
    operator: str
    source: Path
    raw_line: str

    def is_satisfied_by(self, version: tuple[int, int, int]) -> bool:
        running_major, running_minor, _patch = version
        if running_major != self.major:
            return False
        if self.minor is None:
            return True
        if self.operator in {"=", "=="}:
            return running_minor == self.minor
        if self.operator == ">=":
            return running_minor >= self.minor
        if self.operator == "<=":
            return running_minor <= self.minor
        if self.operator == ">":
            return running_minor > self.minor
        if self.operator == "<":
            return running_minor < self.minor
        if self.operator == "~=":
            return running_minor >= self.minor
        return running_minor == self.minor


def parse_python_requirement(env_file: Path) -> Optional[PythonRequirement]:
    if not env_file.exists():
        raise DependencyFileError(f"dependency file not found: {env_file}")
    if not env_file.is_file():
        raise DependencyFileError(f"expected a file but found a directory: {env_file}")
    try:
        text: str = env_file.read_text(encoding="utf-8")
    except OSError as exc:
        raise DependencyFileError(f"could not read {env_file}: {exc}") from exc

    for line in text.splitlines():
        match = _PYTHON_PIN.match(line)
        if match is None:
            continue
        parts: list[int] = [int(part) for part in match.group("version").split(".")]
        return PythonRequirement(
            major=parts[0],
            minor=parts[1] if len(parts) > 1 else None,
            patch=parts[2] if len(parts) > 2 else None,
            operator=match.group("op") or "=",
            source=env_file,
            raw_line=line.strip(),
        )
    return None


def current_python() -> tuple[int, int, int]:
    info = sys.version_info
    return (info.major, info.minor, info.micro)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <path-to-environment.yml>", file=sys.stderr)
        return 2

    env_file: Path = Path(argv[1]).expanduser()
    try:
        requirement = parse_python_requirement(env_file)
    except DependencyFileError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    running = current_python()
    running_str = ".".join(str(part) for part in running)

    if requirement is None:
        print(
            f"No explicit Python pin in {env_file.name}; running {running_str}. "
            "Proceed, but treat import errors as a likely version problem."
        )
        return 0

    if requirement.is_satisfied_by(running):
        print(f"OK: Python {running_str} satisfies '{requirement.raw_line}'.")
        return 0

    minor = requirement.minor if requirement.minor is not None else "x"
    print(
        f"MISMATCH: repo wants python {requirement.operator}{requirement.major}.{minor} "
        f"(line: '{requirement.raw_line}') but you are running {running_str}. "
        "Build a matching interpreter before installing (see Step 4).",
        file=sys.stderr,
    )
    return 3


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

Run it:

```bash
python check_python_pin.py environment.yml
# Exit 0 = OK, Exit 3 = mismatch (build matching interpreter)
```

### Step 4 — Build a matching interpreter if needed (isolated, never system)

**HARD RULE:** Never overwrite the system Python. Always create an isolated `venv`.

**Bash (Linux/WSL) with `uv`:**

```bash
#!/usr/bin/env bash
set -euo pipefail

REQUIRED_PYTHON="3.12.5"
VENV_DIR="/opt/py312"

# Install uv only if missing (idempotent re-runs).
if ! command -v uv >/dev/null 2>&1; then
  apt-get update
  apt-get install -y --no-install-recommends curl ca-certificates
  rm -rf /var/lib/apt/lists/*
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="/root/.local/bin:$PATH"
fi

uv python install "$REQUIRED_PYTHON"
uv venv --python "$REQUIRED_PYTHON" "$VENV_DIR"

PYBIN="$VENV_DIR/bin/python"
"$PYBIN" -VV
"$PYBIN" -m pip install -U pip setuptools wheel
```

**PowerShell (Windows host) with `uv`:**

```powershell
$REQUIRED_PYTHON = "3.12.5"
$VENV_DIR = "~\venvs\py312"

# Install uv if missing.
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    irm https://astral.sh/uv/install.ps1 | iex
    $env:PATH = "$env:USERPROFILE\.local\bin;$env:PATH"
}

uv python install $REQUIRED_PYTHON
uv venv --python $REQUIRED_PYTHON $VENV_DIR

$PYBIN = "$VENV_DIR\Scripts\python.exe"
& $PYBIN -VV
& $PYBIN -m pip install -U pip setuptools wheel
```

### Step 5 — Install from the repo's dependency files

**HARD RULE:** Install exactly what the repo pins. Do NOT add `--upgrade`. Those pins are the contract; replacing them with newer releases is how results silently diverge.

#### Path A: Repository with `environment.yml` (conda)

```bash
#!/usr/bin/env bash
set -euo pipefail

LOG_FILE="/root/python_int.txt"
ENV_FILE="environment.yml"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "error: $ENV_FILE not found in $(pwd); this repo may use requirements.txt instead." >&2
  exit 1
fi

if ! command -v conda >/dev/null 2>&1; then
  echo "error: conda not on PATH; install Miniconda/Mamba or use the requirements.txt path." >&2
  exit 1
fi

# Snapshot before changing anything.
mkdir -p "$(dirname "$LOG_FILE")"
python -VV              >  "$LOG_FILE"
python -m pip --version >> "$LOG_FILE"
python -m pip freeze    >> "$LOG_FILE"

# Read the declared env name from the file rather than hard-coding a guess.
ENV_NAME="$(grep -E '^[[:space:]]*name:' "$ENV_FILE" | head -n1 | awk '{print $2}' || true)"
if [[ -z "${ENV_NAME:-}" ]]; then
  echo "error: no 'name:' field in $ENV_FILE; add one or pass --name to 'conda env create'." >&2
  exit 1
fi

conda env create -f "$ENV_FILE"

# 'conda activate' needs the shell hook sourced in non-interactive scripts.
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

# Smoke test: importing the heavy libs surfaces version/ABI breakage right away.
python - <<'PY'
import importlib

for module_name in ("torch", "transformers"):
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, "__version__", "unknown")
        print(f"{module_name} {version} OK")
    except Exception as exc:
        print(f"{module_name} import FAILED: {exc!r}")
PY
```

**PowerShell equivalent for conda activation on Windows:**

```powershell
conda env create -f environment.yml
conda activate nlp-research  # Use the env name from environment.yml

# Smoke test
python -c "import torch; print(f'torch {torch.__version__} OK')"
python -c "import transformers; print(f'transformers {transformers.__version__} OK')"
```

#### Path B: Repository with `requirements.txt` only

```bash
#!/usr/bin/env bash
set -euo pipefail

LOG_FILE="/root/python_int.txt"
REQ_FILE="requirements.txt"

if [[ ! -f "$REQ_FILE" ]]; then
  echo "error: $REQ_FILE not found in $(pwd)." >&2
  exit 1
fi

# Snapshot before installing.
mkdir -p "$(dirname "$LOG_FILE")"
python -VV              >  "$LOG_FILE"
python -m pip --version >> "$LOG_FILE"
python -m pip freeze    >> "$LOG_FILE"

# Install exactly what the repo pins; do NOT add --upgrade.
python -m pip install -r "$REQ_FILE"
```

**PowerShell equivalent:**

```powershell
$logFile = "~\python_int.txt"
python -VV              | Out-File -FilePath $logFile -Encoding utf8
python -m pip --version | Out-File -FilePath $logFile -Encoding utf8 -Append
python -m pip freeze    | Out-File -FilePath $logFile -Encoding utf8 -Append

python -m pip install -r requirements.txt
```

#### Path C: Python version mismatch — build matching interpreter, then install

```bash
#!/usr/bin/env bash
set -euo pipefail

REQUIRED_PYTHON="3.11.8"
VENV_DIR="/opt/py311"
REQ_FILE="requirements.txt"

if [[ ! -f "$REQ_FILE" ]]; then
  echo "error: $REQ_FILE not found in $(pwd)." >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  apt-get update
  apt-get install -y --no-install-recommends curl ca-certificates
  rm -rf /var/lib/apt/lists/*
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="/root/.local/bin:$PATH"
fi

uv python install "$REQUIRED_PYTHON"
uv venv --python "$REQUIRED_PYTHON" "$VENV_DIR"

PYBIN="$VENV_DIR/bin/python"
"$PYBIN" -VV
"$PYBIN" -m pip install -U pip setuptools wheel
"$PYBIN" -m pip install -r "$REQ_FILE"

# Confirm the interpreter really is 3.11 before trusting any results.
"$PYBIN" - <<'PY'
import sys

major_minor = sys.version_info[:2]
assert major_minor == (3, 11), f"expected Python 3.11, got {'.'.join(map(str, major_minor))}"
print("interpreter OK:", sys.version.split()[0])
PY
```

## Pitfalls

- **Skipping the snapshot step.** Without a "before" picture of the interpreter and packages, you cannot diagnose what drifted when reproduction fails. Always write the snapshot file *before* the first install.
- **Overwriting the system Python.** OS tooling and other projects depend on it. Always create an isolated `venv` or conda env. Never `apt-get upgrade python3` or replace the system interpreter in place.
- **Adding `--upgrade` to `pip install -r requirements.txt`.** This is the single most common way to break a reproduction. The pins in `requirements.txt` are the contract. Install them exactly.
- **Assuming `pip` maps to the same interpreter as `python`.** They can disagree, especially on systems with multiple Python installations. Always use `python -m pip` (not bare `pip`) to guarantee installs target the correct interpreter.
- **Ignoring `environment.yml` when both files exist.** Conda env files pin Python itself plus C/CUDA dependencies that pip cannot install. If both exist, `environment.yml` is the base layer unless the README says otherwise.
- **Hard-coding the conda env name.** Read it from the `name:` field in `environment.yml` instead of guessing. A wrong env name means you install into a non-existent or wrong environment.
- **Forgetting to source the conda shell hook in non-interactive scripts.** `conda activate` does not work in bash scripts without `source "$(conda info --base)/etc/profile.d/conda.sh"` first. On Windows PowerShell, `conda activate` works if conda's hook is initialized (`conda init powershell`).
- **Treating deprecation warnings as noise.** They often flag exactly the API the repo relies on. Read them before deciding a version bump is safe.
- **Blanket `pip install --upgrade` for a CVE fix.** Bump only the affected dependency to a specific known-good version, then re-run the smoke test. Don't upgrade everything at once.
- **Not smoke-testing heavy libraries after install.** Importing `torch` and `transformers` immediately surfaces ABI/CUDA mismatches. If you skip this, the error surfaces deep inside a training run where it is much harder to diagnose.
- **Windows execution policy blocking venv activation.** Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` if PowerShell refuses to execute `Activate.ps1`.

## Verification

Each check below maps to a failure mode this skill prevents. A failed check tells you *what* drifted:

1. **Interpreter matches the repo.**
   ```bash
   python -VV
   # or for isolated venv:
   "$PYBIN" -VV
   ```
   Output must report the major/minor the repo declares. This is the most common root cause — confirm it first.

2. **Declared dependencies are present at the pinned versions.**
   ```bash
   python -m pip freeze
   # or:
   conda list
   ```
   Output must show the versions from `requirements.txt` / `environment.yml` — not newer ones substituted by an accidental upgrade.

3. **Heavy libraries import cleanly.**
   ```bash
   python -c "import torch; print(f'torch {torch.__version__} OK')"
   python -c "import transformers; print(f'transformers {transformers.__version__} OK')"
   ```
   This catches ABI/CUDA mismatches before they surface mid-run.

4. **No unresolved version conflicts.**
   ```bash
   python -m pip check
   ```
   Must report no broken requirements. A conflict here means a dependency was bumped out of band.

5. **A representative example or the test suite runs.**
   ```bash
   python examples/train.py --dry-run
   # or:
   python -m pytest tests/ -x
   ```
   Executing one of the repo's example scripts (or its tests) is the real proof the environment is usable, not just installable.

6. **Security patches were applied deliberately, not by blanket upgrade.** If you bumped a dependency for a CVE, confirm you changed only that pin to a specific version and re-ran the smoke test.

7. **The environment is isolated.**
   ```bash
   which python
   # Should point to the venv or conda env, NOT /usr/bin/python or system Python
   ```
   On Windows:
   ```powershell
   Get-Command python | Select-Object -ExpandProperty Source
   # Should point to the venv or conda env, NOT C:\Python3xx\python.exe
   ```
   Installs must land in the project's conda env or `venv`, not the system interpreter, so this repo can't disturb other projects (and vice versa).

## Related Skills

- `python-environment-setup` — General Python environment configuration when reproduction guarantees are not the goal.
- `conda-environment-management` — Conda-specific operations (channels, solver, exporting an env).
- `docker-containerization` — Container-based isolation when you need the whole OS layer pinned, not just Python.
- `dependency-resolution` — Untangling conflicting transitive pins after the interpreter already matches.
