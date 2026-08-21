---
name: agents-sdk
description: Build, run, deploy, and evaluate OpenAI Agents SDK apps. Use when the user asks to create or adapt an Agents SDK app, build from a prompt or Codex thread, prepare a runnable agent prototype, add a focused eval harness, or deploy locally through the Agents SDK Deployment Manager. Not for LangChain/CrewAI or generic Chat Completions wrappers without the OpenAI Agents SDK.
version: 1.0.1
---

## When to Use

Use this skill when the user asks to:

- Create a new runnable OpenAI Agents SDK app from an idea, prompt, or prior Codex thread.
- Adapt an existing repo or demo by adding the smallest Agents SDK layer needed to make the workflow agentic.
- Add a focused local eval harness against the real agent path.
- Deploy an existing or newly built Agents SDK app locally through the Deployment Manager.
- Turn prior Codex work (thread IDs, session links, rollout JSONL paths, pasted summaries) into a build brief and then a working app.

Prefer Python unless the user explicitly asks for TypeScript.

## Prerequisites

- **API key**: Agents SDK apps require `OPENAI_API_KEY` to run. Before building, running, or testing an app that calls the OpenAI API, use the `openai-platform-api-key` skill in this plugin as the credential gate. Follow that skill's confirmation flow. Never print, summarize, or commit secret values.
- **Docs gate**: Read the Agents guide before creating or changing any Agents SDK implementation. Read the Sandbox Agents guide before choosing `SandboxAgent`, workspace manifests, shell/file access, skills, or sandbox backend behavior. If a docs MCP/tool is unavailable, read the official docs URLs directly instead of skipping the docs gate.
- **Package manager**: For Python projects, prefer `uv`. Add `openai-agents` when the project owns dependencies.
- **Windows host (primary)**: Commands below that use `$VAR` or `$HOME` are POSIX shell forms used by the Deployment Manager Makefile. On a Windows PowerShell host, set environment variables with `$env:VAR = "value"` and reference paths with backslash or forward-slash forms as appropriate. When invoking `make`, run it in a POSIX-compatible shell (Git Bash, WSL) because the Deployment Manager Makefile uses POSIX syntax.

## References

Load these reference files and URLs at the specific points noted:

- **Agents guide** — `https://developers.openai.com/api/docs/guides/agents` — Read **before creating or changing** any Agents SDK implementation.
- **Sandbox Agents guide** — `https://developers.openai.com/api/docs/guides/agents/sandboxes` — Read **before choosing `SandboxAgent`**, workspace manifests, shell/file access, skills, or sandbox backend behavior.
- **Python SDK** — `https://github.com/openai/openai-agents-python` — Follow for packaging, naming, and command conventions in Python projects.
- **TypeScript SDK** — `https://github.com/openai/openai-agents-js` — Follow only when the user asks for TypeScript.
- **Deployment Manager** — `https://github.com/openai/openai-cookbook/tree/main/examples/agents_sdk/deployment_manager` — Read **before deploying**; verify `$MANAGER_DIR/Makefile` exists before invoking `make`.
- **Agent evals guide** — `https://developers.openai.com/api/docs/guides/agent-evals` — Read **before creating or changing evals** or generating platform eval configs, grader JSON, or dataset upload scripts. Also read trace grading, evals, and graders docs before those specific artifacts.

If a docs MCP/tool is unavailable, read the official docs URLs directly instead of skipping the docs gate.

## Procedure

### 1. Intake — classify the request before editing

- **New app from prompt or idea**: Build the smallest runnable Agents SDK app that proves the workflow.
- **Existing app or demo**: Inspect the repo and add the smallest Agents SDK layer needed to make the workflow agentic.
- **Prior Codex work**: Turn thread IDs, session links, rollout JSONL paths, or pasted summaries into a short build brief before writing code.
- **Evals request**: Add a focused local eval harness against the real agent path.
- **Deployment-only request**: Deploy the existing app without rebuilding unless deployment reveals a small required fix.

### 2. Inspect the target repo

Read `README.md`, dependency files, app entrypoints, existing examples, and any domain-specific `skills/` or policy files.

### 3. Define the app contract

Capture the agent goal, input shape, expected output, tools, state, approval gates, and the local command that proves the workflow.

### 4. Set up dependencies

Use the repo's existing package manager. For Python projects, prefer `uv`; add `openai-agents` when the project owns dependencies.

```powershell
uv init --name my-agent-app
uv add openai-agents
```

### 5. Start with one agent

Use a single `Agent` with clear static `instructions` and `Runner.run` until the workflow proves it needs specialists, handoffs, structured outputs, or sandbox execution.

### 6. Add tools deliberately

Use `@function_tool` for deterministic local actions such as lookups, calculations, file transforms, API calls, or validation. Keep side effects narrow and schemas explicit.

