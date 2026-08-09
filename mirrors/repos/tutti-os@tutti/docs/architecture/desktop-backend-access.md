# Desktop Backend Access

This document records the desktop backend access model for `tutti`.
The planned shared business-stream protocol is documented in
[Business Event Stream](./business-event-stream.md).

## Decision

`tuttid` is the local product backend for `tutti`.

Desktop uses a dual-path model:

- `renderer -> tuttid` for business capabilities and streaming transports
- `renderer -> preload -> main` for Electron and OS capabilities

`main -> tuttid` remains available for a small number of host-assisted flows,
but it is not the default business access path.

## Why

This model keeps one business authority while improving three areas that are
awkward under a main-process relay-only design:

- streaming transports such as WebSocket and SSE
- CLI access to the same local product backend
- desktop feature work that should not require a manual IPC wrapper for every
  daemon capability

The goal is not to make Electron `main` irrelevant. The goal is to stop using
it as a broad business transport relay.

## Ownership Model

### `tuttid`

`tuttid` owns:

- business rules
- durable local state
- domain workflows
- backend contracts shared by desktop and CLI

### `main`

`main` owns:

- daemon lifecycle supervision
- loopback endpoint discovery and session-token issuance
- desktop-only logging and diagnostics
- Electron and OS integrations
- host-assisted flows that require both native capability and daemon access

`main` must not become a second business core.

### `preload`

`preload` owns the narrow renderer-facing desktop SDK.

It should expose:

- runtime configuration needed to reach the managed local backend
- narrow resolved route helpers for managed transport families when renderer
  should not assemble route-local WebSocket URLs itself
- explicit host capabilities such as file pickers, window control, shell open,
  notifications, and similar native actions
- a small number of host-assisted commands when renderer cannot complete the
  flow alone

It should not expose:

- a generic `invoke(channel, payload)` surface for ordinary renderer work
- transport policy details beyond the minimum needed to reach the managed local
  backend

### `renderer`

`renderer` owns:

- UI
- view state
- direct business calls to `tuttid`
- direct SSE / WebSocket consumption when the stream is business-facing

Renderer should treat `tuttid` as the backend and `window.tutti` as the host
capability surface.

## Default Routing Rule

When adding or changing a desktop capability, choose the path by
responsibility.

### Direct `renderer -> tuttid`

Use for:

- ordinary query and command APIs
- workbench and workspace data
- search, list, get, update, save
- terminal and agent streams
- business event subscriptions

Business event subscriptions and bidirectional business event publishing should
follow the shared event-stream contract rather than route-local ad hoc socket
payloads.

### Direct `renderer -> main`

Use for:

- file and directory pickers
- shell reveal and shell open
- notifications
- menus, tray, clipboard, window lifecycle, updater
- any capability that requires Electron or OS APIs

### Host-assisted `renderer -> main -> tuttid`

Reserve for flows that require both native host authority and daemon authority
in one operation.

Examples:

- choose an export destination, then ask `tuttid` to write backend-owned data
- open a file or resource whose resolution depends on daemon-owned metadata plus
  native shell behavior
- choose a host directory, then pass that directory to a host capability that
  needs explicit filesystem input

These flows should stay explicit and few.

## Transport Policy

Desktop transport follows these rules:

- `tuttid` binds to loopback only
- desktop prefers a managed random loopback port over a fixed public port
- `main` discovers or allocates the endpoint, then provides renderer with
  runtime config
- business streaming uses HTTP, SSE, and WebSocket directly where appropriate

This favors a product-style local backend over a desktop-private relay model.

## Desktop Capability Classification

The desktop surface should be designed as three explicit capability groups.

### Backend Business Capabilities

These belong on the direct `renderer -> tuttid` path:

- health, availability, and backend bootstrap checks
- workspace catalog queries and mutations
- workbench snapshot load and save
- workspace file listing, search, creation, deletion, and upload flows
- streaming business APIs such as terminal, agent, and event streams

Terminal streams and business event streams are both direct business transports,
but they should remain separate protocol surfaces because they serve different
semantics.

Workspace file APIs on this path should stay logical-path based, for example
`/workspace/...`, rather than exposing host absolute paths as part of the
business contract.

This is the default path for business-facing desktop product behavior.

### Host Capabilities

These belong on the direct `renderer -> main` path through preload:

- system locale and system theme signals
- host-side preference sync needed for Electron-only side effects
- updater state and update actions
- file and directory pickers
- dropped-path resolution
- workspace window display and dashboard display
- shell reveal, shell open, native preview affordances
- window creation, focus, and replacement
- notifications, menu actions, tray, clipboard, and similar Electron or OS APIs

These capabilities should stay explicit on surfaces such as
`window.tutti.host.*`, `window.tutti.update.*`, and
`window.tutti.platform.*`.

Host capability rules:

- host adapters should normalize Electron-native outputs into durable product values before returning to renderer
- host window commands should stay window-oriented and avoid hiding backend mutations inside IPC handlers

Preference ownership rule:

- renderer should read and write user desktop preferences through `tuttid`
- `main` should stay limited to system-environment inputs and host-only effects such as theme application

### Host-assisted Compound Flows

These belong on the `renderer -> main -> tuttid` path:

- resolve and open a local file whose authority crosses daemon metadata and host
  shell behavior
- read local preview content when host file access is still part of the
  product contract

Use this path when host absolute-path resolution is required at runtime. Do not
push that resolution into the workspace catalog or ordinary business DTOs.

These flows should stay narrow, named, and intentional. They are not a second
business transport layer.

Update capability rule:

- preload-facing update configuration remains a typed contract, so `main/update/*` should validate supported `channel` and `policy` values instead of silently coercing unknown fields

## Security Constraints

Moving business traffic to managed loopback requires explicit guardrails:

- bind only to `127.0.0.1` or equivalent loopback
- prefer random allocated ports over fixed defaults
- require explicit desktop-issued authentication or capability material for
  renderer-visible backend access
- keep untrusted content, external webviews, and arbitrary browser surfaces off
  the desktop backend path
- keep preload surfaces narrow even when renderer can talk to `tuttid`

Renderer visibility of a local backend is acceptable only when the backend is
treated as a real product surface, not as an unguarded internal helper.

## CLI Relationship

This model supports a cleaner CLI story:

- CLI talks to `tuttid` as a client of the same local product backend
- desktop renderer talks to the same backend
- `main` stays a host supervisor, not a CLI dependency

That shared backend contract should reduce duplication across desktop, CLI, and
tests.
