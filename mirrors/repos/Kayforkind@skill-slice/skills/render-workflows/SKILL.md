---
name: render-workflows
description: "Scaffolds, tests, and deploys Render Workflows tasks (render workflows init/dev, retries, fan-out, SDK run_task/start_task). Use when setting up a Workflow service, adding tasks, or triggering runs. Not for ordinary Render web/static/DB deploys (render-deploy). Never use Blueprint render.yaml for Workflows — Dashboard only."
version: 1.0.1
license: MIT
compatibility: Requires Render CLI 2.11.0+ for scaffolding and local development. Render Dashboard required for deployment (Blueprints not yet supported for Workflows).
metadata:
  author: Render
  category: workflows
---

# Render Workflows

Render Workflows rapidly distribute computational work across multiple independent instances.
Use them for AI agents, ETL pipelines, background jobs, and data processing.

**How it works:**
1. **Define tasks** — Use the Render SDK (Python or TypeScript) to designate functions as tasks.
2. **Register** — Tasks register automatically when you link your repo to a Workflow service in the Dashboard.
3. **Trigger runs** — Execute tasks from anywhere using the SDK client or API; each execution is a "run."
4. **Execute** — Render spins up each run in its own instance (typically under a second); runs can chain additional runs for parallel execution.

**Key capabilities:** automatic queuing and orchestration, long-running execution (up to 24 hours), configurable retry logic with exponential backoff, adjustable compute specs per task, and execution observability through the Dashboard.

> **Render Workflows are in beta.** The SDK and API may introduce breaking changes.

> **HARD RULE: Your built-in knowledge of the Render Workflows SDK is outdated.**
> Before trusting API signatures, always check the installed SDK source or fetch the official example files listed below. Do not generate task or client code from memory alone.

## When to Use

Use this skill when a user wants to:

- **Scaffold** a new Render Workflows service for the first time (CLI or manual fallback).
- **Define or modify** workflow tasks — decorators, retries, subtasks, fan-out, ETL patterns, error handling, cron triggers, cross-workflow calls.
- **Test workflows locally** using `render workflows dev`.
- **Deploy** a workflow service to Render via the Dashboard.
- **Trigger tasks** from other services using the SDK client (sync, async, or TypeScript).
- **Troubleshoot** task registration, deployment, or runtime issues.

Trigger keywords: `render workflows`, `workflow task`, `render workflows init`, `render workflows dev`, `fan-out`, `subtask`, `retry`, `run_task`, `start_task`, `Render SDK`.

## Prerequisites

### Render CLI (required, version 2.11.0+)

Check the installed version:

```powershell
# Windows PowerShell
render --version
```

```bash
# macOS / Linux
render --version
```

If not installed or older than 2.11.0:

