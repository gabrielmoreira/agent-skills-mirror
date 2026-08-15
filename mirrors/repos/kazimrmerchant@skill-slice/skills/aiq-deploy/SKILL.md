---
name: aiq-deploy
description: "Deploys, validates, troubleshoots, and stops NVIDIA AI-Q Blueprint 2.1.x (Docker Compose, Kubernetes/Helm, local process, CLI, or web UI). Use when installing or cloning AI-Q, starting the backend, checking /health, fixing port or credential failures, or handing a verified AIQ_SERVER_URL to aiq-research. Not for deep research report generation (that is aiq-research)."
version: 2.1.1
license: Apache-2.0
compatibility: |
  Designed for Claude Code, OpenCode, Codex, and Agent Skills-compatible tools. Requires Git, network
  access to GitHub, and one selected runtime path: Docker Compose v2 for the default local deployment,
  Python 3.11+ and uv for local process or CLI mode, Node.js 20+ and npm for local web UI mode, or
  kubectl 1.28+ and Helm 3.12+ for Kubernetes and Helm mode.
metadata:
  author: "NVIDIA AI-Q Blueprint Team <aiq-blueprint@nvidia.com>"
  github-url: "https://github.com/NVIDIA-AI-Blueprints/aiq"
  tags:
    - nvidia
    - aiq
    - blueprint
    - deploy
    - operations
    - agent-skills
allowed-tools: Read Bash
---

# AIQ Deploy Skill

## Overview

This skill owns setup, deployment, operational checks, troubleshooting, and shutdown of the NVIDIA AI-Q Blueprint server. It does **not** run deep research itself. After deployment is healthy, hand off the verified server URL to `aiq-research`.

The workflow stays explicit so deployment validation and handoff are repeatable across supported agent clients.

**Version Compatibility:** This skill targets NVIDIA AI-Q Blueprint version 2.1.0.

```text
Skill version: X.Y.Z
Blueprint version: A.B.C

Compatible IF:
1. A == X  (Major versions MUST match)
2. B >= Y  (Minor version must be equal or greater)
3. C can be anything (Patch version does not affect compatibility)
```

- Skill 2.1.0 ↔ Blueprint 2.1.0 ✅
- Skill 2.1.0 ↔ Blueprint 2.2.0 ✅
- Skill 2.1.0 ↔ Blueprint 2.1.5 ✅
- Skill 2.1.0 ↔ Blueprint 3.0.0 ❌
- Skill 2.1.0 ↔ Blueprint 2.0.0 ❌

If the Blueprint version is not compatible, check for an updated skill, use a compatible Blueprint version, or proceed only when the user accepts the risk.

## When to Use

Use this skill when the user asks to:

- **Install** or **clone** the NVIDIA AI-Q Blueprint repository.
- **Deploy** or **run** AI-Q locally or on a cluster (Docker Compose, Kubernetes/Helm, local process, CLI, or browser UI).
- **Validate** that the AI-Q backend is healthy and ready for `aiq-research`.
- **Troubleshoot** deployment issues: port conflicts, missing credentials, unhealthy services, config failures.
- **Stop**, restart, rebuild, or clean up AI-Q services.
- **Hand off** a verified `AIQ_SERVER_URL` to `aiq-research`.

Do **not** use this skill for deep research report generation — that belongs to `aiq-research`.

## Prerequisites

- Access to clone or update `https://github.com/NVIDIA-AI-Blueprints/aiq`.
- Git available in the shell.
- One deployment runtime:
  - **Docker Engine with Docker Compose v2** — default durable local deployment.
  - **Python 3.11+ and `uv`** — local process or CLI mode.
  - **Node.js 20+ and `npm`** — local browser UI development mode.
  - **`kubectl` 1.28+, Helm 3.12+, and cluster access** — Kubernetes/Helm mode.
- Network access to GitHub, NVIDIA-hosted model endpoints, and any selected search provider.
- Credentials stored **outside chat**. Hosted-model usage requires `NVIDIA_API_KEY`; web research requires at least one supported search provider key: `TAVILY_API_KEY`, `SERPER_API_KEY`, or `EXA_API_KEY`.
- System capacity for the selected runtime. Docker Compose mode starts the AI-Q backend and PostgreSQL by default; browser UI mode also uses frontend port `3000`. Self-hosted model or RAG deployments may require GPU resources.

> **Windows host (PowerShell) note:** Commands shown in bash syntax work in Git Bash or WSL. In PowerShell, replace `test -f` with `Test-Path`, `cp` with `Copy-Item`, and `export VAR=...` with `$env:VAR = "..."`. Use `curl.exe` (not the `curl` alias to `Invoke-WebRequest`) for health checks.

## Procedure

### Step 1 — Locate or clone AI-Q

**When to load:** If no AI-Q checkout exists or the user asks to install/clone AI-Q, read `references/locate-or-clone.md` **before** cloning.

In an existing checkout, confirm the required files:

