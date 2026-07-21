---
name: openloomi-setup
description: "Run OpenLoomi one-time setup — auto-chains install → set Codex provider → launch → wait API → mint guest session token → ready in one call. Mirrors Claude's `/openloomi:setup`. Triggers: setup openloomi, install openloomi, install and run, 一键装好并跑起来, fix openloomi, finalize openloomi, install_required, awaiting_user_action, session_initialization_required, ai_provider_required, install_failed, api_not_ready."
allowed-tools: "Bash(node $SKILL_DIR/../../scripts/loomi-bridge.mjs setup *)"
---

# OpenLoomi Setup (end-to-end wizard)

The bridge now exposes a **single end-to-end wizard**: `setup --yes`. One
invocation walks the full Codex state machine:

```
install OpenLoomi.app from the official GitHub release
  → set OPENLOOMI_AGENT_PROVIDER=codex in the GUI launchd / environment.d
     (auto-restarts the desktop if it was already running)
  → launch the desktop app (`open -a <desktopMarker>` / platform equivalent)
  → wait for the local HTTP API to come up on http://localhost:3414
  → mint a guest bearer (one-tap sign-in) into ~/.openloomi/token
  → { ready: true }
```

Each transition is automatic. **Do not** ask the user to click anything in
the GUI. The bridge only surfaces a stop condition when the next step
truly requires human action — e.g. AI provider not configured, or the
native Codex runtime isn't reachable.

This wizard is the **Codex-side equivalent of Claude's `/openloomi:setup`**.
Both plugins speak the same bridge commands, the same flag names, and the
same stop-condition vocabulary so an install step that works on one works
on the other.

## Quick workflow

1. Make sure the **Codex sandbox is set to a mode that allows the wizard
   to actually run**. `setup` needs to write to `/Applications` (macOS) or
   `~/.config/environment.d/` (Linux), install/launch the desktop helper,
   and reach `http://localhost:3414`. `workspace-write` is the minimum
   that usually works; `danger-full-access` is the safe choice for the
   first run. If you do not have approval, ask the user before invoking
   the bridge.
2. If the bridge returns `setup: install_attempted` (only happens on the
   very first invocation when `--yes` is required), this is informational
   — `--yes` is already passed through and the wizard proceeds.
3. Run:

   ```bash
   node "$SKILL_DIR/../../scripts/loomi-bridge.mjs" setup --yes [--max-wait <ms>] [--api-timeout <ms>] [--install-timeout <ms>] [--launch-timeout <ms>] [--permission-timeout <ms>] [--bin-path <path>]
   ```
4. Read the JSON. The bridge writes an audit trail of what it did into
   `steps[]`. Surface that to the user so they can see which transitions
   fired (`status_check` → `install` → `runtime_env_write` →
   `quit_for_env_reload` (only when needed) → `launch` → `wait_api` →
   `guest_login`).
