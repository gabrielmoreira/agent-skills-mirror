---
date: 2026-09-30
title: "Stop a leftover app core before the Windows installer overwrites it"
---

# 2026-09-30 — Stop a leftover app core before the Windows installer overwrites it

- **Context:** The app starts `atomic-chat-app-core.exe` detached, and only `RunEvent::Exit` stops
  it. A Windows update never reaches that handler: `tauri-plugin-updater` launches the NSIS
  installer and calls `std::process::exit(0)` (its `on_before_exit` only runs
  `cleanup_before_exit`). The core then lives on until its client lease runs out (about 45 s)
  and keeps `resources\bin\atomic-chat-app-core.exe` locked. The installer copies files right
  away, so the first update from a core build would stop on "Error opening file for writing".
  The update from a pre-core build is not affected: no core runs there yet.
- **Decision:** `NSIS_HOOK_PREINSTALL` in `src-tauri/windows/hooks.nsh` runs
  `taskkill /F /T /IM atomic-chat-app-core.exe` before any file is copied, when the installer
  runs in update mode or the app is not running. A manual install over a running app is left to
  Tauri's `CheckIfAppIsRunning`, which asks first. The uninstall hook stops the core as well.
  The fix lives in the installer, not the app, because the installer that runs is always the
  new one: it also covers the update away from builds that shipped without it.
- **Consequences:** The core is killed, not asked to shut down. The app has already unloaded
  local models before the update (`stopModelsBeforeUpdate`), and the next core treats the stale
  lock and journal as a crash it recovers from. `/T` also ends the core's backends and tunnel.
  A manual or silent install over a running app can still meet the locked binary for up to the
  lease; Retry succeeds once the core has gone. A CLI core the user started from the installed
  `jan-cli.exe` is not touched.
- **Owner:** team
- **Links:** `src-tauri/windows/hooks.nsh`, `web-app/src/hooks/useAppUpdater.ts`,
  [Windows auto-updater uses NSIS as sole relauncher](2026-05-22-windows-auto-updater-uses-nsis-as-sole-relauncher.md),
  [Pin the core version and reject mismatches](2026-09-15-pin-the-core-version-and-reject-mismatches.md)
