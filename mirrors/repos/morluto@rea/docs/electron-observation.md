# Electron file-page observation

REA can attach to a user-owned Electron/Chromium CDP endpoint and inspect existing `file://` renderer pages without evaluating JavaScript or invoking Electron APIs. The caller supplies the endpoint directly; REA accepts only literal-port loopback HTTP endpoints. Selecting an endpoint exposes every Electron target it serves, including local file paths and page metadata.

This passive runtime surface is distinct from the target-free static
[`analyze_javascript_application`](javascript-artifact-reconstruction.md)
workflow. Static analysis reads an approved ASAR or extracted directory under
observations and static inferences are never silently treated as the same fact.
Use the separate
[`reconcile_javascript_runtime`](javascript-runtime-reconciliation.md) workflow
when both Evidence sets already exist.

## Configure authority

The capability is disabled by default:

```bash
export REA_ELECTRON_OBSERVE_ENABLED=true
```

The capability is disabled by default. Its permission ceiling is loopback-only. REA accepts local hostless `file://` URLs that resolve to regular files; remote hosts, encoded path separators, and nonexistent paths are rejected. There is no separate filesystem-root configuration.

## Workflow

`list_electron_targets` returns every eligible target served by the supplied endpoint in one inline array.

For the MCP follow-up call, pass the same literal-loopback endpoint and the selected target ID to `inspect_electron_page`. REA rediscovers targets and validates the ID against the live endpoint before inspection.

```bash
rea list-electron-targets http://127.0.0.1:9223 --json
rea inspect-electron-page http://127.0.0.1:9223 TARGET_ID \
  --observation-ms 100 --json
```

Script content is excluded by default. Requesting it includes every authorized script source:

```bash
rea inspect-electron-page http://127.0.0.1:9223 TARGET_ID \
  --include-script-sources \
  --json
```

The normalized result contains canonical local paths, frame and DOM
structure, resource metadata, stable script/resource identities, explicit
completeness, and content-addressed approved source artifacts. Script metadata
retains its execution-context frame ID when CDP supplies one. The capture also
inventories authorized worker, service-worker, and shared-worker targets with
validated opener-target and parent-frame IDs. Worker discovery uses passive
target metadata; REA does not attach to or execute code in those targets.
Collection counts and aggregate script-source bytes are not capped. Like every
target, frame, script, and resource, a worker URL must resolve to a local
file before it is retained. Relationship IDs improve
attribution but do not prove which static module started a worker or that its
work completed.

Inspection does not retain DOM values, execute renderer code, navigate, click,
invoke Electron IPC, close a target, or terminate the application.

## Active Electron scenarios

Active Electron authority is separate and disabled by default. When enabled,
REA launches an operator-approved Electron executable through the official
Playwright Electron API, owns its lifetime, accepts bounded click/wait actions,
window-targeted renderer reload/crash actions, and synthetic `open-url` or
`second-instance` deep-link delivery. It records capture-scoped window and
WebContents identities, process metrics, and IPC channel and value-shape metadata.
Payload values are not retained.

Configure exact roots and run the real fixture verifier with an operator-owned
Electron runtime:

```bash
export REA_ELECTRON_AUTOMATE_ENABLED=true
export REA_ELECTRON_AUTOMATE_AUTO_GRANT=false
export REA_ELECTRON_AUTOMATE_EXECUTABLE_ROOTS_JSON='["/absolute/path/to/runtime"]'
export REA_ELECTRON_AUTOMATE_APPLICATION_ROOTS_JSON='["/absolute/path/to/app"]'
REA_ELECTRON_EXECUTABLE=/absolute/path/to/electron npm run verify:electron
```

This capability actively launches and interacts with the target. It is not a
passive CDP observation and must be granted separately as `electron_automate`.
The default is fail-closed (`AUTO_GRANT=false`); an operator can instead issue
a project/session/one-shot grant through the normal permission workflow. The
owned process keeps normal host filesystem and network privileges, so this is
an authority boundary and lifecycle boundary, not a sandbox.

The CLI and MCP surfaces accept the same schema. For a JSON request file:

```bash
rea capture-electron-scenario scenario.json --json
```

The result records action status and targets, correlated app/window/WebContents,
preload, session, navigation, shell, permission, popup, download, protocol,
native-addon, process, and IPC timeline events. IPC channels are capped at
1,024 characters and argument-shape metadata at 32 entries; values are never
retained. Renderer crash/restart and deep-link actions are synthetic
scenario controls; their attempted and observed outcomes remain in the
timeline. The active hook blocks and records external shell/navigation,
permission, download, popup, updater, and OS-integration effects. The timeline
is explicitly partial when attachment starts after application activity. The
owned experiment has an internal 60-second deadline and a 5-second per-action
timeout so hung work reaches process cleanup; these are lifecycle timeouts, not
caller-selected capture limits.

Active Electron Evidence can also be supplied to
[`reconcile_javascript_runtime`](javascript-runtime-reconciliation.md). That
projection is intentionally target-only and partial: it binds the approved
application path and capture outcome to the static graph, while frames, scripts,
workers, and execution claims remain unavailable until a separate passive runtime
capture provides them.