```bash
pwd
test -f pyproject.toml
test -f deploy/.env.example
test -d configs
```

**Expected output:** `pwd` prints the AI-Q repository path; the `test` commands exit with status 0 and produce no output.

**PowerShell equivalent:**

```powershell
Get-Location
Test-Path pyproject.toml
Test-Path deploy/.env.example
Test-Path configs
```

### Step 2 — Select the deployment mode

If the user asks to install, deploy, set up, or run AI-Q **without naming a mode**, ask:

```text
How do you want to run AI-Q?

1. Skill backend - backend-only service for aiq-research w/o browser UI.
2. CLI - interactive terminal AI-Q.
3. UI - browser AI-Q app with backend and frontend.
4. Custom - choose an existing AI-Q config or review advanced customization docs before deployment.
```

Wait for the user's answer before starting services.

**Do not ask this question when:**
- The user already specified a mode (Docker Compose, Helm, UI, CLI, or Agent Skill backend).
- `aiq-research` routed here because a deep research request needs a backend. In that case, prefer Agent Skill backend and ask only for permission to start it if needed.

### Step 3 — Prepare environment and secrets

**When to load:** Read `references/env-and-secrets.md` **before** changing `deploy/.env`.

```bash
if [ ! -f deploy/.env ]; then
  cp deploy/.env.example deploy/.env
  echo "created deploy/.env from deploy/.env.example"
fi
```

**Expected output when the file is missing:** `created deploy/.env from deploy/.env.example`
**Expected output when the file exists:** no output; the existing file is preserved.

Before writing secrets, verify `deploy/.env` is git-ignored:

```bash
git check-ignore deploy/.env
```

**Expected output:** `deploy/.env` or a matching ignore rule. If it is not ignored, **stop** and fix the ignore rule before placing credentials in the file.

**HARD RULES:**
- **Never print secret values.** Check only whether required environment variables are set.
- **Never overwrite `deploy/.env`** when it already exists.
- **Never ask the user to paste secret values into chat.** Ask them to update `deploy/.env` directly.

### Step 4 — Route to the selected deployment path

Match the user request, then read the referenced file **before acting**:

| User Intent | Reference to Load |
|---|---|
| No AI-Q checkout exists, install AIQ, clone AIQ, locate repo | `references/locate-or-clone.md` |
| Configure environment, check API keys, inspect `.env` | `references/env-and-secrets.md` |
| Choose an AI-Q workflow config, understand config files, set `BACKEND_CONFIG` or `CONFIG_FILE` | `references/configs.md` |
| Backend-only local server for `aiq-research`, AIQ as an Agent Skill | `references/skill-backend.md` |
| Terminal assistant, CLI-only run, no web UI | `references/terminal-cli.md` |
| Quick local development run, start UI/backend without containers | `references/local-web.md` |
| Default durable local deployment, Docker Compose, containers, PostgreSQL | `references/docker-compose.md` |
| Kubernetes, Helm, cluster deployment | `references/kubernetes-helm.md` |
| Foundational RAG / FRAG integration | `references/frag.md` |
| Basic health checks, shallow smoke checks, handoff to `aiq-research` | `references/validation.md` |
| Optional deep research completion validation | `references/end-to-end-validation.md` |
| Logs, unhealthy services, port conflicts, config failures | `references/troubleshooting.md` |
| Stop services, restart, rebuild, safe cleanup | `references/shutdown.md` |

### Step 5 — Validate and hand off

**When to load:** After startup, read `references/validation.md` and run the appropriate checks for the selected mode.

For the default local backend, verify health:

```bash
curl -sf http://localhost:8000/health
```

**Expected output:** a successful JSON health response or an empty successful response depending on the server build. If the command fails, read `references/troubleshooting.md` and diagnose **before claiming the backend is ready**.

`aiq-research` needs a reachable AI-Q server URL. If the backend is on the default port:

```bash
AIQ_SERVER_URL=http://localhost:8000
```

If the backend runs elsewhere:

```bash
export AIQ_SERVER_URL="http://localhost:<PORT>"
```

**PowerShell:**

```powershell
$env:AIQ_SERVER_URL = "http://localhost:8000"
```

**HARD RULE:** Do not continue into deep research or deep research completion validation unless the user asks for it or confirms the post-deploy validation prompt. This skill's success criterion is a deployed and basically validated server, **not** report generation quality.

## Examples

### Example 1: Deploy a backend-only Skill server with Docker Compose

```bash
test -f deploy/.env || cp deploy/.env.example deploy/.env
git check-ignore deploy/.env
cd deploy/compose
BUILD_TARGET=release docker compose --env-file ../.env -f docker-compose.yaml config --quiet
BUILD_TARGET=release docker compose --env-file ../.env -f docker-compose.yaml up -d --build aiq-agent
curl -sf http://localhost:8000/health
```

**Expected output:**

```text
deploy/.env
<docker compose starts aiq-agent and dependencies>
<health endpoint returns a successful response>
```

