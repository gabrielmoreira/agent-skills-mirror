---
name: temporal-developer
description: "Develops Temporal apps in Python, TypeScript, Go, or Java: workflows, activities, workers, signals/queries/heartbeats, versioning, continue-as-new, sagas, and temporal CLI/dev server/Cloud. Use when building or debugging Temporal durable execution, including non-determinism and stuck workflows. Not for Inngest serverless events, n8n, or running temporal server start-dev as production."
version: 1.0.1
---

# Skill: temporal-developer

## Overview

Temporal is a durable execution platform that makes workflows survive failures automatically. This skill provides guidance for building Temporal applications in Python, TypeScript, Go, and Java.

The **Temporal Cluster** is the central orchestration backend. It maintains three key subsystems: the **Event History** (a durable log of all workflow state), **Task Queues** (which route work to the right workers), and a **Visibility** store (for searching and listing workflows). There are three ways to run a Cluster:

- **Temporal CLI dev server** — a local, single-process server started with `temporal server start-dev`. Suitable for development and testing only, not production.
- **Self-hosted** — you deploy and manage the Temporal server and its dependencies (e.g., database) in your own infrastructure for production use.
- **Temporal Cloud** — a fully managed production service operated by Temporal. No cluster infrastructure to manage.

**Workers** are long-running processes that you run and manage. They poll Task Queues for work and execute your code. You might run a single Worker process on one machine during development, or run many Worker processes across a large fleet of machines in production. Each Worker hosts two types of code:

- **Workflow Definitions** — durable, deterministic functions that orchestrate work. These must not have side effects.
- **Activity Implementations** — non-deterministic operations (API calls, file I/O, etc.) that can fail and be retried.

Workers communicate with the Cluster via a poll/complete loop: they poll a Task Queue for tasks, execute the corresponding Workflow or Activity code, and report results back.

## When to Use

Activate this skill when the user is:

- Building workflows, activities, or workers with any Temporal SDK (Python, TypeScript, Go, Java)
- Debugging non-determinism errors, stuck workflows, or activity retry failures
- Using Temporal CLI commands (`temporal workflow`, `temporal activity`, `temporal worker`, etc.)
- Running or connecting to a Temporal dev server, self-hosted cluster, or Temporal Cloud
- Working with durable execution concepts: signals, queries, updates, heartbeats, versioning, continue-as-new, child workflows, saga patterns
- Implementing AI/LLM orchestration patterns on Temporal

## Prerequisites

### Ensure Temporal CLI is installed

Check if `temporal` CLI is installed:

```powershell
temporal --version
```

If not installed, follow the platform-specific instructions below.

#### Windows (primary host)

