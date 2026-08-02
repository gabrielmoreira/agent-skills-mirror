# Pin to Top Plugin DOX

## Purpose

- Own built-in pinning for chat and scheduled-task rows in the sidebar.

## Ownership

- `plugin.yaml` owns the always-enabled plugin metadata.
- `helpers/pins.py` and `api/` own persistent pin state and authenticated toggle/read endpoints.
- `webui/pin-to-top-store.js` owns row ordering and divider callbacks.
- `extensions/webui/sidebar-row-actions-menu/` owns the dropdown action.

## Local Contracts

- Pin state is separated into `chat` and `task` groups and stored under the `plugin_pin_to_top` persistent KVP key.
- The plugin must register sidebar row-list callbacks; it must not patch chat/task stores or inject controls directly into rows.
- Pinned items sort before unpinned items, older pins remain first, and existing order is preserved within the unpinned group.
- The menu label and icon must reflect whether the active row is pinned.

## Work Guidance

- Keep the plugin always enabled and configuration-free.
- Keep runtime state under `usr/` through the shared persistent KVP helper.

## Verification

- Run `pytest plugins/_pin_to_top/tests tests/test_sidebar_row_actions.py`.

## Child DOX Index

No child DOX files.