If Docker, ports, credentials, or health checks fail, read `references/troubleshooting.md` before retrying.

### Example 2: Hand off a non-default backend URL to aiq-research

```bash
export AIQ_SERVER_URL="http://localhost:8100"
curl -sf "$AIQ_SERVER_URL/health"
```

**Expected output:** a successful health response. Then tell the user to keep `AIQ_SERVER_URL` set before invoking `aiq-research`.

## Pitfalls

### Backend port is already in use

**Symptoms:** Docker Compose fails to bind port `8000`; `curl -sf http://localhost:8000/health` reaches an unexpected service or fails.

**Causes:** Another AI-Q backend or local dev server is running; `PORT` in `deploy/.env` conflicts.

**Solutions:**

1. Identify the process:
   ```bash
   lsof -nP -iTCP:8000 -sTCP:LISTEN
   ```
2. Either stop the conflicting process with the user's approval or set a different port in `deploy/.env` (e.g., `PORT=8100`).
3. Restart and verify:
   ```bash
   curl -sf http://localhost:8100/health
   ```

### Required credentials are missing

**Symptoms:** Infrastructure starts, but model-backed chat or research requests fail. Logs mention unauthorized, forbidden, invalid key, or missing provider configuration.

**Causes:** `NVIDIA_API_KEY` is missing or empty; no supported search provider key is configured.

**Solutions:**

1. Check presence **without printing values** by following `references/env-and-secrets.md`.
2. Ask the user to update `deploy/.env`; do not ask them to paste secrets into chat.
3. Rerun `references/validation.md` after the user updates credentials.

### Backend is healthy but not compatible with aiq-research

**Symptoms:** `/health` succeeds, but `/chat` or `/v1/jobs/async/agents` fails. `aiq-research` reports async agents unavailable.

**Causes:** The selected config is CLI-only or does not expose the web/API backend expected by the skill. `BACKEND_CONFIG` or `CONFIG_FILE` points at the wrong AI-Q config.

**Solutions:**

1. Read `references/configs.md` and confirm the selected config is API-enabled.
2. For the default Skill backend, use `configs/config_web_default_llamaindex.yml`.
3. Restart the backend and rerun `references/validation.md`.

### Docker cleanup would remove useful state

**Symptoms:** Troubleshooting suggests `docker compose down -v`; the user may have local PostgreSQL job or checkpoint data they want to keep.

**Causes:** `down -v` removes Docker volumes. Rebuilds and restarts are often enough for config or image changes.

**Solutions:**

1. Prefer a normal restart from `references/shutdown.md`.
2. **Ask for explicit approval before running volume deletion.**
3. After cleanup, rerun deployment and validation from the selected route.

### FRAG not ready

**HARD RULE:** Do not claim FRAG is ready unless both `RAG_SERVER_URL` and `RAG_INGEST_URL` are configured and reachable. Read `references/frag.md` for setup details.

## Verification

Run these checks after the selected deployment path starts:

1. **Health endpoint** (default port 8000):
   ```bash
   curl -sf http://localhost:8000/health
   ```
   Expected: successful JSON or empty 200 response.

2. **Non-default port** (if applicable):
   ```bash
   curl -sf "$AIQ_SERVER_URL/health"
   ```
   Expected: successful health response.

3. **Git ignore check** (should already be done before secrets):
   ```bash
   git check-ignore deploy/.env
   ```
   Expected: `deploy/.env` or matching ignore rule.

4. **Repository file check** (in existing checkout):
   ```bash
   test -f pyproject.toml && test -f deploy/.env.example && test -d configs && echo "OK"
   ```
   Expected: `OK`

5. **Docker Compose config validation** (Docker mode only):
   ```bash
   cd deploy/compose
   BUILD_TARGET=release docker compose --env-file ../.env -f docker-compose.yaml config --quiet
   ```
   Expected: no output (valid config).

If any check fails, read `references/troubleshooting.md` and diagnose before reporting success.

## Related Skills

- **`aiq-research`** — Consumes the verified `AIQ_SERVER_URL` produced by this skill to run deep research workflows. Hand off the URL only after validation passes.

## References

| Topic | Documentation |
|---|---|
| Locate or clone AI-Q | `references/locate-or-clone.md` |
| Environment and secrets | `references/env-and-secrets.md` |
| Workflow configs | `references/configs.md` |
| Agent Skill backend | `references/skill-backend.md` |
| CLI deployment | `references/terminal-cli.md` |
| Local web deployment | `references/local-web.md` |
| Docker Compose deployment | `references/docker-compose.md` |
| Kubernetes and Helm deployment | `references/kubernetes-helm.md` |
| FRAG integration | `references/frag.md` |
| Basic validation | `references/validation.md` |
| End-to-end validation | `references/end-to-end-validation.md` |
| Troubleshooting | `references/troubleshooting.md` |
| Shutdown and cleanup | `references/shutdown.md` |
