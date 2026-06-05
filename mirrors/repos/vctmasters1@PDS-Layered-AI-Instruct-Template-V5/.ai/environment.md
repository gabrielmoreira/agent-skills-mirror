# Environment — Host Isolation & Workspace Containment Rules

**Scope**: Project-wide canonical reference
**Last Updated**: 2026-05-25

> This file is the **single source of truth** for how AI agents and contributors handle the boundary between the **host machine** and the **project's contained environment** (virtualenv, `node_modules`, build directory, Docker container, devcontainer, VM, WSL distro, etc.).
>
> The rule is not "never install anything." The rule is: **detect the boundary, stay inside it, and never silently mutate the host.** Never duplicate these rules — link here.

---

## Contents

| Section | What's here |
|---|-------------|
| [Why This Exists](#why-this-exists) | The problem host-mutating AI causes for a template-driven workspace |
| [The Core Rule](#the-core-rule) | Detect-then-act: containment first, host last |
| [Environment Detection](#environment-detection) | How to tell whether you are on the host or inside a container |
| [Allowed vs. Restricted Operations](#allowed-vs-restricted-operations) | The matrix that drives AI behavior |
| [Per-Stack Containment](#per-stack-containment) | TypeScript/Node, Python, C/C++ — preferred isolation per stack |
| [Devcontainers & Docker](#devcontainers--docker) | When to recommend, what to scaffold |
| [AI Behavior Rules](#ai-behavior-rules) | What the AI must do, ask, or refuse |
| [`/ai-env-check`](#ai-env-check) | Audit prompt that reports the workspace's isolation state |

---

## Why This Exists

This repository is a **template** that gets imported into many other projects. Once adopted, AI agents will execute commands suggested by these instruction files. If the agent runs `pip install something`, `npm install -g something`, `choco install`, `brew install`, `apt install`, `winget install`, `dotnet tool install -g`, or similar **on the host**, three bad things happen:

1. **Silent host pollution** — the developer's machine gains state they did not consent to, often outside any project's lockfile.
2. **Cross-project contamination** — a package installed for project A breaks project B that pinned a different version.
3. **Non-reproducible builds** — "works on my machine" because the host has state nobody's `package.json`/`requirements.txt`/`CMakeLists.txt` documents.

The fix is not to ban installs. The fix is to make sure **every install lands inside the project's contained environment** (or inside a container/devcontainer the user explicitly chose), and to require explicit confirmation before any host-level mutation.

---

## The Core Rule

**Before any install, build, or tool-bootstrap command, the AI must:**

1. Detect whether the current shell is **inside** a container, devcontainer, VM, WSL distro, virtualenv, or other isolated context — **or** running directly on the host.
2. If **inside a contained environment**: proceed normally. Containers are sacrificial; mutating them is the point.
3. If **on the host**:
   - Prefer the project-local containment for the active stack (see [Per-Stack Containment](#per-stack-containment)).
   - If a host-level install is genuinely required, **ask the user first** and explain (a) what will be installed, (b) why it can't be project-local, (c) how to uninstall.
   - Never run `*-install-global`, `*-install -g`, OS package managers, or system-level tool installers without explicit confirmation.

The AI does **not** refuse host installs categorically. It refuses **silent** host installs.

---

## Environment Detection

Run these checks before any host-mutating command. The first positive match means "inside containment — proceed":

| Signal | Means |
|---|---|
| `/.dockerenv` exists | Inside a Docker container |
| Env var `REMOTE_CONTAINERS=true` or `CODESPACES=true` | Inside a VS Code devcontainer or GitHub Codespace |
| Env var `KUBERNETES_SERVICE_HOST` is set | Inside a Kubernetes pod |
| `cat /proc/1/cgroup` mentions `docker`, `containerd`, `kubepods`, `lxc` | Containerized Linux |
| Env var `VIRTUAL_ENV` is set | Python venv active |
| Env var `CONDA_PREFIX` is set | Conda environment active |
| Env var `WSL_DISTRO_NAME` is set | Running inside WSL (treated as contained for Linux-tool installs; **still host** for Windows-side installs) |
| `uname -r` ends in `-microsoft-standard-WSL2` | WSL2 distro |
| `$env:CONTAINER` is set (custom convention) | Project marker the user can set |

If none match, the shell is **on the host**.

The [`/ai-env-check`](#ai-env-check) prompt automates this audit and reports findings.

---

## Allowed vs. Restricted Operations

| Operation | On Host (no containment) | Inside Container / Devcontainer / venv |
|---|---|---|
| Edit files inside the workspace | ✅ Free | ✅ Free |
| Read/write files under the workspace | ✅ Free | ✅ Free |
| `npm install` / `pnpm install` / `yarn` (project-local, writes to `node_modules`) | ✅ Free | ✅ Free |
| `pip install` **inside an activated venv** | ✅ Free | ✅ Free |
| `cmake --build build/` / out-of-tree compile | ✅ Free | ✅ Free |
| `npm install -g <pkg>` | ⚠️ Ask first | ✅ Free |
| `pip install <pkg>` **without** activated venv | ⚠️ Ask first; offer to create venv | ✅ Free |
| `pipx install <pkg>` | ⚠️ Ask first (pipx is host-level even if isolated per tool) | ✅ Free |
| `choco install`, `winget install`, `brew install`, `apt install`, `dnf install`, `pacman -S` | ⛔ Refuse without explicit confirmation | ✅ Free |
| `dotnet tool install -g`, `cargo install` (global cargo), `go install` (writes to `$GOPATH/bin`) | ⚠️ Ask first | ✅ Free |
| Modify host PATH, registry, dotfiles, shell rc files | ⛔ Refuse without explicit confirmation | ⚠️ Still ask — even in a container, dotfile changes are often unintended |
| Touch files **outside** the workspace root | ⛔ Refuse without explicit confirmation | ⛔ Same |
| Spawn long-running services (databases, message brokers) directly on the host | ⚠️ Recommend Docker Compose instead | ✅ Free |

> **Legend**: ✅ proceed without asking · ⚠️ ask once, then proceed if confirmed · ⛔ refuse unless user explicitly overrides

---

## Per-Stack Containment

For each stack the project uses, prefer the listed containment. The [`/ai-env-check`](#ai-env-check) prompt can scaffold these on request.

### TypeScript / Node

- **Default containment**: project-local `node_modules/` via the project's package manager (`npm`, `pnpm`, `yarn`, `bun`) — already isolated per project.
- **Node version**: pin via `.nvmrc` or `package.json` `engines.node`. Use [`nvm`](https://github.com/nvm-sh/nvm), [`fnm`](https://github.com/Schniz/fnm), or [`volta`](https://volta.sh/) — all install Node into a user-local directory, not the system.
- **CLI tools** (e.g., `tsx`, `vite`, `tsc`): use `npx`, `pnpm dlx`, or add to project `devDependencies` — never `npm install -g`.
- **Avoid**: `npm install -g typescript`, `npm install -g <build-tool>` on the host.

### Python

- **Default containment**: per-project virtualenv at `./.venv/` (created by `python -m venv .venv`, or by `uv venv`, `poetry`, `hatch`, `pdm`, `conda`, etc. — whatever the project picks).
- **Activation**: always activate before installing. The AI must verify `VIRTUAL_ENV` is set, or use the venv's `bin/python -m pip ...` explicitly.
- **CLI tools** (e.g., `black`, `ruff`, `pytest`): prefer adding to project dependencies; if a tool needs to be globally callable across many projects, prefer [`pipx`](https://pipx.pypa.io/) (still ask first) over `pip install --user` or `sudo pip`.
- **System Python**: do not modify. Never `sudo pip install` anything. Never `pip install --user` without asking.
- **Avoid**: any `pip install` while `VIRTUAL_ENV` is unset on the host.

### Embedded C / C++

- **Default containment**: out-of-tree build directory (`build/`, `out/`, or per-target subdir). Build artifacts never live alongside source.
- **Toolchain**: prefer project-local toolchains via [`vcpkg`](https://vcpkg.io/) manifest mode, [`conan`](https://conan.io/) in the project, or a pinned toolchain installed by the project's CI/devcontainer — not a system-wide cross-compiler the user has to remember to keep updated.
- **System libraries** (e.g., `libssl-dev`, vendor SDKs, JTAG drivers): these usually *do* need host installs. When they do, the AI must (a) ask, (b) document the exact commands in the module's `.dev-docs/`, (c) recommend a devcontainer for new contributors so they don't repeat the manual install.
- **IDE/SDK installers** (Silicon Labs Simplicity, STM32CubeIDE, Segger J-Link, etc.): never auto-install. Always link to the vendor page and ask the user to install manually.
- **Avoid**: `sudo apt install` of build-time dependencies without first asking and documenting.

---

## Devcontainers & Docker

A **devcontainer** ([`.devcontainer/devcontainer.json`](https://containers.dev/)) is the gold standard for this template, because it converts the entire host-vs-container question into "the container is always the right answer." When the project ships a devcontainer:

- VS Code, Codespaces, JetBrains Gateway, and others open the workspace **inside** the container automatically.
- All AI installs land in the container — the host stays clean.
- The container definition is part of the repo, so every contributor gets the same toolchain.

**When to recommend scaffolding one** (the AI should suggest, not unilaterally create):

- Project uses **multiple languages or system libraries** (e.g., Node + Python + libpq).
- Project needs **specific tool versions** that differ from typical host installs.
- Project is **embedded** and depends on cross-compilers, JTAG drivers, or vendor SDKs.
- Project has **>2 contributors** and "works on my machine" friction is likely.

**Docker Compose** is the right answer for runtime dependencies (databases, brokers, caches). Never start Postgres/Redis/Kafka directly on the host as a tutorial step — provide a `docker-compose.yml` instead.

---

## AI Behavior Rules

When the AI is about to run any command or suggest a setup step, it must:

1. **Detect first.** Run the [Environment Detection](#environment-detection) checks. If detection is ambiguous, run [`/ai-env-check`](#ai-env-check) or ask the user.
2. **Match the matrix.** Cross-reference the operation with [Allowed vs. Restricted Operations](#allowed-vs-restricted-operations). Treat ⚠️ as a hard stop until the user confirms.
3. **Prefer project-local.** When multiple containment options exist, default to the one closest to the project (project-local > venv/node_modules > devcontainer > host).
4. **Never silently bootstrap.** Do not "helpfully" install a tool the user didn't ask for — even if the user's request implies needing it. Surface the dependency and ask.
5. **Document host installs.** If a host install is genuinely required and approved, record it in the relevant module's `.dev-docs/` so future contributors and CI know about it.
6. **Recommend devcontainer when patterns emerge.** If the project has had two or more host-install conversations, suggest scaffolding a devcontainer.
7. **WSL nuance.** Inside a WSL distro, Linux-tool installs are "in containment." Windows-side installs from the WSL shell (rare, but possible via `cmd.exe`/`powershell.exe`) are **host** mutations.
8. **CI gates.** If CI installs system packages, that's the documented escape hatch. The host-isolation rule applies to local developer machines, not to ephemeral CI runners.

---

## Stage 2b (Environment Gate) Triggers

The Supervisor pipeline's Stage 2b invokes the environment-manager to gate host-mutating operations. Stage 2b is **mandatory** if any of the following operations are present in the change set:

### Host-Mutating Operations (Trigger Stage 2b)

- **Package manager installs**: `npm install -g`, `pip install` (host-level), `pip install --user`, `pipx install`, `brew install`, `apt install`, `choco install`, `dnf install`, `pacman -S`, `winget install`
- **Global tool installs**: `cargo install` (global), `go install` (writes to `$GOPATH/bin`), `dotnet tool install -g`, `gem install` (global)
- **Shell or path modifications**: Adding to `$PATH`, modifying shell rc files (`.bashrc`, `.zshrc`, `.profile`, `$PROFILE`)
- **System-level configuration**: Modifying `/etc/`, Windows registry, or other OS-level config
- **Setup scripts that install globally**: Any setup.sh, setup.ps1, install.sh that runs host-level installs
- **Container image builds**: Modifying a Dockerfile that installs system packages (not the code in the project; the **Dockerfile itself** triggers Stage 2b to decide on containment strategy)
- **Virtual environment creation suggestions**: Proposing `python -m venv`, `poetry install`, `npm ci` if the project has no evidence of the environment existing yet (the gate asks the user to confirm isolation strategy before scaffolding)

### Non-Triggering Operations (Skip Stage 2b)

- Editing files inside the project's existing containment (venv, `node_modules`, `build/`, etc.)
- Running `npm install` / `pip install` inside an **already-activated venv** or project-local context
- Building with `cmake --build`, `npm run build`, `python setup.py`, etc. inside existing containment
- Creating new files or editing source code
- Running tests or linters (even if they require pre-installed packages — assume the project's venv/containers have them)

### Stage 2b Actions

When triggered, environment-manager:

1. **Detects** the current environment (host vs. container, per [Environment Detection](#environment-detection)).
2. **Advises**: If on host and the operation is marked ⚠️ in the matrix, asks for confirmation.
3. **Blocks** if the operation is marked ⛔ and the user has not explicitly overridden.
4. **Scaffolds** if the user requests: creates `.venv/`, `docker-compose.yml`, `.devcontainer/`, or `.nvmrc` as appropriate before the operation proceeds.
5. **Returns** to Supervisor with verdict: `green-light` (proceed), `ask` (awaiting user confirmation), or `refuse` (operation cannot proceed in current environment).

---

## AI Behavior Rules

---

## `/ai-env-check`

The [`/ai-env-check`](../.github/prompts/ai-env-check.prompt.md) slash command:

- Runs all [Environment Detection](#environment-detection) checks against the current shell.
- Inspects the workspace for present containment markers (`.venv/`, `node_modules/`, `package.json`, `pyproject.toml`, `CMakeLists.txt`, `.devcontainer/`, `docker-compose.yml`, `Dockerfile`, `.nvmrc`).
- Reports a clear summary: "you are on the host" or "you are inside `<container>`", and which per-stack containment options are present, missing, or recommended.
- **Does not modify anything.** Pure audit. If the user wants to scaffold (a venv, a `.nvmrc`, a devcontainer, a `docker-compose.yml`), the prompt offers to do so step-by-step — never automatically.

Run it:

- After cloning, before any other setup work.
- Any time the AI is unsure whether a command will land on the host or in a container.
- During [`/ai-onboard`](../.github/prompts/ai-onboard.prompt.md), which invokes it to pick the isolation strategy for the project.
