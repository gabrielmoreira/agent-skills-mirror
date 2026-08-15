---
name: aiq-research
description: "Routes research questions to a reachable NVIDIA AI-Q Blueprint via scripts/aiq.py (health, /chat, async job poll, report). Use when the user asks for AI-Q/AIQ research or to query a trusted AIQ_SERVER_URL. Not for installing, deploying, Docker, Helm, or Blueprint troubleshooting (aiq-deploy). Never put credentials in the query text or fabricate answers if the backend fails."
license: Apache-2.0
permissions:
  env:
    - AIQ_SERVER_URL
  network:
    - http://localhost:8000
compatibility: |
  Designed for Claude Code, OpenCode, Codex, and Agent Skills-compatible tools. Requires Python 3.11+ and network
  access to a running local AI-Q Blueprint server at `http://localhost:8000` by default. Non-local backends must be
  explicitly trusted by the user and granted by the host tool outside this public skill.
metadata:
  version: "2.1.1"
  author: "NVIDIA AI-Q Blueprint Team <aiq-blueprint@nvidia.com>"
  github-url: "https://github.com/NVIDIA-AI-Blueprints/aiq"
  tags:
    - nvidia
    - aiq
    - blueprint
    - deep-research
    - research-agents
    - agent-skills
  languages:
    - python
    - bash
  domain: "research-agents"
allowed-tools: Read Bash
---

# AIQ Research Skill

## When to Use

Use this skill to call a locally running NVIDIA AI-Q Blueprint server through the helper script at `scripts/aiq.py`.

Use this skill for research-shaped requests, including:

- "deep research on ..."
- "AIQ research ..."
- "research ..."
- "use AI-Q to answer ..."
- "ask AI-Q about ..."

**Do not use this skill** for install, deploy, start, stop, UI, CLI, Docker, Helm, or troubleshooting requests. Those belong to `aiq-deploy`.

## Prerequisites

- Python 3.11+ available as `python3` (or `python` on Windows PowerShell).
- A reachable local or self-hosted AI-Q Blueprint backend.
- `AIQ_SERVER_URL` set when the backend is not running at `http://localhost:8000`; non-local values must be trusted by the user before any query is sent.
- A backend configured with authentication disabled for this public helper, or a separate authenticated AI-Q skill for authenticated environments.
- Network access from the local machine to the AI-Q backend URL.
- Credentials configured in the backend environment, not in this skill. This public helper does not collect or manage API keys.

The helper script has no third-party Python package dependencies; it uses Python standard-library HTTP modules.

## Procedure

### Step 1 — Resolve the backend URL

Use `AIQ_SERVER_URL` when set. Otherwise try the default local backend at `http://localhost:8000`.

Run a health check before sending any research request:

```powershell
python $SKILL_DIR/scripts/aiq.py health
```

Expected output: JSON from a reachable AI-Q health endpoint.

If `health` fails and no explicit `AIQ_SERVER_URL` was set, ask:

> I do not see a reachable local AI-Q backend. Do you already have an AI-Q backend URL you want to use, or should I deploy a local Skill backend?

- If the user provides a URL, set `AIQ_SERVER_URL` for subsequent helper calls and rerun `health`.
- If the user wants local deployment, hand off to `aiq-deploy` and preserve the original research request.
- If a reachable backend returns `401` or `403`, stop and explain that this public skill does not manage authentication. Ask the user to use an authenticated AI-Q skill or configure authentication for their environment.
- If `health` succeeds but `/chat` or `/v1/jobs/async/agents` fails, report that the backend is reachable but not compatible with this public research flow, then offer to run `aiq-deploy` validation.

### Step 2 — Send the routed research request

Before sending the request, state the resolved endpoint to the user:

> I will send this query to `<AIQ_SERVER_URL>`. Make sure this endpoint is trusted before sending sensitive information.

**Never** send credentials, cookies, bearer tokens, or secret values through the query text.

Run:

```powershell
python $SKILL_DIR/scripts/aiq.py chat "<USER_QUESTION>"
```

Expected output:

- A normal JSON response for shallow or direct answers — present the result immediately. Do not force polling when there is no `job_id`.
- Or structured JSON containing `{"status": "deep_research_running", "job_id": "<JOB_ID>"}` for asynchronous deep research.

### Step 3 — Poll asynchronous deep research jobs