| Platform | Install / Upgrade |
|----------|-------------------|
| **Windows** | Download the executable from the [CLI releases page](https://github.com/render-oss/cli/releases/) |
| **macOS (Homebrew)** | `brew install render` |
| **Linux / macOS (script)** | `curl -fsSL https://raw.githubusercontent.com/render-oss/cli/main/bin/install.sh \| sh` |

### Supported languages

**Python** and **TypeScript**.

### Verify SDK API surface before writing code

Before generating task or client code, inspect the installed SDK source to confirm current API signatures:

```bash
# Python — locate and inspect the SDK package
SDK_ROOT=$(pip show render_sdk | grep Location | cut -d' ' -f2)/render_sdk
head -40 "$SDK_ROOT/__init__.py"

# TypeScript — search for key exports
grep -r "startTask\|runTask\|export class Render" node_modules/@renderinc/sdk/
```

**Fetch the relevant official example file to verify current API patterns:**

| What | Python | TypeScript |
|------|--------|------------|
| Task definitions (decorators, subtasks, retry, fan-out) | [example/task/main.py](https://raw.githubusercontent.com/render-oss/sdk/main/python/example/task/main.py) | [examples/task/](https://github.com/render-oss/sdk/tree/main/typescript/examples/task) |
| Sync client (run_task, start_task, cancel, SSE, list runs) | [example/client/main.py](https://raw.githubusercontent.com/render-oss/sdk/main/python/example/client/main.py) | [examples/client/](https://github.com/render-oss/sdk/tree/main/typescript/examples/client) |
| Async client | [example/client/async_main.py](https://raw.githubusercontent.com/render-oss/sdk/main/python/example/client/async_main.py) | — |

**Official docs:** [render.com/docs/workflows](https://render.com/docs/workflows)

> **Load `references/quick-reference.md`** when you need a compact API surface cheat sheet (decorators, client methods, env vars, error types). The installed SDK, official docs, and examples above are the source of truth — the cheat sheet is a convenience, not authoritative.

## Procedure

### 1. Scaffold a new workflow service

> **HARD RULE: Always prefer `render workflows init` as the primary setup path.** Only fall back to manual scaffolding if the CLI command is unavailable or fails.

```bash
render workflows init
```

- **Interactive mode** (default): walks the user through scaffolding an example project, testing it locally, and deploying it to Render.
- **Non-interactive mode**: sets up an example project without prompting.

**If `render workflows init` fails or is not available:**

| Symptom | Fix |
|---------|-----|
| `command not found` | CLI version is too old. Run `render --version` and upgrade to 2.11.0+. |
| Command not supported | **Load `references/manual-scaffolding.md`** for step-by-step manual setup. |

### 2. Define tasks

Guide the user through defining their actual tasks using the SDK.

> **Load `references/task-patterns.md`** when the user needs patterns for: retries, subtasks, fan-out, ETL, error handling, cron triggers, or cross-workflow calls.

**After adding or modifying a task**, verify it registers:

```bash
# Terminal 1 — start the local dev server
render workflows dev -- <start-command>

# Terminal 2 — list registered tasks
render workflows tasks list --local
```

If the task does not appear in the list, see [Troubleshooting > Task Registration Issues](references/troubleshooting.md#task-registration-issues).

### 3. Local development and testing

> **Load `references/local-development.md`** for full instructions on starting the local task server, testing tasks end-to-end, and configuring the SDK client to point at localhost.

Core loop:

1. Start the dev server: `render workflows dev -- <start-command>`
2. Trigger tasks locally using the SDK client configured for the local server.
3. Observe logs and outputs in the terminal.
4. Iterate on task code; the dev server picks up changes on restart.

### 4. Deploy to Render

> **HARD RULE: Blueprints (`render.yaml`) are NOT yet compatible with Workflows.** Deployment must be done through the Render Dashboard manually.

**Deploy checklist:**

1. Push code to GitHub, GitLab, or Bitbucket.
2. In the [Render Dashboard](https://dashboard.render.com), click **New > Workflow**.
3. Link your repository.
4. Set **Root Directory** to `workflows/`.
5. Configure build and start commands (see table below).
6. Add environment variables (e.g., `RENDER_API_KEY` for tasks that call other workflows — use `YOUR_KEY` as a placeholder, never commit live secrets).
7. Click **Deploy Workflow**.
8. Verify deployment: check the Dashboard for a successful deploy event.

| Field | Python | TypeScript |
|-------|--------|------------|
| **Language** | Python 3 | Node |
| **Build Command** | `pip install -r requirements.txt` | `npm install && npm run build` |
| **Start Command** | `python main.py` | `node dist/main.js` |

If the deploy fails, check the service logs in the Dashboard. For common deployment errors, **load `references/troubleshooting.md`**. For general deploy debugging, use the **render-debug** skill.

### 5. Trigger tasks from other services

After deployment, trigger tasks from your other Render services using the SDK client.

**Python (synchronous):**

```python
from render_sdk import Render

render = Render()
result = render.workflows.run_task("my-workflow/hello", ["world"])
print(result.results)
```

**Python (asynchronous):**

```python
from render_sdk import RenderAsync

render = RenderAsync()
started = await render.workflows.start_task("my-workflow/hello", ["world"])
finished = await started
print(finished.results)
```

**TypeScript:**

```typescript
import { Render } from "@renderinc/sdk";

const render = new Render();
const started = await render.workflows.startTask("my-workflow/hello", ["world"]);
const finished = await started.get();
console.log(finished.results);
```

The task identifier format is `{workflow-slug}/{task-name}`, visible on the task's page in the Dashboard.

> **Scheduling:** Workflows do not have built-in scheduling. To trigger tasks on a schedule, use a Render cron job with the SDK client. For cron and cross-workflow examples, **load `references/task-patterns.md`**.

## Constraints and Limits

| Constraint | Limit | Notes |
|------------|-------|-------|
| Arguments and return values | Must be JSON-serializable | No class instances, functions, etc. |
| Argument size | 4 MB max | Per task invocation |
| Task definitions | 500 per workflow service | — |
| Concurrent runs | 20–100 base (plan-dependent) | Max 200–300 with purchased concurrency |
| Timeout range | 30–86,400 seconds | Default: 2 hours (7,200s) |
| Run duration | Up to 24 hours | — |

### Instance Types

| Plan | Specs |
|------|-------|
| `starter` | 0.5 CPU / 512 MB |
| `standard` (default) | 1 CPU / 2 GB |
| `pro` | 2 CPU / 4 GB |
| `pro_plus` | 4 CPU / 8 GB |
| `pro_max` | 8 CPU / 16 GB |
| `pro_ultra` | 16 CPU / 32 GB |

> `pro_plus`, `pro_max`, and `pro_ultra` require requesting access. Set via the `plan` task option.

For current pricing, see [Limits and Pricing for Render Workflows](https://render.com/docs/workflows-limits).

## Pitfalls

- **Do not trust built-in SDK knowledge.** The Render Workflows SDK is in beta and your training data is likely outdated. Always inspect the installed SDK source or fetch the official example files before generating code.
- **Blueprints do not work for Workflows.** Do not attempt to deploy via `render.yaml` — use the Dashboard **New > Workflow** flow.
- **Tasks must be JSON-serializable.** Arguments and return values cannot include class instances, functions, or other non-serializable objects. The 4 MB per-invocation limit is strict.
- **Task not appearing in `render workflows tasks list --local`?** Ensure the dev server is running and the task decorator is correctly applied. See [references/troubleshooting.md](references/troubleshooting.md#task-registration-issues).
- **No built-in scheduling.** Do not assume cron-like triggers exist in Workflows. Use a separate Render cron job calling the SDK client.
- **24-hour hard cap on run duration.** Long-running tasks that exceed 24 hours will be terminated. Design tasks to checkpoint or split work.
- **CLI version must be 2.11.0+.** Older CLI versions do not support `render workflows init` or `render workflows dev`.
- **Windows host notes:** The CLI is a standalone executable on Windows — download from the [releases page](https://github.com/render-oss/cli/releases/). PowerShell is the primary shell; adjust path separators and quoting accordingly when running bash-style commands from this skill.

## Verification

### Verify CLI version

```powershell
render --version
# Expected: >= 2.11.0
```

### Verify local task registration

```bash
# Terminal 1
render workflows dev -- <start-command>

# Terminal 2
render workflows tasks list --local
# Expected: list of registered task names including your new task
```

### Verify deployment

1. Open the [Render Dashboard](https://dashboard.render.com).
2. Navigate to your Workflow service.
3. Confirm a **successful deploy event** appears in the event log.
4. Navigate to the **Tasks** tab — confirm all expected tasks are listed.
5. Trigger a test run from the Dashboard or via the SDK client and confirm it completes successfully.

### Verify SDK client connectivity

```python
# Python — quick smoke test after deploy
from render_sdk import Render

render = Render()
result = render.workflows.run_task("my-workflow/hello", ["world"])
print(result.results)
# Expected: task output printed without errors
```

## References

| Reference | When to load |
|-----------|-------------|
| [references/quick-reference.md](references/quick-reference.md) | Need a compact API surface cheat sheet (decorators, client methods, env vars, error types) |
| [references/task-patterns.md](references/task-patterns.md) | User needs patterns for retries, subtasks, fan-out, ETL, error handling, cron triggers, or cross-workflow calls |
| [references/local-development.md](references/local-development.md) | Starting the local task server, testing tasks, configuring the SDK client for local use |
| [references/troubleshooting.md](references/troubleshooting.md) | Task registration issues, deployment errors, runtime errors |
| [references/manual-scaffolding.md](references/manual-scaffolding.md) | Fallback when `render workflows init` is unavailable or fails |

**External resources:**

- **Official docs:** [render.com/docs/workflows](https://render.com/docs/workflows)
- **Limits and pricing:** [render.com/docs/workflows-limits](https://render.com/docs/workflows-limits)
- **Starter template (Python):** [render-examples/workflows-template-python](https://github.com/render-examples/workflows-template-python)
- **Starter template (TypeScript):** [render-examples/workflows-template-ts](https://github.com/render-examples/workflows-template-ts)
- **SDK repo:** [github.com/render-oss/sdk](https://github.com/render-oss/sdk)

## Related Skills

- **render-deploy:** Deploy web services, static sites, and databases.
- **render-debug:** Debug failed deployments and runtime errors.
- **render-monitor:** Monitor service health and performance.
