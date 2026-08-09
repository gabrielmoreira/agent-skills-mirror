# Tuttid Layering

This document defines the internal layering rules for `services/tuttid`.

## Purpose

`tuttid` is the primary business core for the open-source local product.

Its directory structure should follow a clear layered desktop-daemon model,
while remaining scaled to the current size of `tuttid`.

## Current Layout

```text
services/tuttid/
  main.go
  wiring.go
  app/
  api/
  biz/
  data/
  integration/
  server/
  service/
  types/
```

## Layer Responsibilities

### `main.go`

Owns process bootstrap only:

- logger setup
- signal handling
- startup error handling
- calling into `app`

`main.go` should not contain domain logic or route wiring details.

### `wiring.go`

Owns composition root responsibilities:

- open local backends
- run migrations
- construct services and handlers
- register route dependencies
- close long-lived resources on shutdown

`wiring.go` is allowed to know concrete implementations.
Other layers should depend on interfaces or narrow collaborators whenever possible.

### `app/`

Owns process lifecycle around the HTTP server:

- listen
- shutdown
- signal-aware termination

`app/` should not grow domain-specific behavior.

### `server/`

Owns HTTP server assembly:

- mux creation
- route registration entrypoint
- HTTP middleware such as CORS
- address selection helpers

`server/` should not contain domain request handling logic.

### `api/`

Owns transport-facing HTTP behavior:

- request decoding
- response encoding
- HTTP status selection
- path and method dispatch
- generated API-specific DTOs

Domain transport support should live under its domain package, for example:

- `api/workspace/types.go`

The `api/` layer may depend on:

- `service/`
- domain-local DTOs
- shared helpers from `types/`

The `api/` layer must not depend on concrete persistence details except for narrow sentinel error mapping where needed.

### `service/`

Owns use-case orchestration:

- business workflow sequencing
- validation that belongs to domain behavior
- translating between domain models and API DTOs
- calling persistence and other configured collaborators

`service/` should not perform direct SQL or HTTP response writing.

#### Agent service composition

The `service/agent` facade is constructed from one responsibility-grouped
`ServiceConfig`. Production wiring must resolve canonical/runtime ports,
provider preparation, query/projection, composer, import, resource, and
observer dependencies before calling `NewService`; it must not fill Service
fields or install an application Host afterward.

`packages/agent/host` remains the lifecycle owner. Its tuttid support ports are
narrow components created from the completed config and must not retain the
complete Service facade. A support component may share a lock, cache, runtime
preparer, or observer registry with Service. Read-only canonical seams are
allowed only when their lifecycle ownership is explicit; the Session Fork
runtime-preparation seam reads lineage that can exist only after commit and
never performs a lifecycle write.

### `biz/`

Owns small, transport-agnostic domain models and domain rules that need to be shared across layers.

Use `biz/` when:

- both `service/` and `data/` need the same domain object
- the type should not live in `api/`
- the type is still domain-local rather than global

Example:

- `biz/workspace/model.go`

Do not turn `biz/` into a giant dumping ground. Keep it domain-scoped and intentionally small.

### `data/`

Owns concrete persistence adapters:

- SQLite access
- migrations
- local file-backed repositories when they belong to persistence

`data/` should depend on:

- `biz/`
- minimal shared helpers from `types/`

`data/` must not depend on `api/`.

Within a domain adapter directory, prefer splitting by responsibility:

- `store.go` for interfaces and sentinel errors
- backend implementation files such as `sqlite_store.go`
- `migrations.go` for schema setup

### `integration/`

Owns process-level and cross-layer black-box tests:

- starting a real `tuttid` process
- exercising real HTTP endpoints
- verifying durable state behavior through the public daemon surface
- covering startup, recovery, and other flows that cross `api/`, `service/`, and `data/`

Use `integration/` when a test is no longer about one layer in isolation.
Keep unit and near-layer tests next to the code they exercise; use `integration/` only for daemon-wide behavior.

### `types/`

Owns cross-domain support code only:

- HTTP helpers
- state path helpers
- truly shared primitives

Do not place domain-local request or response DTOs in `types/`.

## Complexity Guidance

Directory and layering rules exist to clarify ownership, not to maximize file count.

When logic is still small, focused, and easy to understand, prefer the narrowest structure that keeps responsibility clear.
Do not split code into multiple files or layers unless the split creates a clearer boundary.

Prefer keeping code together when:

- it still serves one responsibility
- there is only one implementation
- the control flow is easy to follow in one place
- testing and future changes are not being made harder by the current shape

Prefer splitting code when:

- one unit is carrying more than one responsibility
- transport, domain, and persistence concerns are starting to mix
- a separate interface is needed for multiple implementations
- the current file is becoming harder to understand than the boundary you would introduce
- readers need to jump across several thin files to understand one simple flow

Clear boundaries matter more than symmetric directory shapes.

Do not create a full domain slice until that domain has enough real behavior to justify it.

Examples:

- a simple health endpoint does not need a full `runtime` domain
- a small helper does not need its own package
- a domain does not need `api/`, `biz/`, `service/`, and `data/` on day one if only one slice is real

### Rule Of Thumb

When adding new logic, ask:

1. Is this a new responsibility, or just more code for the same responsibility?
2. If I keep this in the current file, does it become confusing?
3. If I split this out, does the new boundary make the code easier to understand, test, or replace?

If the answer to `2` and `3` is "not really", keep it together for now.

## Dependency Direction

Preferred dependency flow:

```text
main
  -> wiring
    -> app
    -> server
    -> api
      -> service
        -> biz
        -> data
          -> biz
    -> types
```

Practical rules:

- `api` can depend on `service`
- `service` can depend on `biz` and `data`
- `data` can depend on `biz`
- `data` must not depend on `api`
- `biz` must not depend on `api`, `service`, or `data`

## Test Placement

Prefer placing tests according to the responsibility they validate:

- keep unit and near-layer tests beside the owning package with `*_test.go`
- keep process-level and cross-layer daemon tests under `integration/`
- use `testdata/` only for fixtures and sample data, not for test logic

Examples:

- `api/daemon_test.go` for generated daemon adapter behavior
- `data/workspace/sqlite_store_test.go` for persistence behavior
- `integration/blackbox_test.go` for real-process daemon regression coverage

## When To Add A New Domain

Create a full domain slice only when a domain has enough real behavior to justify its own boundary.

When a new domain such as `runtime` or `agent` is introduced, follow the same structure:

```text
api/runtime/
biz/runtime/
data/runtime/
service/runtime/
```

Create only the slices that are justified by actual use. Do not pre-create deep empty trees.

## Review Rules

When reviewing `tuttid` changes, ask:

1. Does this code belong to a transport layer, business layer, or persistence layer?
2. Is a domain-local DTO being pushed into global `types/`?
3. Is `data/` accidentally depending on `api/`?
4. Is `wiring.go` staying as composition root instead of becoming a second service layer?
5. Are empty directories being introduced before they have real ownership?
