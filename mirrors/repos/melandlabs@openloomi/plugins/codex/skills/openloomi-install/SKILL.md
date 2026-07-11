---
name: openloomi-install
description: "OpenLoomi install & first-use setup helper for Codex. Use when the user wants to install OpenLoomi, configure it, or troubleshoot `INSTALL_REQUIRED` / `SOURCE_FOUND_CLI_NOT_BUILT` / `AI_PROVIDER_REQUIRED` / `SESSION_INITIALIZATION_REQUIRED` after running setup-status. Triggers: install openloomi, 配置 openloomi, setup openloomi, openloomi not installed, openloomi not finalized, install_required, install missing, AI provider setup, guest session."
allowed-tools: "Bash(node $SKILL_DIR/../../scripts/loomi-bridge.mjs *)"
---

# OpenLoomi Install Sub-skill

This sub-skill is auto-loaded when the user wants to install or fix OpenLoomi
on their machine. It composes `loomi-bridge` operations and never downloads
or executes anything outside the plugin's own scripts.

## Quick workflow

1. `node "$SKILL_DIR/../../scripts/loomi-bridge.mjs" setup-status`
2. Based on `nextAction` / `reason`:

| Reason / nextAction | Action |
|---|---|
| `install_openloomi` / `INSTALL_REQUIRED` | OpenLoomi Desktop is not on this machine. Call `install-instructions` to show the platform plan. Only call `install-openloomi --confirm` after the user explicitly approves installation. |
| `SOURCE_FOUND_CLI_NOT_BUILT` | A source checkout is present but `openloomi-ctl` is not built. Recommend either building the source (`pnpm tauri:dev` / `pnpm build` per the OpenLoomi repo's `apps/web/src-tauri/README.md`) or installing the packaged Desktop release. |
| `open_openloomi` / `SESSION_INITIALIZATION_REQUIRED` | OpenLoomi is installed but the local guest/session token could not be created. Ask the user to open OpenLoomi Desktop once so the local API can mint a guest session, then re-run `setup-status`. |
| `open_openloomi_ai_provider_setup` / `AI_PROVIDER_REQUIRED` | Walk the user through `configure-ai-provider`. Never pass an API key in argv. Secret entry must happen in OpenLoomi-owned UI / interactive CLI surfaces. |
| `AI_PROVIDER_STATUS_UNAVAILABLE` | The local OpenLoomi API is not reachable, so the bridge cannot confirm whether provider settings are saved. Ask the user to open OpenLoomi Desktop and re-run `setup-status`. |
| `run` / `READY_SESSION_BOOTSTRAP_PENDING` | Nothing to install. The bridge will bootstrap a guest session on the next `run`. |

## Reminder: secrets contract

- The bridge reads `ANTHROPIC_API_KEY` / `ANTHROPIC_AUTH_TOKEN` / `OPENLOOMI_AUTH_TOKEN` etc. only as presence flags; values are never printed.
- If the user pastes a key into chat, redact it: do NOT echo it back, and tell them to remove it from chat history.
- Never pass `--api-key` as an argv flag — the bridge has no such flag, by design.
- The bridge does not auto-install. Always require an explicit user confirmation before calling `install-openloomi --confirm`.

---


## Launching the desktop app with the Codex runtime

The packaged desktop app defaults to the Claude provider. To switch its
agent runtime to the Codex CLI, export `OPENLOOMI_AGENT_PROVIDER=codex` in
the shell that opens the app so the variable reaches the Tauri-launched
web server:

```bash
export OPENLOOMI_AGENT_PROVIDER=codex
open /Applications/openloomi.app
```

For a permanent switch, add it to your shell rc (`~/.zshrc`):

```bash
echo 'export OPENLOOMI_AGENT_PROVIDER=codex' >> ~/.zshrc
```

Optional companion variables (read by the native-agent env resolver at
startup):

- `OPENLOOMI_AGENT_CODEX_COMMAND` — path to the Codex CLI binary (default: `codex` on `PATH`)
- `OPENLOOMI_AGENT_CODEX_MODEL` — e.g. `gpt-5.4`
- `OPENLOOMI_AGENT_CODEX_PROFILE` — passed as `-p <name>`
- `OPENLOOMI_AGENT_CODEX_SANDBOX` — `read-only` | `workspace-write` | `danger-full-access` (default `workspace-write`; plan phase is always forced to `read-only`)
- `OPENLOOMI_AGENT_CODEX_ASK_FOR_APPROVAL` — `untrusted` | `on-failure` | `on-request` | `never` (default `on-request`)
- `OPENLOOMI_AGENT_CODEX_SKIP_GIT_REPO_CHECK` — default `true`
- `OPENLOOMI_AGENT_CODEX_FULL_AUTO` — set `true` to allow `--full-auto` only under `bypassPermissions`
- `OPENLOOMI_AGENT_CODEX_TIMEOUT_MS` — CLI runtime budget in milliseconds

### Prerequisites

- `which codex` resolves to a working Codex CLI binary (`brew install --cask codex` or `npm i -g @openai/codex`).
- `~/.codex/config.toml` is configured and `OPENAI_API_KEY` (or Codex CLI's other auth) is available to the spawned process.

### Verify

After launch, `GET /api/native/providers` should report `defaultAgent: "codex"` and include a `codex` entry in `agents`. If you still see `defaultAgent: "claude"`, the env var did not reach the web server — relaunch from a shell that has the export set, or check that the launcher script is not stripping the environment.
