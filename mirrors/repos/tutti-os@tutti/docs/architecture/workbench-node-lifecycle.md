# Workbench Node Lifecycle

This document describes the lifecycle model for shared Workbench nodes.

The goal is to keep `@tutti-os/workbench-surface` usable by Tutti desktop and
TSH without turning Workbench into a second business core.

## Ownership Model

Workbench owns node shell presentation:

- node shell creation, removal, focus, drag, resize, snap, and minimize mechanics
- frame, display mode, restore frame, minimized state, and stack order
- generic dock and window chrome mechanics
- snapshot persistence for shell presentation state

Host code owns business state:

- whether a business instance exists
- how a business instance is created, reused, closed, or restored
- node body data such as terminal cwd, exit code, browser runtime URL, agent
  session status, workspace tree state, or task progress
- business persistence and external runtime subscriptions

Workbench may receive stable identity metadata for a node shell, but it must not
become the durable store for business payloads.

## Core Concepts

The Workbench host interface should separate five concepts that were previously
easy to blur together:

- node definition
- projected node presence
- launch request
- activation
- snapshot contract

### Node Definition

A node definition describes how a node type renders and behaves at the shell
level.

It answers: "Given a node shell of this type, how should Workbench render it?"

Examples:

- `workspace-files`
- `browser`
- `terminal`
- `agent`

Node definitions may include:

- `typeId`
- default title and frame
- body and header renderers
- shell capabilities such as closable, minimizable, or fullscreenable

Node definitions must not own host business state or host-specific transport.

Dock presentation and grouping should be modeled separately at the host level.
See [Workbench Dock Model](./workbench-dock-model.md).

### Projected Node Presence

Projected node presence is a declarative input from the host into Workbench.

It answers: "Which host-owned business instances should currently have a
Workbench shell?"

This is for nodes whose presence is owned by host or runtime facts, such as:

- terminal sessions that already exist in a runtime
- agent sessions created by a host service
- other host-owned long-lived sessions whose UI should be projected into the
  Workbench

Illustrative shape:

```ts
export interface WorkbenchProjectedNode {
  typeId: string;
  instanceId: string;
  instanceKey?: string | null;
  title: string;
  defaultFrame?: WorkbenchFrame;
  subject?: {
    type: string;
    id: string;
  };
}
```

Semantics:

- when the host projects a node, Workbench reconciles a shell into current
  Workbench state
- when a projected node has the same stable shell identity as a snapshot node,
  Workbench restores presentation state from the snapshot
- when a projected node is no longer present in the host input, Workbench removes
  the shell by default
- projected node disappearance is not a business close policy; hosts that want
  an ended session to remain visible should keep projecting it and expose the
  ended state through host-owned external state

Projected presence should be reconciled in the Workbench host/session layer, not
in the lower-level reducer. The reducer should remain a pure shell state machine
for window mechanics.

Projected node `subject` is live lookup metadata. It should not be persisted in
the Workbench snapshot unless it later becomes a deliberately minimal shell
identity field. The default position is to keep it out of snapshots.

### Launch Request

A launch request is a command from Workbench or host UI asking the host to create
or resolve a business instance.

It answers: "The user or shell wants to open this kind of node; host, which
business instance should back it?"

This keeps "create or reuse an instance" as an explicit host decision instead
of folding it into a catch-all shell command.

Illustrative shape:

```ts
export interface WorkbenchLaunchRequest {
  typeId: string;
  reason: "dock" | "command" | "shortcut" | "host";
}

export interface WorkbenchLaunchResult {
  typeId: string;
  instanceId: string;
  instanceKey?: string | null;
  title?: string;
  defaultFrame?: WorkbenchFrame;
  activation?: WorkbenchActivation;
}
```

Launch requests may be asynchronous.

This supports flows such as:

```text
User clicks Terminal in the dock
  -> Workbench sends a launch request
  -> host creates or reuses a terminal session
  -> host returns stable shell identity
  -> Workbench opens or focuses the shell
```

Workbench should not infer business creation policy. The host decides whether a
launch creates a new instance, reuses an existing instance, fails, or maps to an
already projected instance.

### Activation

Activation is a one-shot business action delivered to an existing node shell.

It answers: "This node already exists; ask it to do this one thing."

Examples:

- reveal a path in the files node
- open a URL in a browser node
- focus a pane inside a terminal node
- jump to a message in an agent node

Illustrative shape:

```ts
export interface WorkbenchActivation {
  type: string;
  payload?: unknown;
  sequence: number;
}
```

Activation does not decide whether a node exists. If an action requires a node
to exist first, the caller should use launch or projected presence to obtain a
shell, then deliver activation.

Activation targets may be addressed by concrete shell node id, or by
`typeId` plus `instanceId`. Single-instance nodes may also be addressed by
`typeId` alone. Multi-instance nodes require an explicit shell id or instance
id to avoid ambiguous delivery.