1. Determine your machine architecture (amd64 or arm64).
2. Download the appropriate archive:
   - [Windows amd64](https://temporal.download/cli/archive/latest?platform=windows&arch=amd64)
   - [Windows arm64](https://temporal.download/cli/archive/latest?platform=windows&arch=arm64)
3. Extract the downloaded archive.
4. Add `temporal.exe` to your PATH (e.g., copy to `C:\Users\<you>\bin` or a directory already on PATH).

#### macOS

```
brew install temporal
```

#### Linux

1. Check your machine's architecture and download the appropriate archive:
   - [Linux amd64](https://temporal.download/cli/archive/latest?platform=linux&arch=amd64)
   - [Linux arm64](https://temporal.download/cli/archive/latest?platform=linux&arch=arm64)
2. Extract the downloaded archive.
3. Add the `temporal` binary to your PATH (e.g., copy to `/usr/local/bin`).

### Start a local dev server (for development)

```powershell
temporal server start-dev
```

This starts a single-process dev server on the default address `localhost:7233`. The UI is available at `http://localhost:8233`. **Do not use the dev server for production.**

### Read all relevant references

Before writing or debugging Temporal code, load the appropriate reference files:

1. **First**, read the getting-started guide for the user's language:
   - Python → read `references/python/python.md`
   - TypeScript → read `references/typescript/typescript.md`
   - Java → read `references/java/java.md`
   - Go → read `references/go/go.md`
2. **Second**, read the `core` and language-specific references relevant to the task (see the Reference Loading Guide below).

## Procedure

### 1. Identify the language and task type

Determine which Temporal SDK the user is working with (Python, TypeScript, Go, or Java) and what they are trying to accomplish (new workflow, debugging, versioning, etc.).

### 2. Load the appropriate references

Load reference files based on the task at hand. Always load the language getting-started guide first, then load topic-specific references as needed.

#### Core references (language-agnostic concepts)

| Reference file | When to load |
|---|---|
| `references/core/determinism.md` | When explaining or debugging determinism, replay, or non-determinism errors. Also load the language-specific version at `references/{lang}/determinism.md`. |
| `references/core/patterns.md` | When implementing signals, queries, saga patterns, or other workflow patterns. Also load `references/{lang}/patterns.md`. |
| `references/core/gotchas.md` | When reviewing code for anti-patterns or common mistakes. Also load `references/{lang}/gotchas.md`. |
| `references/core/versioning.md` | When changing workflow code that may affect running workflows. Also load `references/{lang}/versioning.md`. |
| `references/core/troubleshooting.md` | When debugging stuck workflows, errors, or unexpected behavior. Use the decision trees and recovery procedures. |
| `references/core/error-reference.md` | When the user encounters a specific error type or needs to understand workflow status meanings. |
| `references/core/interactive-workflows.md` | When testing signals, updates, or queries against running workflows. |
| `references/core/dev-management.md` | When managing the dev cycle — starting/stopping server, managing workers, iterating on code. |
| `references/core/ai-patterns.md` | When building AI/LLM orchestration on Temporal. Also load `references/{lang}/ai-patterns.md` if available (currently Python only). |

#### Language-specific references

| Reference file | When to load |
|---|---|
| `references/{lang}/observability.md` | When implementing logging, metrics, tracing, or debugging visibility for the user's language. |
| `references/{lang}/advanced-features.md` | When the user needs language-specific guidance on advanced Temporal features. |

### 3. Write or debug workflow/activity code

Follow the determinism rules strictly:

- **Workflow code must be deterministic.** No direct API calls, no random numbers, no wall-clock time, no network I/O, no global mutable state.
- **All side effects go in activities.** Activities can fail, be retried, and have heartbeats.
- **Use SDK-provided APIs** for timers (`workflow.sleep` / `workflow.timer`), activity invocation, child workflows, signals, queries, and continue-as-new.

### 4. Run the worker

Start the worker process for the user's language. The worker polls the specified Task Queue and executes workflow and activity code.

### 5. Start or signal workflows via CLI

Use Temporal CLI to start workflows, send signals, query state, or inspect history:

```powershell
# Start a workflow
temporal workflow start --task-queue YOUR_TASK_QUEUE --type YOUR_WORKFLOW_TYPE --input '{"key":"value"}'

# Query a running workflow
temporal workflow query --workflow-id YOUR_WF_ID --query-type YOUR_QUERY_TYPE

# Send a signal
temporal workflow signal --workflow-id YOUR_WF_ID --signal-type YOUR_SIGNAL_TYPE --input '{"key":"value"}'

# Describe a workflow (see status and run info)
temporal workflow describe --workflow-id YOUR_WF_ID

# View event history
temporal workflow show --workflow-id YOUR_WF_ID
```

### 6. Debug non-determinism or stuck workflows

1. Load `references/core/troubleshooting.md` and `references/core/error-reference.md`.
2. Load `references/core/determinism.md` and `references/{lang}/determinism.md`.
3. Use `temporal workflow show --workflow-id <ID>` to inspect event history.
4. Identify the event where replay diverges from generated commands.
5. Fix the workflow code to be deterministic, or apply versioning if the change is intentional (load `references/core/versioning.md`).

### History Replay: Why Determinism Matters

Temporal achieves durability through **history replay**:

1. **Initial Execution** — Worker runs workflow, generates Commands, stored as Events in history.
2. **Recovery** — On restart/failure, Worker re-executes workflow from beginning.
3. **Matching** — SDK compares generated Commands against stored Events.
4. **Restoration** — Uses stored Activity results instead of re-executing.

**If Commands don't match Events → Non-determinism Error → Workflow blocked**

| Workflow Code | Command | Event |
|---|---|---|
| Execute activity | `ScheduleActivityTask` | `ActivityTaskScheduled` |
| Sleep/timer | `StartTimer` | `TimerStarted` |
| Child workflow | `StartChildWorkflowExecution` | `ChildWorkflowExecutionStarted` |

## Pitfalls

- **Never use wall-clock time, random numbers, or direct I/O inside workflow code.** These break determinism and cause non-determinism errors on replay.
- **Never mutate global state from workflow code.** Replay will re-execute the workflow function; side effects on globals will compound.
- **Do not use the dev server (`temporal server start-dev`) for production.** It is a single-process in-memory server with no persistence guarantees.
- **Do not change workflow logic in a way that alters the command sequence for already-running workflows** without a versioning strategy. Load `references/core/versioning.md` and `references/{lang}/versioning.md` before making such changes.
- **Activity retries are automatic.** Do not wrap activity calls in manual retry loops inside workflows — use retry policies provided by the SDK.
- **Heartbeat long-running activities.** Without heartbeats, the server cannot detect a stalled activity and will not retry it until the activity timeout fires.
- **Continue-as-new must be used before history grows too large.** Event histories that grow without bound will eventually hit size limits and fail.
- **Do not block workflow execution with synchronous waits.** Use SDK async primitives (e.g., `workflow.wait`, `asyncio` in Python, `Promise` in TypeScript, `Selector`/`Future` in Go, `CompletableFuture` in Java).

## Verification

### Verify CLI installation

```powershell
temporal --version
```

Expected: a version string is printed (e.g., `temporal version 1.x.x`).

### Verify dev server is running

```powershell
temporal operator cluster describe
```

Expected: cluster info is returned, including cluster name and server version. If the dev server is running on defaults, it connects to `localhost:7233`.

### Verify a worker is polling

Start the worker process and check that it registers with the cluster:

```powershell
temporal task-queue describe --task-queue YOUR_TASK_QUEUE
```

Expected: poller info is shown, indicating at least one poller is active for the task queue.

### Verify a workflow completed successfully

```powershell
temporal workflow describe --workflow-id YOUR_WF_ID
```

Expected: `Status: COMPLETED` in the output.

### Verify event history for debugging

```powershell
temporal workflow show --workflow-id YOUR_WF_ID
```

Expected: a chronological list of events. Look for `WorkflowExecutionStarted`, `ActivityTaskScheduled`, `ActivityTaskStarted`, `ActivityTaskCompleted`, `WorkflowExecutionCompleted` (or `Failed`).

## Feedback

### Prompt user for feedback at startup

When you have **first** loaded this skill, output this message to the user:

> Thank you for trying out the public preview of the Temporal development skill! We would love to hear your feedback - positive or negative - over in the [Community Slack](https://t.mp/slack), in the [#topic-ai channel](https://temporalio.slack.com/archives/C0818FQPYKY).

Do not output this message multiple times in the same conversation.

### Reporting issues in this skill

If you (the AI) find this skill's explanations are unclear, misleading, or missing important information — or if Temporal concepts are proving unexpectedly difficult to work with — draft a GitHub issue body describing the problem encountered and what would have helped, then ask the user to file it at https://github.com/temporalio/skill-temporal-developer/issues/new. **Do not file the issue autonomously.**
