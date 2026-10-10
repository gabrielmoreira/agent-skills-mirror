---
description: >-
  How to run the end-to-end suites: the WDIO and tauri-driver harness, a spec
  locally or in Docker, the environment variables, and which lanes run in CI.
icon: vials
---

# E2E testing

End-to-end coverage runs in three lanes: a Rust mock-backend suite, a Playwright web suite, and a desktop suite driven through `tauri-driver`. Only the Linux desktop harness runs in CI. macOS and Windows are manual.

## Overview

Desktop E2E tests use WebDriverIO (WDIO) to drive the app through a single `tauri-driver` (WebDriver) session against its native Wry/WebKit webview:

| Platform  | Driver                         | Port | App format   | Selectors |
| --------- | ------------------------------ | ---- | ------------ | --------- |
| Linux     | tauri-driver + WebKitWebDriver | 4444 | Debug binary | CSS / DOM |

Linux CI drives the debug binary under Xvfb through `tauri-driver`. macOS and Windows have no automated desktop E2E coverage yet. The Chromium-based driver they used is gone, and a native driver (Appium Mac2 on macOS, WinAppDriver on Windows) would have to replace it. `pnpm --filter openhuman-app test:e2e:build` still produces a `.app` bundle on macOS for manual testing, but there is no supported automated session there.

---

## Quick start

### Linux

```bash
# Build the E2E app
pnpm --filter openhuman-app test:e2e:build

# Run every spec in one shared tauri-driver session
pnpm --filter openhuman-app test:e2e:session

# Run all flows, sharded by suite category
pnpm --filter openhuman-app test:e2e:all:flows

# Run a single spec
bash app/scripts/e2e-run-spec.sh test/e2e/specs/smoke.spec.ts smoke
```

`app/scripts/e2e-run-session.sh` starts `tauri-driver` on `TAURI_DRIVER_PORT`
(default `4444`) with `WebKitWebDriver` as its native driver, waits for its
`/status` endpoint, then runs WDIO against `app/test/wdio.conf.ts`. On
headless Linux the app itself runs under Xvfb for a virtual display; the
driver process does not need one.

### Docker on macOS (Linux harness locally)

To run the same Linux harness from macOS, use Docker.

```bash
# Build and run all E2E flows
docker compose -f e2e/docker-compose.yml run --rm e2e

# Build the app first (if needed)
docker compose -f e2e/docker-compose.yml run --rm e2e \
  pnpm --filter openhuman-app test:e2e:build

# Run a single spec
docker compose -f e2e/docker-compose.yml run --rm e2e \
  bash app/scripts/e2e-run-spec.sh test/e2e/specs/smoke.spec.ts smoke
```

Requires Docker Desktop or Colima. The repo is bind-mounted so builds persist between runs.

---

## Architecture

### Platform detection

`app/test/e2e/helpers/platform.ts` exports two functions, both hardcoded to `true`: `isTauriDriver()` and `supportsExecuteScript()`. Every session exposes the webview DOM and supports `browser.execute()`, so specs that still branch on either check always take the DOM path. Treat them as compatibility shims, not as platform detection.

### Element helpers

`app/test/e2e/helpers/element-helpers.ts` provides one API over the webview DOM:

| Helper                    | Behavior                                     |
| ------------------------- | -------------------------------------------- |
| `waitForText(text)`       | XPath over DOM text content                  |
| `waitForButton(text)`     | `button` / `[role="button"]` XPath           |
| `clickText(text)`         | Standard `el.click()`                        |
| `clickNativeButton(text)` | Standard `el.click()` on button              |
| `clickToggle()`           | `[role="switch"]` / `input[type="checkbox"]` |
| `waitForWindowVisible()`  | Window handle check                          |
| `waitForWebView()`        | `document.readyState` check                  |
| `hasAppChrome()`          | Window handle check                          |
| `dumpAccessibilityTree()` | HTML page source                             |

### Stable test IDs

Prefer stable `data-testid` hooks for UI affordances that E2E specs click or poll. Use the taxonomy `<surface>-<element>-<id?>`, for example:

- `cron-jobs-panel`, `cron-refresh`
- `cron-job-row-<jobId>`, `cron-job-toggle-<jobId>`, `cron-job-run-<jobId>`, `cron-job-view-runs-<jobId>`, `cron-job-remove-<jobId>`
- `settings-nav-<routeId>`
- `skill-row-<skillId>`, `skill-install-<skillId>`, `skill-uninstall-<skillId>`
- `thread-row-<threadId>`, `new-thread-button`, `send-message-button`
- `onboarding-next-button`

