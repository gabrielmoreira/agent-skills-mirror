# Lab trace

Observability UI built into the local web channel: timeline of agent runs, streaming output chunks, IPC sends, scheduled tasks, and Docker spawns. Data is stored in SQLite (`agent_trace_events`) and pushed to the browser via **SSE**.

## How it works

When `ENABLE_LOCAL_WEB=true`, the **chat and lab trace share one page** at `/` — top tabs on narrow screens, side-by-side columns from ~1100px width. `/dashboard` redirects to `/?tab=trace`.

Quick start: `npm run web`.

## Optional auth

In `.env`:

```bash
# Require auth for trace/workspace APIs
# DASHBOARD_TOKEN=your-secret
```

## Event types

| `type` | Source | Meaning |
|--------|--------|---------|
| `run_start` | `index` | User/chat batch handed to the agent (prompt preview, counts). |
| `container_spawn` | `container-runner` | Docker container name for this run. |
| `stream_output` | `index` / scheduler | Each parsed streaming result from the agent (preview capped). |
| `run_end` / `run_error` | `index` | Final status for a chat-driven run. |
| `agent_thinking` | `ipc` | Agent's reasoning text (from container IPC). |
| `agent_tool_use` | `ipc` | Agent tool invocation (name + input preview). |
| `scheduled_run_*` | `task-scheduler` | Cron/interval task lifecycle. |
| `ipc_send` | `ipc` | Text or image forwarded from the container to a channel. |

## API

- `GET /api/trace/list?limit=200&group_folder=…&compact=1`
- `GET /api/trace/stream` — SSE; with token use `?token=…` (EventSource cannot set headers).
- `GET /api/workspace/groups` — folder names under `groups/`.
- `GET /api/workspace/tree?group_folder=…` — read-only tree (depth/node limits).

## Privacy

Trace rows may contain **prompt previews** and **model output previews**. Do not expose on a public interface without `DASHBOARD_TOKEN` and a reverse proxy.