### 7. Add sandbox only for workspace tasks

Use `SandboxAgent` when the agent must inspect files, run shell commands, use workspace skills, or create artifacts in an isolated environment. Keep ordinary business workflows on normal `Agent` plus tools. Read the Sandbox Agents guide before this step.

### 8. Make it runnable

Provide a local smoke command, sample input, and expected observable output. If there is a UI, wire it to the agent path and verify the core workflow, not just rendering.

For HTTP apps that may be deployed:

- Make `uv run python main.py` start the web service when `PORT` is present.
- Keep CLI-only smoke behavior behind explicit arguments or the no-`PORT` path.
- Expose `/health` for readiness.

### 9. Recommended project layout

For every new prototype or substantial app build, prefer:

```text
<project>/
  agent.py              # Agent definition, tools, and run helper
  main.py               # API/server/CLI entrypoint if needed
  pyproject.toml        # includes openai-agents if the project owns deps
  docs/
    prompt.md           # runtime prompt or instructions used by the app agent
    agent-interactions.png
    agent-sequence.png
  data/                 # small sample inputs or fixtures
  skills/<domain>/      # optional domain instructions or reusable policy
  README.md             # local run instructions if the project already uses READMEs
```

Generate diagrams directly as PNG files. Do not create SVG diagram sources or rely on browser screenshots of SVGs unless the user explicitly asks for editable vector sources. For one-off diagram generation, prefer a small `generate_diagrams.py` at the app root and run extra drawing dependencies with `uv run --no-project --with ...` so the app dependency file stays focused. This folder does not ship that helper.

### 10. Build from Codex (when source is prior Codex work)

Create a compact brief before building:

- Confirmed facts from the source threads.
- Inferences and open questions.
- App goal, agent behavior, tools, state, UI, approvals, sandbox needs, and deployment assumptions.
- A standalone build prompt that can drive the implementation.

Prefer the newest user direction when threads conflict. Keep secrets out of the brief and mention missing environment variable names only.

If the user already asked to build after planning, continue from the brief into the build workflow. Otherwise ask for approval before implementing.

### 11. Eval workflow

Add evals when requested. Default to a local harness that exercises the real agent workflow rather than a mock or contract-only path.

Before creating or changing evals, read the Agents guide and Agent evals guide. Read trace grading, evals, and graders docs before generating platform eval configs, grader JSON, or dataset upload scripts.

Prefer an `evals/` folder unless the repo already has a stronger convention:

```text
<project>/
  evals/
    README.md
    cases.jsonl
    graders.py
    run_local.py
    results/
      .gitignore
```

Design a small case matrix around meaningful behavior: happy path, missing evidence, escalation boundary, required or forbidden tool calls, approval gates, state updates, and regressions from observed bugs. Grade behavior such as structured output, tool calls, handoffs, guardrails, trace IDs, event logs, state changes, and approval behavior instead of volatile IDs or exact prose unless wording is contractual.

`evals/run_local.py` should:

1. Load cases from `cases.jsonl`.
2. Add the app root to `sys.path`.
3. Run each case through the app's real agent path.
4. Isolate or reset state between cases.
5. Require needed environment variable names up front.
6. Write `evals/results/latest.json`.
7. Exit non-zero on failures.

### 12. Deploy workflow

Use the Deployment Manager from `openai-cookbook` for local deployments. Default to `local-docker` unless the user or app requires a different local target.

#### 12a. Check deployable app signals

- An app/orchestrator entrypoint, usually `main.py`.
- Dependency metadata, preferably `pyproject.toml`.
- `openai-agents` in the app dependencies.
- `PORT` support for local app startup, with `uv run python main.py` starting the HTTP service when `PORT` is set.
- `/health` readiness endpoint.
- Optional `SANDBOX_BACKEND` support for sandbox-backed apps.
- Optional `docs/prompt.md`, `docs/agent-interactions.png`, and `docs/agent-sequence.png` for manager app details.

#### 12b. Resolve the manager directory

1. Prefer `DEPLOYMENT_MANAGER_ROOT` when set.
2. Otherwise use `$HOME/code/openai-cookbook/examples/agents_sdk/deployment_manager`.
3. If the cookbook checkout is missing, clone `https://github.com/openai/openai-cookbook`.
4. If it exists, update it with `git pull --ff-only` unless the user asked to avoid updating local checkouts.
5. **Stop and report** local changes or diverged history instead of forcing the checkout. Do not force-push or discard user local changes.
6. Verify `$MANAGER_DIR/Makefile` exists before deploying.

On Windows PowerShell, set the manager directory explicitly:

```powershell
$env:DEPLOYMENT_MANAGER_ROOT = "~\code\openai-cookbook\examples\agents_sdk\deployment_manager"
```

#### 12c. Deploy through the manager