Use `waitForTestId(testId)` and `clickTestId(testId)` from `element-helpers.ts` when a spec targets one of these hooks. Keep text selectors for user-visible copy assertions, not row/action discovery.

### Deep link helpers

`app/test/e2e/helpers/deep-link-helpers.ts` handles auth deep links:

- Primary path: `browser.execute(window.__simulateDeepLink(url))`. It works against the webview on every platform tauri-driver supports.
- macOS-only fallbacks: the `macos: deepLink` extension command, then `open -a ...`. CI does not exercise these, because macOS has no automated desktop session.
- Linux has no shell fallback. `xdg-open openhuman://...` needs a `.desktop` file that registers the URL scheme, and the CI container does not have one. If the webview simulate call fails there, `triggerDeepLink` throws immediately.

For release candidates, also run one manual secondary-instance smoke test on Linux
or macOS when you touch single-instance or deep-link startup code. It exercises
`tauri-plugin-single-instance`, which OpenHuman registers with the
`deep-link` feature.

1. Launch OpenHuman normally and leave it running.
2. Trigger `openhuman://auth?token=e2e-token&key=auth` through the OS opener.
3. Confirm the already-running window receives the callback instead of a
   second app instance starting.
4. Confirm the secondary process exits cleanly.

This catches a second instance that starts, or exits with an
error, before Tauri's deep-link forwarding path is installed.

### Writing cross-platform specs

1. Use the helpers in `element-helpers.ts`. Never use raw `XCUIElementType*` selectors in specs.
2. Use `clickNativeButton(text)` instead of inline button-clicking code.
3. Use `hasAppChrome()` instead of checking for `XCUIElementTypeMenuBar`.
4. Use `waitForWebView()` instead of checking for `XCUIElementTypeWebView`.
5. For macOS-only tests, use `process.platform` guards or separate spec files.
6. Use `navigateViaHash(route)` for hash routes. It waits for the hash, `document.readyState` and a mounted React root before it returns. After onboarding, `walkOnboarding()` also waits for `#/home` and a Home-page marker before specs navigate elsewhere.

---

## Environment variables

| Variable                    | Default    | Description                                                            |
| --------------------------- | ---------- | ---------------------------------------------------------------------- |
| `TAURI_DRIVER_PORT`         | `4444`     | Port `tauri-driver` listens on; `wdio.conf.ts` connects here           |
| `E2E_MOCK_PORT`             | `18473`    | Mock backend server port                                               |
| `E2E_PORT_BASE`             | unset      | Web lane port block: mock `base`, core `base+1`, web host `base+2`     |
| `OPENHUMAN_WORKSPACE`       | (temp dir) | App workspace directory                                                |
| `OPENHUMAN_SERVICE_MOCK`    | `0`        | Enable service mock mode                                               |
| `OPENHUMAN_E2E_MODE`        | unset      | Enables destructive test-support RPCs; the E2E runner sets this to `1` |
| `OPENHUMAN_E2E_AUTH_BYPASS` | unset      | Enable JWT bypass auth                                                 |
| `DEBUG_E2E_DEEPLINK`        | (verbose)  | Set to `0` to silence deep link logs                                   |
| `E2E_FORCE_CARGO_CLEAN`     | unset      | Force cargo clean before E2E build                                     |

Two web E2E sessions on one machine need separate ports. The lane refuses to start when any of its three ports is already listening. Its readiness probes are ordinary HTTP GETs that another session's mock, core and web host would answer just as happily, and `openhuman-core run` falls back to a neighboring port instead of exiting, so it could stay alive on a port nothing probes. Set `E2E_PORT_BASE` for the build and the run alike. The mock and core ports are compiled into the bundle and cannot be changed afterwards.

```bash
E2E_PORT_BASE=31000 pnpm --filter openhuman-app test:e2e:web
```

---

## CI workflows

### Push / PR checks

The default pull-request gate is `.github/workflows/ci-fast.yml`: quality
checks plus the complete unit-test suites for each changed area. No E2E suite
runs on a pull request to `main`.

`.github/workflows/ci-full.yml` runs on pull requests targeting `release` and
on every push to it, and carries three E2E lanes:

| Lane | Job | Platform |
| --- | --- | --- |
| Rust mock backend | `rust-e2e` | Linux |
| Playwright web | `playwright-e2e` | Linux |
| Desktop | `e2e-desktop`, via `e2e-reusable.yml` | Linux only |

The desktop lane calls the reusable workflow with `run_linux: true`, `run_macos: false` and `run_windows: false`, so only the Linux harness runs. The job's "3 OS" title names the matrix the reusable workflow can run, not the one CI Full asks for.

