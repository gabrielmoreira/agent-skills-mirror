# What's New Plugin DOX

## Purpose

- Own the built-in version-gated "What's New" modal for showcasing Agent Zero features after updates.

## Ownership

- `plugin.yaml` owns metadata and always-enabled status.
- `webui/main.html` owns the canonical modal opened by startup and the Builtin Plugins `Open` button.
- `webui/whats-new.html` is a compatibility redirect to `webui/main.html`.
- `webui/` owns the Alpine store, copy, and showcase media assets.
- `extensions/webui/initFw_end/` owns the startup trigger that opens the modal once per newer installed version unless the user has permanently opted out.

## Local Contracts

- Closing, Skip, or Done records only the current installed version as seen.
- Future updates should auto-open the modal again unless the user checks the modal's permanent opt-out checkbox.
- The permanent opt-out is stored in browser-local state under `a0_whats_new_never_show`.
- Honor the legacy `a0_whats_new_seen_version` browser-local marker as the last seen version.
- Keep the modal copy concise, left-aligned, and paired with feature media.
- Keep modal actions in the pinned footer using the shared Agent Zero button classes.
- Store seen-version and opt-out markers in browser-local state only; do not persist this under `usr/`.

## Work Guidance

- Add showcase assets under `webui/assets/` and reference them through `/plugins/_whats_new/webui/assets/...`.
- Keep the startup extension idempotent and tolerant of missing or non-comparable version labels.
- Prefer release-line comparisons over development commit-distance comparisons so local development builds do not reopen the modal on every commit.
- Preserve `webui/main.html` so the plugin list exposes the standard `Open` action.

## Verification

- Run `pytest tests/test_whats_new_static.py` after changing the modal, trigger, or assets.
- Smoke-test startup display, slide navigation, dismissal, same-version reload behavior, newer-version display behavior, opt-out behavior, and manual Builtin Plugins `Open` behavior in the WebUI.

## Child DOX Index

No child DOX files.
