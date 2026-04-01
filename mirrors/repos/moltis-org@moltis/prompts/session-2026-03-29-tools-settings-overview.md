# Session: Settings Tools Overview

## What landed

- Added `Settings -> Tools` in the web UI.
- The page uses `chat.context` plus `node.list` to show the effective tool inventory for the active session and model.
- It surfaces:
  - tool-calling availability
  - active model/provider
  - MCP server state and running MCP tool count
  - execution-route availability, including paired nodes and SSH targets
  - grouped registered tools
  - discovered skills/plugins
- Added a dedicated Tools nav icon in settings and updated nav tests/order assertions.
- Updated docs and README to mention the new inventory view.

## Deliberate scope choice

This does **not** add a new backend-wide tool catalog RPC. The page is intentionally
session-aware because the effective tool set changes with:

- current model/tool-calling support
- session MCP toggle
- connected MCP servers
- available exec routing targets

If a future pass needs a true global catalog for admin/debug use, add a separate
backend method rather than weakening this page's "effective current reality"
semantics.

## Validation

- `biome check --write crates/web/src/assets/js/page-settings.js crates/web/ui/e2e/specs/settings-nav.spec.js`
- `cd crates/web/ui && npx tailwindcss -i input.css -o ../src/assets/style.css --minify`
- `cd crates/web/ui && npx playwright test e2e/specs/settings-nav.spec.js e2e/specs/ssh-settings.spec.js`