If the response includes `deep_research_running`, extract the `job_id` and poll:

```powershell
python $SKILL_DIR/scripts/aiq.py research_poll <JOB_ID>
```

Expected output: the final report JSON when the job completes successfully.

Use the runtime's non-blocking or background execution mechanism when available. If the chosen execution method requires escalated permissions, request explicit user approval first and explain why. Tell the user that deep research is running in the background.

### Step 4 — Resume after interruptions

If polling is interrupted, the job continues server-side. Resume with any of:

```powershell
python $SKILL_DIR/scripts/aiq.py status <JOB_ID>
python $SKILL_DIR/scripts/aiq.py report <JOB_ID>
python $SKILL_DIR/scripts/aiq.py research_poll <JOB_ID>
```

- Use `status` to inspect job status and saved artifacts.
- Use `report` when the job has already finished and you only need the final output.
- Use `research_poll` to keep waiting for completion.

### Step 5 — Present the report

When `research_poll` completes successfully, fetch and present the full report. Keep citations and source URLs intact — do not truncate or strip them.

If the job status is `failed`, `failure`, or `cancelled`, show the error from the status response and ask whether the user wants to retry with a narrower query or different approach. Do not retry automatically.

## Available Scripts

All commands are invoked via `python $SKILL_DIR/scripts/aiq.py <subcommand>`. When the host supports a `run_script()` helper, call it with `scripts/aiq.py` and the arguments below.

| Script | Purpose | Arguments |
|---|---|---|
| `health` | Check whether the configured server responds | none |
| `chat` | POST `/chat`; may return inline output or a deep-research job ID | `<query>` |
| `agents` | List available async agent types | none |
| `submit` | Submit an explicit async job | `<query> [agent_type]` |
| `research` | Submit an async job, poll, and print the final report JSON | `<query> [agent_type]` |
| `research_poll` | Resume polling an existing async job | `<job_id>` |
| `status` | Fetch job status plus `/state` artifacts | `<job_id>` |
| `state` | Fetch event-store artifacts only | `<job_id>` |
| `report` | Fetch the final report for a completed job | `<job_id>` |
| `stream` | Stream SSE events from a job | `<job_id>` |
| `cancel` | Cancel a running job | `<job_id>` |

## Environment Variables

| Variable | Required | Default | Description |
|---|---:|---|---|
| `AIQ_SERVER_URL` | No | `http://localhost:8000` | Local or self-hosted AI-Q server base URL |

## Version Compatibility

This skill is designed for NVIDIA AI-Q Blueprint version 2.1.0.

Semantic Versioning Compatibility Rules:

```
Skill version: X.Y.Z
Blueprint or endpoint version: A.B.C

Compatible IF:
1. A == X (Major versions MUST match)
2. B >= Y (Minor version must be equal or greater)
3. C can be anything (Patch version does not affect compatibility)
```

Examples:

- Skill 2.1.0 is compatible with Blueprint 2.1.0, 2.2.0, and 2.1.5.
- Skill 2.1.0 is **not** compatible with Blueprint 3.0.0 or 2.0.0.

If your Blueprint version is not compatible:

1. Check for an updated skill version matching your Blueprint version.
2. Use a Blueprint version compatible with this skill.
3. Proceed with caution only when the user accepts the compatibility risk; API routes or response shapes may have changed.

## Security Best Practices

- Do not put API keys, bearer tokens, cookies, or basic-auth credentials in `AIQ_SERVER_URL`.
- Store backend credentials in the AI-Q deployment environment, not in this skill or command examples.
- User query text is transmitted to the configured `AIQ_SERVER_URL`. Confirm the endpoint is trusted before sending sensitive or confidential information.
- Treat returned reports as potentially sensitive if the backend uses private data sources.
- Do not truncate citations or source URLs from returned reports.

## Pitfalls

### No backend is reachable

**Symptoms:** `health` fails with connection refused; default `http://localhost:8000` does not respond.

**Causes:** AI-Q is not running, is on a different host/port, or a firewall blocks the connection.

**Solutions:**

1. Ask whether the user has an existing AI-Q backend URL.
2. If they provide one, set it and rerun health:

   ```powershell
   $env:AIQ_SERVER_URL = "http://localhost:<PORT>"
   python $SKILL_DIR/scripts/aiq.py health
   ```