macOS and Windows desktop E2E therefore have no scheduled coverage on any branch. `.github/workflows/e2e.yml` is a manual dispatch whose `run_macos` and `run_windows` inputs also default to `false`. To get cross-platform desktop signal before a promotion, someone has to opt in. Both stay off until a native driver exists for each platform.

---

## Troubleshooting

### Linux: "WebView not ready" timeout

This usually means `tauri-driver` never reached its `/status` endpoint, or the app crashed before mounting its webview. Use `app/scripts/e2e-run-session.sh`, which starts `tauri-driver` and waits on that endpoint before invoking WDIO, rather than driving the app by hand.

Ensure `DISPLAY` is set and Xvfb is running:

```bash
export DISPLAY=:99
Xvfb :99 -screen 0 1280x1024x24 &
```

Also make sure dbus is running (webkit2gtk needs it):

```bash
eval $(dbus-launch --sh-syntax)
```

### Linux: `tauri-driver` or `WebKitWebDriver` not found

Install `tauri-driver` with `cargo install tauri-driver`, and make sure `WebKitWebDriver` is on `PATH` (on Debian and Ubuntu it ships in `webkit2gtk-driver`) or point `WEBKIT_WEBDRIVER` at its location. `e2e-run-session.sh` defaults to `/usr/bin/WebKitWebDriver`.

### macOS: Deep links not working in `tauri dev`

Deep links require a `.app` bundle. Use `pnpm tauri build --debug --bundles app` instead.

### Docker: Build is slow on first run

The first Docker build compiles Rust and installs the E2E harness dependencies. Subsequent runs use cached layers. Docker volumes cache the Cargo registry and git sources.

## Spec: notifications

The spec `app/test/e2e/specs/notifications.spec.ts` tests notification RPC methods through the in-process core and the Notifications UI page:

- `notification_ingest`, creates a new notification via core RPC
- `notification_list`, verifies the ingested notification is returned
- `notification_mark_read`, marks a notification as read
- `notification_stats`, checks aggregate statistics shape
- UI: Notifications page renders the integration notifications section (`[data-testid="integration-notifications-section"]`)
- UI: Notifications page shows the System Events section (`[data-testid="system-events-section"]`)

Run it with:

```bash
bash app/scripts/e2e-run-spec.sh test/e2e/specs/notifications.spec.ts notifications
```

Both the RPC calls and the UI assertions in this spec run inside the same `tauri-driver` session, which supports `browser.execute()`.

---

## Agent-observable artifact flow

### Starting a composer test

Chat drafts persist per thread. Before a spec types its initial prompt, call
`replaceChatComposerText(input, prompt)` from
`app/test/playwright/helpers/chat-composer.ts`. It selects and deletes the
restored draft, waits for the empty value, types through keyboard events, and
checks the exact prompt. Use `clearChatComposer(input)` when a case needs an
empty composer. These helpers support both textarea and Lexical surfaces.

Cases that exercise draft restoration or append a follow-up should keep their
draft and drive that behavior explicitly. The helper's browser regressions live
in `app/test/playwright/specs/chat-composer-helper.spec.ts`.

For a canonical, inspectable run that drops screenshots, page-source dumps, and mock request logs on disk:

```bash
bash app/scripts/e2e-agent-review.sh
```

Artifacts land in `app/test/e2e/artifacts/<timestamp>-agent-review/`. Full details and the helper API: [`agent-observability.md`](agent-observability.md). Any failing test triggers `wdio.conf.ts`'s `afterTest` hook, which writes `failure-*.png` and `failure-*.source.xml` into the same run dir.

---

## Rust inference provider E2E

These tests (`tests/inference_provider_e2e.rs`) use wiremock to mock HTTP upstreams and require no live LLM API calls. They cover OpenAI-compat chat, Anthropic auth style, per-model temperature suppression, Ollama local provider, and the `/v1` HTTP endpoint auth layer.

```bash
# Local:
bash scripts/test-rust-inference-e2e.sh

# Via Docker (Linux, same image as CI):
docker compose -f e2e/docker-compose.yml run --rm inference-e2e
```

---

## See also

- [Testing strategy](testing-strategy.md): which layer a given test belongs in.
- [Agent observability](agent-observability.md): the artifact flow the review run writes to.
- [Tauri shell](architecture/tauri-shell.md): the Wry webview `tauri-driver` attaches to.
- [Getting set up](getting-set-up.md): toolchain and submodules a local E2E build needs.
