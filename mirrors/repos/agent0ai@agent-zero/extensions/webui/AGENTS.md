# WebUI Extensions DOX

## Purpose

- Own built-in frontend extension contributions under `extensions/webui/`.
- Keep WebUI extension points compatible with the core loader and plugin extension model.

## Ownership

- Each direct subdirectory is one frontend extension point.
- `.html` files are injected as component references through `<x-extension>`.
- `.js` and `.mjs` files export default functions called by `callJsExtensions`.

## Local Contracts

- HTML contributions must be valid component fragments and include Alpine state only where needed.
- JavaScript extension modules must export a default function.
- Extension code must not assume a plugin is installed unless it guards that dependency.
- Keep extension point names synchronized with `x-extension` IDs and `callJsExtensions()` callers.

## Work Guidance

- Prefer small extension modules that delegate to existing WebUI stores or helpers.
- Use the notification store for user-facing success, warning, or error feedback.
- Avoid global DOM queries when an extension hook provides scoped nodes or context.

## Verification

- Manually load the WebUI or run targeted frontend/WebUI tests after changing visible extension behavior.
- Verify extension cache clearing paths when adding new extension points.

## Child DOX Index

No child DOX files.