3. If they want a local backend, hand off to `aiq-deploy` and preserve the original research request.

### Backend requires authentication

**Symptoms:** Requests fail with HTTP 401 or 403; backend is reachable but rejects `/chat` or async job calls.

**Causes:** Backend deployed with authentication enabled; the public helper does not attach user tokens or cookies.

**Solutions:**

1. Stop and explain that this public skill does not manage authentication.
2. Ask the user to use an authenticated AI-Q skill or configure their backend for this public local workflow.
3. Rerun `health` and the original query only after the authentication boundary is resolved.

### Health succeeds but research routes fail

**Symptoms:** `health` returns successfully, but `/chat`, `/v1/jobs/async/agents`, or polling commands fail.

**Causes:** Backend not using an API-enabled AI-Q config; async job registry unavailable; backend version incompatible.

**Solutions:**

1. Run:

   ```powershell
   python $SKILL_DIR/scripts/aiq.py agents
   ```

2. If agents are unavailable, report the compatibility failure and offer to run `aiq-deploy` validation.
3. Confirm the deployed Blueprint version is compatible with skill version 2.1.x.

### Job is interrupted or appears stuck

**Symptoms:** Local polling interrupted; job keeps showing `running`; poll output shows `running` but a report is returned or cancel says the job is already `success`.

**Causes:** Deep research is asynchronous and continues server-side; local polling output can lag behind terminal server state.

**Solutions:**

1. Check current state:

   ```powershell
   python $SKILL_DIR/scripts/aiq.py status <JOB_ID>
   ```

2. If `has_report: true` or `job_status.status: success`, fetch the report:

   ```powershell
   python $SKILL_DIR/scripts/aiq.py report <JOB_ID>
   ```

3. If the job is still running, continue polling:

   ```powershell
   python $SKILL_DIR/scripts/aiq.py research_poll <JOB_ID>
   ```

### Fabricating answers on backend failure

If the backend returns HTTP 500 or lacks async agents, report the failure to the user. **Never fabricate a research answer** when the backend is unreachable or returns an error.

## Verification

1. Confirm the backend is reachable:

   ```powershell
   python $SKILL_DIR/scripts/aiq.py health
   ```

   Expected: JSON health response with HTTP 200.

2. Confirm async agents are available:

   ```powershell
   python $SKILL_DIR/scripts/aiq.py agents
   ```

   Expected: JSON listing available agent types.

3. Confirm a chat request returns either inline JSON or a `deep_research_running` job ID:

   ```powershell
   python $SKILL_DIR/scripts/aiq.py chat "test query"
   ```

4. If a job ID was returned, confirm polling retrieves the final report:

   ```powershell
   python $SKILL_DIR/scripts/aiq.py research_poll <JOB_ID>
   ```

   Expected: final report JSON with citations and source URLs intact.

## Examples

### Example 1: Run a routed chat or research request

```powershell
python $SKILL_DIR/scripts/aiq.py health
python $SKILL_DIR/scripts/aiq.py chat "Compare local AIQ deep research with a standard web search workflow"
```

Expected output:

```
<health JSON from AI-Q>
<JSON chat response or {"status": "deep_research_running", "job_id": "<JOB_ID>"}>
```

If AI-Q returns a job ID, continue with `research_poll`.

### Example 2: Resume an existing job

```powershell
python $SKILL_DIR/scripts/aiq.py status <JOB_ID>
python $SKILL_DIR/scripts/aiq.py research_poll <JOB_ID>
```

Replace `<JOB_ID>` with the UUID returned by AI-Q. Expected output: status JSON followed by the report JSON when the job completes. If the job failed, show the returned status and do not retry automatically.

## References

| Topic | Documentation |
|---|---|
| Helper script | `scripts/aiq.py` |
| Deployment and backend validation | `../aiq-deploy/SKILL.md` |

Load `scripts/aiq.py` when executing any AI-Q command. Load `../aiq-deploy/SKILL.md` only when handing off deployment, validation, or troubleshooting requests.

## Limitations

- This skill requires a running AI-Q backend; it does not deploy one.
- The public helper does not manage authentication tokens or cookies.
- Remote `AIQ_SERVER_URL` endpoints may log prompts, responses, and metadata.
- If the backend returns HTTP 500 or lacks async agents, report the failure instead of fabricating a research answer.
