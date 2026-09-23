---
name: opencode-v2
description: Load for any work that touches OpenCode — its routes, events, message or session shapes, plugins, the pinned CLI/client version, "what's new in OpenCode 2.0.x", or a bug that looks like OpenCode behaving differently than OpenChamber expects. OpenChamber runs on OpenCode 2.x since 2026-09; 1.x code paths are gone.
---

# OpenCode 2.x in this repository

OpenChamber moved from the OpenCode 1.x API to 2.x in one cutover (PR #3837,
2026-09). Everything OpenCode-facing speaks 2.x: routes under `/api/*`, one
global `/api/event` stream of `session.*` events, sessions as cursor-paged
lists, messages with their parts inline, plugins hot-reloaded from watched
config, `@opencode/client` + `@opencode/schema` as the only SDK. A bug report
that mentions 1.x behaviour (`/session` without `/api`, `message.updated`
events, `auth.json`, `@opencode-ai/sdk`) describes the old world; answer from
the 2.x code, not from memory of 1.x.

## Where the boundary lives

- `packages/ui/src/lib/opencode/client.ts` — every official OpenCode call the
  shared UI makes; `projection.ts` turns wire shapes into the OpenChamber
  domain model in `model.ts`; `events.ts` translates wire events. These three
  files are the only place that knows 2.x wire shapes. Rendering and stores
  read the domain model; fix a missing field there, never with a shim.
- `packages/web/server/lib/opencode/proxy.js` forwards `/api/*` as-is (2.x
  serves under `/api` itself) and folds OpenChamber-owned session state into
  the records it serves. `env-runtime.js` launches `opencode serve`.
- Plugins OpenChamber generates for OpenCode: `plugin-spec.js` and
  `agent-tool/runtime.js`, declared through the watched
  `<dataDir>/opencode.managed.json` (`OPENCODE_CONFIG`), so a settings change
  applies without a restart. Only the binary, port and external toggle restart.

## Workarounds for what 2.x cannot do

Each exists because 2.x has no route for it. When a tag adds the route,
the workaround goes and the record comes from OpenCode.

- **Archive and OpenChamber session metadata** (review/btw links, linked
  issues, goals): 2.x accepts metadata only on create and has no archive
  route. `openchamber-sessions/` keeps both per data dir; the proxy folds
  them into session reads and the UI writes through
  `/api/openchamber/sessions/*`.
- **Provider credentials**: not readable over HTTP. `credential-db.js` reads
  OpenCode's own SQLite `credential` table read-only, `auth.json` as legacy
  fallback. Private schema: re-verify on every bump.
- **1.x sessions created after the one-shot migration**:
  `v1-migration-topup.js` rewinds the migration cursor before a managed start,
  only when no revisited session has 2.x activity.
- **Error bodies**: the generated client drops the body of an HTTP status a
  route does not declare, so session update/delete/archive report the status
  without OpenCode's message or log `ref`.

Open asks upstream (OpenCode Slack): session metadata PATCH, credential read
over HTTP, an import route for missing 1.x sessions, declaring 500 bodies on
session mutations. Check the newest tag before re-asking.

## Sources of truth

- Reference checkout `~/projects/opencode`, branch `origin/v2` and its
  `v2.x.y` tags (`git fetch origin --tags` there; never edit it). Server
  behaviour: `packages/core/src`, HTTP surface: `packages/server/src/handlers/*`,
  wire types: `packages/schema/src`, `packages/protocol/src/groups`.
- Pinned version: `opencodeCli.version` in `packages/electron/package.json`
  (the bundled binary) and `@opencode/client` / `@opencode/schema` in the
  root, ui, web and vscode manifests, plus `@opencode/cli@` in the
  Dockerfile. They move together.

## "What's new in OpenCode 2.0.x?"

Answer from the diff. Done when every API-facing change between the pinned
tag and the newest tag is classified.

1. In the reference checkout: `git fetch origin --tags`, pinned = `opencodeCli.version`,
   newest = `git tag -l 'v2.*' | sort -V | tail -1`, then
   `git diff --stat vPINNED..vNEWEST -- packages/schema/src packages/protocol/src packages/server/src packages/client packages/plugin/src`. Ignore `packages/tui`, `packages/app`, `packages/web`.
2. Classify each change to a route, event, schema or plugin hook:
   **breaks us** (name the consuming OpenChamber file), **fixes a workaround**
   (name the one above that can go and what the user gains), **closes an open
   ask**, or **neutral**.
3. Report in that order with the maintainer's decisions explicit: remove,
   adopt, still ask.

## Bumping the pinned OpenCode

Move every pin to the same tag and check out that tag in the reference
checkout (`git checkout vX.Y.Z` in `~/projects/opencode`), `bun install`, then `tsc` in `packages/ui`,
`packages/web`, `packages/vscode`; the isolated ui suites; web vitest; vscode
tests. A new message `type` or event needs a case in `model.ts` and
`events.ts` before it renders. Verify `@opencode/cli@<tag>` exists on npm:
the desktop packaging and the Docker image install it.