```bash
make -C "$MANAGER_DIR" deploy PROJECT_PATH=<absolute-app-path>
```

Useful options:

```bash
make -C "$MANAGER_DIR" deploy PROJECT_PATH=/path/to/app APP_PORT=8421
make -C "$MANAGER_DIR" deploy PROJECT_PATH=/path/to/app TARGET=local-process
make -C "$MANAGER_DIR" deploy PROJECT_PATH=/path/to/app SANDBOX_BACKEND=docker
make -C "$MANAGER_DIR" start
make -C "$MANAGER_DIR" health
```

#### 12d. Let the manager own extraction and deployment records

The helper imports the project, creates or reuses a matching deployment, starts it, and prints JSON with `manager_url`, `deployment`, and `app_url`. For `local-docker`, it may generate or reuse an app-level `Dockerfile`. If that changes the app worktree, report it and **do not revert** user files.

#### 12e. Verify the result

Check manager health, the app `/health` readiness endpoint, and deployment sessions/containers when available.

```bash
curl -fsS http://127.0.0.1:8732/api/health
curl -fsS <app-url>/health
curl -fsS http://127.0.0.1:8732/api/deployments/<deployment-id>/sessions
curl -fsS http://127.0.0.1:8732/api/deployments/<deployment-id>/containers
```

Run `git -C <app-path> status --short` when the app path is inside a git checkout so generated Dockerfiles or other local edits are visible.

## Pitfalls

- **Skipping the docs gate**: Never create or change an Agents SDK implementation without reading the Agents guide first. Never choose `SandboxAgent` without reading the Sandbox Agents guide. If a docs MCP/tool is unavailable, read the official docs URLs directly.
- **Leaking secrets**: Never print, summarize, or commit `OPENAI_API_KEY` or any secret value. Use the `openai-platform-api-key` skill as the credential gate. Keep secrets out of Codex build briefs; mention missing environment variable names only.
- **Over-engineering on first build**: Start with one `Agent` and `Runner.run`. Do not add handoffs, specialists, structured outputs, or sandbox execution until the workflow proves it needs them.
- **Sandbox misuse**: Do not use `SandboxAgent` for ordinary business workflows. Reserve it for workspace tasks: file inspection, shell commands, workspace skills, artifact creation in an isolated environment.
- **Missing `/health` or `PORT` support**: HTTP apps that may be deployed must start the web service when `PORT` is present via `uv run python main.py` and expose `/health`. Without these, the Deployment Manager cannot verify readiness.
- **Forcing cookbook checkout updates**: If `git pull --ff-only` fails due to local changes or diverged history, stop and report. Do not force-push, force-pull, or discard user local changes.
- **Reverting manager-generated files**: If the Deployment Manager generates or reuses an app-level `Dockerfile` that changes the app worktree, report it but do not revert user files.
- **Evaluating volatile values**: Grade behavior (structured output, tool calls, handoffs, guardrails, trace IDs, event logs, state changes, approval behavior), not volatile IDs or exact prose unless wording is contractual.
- **SVG diagrams**: Do not create SVG diagram sources or rely on browser screenshots of SVGs. Generate PNGs directly. Use a project-local `generate_diagrams.py` with `uv run --no-project --with ...` to keep app dependencies clean.
- **Mixing generated files in summary**: Keep generated app files, eval files, and deployment-generated files separated in the final summary.

## Verification

Before handing back, confirm each item:

1. **Local run command**: The app has a clear local run command and a smoke result, or a clear blocker is reported.
2. **Deployment**: If deployment was requested, the manager URL and app URL are reported.
3. **Blockers explicit**: Any missing credentials, model access, port conflicts, Docker issues, or layout warnings are stated explicitly.
4. **File separation**: Generated app files, eval files, and deployment-generated files are separated in the summary.

Checkable commands:

```bash
# Local smoke (Python, no PORT → CLI mode)
uv run python main.py

# Local smoke (HTTP mode)
PORT=8421 uv run python main.py
curl -fsS http://127.0.0.1:8421/health

# Eval harness
uv run python evals/run_local.py
cat evals/results/latest.json

# Deployment Manager health
curl -fsS http://127.0.0.1:8732/api/health

# Deployed app health
curl -fsS <app-url>/health

# Check for manager-generated files in app worktree
git -C <app-path> status --short
```

On Windows PowerShell:

```powershell
# Local smoke (CLI mode)
uv run python main.py

# Local smoke (HTTP mode)
$env:PORT = "8421"; uv run python main.py
Invoke-RestMethod -Uri http://127.0.0.1:8421/health

# Eval harness
uv run python evals/run_local.py
Get-Content evals/results/latest.json
```

## Related skills

- `openai-platform-api-key` — Credential gate for `OPENAI_API_KEY`. Always use before building, running, or testing an Agents SDK app that calls the OpenAI API.
