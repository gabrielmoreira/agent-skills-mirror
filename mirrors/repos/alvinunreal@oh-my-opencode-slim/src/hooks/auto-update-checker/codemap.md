# src/hooks/auto-update-checker/

## Responsibility

- Provide a startup hook that detects plugin update availability for `oh-my-opencode-slim`, reports status through TUI toasts, and optionally performs a cache-safe `bun install` refresh.
- Handle local dev mode and pinned plugin versions distinctly (`file://`, pinned tags, and `latest` channel semantics).

## Design

- `createAutoUpdateCheckerHook(ctx, options)` in `index.ts` registers an `event` handler for `session.created` and guards one-time startup execution (`hasChecked`).
- `runBackgroundUpdateCheck` performs version resolution and branches into:
  - local-dev no-op path,
  - pinned plugin notification,
  - manual notification when `autoUpdate=false`,
  - or auto-update execution path.
- `checker.ts` is the core discovery layer and exports:
  - `findPluginEntry`, `extractChannel`, `getCachedVersion`, `getLocalDevVersion`, `getLatestVersion`, `updatePinnedVersion`.
- `cache.ts` owns cache preparation with `resolveInstallContext` and `preparePackageUpdate`.
- `constants.ts` centralizes install and config-path constants (`CACHE_DIR`, `PACKAGE_NAME`, `NPM_REGISTRY_URL`, `NPM_FETCH_TIMEOUT`, config path aliases).
- `types.ts` declares `AutoUpdateCheckerOptions`, `PluginEntryInfo`, config/package typed envelopes.

## Flow

1. On first eligible `session.created` (root/no parent), schedule asynchronous update check.
2. If local development plugin is detected (`getLocalDevVersion`), emit info toast and return.
3. Resolve current version from `getCachedVersion` + plugin entry in config (`findPluginEntry`).
4. Fetch channel metadata (`extractChannel` + `getLatestVersion`).
5. If update is needed:
   - pinned entry ⇒ notify only,
   - unpinned and `autoUpdate=false` ⇒ notify only,
   - unpinned and auto-update enabled ⇒ call `preparePackageUpdate`, then `runBunInstallSafe`.
6. Surface success/failure via `ctx.client.tui.showToast` and `utils/logger`.

## Integration

- Wired through `src/hooks/index.ts` and plugin initialization (`src/index.ts`) as an `event` hook.
- Consumes `PluginInput.client.tui.showToast`, `PluginInput.directory`, `ctx.client` context, and reads config paths through `cli/config-manager` (`stripJsonComments`, `getOpenCodeConfigPaths`).
- Runtime interactions use `crossSpawn` for `bun install`, Node `fs/path`, and `fetch` against `NPM_REGISTRY_URL`.
- Export surface includes `getAutoUpdateInstallDir` and `AutoUpdateCheckerOptions` for testability and host-side overrides.