Activation payloads are transient and must not be written to the Workbench
snapshot.

## Snapshot Rules

Workbench snapshots store shell presentation state only.

Snapshot purity is a P0 architecture requirement. It should be enforced by a
package-level sanitizer or validator before host snapshots are persisted.

Allowed snapshot data:

- node shell id
- node kind or type id
- title
- frame
- display mode
- restore frame
- minimized state
- node stack
- minimal shell identity metadata such as `typeId`, `instanceId`, and
  `instanceKey`
- projected shell marker such as `isProjected`

Disallowed snapshot data:

- terminal cwd
- terminal process status or exit code
- browser runtime URL or page state unless deliberately modeled as shell
  identity
- agent session status, messages, or active task state
- workspace tree contents
- launch payloads
- activation payloads
- host-owned subject details

Reload behavior for host-owned projected nodes:

```text
snapshot contains layout for terminal:session-1
host projects terminal session-1
  -> Workbench restores shell layout

snapshot contains layout for terminal:session-1
host does not project terminal session-1
  -> Workbench does not restore the shell
```

The snapshot may remember presentation for a shell identity, but it is not the
source of truth for host-owned presence.

Snapshot sanitation should preserve only the shell fields Workbench owns and the
minimal identity metadata required to reconnect shell layout with a host-owned
business instance. Host-owned business payloads should be stripped or rejected
before persistence.

## External State

Node renderers should read host-owned business state through an external state
source or equivalent host adapter.

The lookup input should include stable shell identity:

- workspace id
- node id
- type id
- instance id
- instance key when available

If projected node `subject` is needed for lookup, it may be included in live
render context or external state lookup input. That does not imply that
`subject` belongs in the persisted snapshot.

## Close Semantics

Workbench close removes or requests removal of a shell. It must not implicitly
decide host business lifecycle.

For host-owned projected nodes, close usually needs a host callback such as
`onNodeCloseRequest`. The host decides whether close means:

- hide the shell while keeping the business instance alive
- terminate the business instance
- mark the instance closed and stop projecting it
- reject or ignore the close

If the host continues projecting the same node after a shell close, Workbench
will reconcile it back into view. Host-owned close policy must therefore be
explicit.

## Placement In The Package

Projected presence reconciliation belongs in `packages/workbench/surface` at the
Workbench host/session layer.

It should not be pushed into:

- `packages/workbench/snapshot`, which owns durable snapshot compatibility
- `packages/workbench/service`, which owns Go snapshot validation and storage
- the core reducer, which should stay focused on shell state transitions
- product-specific desktop feature code, where reconciliation would become
  duplicated host glue

The lower-level reducer should remain deep and small: given a shell state and a
window-mechanics action, return the next shell state.

The host/session layer is the right module for combining:

- node definitions
- current projected presence
- loaded snapshot
- launch results
- Workbench controller commands

## Current Package Contract

`@tutti-os/workbench-surface` exposes the Workbench host lifecycle through
these public mechanisms:

- `projectedNodes` for host-owned presence
- `onLaunchRequest` and `launchNode(...)` for async dock, shortcut, command, or
  host opens
- `onNodeCloseRequest` and `requestNodeClose(...)` for explicit host close
  policy
- `activateNode(...)` and render-context `activation` for transient one-shot
  actions
- `externalStateSource` for host-owned business view state
- `createWorkbenchHostProjectedNodeId(...)` and
  `createWorkbenchHostLaunchedNodeId(...)` for stable shell id derivation

Snapshot sanitization is package-internal. Hosts should provide a repository;
Workbench owns stripping business payloads before persistence.

The public node definition contract describes shell and rendering behavior:

- type id
- default frame
- dock presentation
- chrome behavior
- render body and header
- shell capabilities
- single or multi shell mode

It does not describe business instance creation, reuse, close policy, or
business state persistence. Those stay in the host adapter or host services.

## Extension Guardrails

Allowed helper direction:

- stable shell identity helpers
- snapshot sanitation helpers
- small type guards for projected node inputs

Avoid helpers that make hosts manually restore frame or stack state from
snapshots. Layout restoration should remain behind WorkbenchHost reconciliation.

Avoid definition fields that encode business creation or reuse policy. When a
host needs custom creation behavior, use `onLaunchRequest`.

## Acceptance Criteria

- projected node first appearance creates a visible shell
- projected node with matching snapshot identity restores frame, display mode,
  minimized state, and stack order
- projected node disappearance removes the shell by default
- ordinary dock and launch-created nodes continue to work
- user layout changes are persisted as shell presentation state
- snapshot does not persist business payloads or activation payloads
- node renderers can read host-owned data through external state lookup
- close behavior for host-owned projected nodes is explicit and testable
