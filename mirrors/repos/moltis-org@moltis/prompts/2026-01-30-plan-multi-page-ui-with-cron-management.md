# Plan: Multi-Page UI with Cron Management

## Overview

Convert the single-page web UI into a multi-page SPA with client-side routing (history.pushState), add a burger menu for navigation, and build a `/crons` page for viewing/editing/deleting cron jobs.

## Changes

### 1. `crates/gateway/src/server.rs` — SPA fallback route

Replace the explicit `GET /` route with a fallback handler so `/`, `/crons`, `/methods`, and any future routes all serve `index.html`. Asset routes (`/assets/*`, `/ws`, `/health`) remain explicit and take priority.

### 2. `crates/gateway/src/assets/index.html` — Shell restructure

- Add burger menu button (hamburger icon) left of the "moltis" title
- Add burger dropdown `<nav>` with links: Chat `/`, Crons `/crons`, Methods `/methods`
- Wrap the chat column + methods panel in a `<div id="pageContent">` container
- Sessions sidebar stays outside `pageContent` (persists across pages)

### 3. `crates/gateway/src/assets/app.js` — Router + pages

**Minimal router** (~30 lines): `registerPage(path, init, teardown)`, `navigate(path)`, `mount(path)`, `popstate` listener. No library needed.

**Chat page** (`/`): Extract current chat column DOM creation into `registerPage("/", init, teardown)`. All existing chat logic stays, just moved into the init callback.

**Methods page** (`/methods`): Move methods explorer from header-toggled sidebar to its own page.

**Crons page** (`/crons`): New page with:
- **Status bar**: running state, job count, enabled count, next run time (calls `cron.status`)
- **Job list table**: name, human-readable schedule, enabled toggle, next run, last status badge, actions (edit/delete/run-now/history)
- **Add/Edit modal**: name, schedule type picker (At/Every/Cron) with appropriate inputs, payload type (SystemEvent/AgentTurn), session target, delete-after-run, enabled
- **Run history panel**: shown when clicking history on a job, calls `cron.runs`, shows recent runs with time/status/duration/error

**Burger menu**: toggle on click, close on outside click or navigation. Highlight active page.

**WS sharing**: Connection stays alive across page transitions (no reload). Chat events guarded to only process when chat page is mounted.

### 4. `crates/gateway/src/assets/style.css` — New component styles

Add to `@layer components`:
- `.burger-btn`, `.burger-menu`, `.burger-menu a` — hamburger button and nav dropdown
- `.cron-status-bar` — top status row
- `.cron-table`, `.cron-table th/td` — job list
- `.cron-toggle` — enabled/disabled switch
- `.cron-badge.ok/.error/.skipped` — status badges
- `.cron-modal` — add/edit form (reuses provider-modal pattern)
- `.cron-runs`, `.cron-run-item` — run history

## Verification

1. `cargo check` — compiles
2. `cargo test -p moltis-gateway` — existing tests pass
3. Manual: open `http://localhost:PORT/`, verify chat works as before
4. Manual: click burger → Crons, verify `/crons` URL and page renders
5. Manual: on crons page — add a job, see it in list, toggle enabled, edit, delete, run now, view history
6. Manual: browser back/forward navigation works between pages
7. Manual: sessions sidebar works on all pages
