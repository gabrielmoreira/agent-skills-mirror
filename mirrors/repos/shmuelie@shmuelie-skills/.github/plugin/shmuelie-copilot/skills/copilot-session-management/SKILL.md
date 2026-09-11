---
name: copilot-session-management
description: "Manage and diagnose GitHub Copilot CLI sessions, plugins, marketplaces, and MCP configuration. Use when sessions cannot resume, plugin installation fails, or local Copilot state needs repair."
---

# GitHub Copilot CLI Session Management

## Session state

Record the installed CLI version before diagnosis. Storage details can change:
the exact event payloads, checkpoint contents, rewind snapshot schema, and
tool-specific reference fields are **not** treated here as a stable published
contract. The paths below are discovery hints, not permission to rewrite an
unrecognized format. Repair guidance stops at what the current version clearly
supports.

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

If the session format for your CLI version is unknown, unsupported, or no
longer line-oriented text, stop and recover conservatively instead of guessing
at edits.

## Safe repair workflow

1. Exit every process using the session.
2. Copy the complete session directory to a backup.
3. Validate `workspace.yaml` and inspect line-delimited JSON files without
   rewriting them yet.
4. Record the identifiers present in the region you may edit: session ID, event
   IDs, request/result IDs, tool call IDs, checkpoint IDs, and any explicit
   cross-references that the current schema version exposes.
5. Repair only the smallest malformed file or event.
6. Preserve event order, request/result pairing, and untouched lines byte for
   byte whenever possible.
7. Re-validate rewind data and other schema-defined cross-references after any
   removal or compaction.
8. Resume the session and confirm it loads before deleting the backup.

Never silently discard malformed events. Record what was removed or repaired.

## Authorized repair boundaries

- Repair only an **inactive** session. Do not rewrite a session that the CLI or
  another process may still be appending to.
- Preserve the original session ID, surviving event IDs, and surviving tool
  request/result IDs.
- Never invent a successful tool result, assistant reply, or synthetic
  completion record to make the history "look consistent."
- Never represent a fabricated repair note as original session history. Keep
  repair notes outside the original event log.
- Do not blanket-delete whole event categories just because one record is bad.
- Respect runtime-owned database or cache files even when nearby text files are
  safe to inspect.

## Event and reference integrity

### Request/result pairing

If the current event schema exposes explicit request/result linkage, verify it
before **and** after an authorized repair:

- Every surviving result must still point to a surviving request.
- Preserve genuine results and the linkage/cardinality rules of the supported
  schema; do not synthesize a counterpart merely to make a pair look complete.
- A request with no recorded result has an **unknown outcome**, unless
  authoritative evidence establishes otherwise. The operation may have
  completed its side effects before the result was persisted.
- Do not infer success, failure, or interruption from a missing result, and do
  not automatically repeat a state-changing operation. Reconcile its actual
  state using an authorized, authoritative source before considering a retry.
- If the supported format cannot retain an unresolved request safely, recover
  from a verified backup or start a new session rather than inventing an event.
- If the schema for pairing is unknown in this CLI version, stop instead of
  guessing which records belong together.

### Session-relative order beats global timestamp sorting

Preserve the existing line order for surviving records. Do **not** globally
sort merged or repaired events only by timestamp:

- Equal timestamps can legitimately occur for a request and its result.
- Interleaved sessions can share timestamps while still having different local
  causal order.
- Global re-sorting can move a result ahead of its request, split assistant/tool
  phases, or reorder two sessions that were merely merged into one file by
  mistake.

Repair the malformed slice in place and keep untouched prefixes and suffixes in
their original order.

### Preserve untouched lines instead of reserializing the whole file

Prefer targeted line repair over "parse everything and write it back":

- Copy untouched event lines verbatim.
- Replace or remove only the minimal malformed range.
- Avoid reformatting timestamps, property order, whitespace, or escaping on
  unaffected lines.

Whole-file reserialization can accidentally normalize equal timestamps, reorder
maps, drop unknown fields, or rewrite extension-owned metadata that the current
CLI still understands.

### Rewind and cross-reference validation

After removals, truncation repair, or compaction, validate every
**schema-defined** reference that the current CLI version documents or exposes:

- rewind snapshots that point back into surviving history
- checkpoint metadata that summarizes or indexes event ranges
- attachment or artifact references that must still resolve
- parent/child or request/result links carried by the event schema

If you cannot authoritatively determine how a reference is encoded for the
current version, stop and recover from backup or start a new session that
imports only safe artifacts such as `plan.md`.

## Synthetic repair fixtures

The examples in [synthetic-repair-fixtures.md](synthetic-repair-fixtures.md) are **fictional diagnostic
models**, not authoritative Copilot CLI event schemas. Use them to reason about
safe dispositions:

- missing result after a request
- equal timestamps that must keep original line order
- interleaved records from different sessions
- dangling references after removal or compaction

Those fixtures never operate on real user session data.

## Resume problems

When a session cannot be resumed:

- Confirm the session directory still exists.
- Check that `workspace.yaml` contains a valid session ID and working directory.
- Check whether the repository or worktree moved.
- Inspect the final lines of `events.jsonl` for truncated JSON.
- If a tool request appears to be missing its result, determine whether the
  outcome can be established from authoritative evidence before editing or
  retrying anything; otherwise keep it explicitly unknown.
- Try an explicit session ID instead of an inferred current-directory match.
- Start a new session and attach the old `plan.md` when repair would be riskier
  than recovery.
- Prefer recovery over repair when the active CLI version's event or rewind
  schema is unknown.

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
- Preserve request/result pairings and cross-references, not just individual
  event bodies.
- Keep event order relative to each session; never re-sort only by global
  timestamp.
- Keep attachments and referenced artifacts with their originating event.
- Report partial failures instead of returning success-shaped output.
