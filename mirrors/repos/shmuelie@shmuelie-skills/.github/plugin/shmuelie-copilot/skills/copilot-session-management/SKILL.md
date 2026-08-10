---
name: copilot-session-management
description: "Manage and diagnose GitHub Copilot CLI sessions, plugins, marketplaces, and MCP configuration. Use when sessions cannot resume, plugin installation fails, or local Copilot state needs repair."
---

# GitHub Copilot CLI Session Management

## Session state

Interactive sessions are stored under:

```text
~/.copilot/session-state/<session-id>/
```

Common files include:

- `workspace.yaml` - session identity, repository, branch, name, and timestamps
- `events.jsonl` - append-only conversation events
- `plan.md` - saved implementation plan
- `checkpoints/` - checkpoint metadata
- `rewind-snapshots/` - rewind history
- `files/` - session-scoped artifacts

Treat database and cache files as runtime-owned. Do not copy or merge them
manually.

## Safe repair workflow

1. Exit every process using the session.
2. Copy the complete session directory to a backup.
3. Validate `workspace.yaml` and line-delimited JSON files.
4. Repair only the smallest malformed file or event.
5. Preserve event order and IDs.
6. Resume the session and confirm it loads before deleting the backup.

Never silently discard malformed events. Record what was removed or repaired.

## Resume problems

When a session cannot be resumed:

- Confirm the session directory still exists.
- Check that `workspace.yaml` contains a valid session ID and working directory.
- Check whether the repository or worktree moved.
- Inspect the final lines of `events.jsonl` for truncated JSON.
- Try an explicit session ID instead of an inferred current-directory match.
- Start a new session and attach the old `plan.md` when repair would be riskier
  than recovery.

## Plugin management

Native commands:

```text
copilot plugin list
copilot plugin install owner/repository
copilot plugin install owner/repository:path/to/plugin
copilot plugin update plugin-name
copilot plugin update --all
copilot plugin uninstall plugin-name
```

Marketplace commands:

```text
copilot plugin marketplace add owner/repository
copilot plugin marketplace list
copilot plugin marketplace browse marketplace-name
copilot plugin marketplace update marketplace-name
copilot plugin marketplace remove marketplace-name
copilot plugin install plugin-name@marketplace-name
```

When installation fails:

- Verify the repository and source directory are accessible.
- Confirm `plugin.json` parses and its paths are relative to the plugin root.
- Confirm a marketplace entry's name and version match the plugin manifest.
- Remove stale cached copies only after recording the installed source.
- Reinstall from a local path to distinguish packaging errors from network errors.

## MCP configuration

Keep MCP server configuration declarative and source-controlled when possible.

- Use valid server names containing only letters, numbers, hyphens, and underscores.
- Prefer explicit executable paths when a shell shim is not directly spawnable.
- Keep credentials in environment variables or platform credential stores.
- Validate stdio servers independently before adding them to Copilot CLI.
- Avoid automatically enabling expensive or environment-specific servers in
  every repository.

## Windows desktop notifications

Copilot CLI raises native Windows toasts ("Agent finished" / "Needs your
attention") from a bundled native addon (`prebuilds/win32-x64/cli-native.node`)
using the WinRT toast API. Understanding the mechanism is the key to diagnosing
missing notifications.

- The toast is sent under a fixed **AppUserModelID (AUMID)** `GitHub.Copilot.CLI`.
  The addon self-registers app identity under
  `HKCU\Software\Classes\AppUserModelId\GitHub.Copilot.CLI` (DisplayName, IconUri).
- It fires on session idle/attention **only while the terminal is unfocused**
  (the CLI tracks focus via DECSET 1004 focus reporting). A terminal that never
  reports blur can suppress it.
- `COPILOT_DISABLE_DESKTOP_NOTIFICATIONS=1` disables it. Failures are swallowed
  silently, so nothing surfaces when a toast is dropped.

Diagnosis checklist when Windows toasts do not appear:

1. **AUMID registration** — the top cause. WinRT
   `ToastNotificationManager.CreateToastNotifier("GitHub.Copilot.CLI").Show()`
   **does not throw** when the AUMID is unregistered; Windows just silently drops
   the banner. Confirm `HKCU:\Software\Classes\AppUserModelId\GitHub.Copilot.CLI`
   exists. If missing, notifications are dropped.
2. **Global/app toggles** — `HKCU:\...\PushNotifications\ToastEnabled = 1`; no
   Focus Assist / Do Not Disturb; per-app entry under
   `...\Notifications\Settings\GitHub.Copilot.CLI` not disabled.
3. **Env kill switch** — `COPILOT_DISABLE_DESKTOP_NOTIFICATIONS` unset.
4. **Addon loaded** — `logLevel: all` logs show the native addon loading.
5. **Test the OS pipeline** — send a toast from **Windows PowerShell 5.1** (the
   `[Windows.UI.Notifications...,ContentType=WindowsRuntime]` projection does not
   load in PowerShell 7). A toast under the built-in PowerShell AUMID
   (`{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe`)
   verifies the OS can display toasts and isolates the fault to AUMID registration.

To inspect a compiled native addon's mechanism, extract its printable strings
(the Rust addon exposes `Windows.UI.Notifications.ToastNotification`,
`SOFTWARE\Classes\AppUserModelId\`, and the AUMID literal).

## Session maintenance rules

- Back up before merge, compaction, or repair.
- Merge only sessions from the same logical task.
- Preserve the newer session's identity and metadata.
- Deduplicate repeated events by stable event IDs, not by message text.
- Keep attachments and referenced artifacts with their originating event.
- Report partial failures instead of returning success-shaped output.
