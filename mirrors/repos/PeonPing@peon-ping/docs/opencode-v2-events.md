# OpenCode v2 event mapping

`adapters/opencode/peon-ping.ts` targets the OpenCode **v2** plugin API
(`opencode >= 2.0`). Two things changed together in v2, and both are required
for the adapter to load and fire.

## 1. Plugin module format

v2 removed the v1 server plugin API entirely. Local plugins under
`~/.config/opencode/plugin{,s}/` are loaded by
`packages/core/src/plugin/module.ts`, which decodes the module's default export
against:

```ts
Schema.Struct({
  default: Schema.Union([
    Schema.Struct({ id: Schema.String, effect: /* (ctx) => Effect */ }),
    Schema.Struct({ id: Schema.String, setup: /* (ctx) => Promise<Cleanup|void> */ }),
  ]),
})
```

A v1 adapter — whose default export is a bare async function — fails with:

```
PluginModule.LoadError: Plugin must export a default definition with an id and
an effect or setup function.
cause: SchemaError(Expected object at ["default"])
```

`Expected object` rather than `Missing key` is the tell: the key is present, it
just is not an object.

The v2 package is `@opencode/plugin`. This single-file adapter uses the
definition object directly and has no runtime package import.

## 2. Event taxonomy

v2 also replaced the event names the adapter used to switch on. The v1 targets
no longer exist; `session.idle` survives only as a `// deprecated` definition
and `session.status` is defined but never published.

| peon-ping hook event   | v1 event (removed)         | v2 event used instead                     |
| ---------------------- | -------------------------- | ----------------------------------------- |
| `SessionStart`         | `session.created`          | first `session.execution.started`          |
| `UserPromptSubmit`     | `session.status` (busy)    | `session.execution.started`                |
| `Stop`                 | `session.idle`             | `session.execution.succeeded`              |
| `PostToolUseFailure`   | `session.error`            | `session.execution.failed`                 |
| `PermissionRequest`    | `permission.asked`         | `permission.asked` (unchanged)             |
| `Notification`         | `question.asked`           | `form.created`                             |
| silent state cleanup   | no direct equivalent      | `session.execution.interrupted`            |

v2 payloads also carry the event body under `data` rather than `properties`:

```ts
for await (const event of ctx.event.subscribe()) {
  // event: { id, type, location?, data: { sessionID, ... } }
}
```

## Notes

- The first execution in each primary session emits `SessionStart`. Later
  executions emit `UserPromptSubmit` after the existing 3s startup debounce.
  Repeated starts while the session is busy are ignored. Success, failure,
  interruption and deletion clear busy state.
- A tool failure surfaces as `session.execution.failed`. There is no longer a
  per-tool error event, so `PostToolUseFailure` now covers any failed
  execution, not just tool errors.
- `session.created` identifies the new session with `data.sessionID` and
  marks a child with `data.parentID`. Child lifecycle, permission and form
  notifications are suppressed after creation has been observed. For events
  without a location, the host session lookup also identifies child sessions.
- `form.created` nests its request under `data.form`: the adapter reads
  `data.form.id` and `data.form.sessionID`. Replies and cancellations use
  `data.id`. Form text, fields, answers and request IDs are never forwarded
  to the hook.
- The stream covers the connected server. Events carrying a different
  `location.directory` are ignored. Durable execution events have no location
  envelope, so the adapter resolves their session through `ctx.session.get`
  and compares its directory before forwarding. An unresolved directory is
  ignored. Symlink aliases identify the same physical directory. If the host
  loads multiple plugin instances for that directory, one instance owns the
  bridge until its cleanup releases ownership to a surviving instance.
- Cleanup aborts the event subscription and releases directory ownership.
  A session lookup that finishes after cleanup cannot send a notification.
  `session.deleted` silently clears state by its globally unique session ID
  without retrieving a session that the host has already removed.

These payloads were checked against the [OpenCode v2 session schema](https://github.com/anomalyco/opencode/blob/0a46301e36d7edd517dd89736acc5daf9c74898e/packages/schema/src/session-event.ts),
[form schema](https://github.com/anomalyco/opencode/blob/0a46301e36d7edd517dd89736acc5daf9c74898e/packages/schema/src/form.ts)
and [plugin API](https://opencode.ai/v2/docs/build/plugins) on 2026-10-04.

## Native hook bridge

On Windows, the adapter invokes `powershell.exe -NoProfile -NonInteractive
-File peon.ps1` directly, with UTF-8 JSON on stdin. It requires no Bash
wrapper. On macOS and Linux it invokes `bash peon.sh` with the same JSON.
The script path is an argument rather than shell command text. Stdin is
closed after writing the payload, and asynchronous process/pipe errors are
contained.

Discovery checks `CLAUDE_PEON_DIR`, then the Claude hook directory
(`CLAUDE_CONFIG_DIR` or `~/.claude`), the Windows OpenPeon hook directory,
the shared `~/.openpeon` directory and the legacy OpenClaw hook directory.
Only the platform's native script is required.

## Validation and compatibility gates

Run `npm ci` and `npx vitest run` from `adapters/opencode`. The adapter
workflow runs on Ubuntu and Windows. `tests/opencode-bridge.test.ts`
launches the real native executable and checks UTF-8 JSON delivery through
a script path containing spaces, quotes and Unicode. Windows Pester checks
run separately in the main test workflow. Both Windows jobs must pass
before the native bridge is shipped.

On 2026-10-04, the exact adapter was loaded by the official
`@opencode/cli-darwin-arm64@2.0.22` binary in isolated temporary HOME and XDG
directories. The [official update manifest](https://opencode.ai/update/api/latest/cli/npm)
identified build source `05018b8862a8fc198ec9810aafd397c96bb7d86e`.
Actual host events verified forms, permissions, successful and failed
executions, child suppression, routing between two projects and a `/tmp`
symlink alias. Three real location reloads produced one notification each;
all 12 plugin setups received cleanup and closed their streams. A local
OpenAI-compatible fixture supplied model responses without external model
calls. These macOS checks complement the required native Windows jobs.

This adapter targets OpenCode v2. OpenCode v1 uses a different export and
event contract. The Kilo installers download the preserved v1 server
adapter from `adapters/kilo/peon-ping.ts` directly, so the OpenCode v2
migration does not change Kilo's event contract. The dedicated adapter
exports a `server` function and reads v1 `properties` payloads, matching
[Kilo's documented plugin API](https://kilo.ai/docs/automate/extending/plugins)
and the [Kilo host bridge](https://github.com/Kilo-Org/kilocode/blob/76bcfd40be616a72f4697b3041565f322245b462/packages/opencode/src/plugin/index.ts).
The shell installer integration test loads the installed plugin and
checks `session.idle` delivery through its real hook process. Windows
installer behavior is covered by `tests/opencode-installer.Tests.ps1`.
On 2026-10-04, the exact dedicated adapter also loaded from the global plugin
directory in the official `@kilocode/cli-darwin-arm64@7.8.3` binary. Actual
`session.created` events carried `properties.info`; a primary session
delivered `SessionStart` through Bash, and a child carrying `parentID`
remained silent. The host was isolated in temporary HOME and XDG directories
and terminated after validation.
