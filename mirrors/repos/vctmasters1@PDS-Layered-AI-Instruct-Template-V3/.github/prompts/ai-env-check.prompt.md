---
mode: agent
description: Audit the workspace's host-vs-container isolation state and recommend containment for the active stack. Read-only — never installs or modifies.
---

# /ai-env-check

Report whether the current shell is on the **host** or inside a **contained environment** (container, devcontainer, venv, WSL, etc.), and which per-stack containment options the workspace has, is missing, or should adopt.

This prompt is the authoritative interactive entry point for [.ai/environment.md](../../.ai/environment.md). It **never installs, modifies, or scaffolds anything on its own** — every action requires explicit user confirmation.

---

## Steps

### 1. Read the canonical rules

Read [.ai/environment.md](../../.ai/environment.md) once for the matrix and per-stack guidance. Do not restate it in the output; reference the section anchors instead.

### 2. Detect the environment

Run the checks from [.ai/environment.md → Environment Detection](../../.ai/environment.md#environment-detection). At minimum:

- `Test-Path /.dockerenv` (or `[ -f /.dockerenv ]`)
- Env vars: `REMOTE_CONTAINERS`, `CODESPACES`, `KUBERNETES_SERVICE_HOST`, `VIRTUAL_ENV`, `CONDA_PREFIX`, `WSL_DISTRO_NAME`, `CONTAINER`
- `uname -r` (skip on pure Windows)
- `cat /proc/1/cgroup` (skip on Windows)

Read the relevant signals using the project's shell (see [.github/dev-specs.md](../dev-specs.md)). Do not install detection tools — only use what the shell provides.

Classify the shell as exactly one of:

- **Host** (no containment detected)
- **WSL distro** (Linux-side host — treat Linux installs as contained, Windows installs as host)
- **Devcontainer / Codespace**
- **Docker container**
- **Kubernetes pod**
- **Python venv active**
- **Conda environment active**

### 3. Inspect the workspace for containment markers

Use `file_search` / `list_dir` (not the network) to detect:

| Marker | Means |
|---|---|
| `.devcontainer/devcontainer.json` | Devcontainer scaffold present |
| `Dockerfile` or `docker-compose.yml` / `compose.yaml` | Docker available for runtime services |
| `.venv/`, `venv/`, `env/` | Python venv directory present |
| `pyproject.toml` + `[tool.poetry]` / `[tool.uv]` / `[tool.hatch]` / `[tool.pdm]` | Project-managed Python env tool |
| `requirements.txt` only (no venv) | Python project without containment |
| `package.json` | Node project |
| `node_modules/` | Node deps installed locally |
| `.nvmrc` / `engines.node` in `package.json` | Node version pinned |
| `CMakeLists.txt`, `Makefile`, `meson.build` | C/C++ project |
| `vcpkg.json`, `conanfile.txt`, `conanfile.py` | Project-managed C/C++ deps |
| `build/`, `out/`, `cmake-build-*/` | Out-of-tree build dir present |

### 4. Cross-reference with `dev-specs.md`

Read [.github/dev-specs.md](../dev-specs.md). If the project declares a stack (TypeScript, Python, C/C++, etc.), match it against the containment markers and use the per-stack guidance in [.ai/environment.md → Per-Stack Containment](../../.ai/environment.md#per-stack-containment).

If `dev-specs.md` is still template-empty, note that and recommend running `/ai-onboard` first.

### 5. Produce the report

Output exactly these sections, in this order. Use Markdown. Do not pad.

#### Environment

> **You are on**: `Host` | `WSL distro: <name>` | `Devcontainer` | `Docker container` | `Python venv: <path>` | `Conda env: <name>` | `Codespace` | ...

One line. Include any secondary signals (e.g., "Host with Python venv active at `./.venv/`").

#### Containment markers found

Table with three columns: **Marker**, **Path**, **Means**. Only list markers that exist.

#### Per-stack assessment

For each stack present in the workspace (Node, Python, C/C++):

- **Status**: `✅ contained` | `⚠️ partial` | `❌ host-only`
- **What's present**: short bullet list
- **What's missing or recommended**: short bullet list — each item links to the relevant section of [.ai/environment.md](../../.ai/environment.md)

#### Risk summary

One sentence per risk, only if real. Examples (do not invent risks that don't apply):

- "`pip install` from this shell would land on the host because no venv is active."
- "`npm install -g <tool>` would mutate the user's global Node install."
- "No devcontainer is present; new contributors will repeat manual host setup."

#### Recommended next steps

A numbered list, **ordered least-invasive to most-invasive**. Examples (offer only when applicable):

1. Activate the existing `.venv/` before running Python commands.
2. Add `.nvmrc` pinning Node version `<X>`.
3. Create a `.venv/` with `python -m venv .venv` (offer to walk through it).
4. Add a `docker-compose.yml` for runtime dependencies (Postgres, Redis, etc.).
5. Scaffold a `.devcontainer/devcontainer.json` (offer to walk through it).

For each recommendation, end with: **"Would you like me to walk through this now?"** — and stop. Do not begin scaffolding without an affirmative answer.

### 6. Stop. Do not modify.

This prompt finishes with the report and a single follow-up question. Any scaffolding (venv creation, devcontainer setup, docker-compose drafting) only happens if the user picks one of the offered steps in their next message.

---

## Notes

- This prompt **never** runs `pip install`, `npm install`, `apt install`, `brew install`, `choco install`, `winget install`, or any package-manager command. Its only side effect is the report.
- If the shell context cannot be determined (e.g., no terminal access), say so and recommend the user run the detection commands themselves; provide the commands.
- If the user is clearly already inside a contained environment, lead with that and keep the report short — they're already doing the right thing.
- Cross-platform commands: prefer PowerShell on Windows hosts (see [.github/dev-specs.md](../dev-specs.md)); use POSIX shell on macOS/Linux/WSL.
