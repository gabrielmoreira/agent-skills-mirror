---
name: openloomi-install
description: "OpenLoomi install & first-use setup helper for Codex. Use when the user wants to install OpenLoomi, configure it, or troubleshoot `INSTALL_REQUIRED` / `SOURCE_FOUND_APP_NOT_BUILT` / `SESSION_INITIALIZATION_REQUIRED` after running setup-status. Triggers: install openloomi, configure openloomi, setup openloomi, openloomi not installed, openloomi not finalized, install_required, install missing, guest session."
allowed-tools: "Bash(node $SKILL_DIR/../../scripts/loomi-bridge.mjs *)"
---

# OpenLoomi Install Sub-skill

This sub-skill is auto-loaded when the user wants to install or fix OpenLoomi
on their machine. It composes `loomi-bridge` operations and never downloads
or executes anything outside the plugin's own scripts.

## Quick workflow

1. **Always run `setup` (and the loopback checks below) outside the Codex
   sandbox** — the install + launch path needs writes to `/Applications`,
   desktop GUI launch, and `http://localhost:3414`. Default `read-only` /
   `workspace-write` modes will silently fail. Ask the user to drop
   `sandbox=workspace-write` (or move to `danger-full-access`) before
   invoking the bridge.
2. `node "$SKILL_DIR/../../scripts/loomi-bridge.mjs" setup-status`
3. Based on `nextAction` / `reason`:

| Reason / nextAction | Action |
|---|---|
| `install_openloomi` / `INSTALL_REQUIRED` | OpenLoomi Desktop is not on this machine. **Call `setup --yes` to run the end-to-end wizard in one invocation**: resolve → download → install → set `OPENLOOMI_AGENT_PROVIDER=codex` → launch the desktop app → wait for the local API → mint a guest session token. Invoking this skill counts as explicit approval to pass `--yes`. For offline / corporate-proxy installs, point the user at the restricted-network guide (link below) and call `install-instructions` first. |
| `SOURCE_FOUND_APP_NOT_BUILT` | A source checkout is present but the OpenLoomi Desktop GUI app has not been built yet. Recommend either building the source per the OpenLoomi repo's Tauri build docs (or run `loomi-bridge install-instructions`) or installing the packaged Desktop release. |
| `open_openloomi` / `OPENLOOMI_API_UNREACHABLE` / `SESSION_INITIALIZATION_REQUIRED` | OpenLoomi is installed but the local API or guest/session token is not ready. Ask the user to open OpenLoomi Desktop once, or run `setup` so the bridge can launch/init through OpenLoomi-owned surfaces. |
| `inspect_codex_runtime` | OpenLoomi is up but the native Codex provider is not the active default agent. Have the user confirm the Codex CLI is installed (`codex --version`) and rerun `setup` so the runtime env + LaunchAgent get re-applied. |

Before applying the API-unreachable row, inspect `loopbackAccessAmbiguous`.
When it is `true`, the result is inconclusive because the current Codex sandbox
may block host loopback traffic. Request approval and run
`loopbackAccess.verification.commands` outside the sandbox. Only tell the user
to restart OpenLoomi if the outside-sandbox checks also fail.

## Sandbox and installation

Downloading and installing OpenLoomi can require capabilities that are blocked
inside the current Codex sandbox:

- GitHub release lookup and artifact download require network access.
- The default installer may write to a system application directory such as
  `/Applications`.
- Interactive installers and launching OpenLoomi Desktop require GUI/process
  access outside the sandbox.

When an install command fails with a likely network, permission, filesystem, or
GUI sandbox error, request approval and retry the same `loomi-bridge` command
outside the sandbox. Do not work around the bridge by downloading or installing
the artifact with unrelated commands. Do not report that the release URL is
invalid or the installer is broken until the approved retry also fails.

## Codex runtime setup

If the user is setting up OpenLoomi from Codex, explicitly asks to switch the
desktop runtime executor to Codex, or diagnostics show a native-agent provider
mismatch, call:

```bash
node "$SKILL_DIR/../../scripts/loomi-bridge.mjs" codex-runtime-info
```

## Reminder: secrets contract

- The bridge never reads AI provider env vars and never reports provider readiness from `/api/preferences/ai` — it only checks whether the native Codex runtime is active via `/api/native/providers`. Provider configuration is the OpenLoomi runtime's job, surfaced through the desktop app's own settings UI.
- If the user pastes a key into chat, redact it: do NOT echo it back, and tell them to remove it from chat history.
- Never pass `--api-key` as an argv flag. The bridge has no such flag, by design.
- The bridge's end-to-end wizard is `setup --yes` (one-shot: install + set codex provider + launch desktop + mint guest session token). Invoke it from this skill when the user asks to install or finalize OpenLoomi. **Do not call `install-openloomi --confirm` by itself** — that only installs and leaves the desktop app unlaunched and the session token unminted. Use `install-openloomi --confirm` only when the user explicitly asks to install without launching (rare).
