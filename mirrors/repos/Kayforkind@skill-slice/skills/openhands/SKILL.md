---
name: openhands
description: "Delegates coding tasks to the OpenHands CLI in headless JSON mode over any LiteLLM provider. Use when the user requests OpenHands, a vendor-unlocked coding agent, or multi-step file-plus-shell work on OpenRouter, Ollama, or vLLM. Not for Claude-native (claude-code), OpenAI Codex, Hermes delegate_task, or native Windows (WSL only)."
version: 0.1.1
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Coding-Agent, OpenHands, Model-Agnostic, LiteLLM]
    related_skills: [claude-code, codex, opencode, hermes-agent]
---

# OpenHands CLI

Delegate coding tasks to the [OpenHands CLI](https://github.com/All-Hands-AI/OpenHands) via the `terminal` tool. OpenHands is model-agnostic: any LiteLLM-supported provider (OpenAI, Anthropic, OpenRouter, DeepSeek, Ollama, vLLM, etc.).

This skill is the headless-mode wrapper for batch / one-shot delegation. The interactive textual UI is not used from Hermes.

## When to Use

- User explicitly requests OpenHands for a coding task.
- User wants a coding agent that can run on a non-Anthropic / non-OpenAI provider (DeepSeek, Qwen, Ollama, vLLM, Nous, etc.) — sibling skills `claude-code` and `codex` are tied to one vendor.
- Multi-step file edits plus shell commands inside a workspace are needed and the user prefers an open-source, model-agnostic agent.

For Claude-native workflows, prefer `claude-code`. For OpenAI-native workflows, prefer `codex`. For Hermes-native subagents, use `delegate_task`.

## Prerequisites

1. **Install upstream** (requires Python 3.12+ and `uv`):

   ```bash
   uv tool install openhands --python 3.12
   ```

   Verify the install:

   ```bash
   openhands --version
   ```

   Expected output at time of writing: `OpenHands CLI 1.16.0` / `SDK v1.21.0`.

2. **Pick a model and set env vars** for `--override-with-envs`:

   ```bash
   export LLM_MODEL=openrouter/openai/gpt-4o-mini       # or any LiteLLM slug
   export LLM_API_KEY=$OPENROUTER_API_KEY
   export LLM_BASE_URL=https://openrouter.ai/api/v1     # omit for native OpenAI
   ```

   `LLM_MODEL` uses LiteLLM's full slug. When the provider is OpenRouter the slug is doubly-prefixed: `openrouter/<vendor>/<model>` (e.g. `openrouter/anthropic/claude-sonnet-4.5`). For native Anthropic: `anthropic/claude-sonnet-4-5`. For native OpenAI: `openai/gpt-4o-mini`.

3. **Suppress the startup banner** so JSON output is not preceded by ASCII art:

   ```bash
   export OPENHANDS_SUPPRESS_BANNER=1
   ```

4. **Platform note — no native Windows support.** The OpenHands docs require WSL on Windows. This skill is gated `[linux, macos]`. On a Windows host, run inside WSL (Ubuntu) and invoke commands from the WSL shell, not PowerShell.

## Procedure

Always invoke through the `terminal` tool. Always pass `--headless --json --override-with-envs --exit-without-confirmation` for automation.

### Step 1 — One-shot task

```bash
OPENHANDS_SUPPRESS_BANNER=1 \
  LLM_MODEL=openrouter/openai/gpt-4o-mini \
  LLM_API_KEY=$OPENROUTER_API_KEY \
  LLM_BASE_URL=https://openrouter.ai/api/v1 \
  openhands --headless --json --override-with-envs --exit-without-confirmation \
  -t 'Add error handling to all API calls in src/'
```

Set `workdir` to the project root and `timeout` to at least 600 for non-trivial tasks.

### Step 2 — Background execution for long tasks

```bash
# Launch in background
terminal(command="<same as above>", workdir="/path/to/project", background=true, notify_on_complete=true)

# Poll status
process(action="poll", session_id="<id>")

# Retrieve logs
process(action="log", session_id="<id>")
```

### Step 3 — Resume a previous conversation

OpenHands prints `Conversation ID: <32-hex>` and a `Hint: openhands --resume <dashed-uuid>` line at the end of each run. Use the **dashed** form to resume:

```bash
OPENHANDS_SUPPRESS_BANNER=1 \
  LLM_MODEL=openrouter/openai/gpt-4o-mini \
  LLM_API_KEY=$OPENROUTER_API_KEY \
  LLM_BASE_URL=https://openrouter.ai/api/v1 \
  openhands --headless --json --override-with-envs --exit-without-confirmation \
  --resume f46573d9-cfdb-45e4-92ca-189bde40019b \
  -t 'Now fix the bug you found'
```

### Verified flag list

Verified against `openhands --help` (CLI 1.16.0). Anything not in this table is not a flag — pass it via env var or settings file.

| Flag | Effect |
|------|--------|
| `--headless` | No UI, requires `-t` or `-f`. Auto-approves all actions (no `--llm-approve` in this mode). |
| `--json` | JSONL event stream (requires `--headless`). |
| `-t TEXT` | Task prompt. |
| `-f PATH` | Read task from file. |
| `--resume [ID]` | Resume conversation. No ID → list recent. |
| `--last` | Resume most recent (with `--resume`). |
| `--override-with-envs` | Apply `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL` env vars. Without this, OpenHands uses `~/.openhands/settings.json` and ignores the env. |
| `--exit-without-confirmation` | Don't show the "are you sure" exit dialog. |
| `--always-approve` / `--yolo` | Auto-approve every action (default in `--headless`). |
| `--llm-approve` | LLM-based security gate (interactive only — does NOT work in headless). |
| `--version` / `-v` | Print version and exit. |

**There is no `--model`, `--max-iterations`, `--workspace`, `--sandbox`, or `--sandbox-type` flag.** Model is `LLM_MODEL`. Workspace is the `workdir` you pass to the `terminal` tool. Sandbox / runtime is controlled via `RUNTIME` and `SANDBOX_VOLUMES` env vars.

### JSON event schema

With `--json --headless`, OpenHands emits JSONL — one JSON object per line, plus a handful of non-JSON status lines (`Initializing agent...`, `Agent is working`, `Agent finished`, the final summary box, `Goodbye!`, `Conversation ID:`, `Hint:`). Filter for lines starting with `{`.

Top-level `kind` field discriminates events:

- `MessageEvent` — user / agent text turn. `source` is `user` or `agent`.
- `ActionEvent` — agent picked a tool. Read `tool_name` (`file_editor`, `terminal`, `finish`) and `action.kind` (`FileEditorAction`, `TerminalAction`, `FinishAction`).
- `ObservationEvent` — tool result. `observation.is_error` is the success flag. `source` is `environment`.
- `FinishAction` inside an `ActionEvent` carries the agent's final message in `action.message`.

The CLI prints all stderr from LiteLLM/Authlib first — see Pitfalls. Parse only stdout, line by line, ignoring lines that don't start with `{`.

## Pitfalls

- **LiteLLM warnings on every invocation.** The CLI prints `bedrock-runtime` and `sagemaker-runtime` warnings to stderr because `botocore` isn't installed. Plus an Authlib deprecation. These are noise, not failures. Pipe stderr to `/dev/null` or filter it out before showing the user.
- **Banner spam.** Without `OPENHANDS_SUPPRESS_BANNER=1`, every run starts with a multi-line `+--+` ASCII box advertising the SDK. Always export it.
- **`--override-with-envs` is mandatory for automation.** Without it, OpenHands ignores `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL` and falls back to `~/.openhands/settings.json`. On a fresh install this file doesn't exist and the CLI hangs waiting for first-run setup.
- **Model slug is LiteLLM's, not the provider's.** `openrouter/openai/gpt-4o-mini` works; `openai/gpt-4o-mini` while pointed at OpenRouter does not. `anthropic/claude-sonnet-4-5` (hyphen) is native Anthropic; `openrouter/anthropic/claude-sonnet-4.5` (dot) is via OpenRouter. Get it wrong → cryptic LiteLLM 400.
- **`pip install openhands-ai` is the wrong package.** That's the legacy V0 SDK. The new CLI is `uv tool install openhands --python 3.12`. There is no maintained conda package.
- **Resume ID format is fiddly.** The CLI ends with `Conversation ID: f46573d9cfdb45e492ca189bde40019b` (no dashes) and then a `Hint: openhands --resume f46573d9-cfdb-45e4-92ca-189bde40019b` (with dashes). Use the dashed form.
- **Headless ignores `--llm-approve`.** If you pass it, you get an argparse error. Headless mode hardcodes always-approve.
- **No Windows support upstream.** The OpenHands docs require WSL on Windows. This skill is gated `[linux, macos]` accordingly.
- **`~/.openhands/conversations/<id>/` accumulates.** Each run persists a trajectory. Clean it up if running batches.
- **Heavy install (~200 packages).** Use `uv tool install` (isolated venv) to avoid dependency conflicts with the active project.

## Verification

Run a minimal smoke test to confirm the install and model configuration are working:

```bash
OPENHANDS_SUPPRESS_BANNER=1 \
  LLM_MODEL=openrouter/openai/gpt-4o-mini \
  LLM_API_KEY=$OPENROUTER_API_KEY \
  LLM_BASE_URL=https://openrouter.ai/api/v1 \
  openhands --headless --json --override-with-envs --exit-without-confirmation \
  -t 'Print the string OPENHANDS_OK to stdout via the terminal tool.'
```

Set `workdir` to `/tmp` and `timeout` to 120.

**Pass criteria:** The JSONL stream ends with a `FinishAction` whose `action.message` mentions `OPENHANDS_OK`. If you see a LiteLLM 400 or authentication error, check the model slug and API key first.

## Related

- [OpenHands GitHub](https://github.com/All-Hands-AI/OpenHands)
- [OpenHands CLI command reference](https://docs.openhands.dev/openhands/usage/cli/command-reference)
- Sibling skills: `claude-code` (Anthropic-only), `codex` (OpenAI-only), `opencode` (multi-provider via OpenCode), `hermes-agent` (Hermes subagents via `delegate_task`).
