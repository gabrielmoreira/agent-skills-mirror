# OpenClaw Integration Reference

This document covers how ClawPort integrates with [OpenClaw](https://openclaw.ai) -- the AI agent runtime that powers everything behind the dashboard.

## Overview

OpenClaw is the runtime layer. ClawPort is the UI layer. The separation is deliberate:

| Layer | Responsibility | Repository |
|-------|---------------|------------|
| **OpenClaw** | Agent execution, gateway API, cron scheduling, memory management, CLI | [openclaw.ai](https://openclaw.ai) |
| **ClawPort** | Dashboard UI, visualization, chat interface, settings, theming | [clawport-ui](https://github.com/JohnRiceML/clawport-ui) |

ClawPort never executes agents directly. It reads workspace data, calls gateway endpoints, and invokes CLI commands to present information and relay user actions.

## How ClawPort Reads Workspace Data

ClawPort uses `$WORKSPACE_PATH` to read agent and operational data from the OpenClaw workspace on disk:

| Data | Source | ClawPort usage |
|------|--------|----------------|
| Agents | `$WORKSPACE_PATH/agents/*/SOUL.md` | Agent discovery, org map, profiles |
| Root agent | `$WORKSPACE_PATH/SOUL.md`, `IDENTITY.md` | Root orchestrator node |
| Memory | `$WORKSPACE_PATH/memory/` | Memory browser |
| Cron runs | `$WORKSPACE_PATH/cron-runs/` | Cost dashboard, activity logs |
| Agent registry override | `$WORKSPACE_PATH/clawport/agents.json` | Custom agent names, colors, hierarchy |
| Pipeline config | `$WORKSPACE_PATH/clawport/pipelines.json` | Cron pipeline DAG |
| OpenClaw config | `$WORKSPACE_PATH/../openclaw.json` | Memory status, gateway settings |

## Gateway HTTP Endpoints

ClawPort routes all AI calls through the OpenClaw gateway (default `localhost:18789`):

| Endpoint | Method | Purpose | ClawPort usage |
|----------|--------|---------|----------------|
| `/v1/chat/completions` | POST | Text chat (streaming SSE) | Agent chat, health check, cost analysis, pipeline wizard |
| `/v1/audio/transcriptions` | POST | Whisper transcription | Voice message transcription |

The gateway proxies requests to Claude using the workspace's configured API key. ClawPort authenticates with `OPENCLAW_GATEWAY_TOKEN`.

## CLI Commands

For operations that require device keypair signing or aren't exposed via HTTP, ClawPort shells out to the `openclaw` CLI:

| Command | Purpose | ClawPort usage |
|---------|---------|----------------|
| `openclaw cron list --json` | List all cron jobs | Cron monitor, pipeline graph |
| `openclaw logs --follow --json` | Stream live logs | Live stream widget |
| `openclaw gateway call chat.send` | Send message with attachments | Vision pipeline (image chat) |
| `openclaw gateway call chat.history` | Get conversation history | Vision pipeline (poll for response) |
| `openclaw gateway call health` | Check gateway health | Status check, debugging |

**Why CLI for vision?** The gateway's HTTP endpoint strips `image_url` content from messages. The CLI has device keys for `operator.write` scope, which `chat.send` requires. ClawPort sends the image via CLI, then polls `chat.history` for the response.

## Agent Client Protocol (ACP)

ACP is OpenClaw's protocol for external tools to interact with running agent sessions. Key concepts:

- **Sessions** -- identified by a `sessionKey` (e.g., `agent:main:clawport`), sessions scope conversations between a client and an agent
- **Device keys** -- keypair-based authentication for write operations; the CLI manages these automatically
- **Scopes** -- `operator.read` (via HTTP) and `operator.write` (via CLI with device keys)

ClawPort uses ACP implicitly through the gateway endpoints and CLI commands listed above. The vision pipeline is the primary ACP consumer, using `chat.send` and `chat.history` methods.

## Recent OpenClaw Features

Features shipped in recent OpenClaw versions that are relevant to ClawPort:

### v2026.3.7 -- Context Engine Plugins

- Pluggable context engine that agents can extend with custom providers
- Agents can register context plugins in their SOUL.md configuration
- ClawPort surfaces this via the agent detail view (tools and capabilities)

### v2026.3.8 -- Backup & Provenance

- `openclaw backup create` / `openclaw backup restore` -- workspace backup commands
- Provenance tracking for agent outputs (which agent produced what, when)
- ClawPort's activity console can display provenance metadata in log entries

### ACP Sessions

- Persistent conversation sessions between clients and agents
- Session history survives gateway restarts
- ClawPort's chat persistence (localStorage) complements server-side ACP session history

### TUI Workspace Inference

- OpenClaw TUI auto-infers the active workspace from the current directory
- `clawport setup` leverages the same detection logic for `WORKSPACE_PATH`

## Scope Boundaries for Contributors

Understanding what belongs where prevents misrouted contributions:

### Belongs in ClawPort (this repo)

- Dashboard UI components and pages
- Data visualization (charts, graphs, org map)
- Chat interface and message rendering
- Theme system and settings
- Client-side slash commands
- Reading and displaying workspace data

### Belongs in OpenClaw (upstream)

- Agent execution and orchestration
- Gateway protocol and endpoints
- Cron scheduling and execution
- Memory management and storage
- CLI commands and flags
- ACP protocol changes
- New agent capabilities or tools

### Grey area (discuss first)

- New API routes that invoke CLI commands not currently used
- Features that require new OpenClaw CLI flags or gateway endpoints
- Changes to how workspace data is structured or discovered

When in doubt, open an issue describing what you want to build and we'll help determine the right place for it.
