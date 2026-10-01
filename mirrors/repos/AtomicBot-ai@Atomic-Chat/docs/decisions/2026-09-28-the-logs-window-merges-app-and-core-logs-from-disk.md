---
date: 2026-09-28
title: "The Logs window merges the app's and the core's logs from disk"
---

# 2026-09-28 — The Logs window merges the app's and the core's logs from disk

- **Context:** before the core migration, `<data>/logs/app.log` held the app's lines and every
  engine's output, and "Open Logs" showed all of it. After it the history split three ways:
  `app.log` kept the app's lines only; the core's own lines went to `core-start.log`, which has
  no time, no rotation, is recreated on every start and shows nowhere; engine output was kept
  nowhere at all. The times did not agree either: `app.log` is UTC, the core's stderr had none,
  and the window printed local `HH:MM:SS` without a date. A user could neither see what happened
  nor send us a file that shows it. The core is a detached process that outlives the app and
  that the app reattaches to, so there is no pipe to read its output from.
- **Decision:** the core writes `<data>/atomic-core/logs/core.log` itself (core ADR
  `2026-09-28-the-app-core-writes-its-own-log-file`), in `app.log`'s line format and rotation.
  The app reads both files from disk in one Rust module, `src-tauri/src/core/logs/`: the tail of
  each active file, then its newest `<stem>_*.log` archives, up to a byte budget per source;
  entries are split on a strict header
  (`[YYYY-MM-DD][HH:MM:SS][target][TRACE|DEBUG|INFO|WARN|ERROR] ` with a real date and time)
  and merged by (time, app before core, position in the source). `read_unified_logs` (2 MiB per
  source) feeds the Logs window; `export_logs` (10 MiB per source) writes one file with a `# `
  header and `[app]` / `[core]` on every entry, each line through `core::telemetry::scrub`,
  via a temporary file renamed into place. Times are shown as written — `YYYY-MM-DD HH:MM:SS UTC`
  — in the window, the MCP log and the export; the export header adds the user's local offset.
  A `CORE_START_FAILED` is logged as one `WARN` record in `app.log` with the tail of
  `core-start.log` indented by `  | `, so the strict header does not split it.
- **Consequences:**
  - The core's history survives a crash of either process and shows even while the core is
    down. Without `core.log` (an older core, mobile) the window shows the app alone.
  - `app.log`'s header is now spelled out in `lib.rs` (`core::logs::line_header`) instead of
    inherited from `tauri-plugin-log`: the plugin's `timezone_strategy` installs a format with
    the level and target columns swapped (2.8.0), so setting UTC explicitly meant setting the
    format too. The line format itself did not change.
  - One merge implementation serves the window and the export; `read_logs` and `parseLogLine`
    stay for the MCP log viewer, which follows live `log://log` events.
  - "Show in Finder" still opens `<data>/logs` only; handing logs over is what the export is for.
  - Times are to the second, so the order of an app and a core entry within one second is the
    merge rule's, not the clock's.
  - The repository ignores `logs/` and `*.log`; `.gitignore` re-includes the module and its
    fixtures.
- **Owner:** `team`
- **Links:** change `add-unified-logs` in `atomic-chat-spec`; `src-tauri/src/core/logs/`;
  `web-app/src/routes/logs.tsx`; `web-app/src/lib/log-time.ts`; the core contract row for
  `core.log` in `atomic-chat-core/docs/contracts.md` and its fixture
  `test/fixtures/core-log/sample.log`, copied to `src-tauri/src/core/logs/testdata/`.
