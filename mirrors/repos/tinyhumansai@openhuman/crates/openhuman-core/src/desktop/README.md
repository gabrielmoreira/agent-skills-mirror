# desktop

Domain logic that exists only to serve the desktop client: things a headless
or embedded host has no use for. The module is grouped this way so a future
`desktop` Cargo feature can drop the whole family as one unit; today only two
of its members are gated (see below), and the rest compile unconditionally.

This is not the Tauri shell itself. The shell lives in `crates/openhuman-app/`
and hosts the windows, tray, and native OS integration; this module is the
core-side business logic those windows call into over RPC and Socket.IO
(accessibility queries, app-state snapshots, notification routing, and so
on). OpenHuman also ships the same frontend as a browser SPA and a ratatui
TUI (`crates/openhuman-tui`), neither of which reaches most of this module,
since it is specifically the desktop-only slice.

## Subfolders

| Folder | Owns |
| --- | --- |
| [`accessibility`](accessibility/README.md) | macOS AX/IOKit FFI, the Swift helper process, focus queries, permission detection, the Globe-key listener. Reached today only from the `voice` family. |
| [`app_state`](app_state/README.md) | The aggregator the React shell polls (`openhuman.app_state_snapshot`): stored credential, local-AI status, service health, onboarding tasks, keyring status. |
| `control` | Local opt-in desktop automation: native window inspection and control, driven through [Jev](../../../../gitbooks/developing/jev.md)-ranked accessibility actions. See its `WORKFLOW.md`. Gated by `#[cfg(feature = "modules")]`. |
| [`dashboard`](dashboard/README.md) | Aggregate operator-facing views over local config; today a single read-only per-model health comparison table. |
| [`notifications`](notifications/README.md) | Translates cross-domain events into user-facing notifications, and separately ingests, triages, and stores notifications captured from embedded webview integrations. |
| [`overlay`](overlay/README.md) | A broadcast bus for short "attention" messages pushed to the desktop overlay/notch window. |
| [`provider_surfaces`](provider_surfaces/README.md) | An early scaffold for a normalized event model and respond queue over embedded provider webviews (LinkedIn, Gmail, and similar). |

## Gating

Only two members are feature-gated today:

- `accessibility`'s microphone probe rides the `inference` feature (it calls
  `cpal`, which without `inference` reports `PermissionState::Unknown`).
- `control` is compiled only under `#[cfg(feature = "modules")]`.

Everything else in this module compiles unconditionally. See
`docs/specs/2026-08-02-core-kernel-domain-reorg.md` for the reorg that
grouped these domains together and the plan for a dedicated gate.

## Where to look next

Each subfolder's own README covers its RPC surface, persistence, and event
wiring in detail. Start with [`app_state`](app_state/README.md) if you are
looking for the shell's general health/status picture, or
[`notifications`](notifications/README.md) for anything about the in-app
notification center.