5. If `setup: ready` → done.
6. If `setup: awaiting_user_action` → the chain hit a step that genuinely
   needs the user (e.g. `nextAction: install_openloomi` because `--yes`
   wasn't passed, `nextAction: configure_ai_provider` because no AI
   provider is configured, or `nextAction: open_openloomi` because the
   desktop process won't auto-launch). Explain what the user needs to do
   and stop — do **not** auto-retry.
7. If `setup: api_not_ready` → show the bridge's `hints[]` and the
   pre-built `resumeCommand`. Re-running the wizard is always safe; the
   state machine is idempotent. Re-approval may be needed to leave the
   sandbox.

## Flags

All flags are also accepted by the bridge directly. Names + defaults are
identical to Claude's `/openloomi:setup` so the two plugins speak the same
dial language.

| Flag                   | Default | Meaning                                                                                                                                                          |
| ---------------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--yes`                | off     | Pre-approve install. Without it, the bridge stops at `INSTALL_CONFIRMATION_REQUIRED` because Codex can't presume consent. With it, the chain runs end-to-end.    |
| `--max-wait`           | 120000  | Global cap (ms) across the wait stages. Defaults to 120 s to absorb the first-run install + TCC prompts.                                                        |
| `--api-timeout`        | 120000  | Per-stage budget for "waiting for local API". Independent of `--max-wait`.                                                                                       |
| `--install-timeout`    | 300000  | Per-stage budget for "installing OpenLoomi". Covers download + copy on a 50 Mbps link.                                                                           |
| `--launch-timeout`     | 10000   | Per-stage budget for `open -a <bundle>` (and platform equivalents). Almost never actually hit; included for parity with the Claude side.                       |
| `--permission-timeout` | 60000   | Extra grace wait after `--api-timeout` when the desktop process is up but the API never woke up — only fires when the bridge can confirm the process is alive.   |
| `--bin-path`           | _auto_  | Explicit path to the OpenLoomi desktop bundle (e.g. `/Applications/OpenLoomi.app`). Mirrors Claude's flag and overrides the usual discovery order.                |

## Live status

While the wizard is inside a long stage, the bridge writes a throttled
1 Hz line to **stderr** so the user can see progress:

```
  · installing OpenLoomi  (12s / max 5m) …
  · waiting for local API  (4s / max 2m) …
  · waiting on macOS permission prompt  (3s / max 1m) …
```

Stdout is reserved for the final JSON result — do not mix it.

## `api_not_ready` payload

When `--api-timeout` (+ `--permission-timeout` grace) elapses, the wizard
returns an **actionable** JSON payload you can use to drive chat-side
guidance. The original `setup: "api_not_ready"` shape is preserved for
backwards compatibility; new fields are added alongside it.

| Field               | Type     | Meaning                                                                                                              |
| ------------------- | -------- | -------------------------------------------------------------------------------------------------------------------- |
| `ok`                | bool     | Always `false` for this stop condition.                                                                              |
| `setup`             | string   | Always `"api_not_ready"` here.                                                                                       |
| `code`              | string   | Stable machine code: `"API_NOT_READY"` or `"PERMISSION_PROMPT_LIKELY"` (when desktop process is up but API is not). |
| `stage`             | string   | Always `"wait_api"`. Reserved for future per-stage error codes.                                                      |
| `elapsedMs`         | number   | Wall-clock time since `setup --yes` started.                                                                         |
| `effectiveBudgetMs` | number   | Total wait budget actually granted (api + permission grace).                                                         |
| `canResume`         | bool     | Always `true`. Re-running the wizard is the supported "keep waiting" action.                                         |
| `resumeCommand`     | string   | A pre-built command the user can paste — already uses a sensible raised `--max-wait`.                                |
| `hints`             | string[] | 1–3 hints, safe to print verbatim. Includes the macOS TCC prompt hint on Darwin.                                     |
| `overCap`           | bool     | `true` if the elapsed time exceeded the global `--max-wait` cap (informational).                                     |
| `steps`             | Step[]   | The existing audit trail.                                                                                            |
| `wait`              | object   | The raw `waitForApi` payload (code, elapsedMs, attempted, lastError, optional graceWait).                             |
| `status`            | object   | The latest `setup-status` snapshot.                                                                                  |

## Stop conditions and what they mean

| `setup`                        | When it fires                                                                                                                                                                                                                                                                                                |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `ready`                        | All transitions completed. The desktop app is running, the API is reachable, the guest session token is minted, **and** the native Codex provider is the active agent. Surface `mode`, `version`, and `executionProviderSource` from `status`. |
| `awaiting_user_action`         | A transition that needs the user ran without a programmatic path. Most commonly: `nextAction: install_openloomi` because `--yes` wasn't passed, `nextAction: configure_ai_provider` because no provider is configured, `nextAction: open_openloomi` because the desktop process didn't wake, or `nextAction: inspect_codex_runtime` because the native Codex agent is not active. Walk the user through what they need to do and stop. |
| `install_attempted`            | (Informational.) The first `setup` invocation in a fresh environment must install before it can confirm READY. `--yes` already authorised the install; treat this as a normal await. |
| `install_failed`               | The platform install script exited non-zero (or hit `--install-timeout`). Show `install.code` / `install.message`.                                                                                                                                                                                            |
| `runtime_env_failed`           | The `set-codex-runtime-env` step failed (rare; usually a TCC prompt on macOS, or a write-permission error on Linux). Follow `runtimeEnv.message`.                                                                                                                                                            |
| `quit_for_env_reload_failed`   | The desktop app was running, the env var was written, but `quitDesktopApp` couldn't bring it down (TCC prompt blocking the kill). The only stop condition that **truly** needs the user to Quit+Reopen by hand. Surface `quit.message`.                                                                       |
| `launch_failed`                | `open -a <desktopMarker>` (or platform equivalent) returned a non-zero exit. On macOS this almost never happens for a signed .app; if it does, fall back to manual launch instructions.                                                                                                                       |
| `api_not_ready`                | The desktop app was launched but the local HTTP API didn't respond within `--api-timeout`. The bridge only adds `--permission-timeout` grace when it can confirm the desktop process is alive. `code` distinguishes network/slow (`API_NOT_READY`) vs TCC prompt (`PERMISSION_PROMPT_LIKELY`); `hints[]` and `resumeCommand` are pre-built; `canResume: true` makes re-running the wizard the recommended action. |
| `guest_login_failed`           | API is up but the one-tap guest login was rejected by `/api/auth/guest`. Show `session.code` / `session.error`. The user can sign in via the GUI and re-run setup.                                                                                                                                         |
| `step_limit_reached`           | Hit the internal step ceiling without reaching READY (default 8 transitions). Almost certainly a state-machine bug; show `steps[]`.                                                                                                                                                                          |

The bridge's stdout output is authoritative. Never invoke the platform
install script (`setup.{macos,linux,windows}.*`) directly — only the
bridge may run it, and only after explicit user consent (which is what
`--yes` records).

## Codex provider wiring

Before any launch, the bridge writes `OPENLOOMI_AGENT_PROVIDER=codex` so
the freshly-started desktop server picks up the Codex runtime. On macOS
this is done via `launchctl setenv` plus a LaunchAgent so the variable
survives reboot; on Linux the bridge edits `~/.config/environment.d/`; on
Windows the user must set the variable manually. `codex-runtime-info`
always reports the current effective value.

## Post-`ready` guidance

When `setup: ready` fires, the wizard is done. Do **not** improvise a
"Next: run X" hint — pick from the closed list below, or say nothing
beyond the audit table.

## After `api_not_ready`

When the wizard times out waiting for the API, the recommended chat-side
flow is:

1. Show the bridge's `hints[]` verbatim. Each is safe-to-print.
2. If `canResume: true` (always the case for `api_not_ready`), suggest
   the user simply re-runs the wizard. The state machine is idempotent —
   already-completed steps (e.g. install, env write) will be skipped
   immediately, and the wizard will land back inside `wait_api`.
3. If the user wants to _raise_ the budget once, ship the pre-built
   `resumeCommand` (e.g. `node <plugin>/scripts/loomi-bridge.mjs setup
   --yes --max-wait 180000`) rather than asking them to invent the flag.

## Follow-up commands

| Follow-up         | Bridge command                                          | When to suggest                                                                |
| ----------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Status snapshot   | `setup-status`                                          | User asks "is everything wired up?" — read-only snapshot.                      |
| Pet state         | `pet happy` / `pet normal` / etc.                       | User asks about the Pet widget or wants to flip its state manually.            |
| Code runtime env  | `codex-runtime-info`                                    | User asks whether the desktop app is wired to Codex.                           |
| Install-only      | `install-openloomi --confirm`                           | User asks to install without launching (rare; mostly CI / VDI).                |

## Sandbox notes

The `setup` wizard **must be run outside the Codex sandbox** (or with
`danger-full-access`) — it needs to write to system application
directories (`/Applications` on macOS, `~/.config/environment.d/` on
Linux), launch a signed GUI helper, and reach the local HTTP API at
`http://localhost:3414`. None of those survive `read-only` or default
`workspace-write` mode in a fresh environment. If you are still inside a
sandbox when the user asks for setup, request approval and re-run
outside the sandbox before invoking the bridge. The bridge surfaces a
sandbox-y reason in `awaiting_user_action`, `launch_failed`, or
`api_not_ready`; the `hints[]` payload calls out the next concrete step
(approve the request and retry).
