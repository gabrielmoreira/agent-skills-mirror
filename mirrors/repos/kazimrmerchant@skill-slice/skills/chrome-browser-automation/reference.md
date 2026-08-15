# Chrome Browser Automation — reference

Deep operational reference. Recipes with full code live in
[playwright-cdp-recipes.md](playwright-cdp-recipes.md) (referenced as R1…R24).
Facts are marked **verified** (confirmed on this machine / in `browser-connection` v3.0.0,
2026-07-15) or **hedged** (correct per Playwright/CDP docs as of Jan-2026 knowledge, not yet
exercised on this machine — confirm on first live use and update §15).

---

## §1 Environment & prerequisites

- **OS:** Windows 11, PowerShell primary. Always invoke scripts as
  `powershell -NoProfile -ExecutionPolicy Bypass -File "<path>"`.
- **Node + Playwright cwd (verified):** run Node recipe scripts from a directory that has
  `playwright` installed. Known-good: `~\.cursor\skills\grok-imagine\scripts`.
  Pattern: write your `.mjs` to a temp file, `Set-Location` to the known-good cwd, `node <temp>.mjs`.
  Do **not** `npm init` new throwaway projects for one-off scripts; reuse the known cwd.
- **No browser install needed.** `connectOverCDP` talks to the already-running branded Chrome;
  `npx playwright install` is unnecessary and must not be used to launch anything.
- **Artifacts:** everything you produce (screenshots, DOM dumps, JSONL, downloads you relocate)
  goes under `~\.cursor\browser-hub\out\`, named
  `<task>-<yyyyMMdd-HHmmss>-<step>.<ext>`. Create subfolders per task for multi-file runs.
- **Reading results:** agents can visually inspect saved PNGs with the file Read tool — the
  screenshot → Read → judge loop is the primary visual-verification mechanism (§9).

## §2 Lifecycle: start → attach → work → teardown

```powershell
# 1. Is CDP up?
powershell -NoProfile -ExecutionPolicy Bypass -File "~\.cursor\browser-hub\scripts\status.ps1"
# 2. If down — the ONLY permitted launch:
powershell -NoProfile -ExecutionPolicy Bypass -File "~\.cursor\browser-hub\scripts\start.ps1"
# 3. If start fails or things look wrong:
powershell -NoProfile -ExecutionPolicy Bypass -File "~\.cursor\browser-hub\scripts\doctor.ps1" -Deep
# 4. Never as part of normal teardown; human-approved shutdown only:
#    stop.ps1  — do NOT call while any other agent may be attached.
```

Quick raw probe (no Playwright): `curl.exe -s http://127.0.0.1:9222/json/version` — JSON back
means CDP is up. `/json/list` enumerates targets (inspection only; do not drive tabs via raw
HTTP endpoints — attach properly).

**Teardown semantics (verified in browser-connection):** after `connectOverCDP`, Playwright's
`browser.close()` disconnects the client and does **not** quit the real Chrome (it only tears
down contexts Playwright itself created — you created none). Correct teardown is: close your
own pages → `browser.close()`. Actually quitting Chrome is exclusively `stop.ps1` (which uses
raw CDP `Browser.close` then force-kill) and is almost never your job.

## §3 The CDP + Playwright model

```
chromium.connectOverCDP("http://127.0.0.1:9222")   → Browser (the user's real Chrome)
browser.contexts()[0]                              → the ONE default context: all cookies, all identities
context.newPage()                                  → your own tab (the only thing you own)
context.newCDPSession(page)                        → raw CDP for page-level domains (Chromium-only)
browser.newBrowserCDPSession()                     → raw CDP for browser-level domains (hedged; used for downloads §7)
```

Key properties:

- **One context.** All Google/Grok/Flow auth lives in `contexts()[0]`. `newContext()` would be a
  clean-jar incognito-like context with no auth — forbidden and useless here.
- **Trusted input.** `page.keyboard.*` and `page.mouse.*` go through the CDP `Input` domain, so
  the page receives events with `isTrusted: true` — unlike `element.dispatchEvent(...)` from
  `evaluate`, which many games and hardened apps ignore. Prefer keyboard/mouse APIs for games (§10).
- **Main-world evaluate.** `page.evaluate` runs in the page's main world: you can read game
  globals (`window.__game`), canvas pixels, `performance` entries. Content inside cross-origin
  iframes needs `page.frames()` / `frameLocator` (same-process access rules apply).
- **CDP sessions are additive.** Multiple clients (you, other agents, DevTools) can attach
  simultaneously. Don't assume you're alone: never mutate global browser state
  (`Browser.setDownloadBehavior` is the one sanctioned exception, §7, and you must reset it).
- **Locator dialect.** All `getByRole`/`:has-text(...)` guidance from `playwright-test-automation`
  applies verbatim; that skill is the authority on locator strategy, auto-waiting semantics, and
  flake diagnosis. Don't duplicate it — load it when writing anything selector-heavy.

## §4 Tab & window management

- **Own-tab discipline (verified rule):** open with `context.newPage()`, track every page you
  open in an array, close them all in `finally`. Never touch `context.pages()` entries you did
  not create — the user's tabs and other agents' tabs live there.
- **Inspection is allowed, control is not:** reading `context.pages().map(p => p.url())` to
  understand browser state is fine (status.ps1 does this); navigating/closing them is not.
- **Popups:** a link with `target=_blank` or `window.open` from *your* tab produces a page you
  do own. Capture it with `page.waitForEvent('popup')` *registered before the click* (R5).
  Close popups you spawned.
- **Tab budget:** keep ≤ 4 concurrent own tabs (fan-out recipes R4 chunk work in batches).
  Long-running agents must not accrete `about:blank` zombies — doctor GC exists but don't rely on it.
- **New windows vs tabs:** `context.newPage()` may open as a tab in the user's current window.
  That's acceptable; do not try to create separate OS windows or move tabs between windows.
- **Site locks (verified):** for sites with per-session stateful UI (one composer, one editor —
  e.g. grok.com), acquire the per-hostname advisory lock: `attachHub({ siteLock: true })` or
  `acquireSiteLock("<hostname>")` from `connect.mjs`. Lock files live in `browser-hub\locks\`;
  stale after ~minutes. If a lock is held and fresh: wait or report — never barge.

## §5 Navigation & waiting

Default navigation pattern:

```js
await page.goto(url, { waitUntil: "domcontentloaded", timeout: 45_000 });
await page.locator("<thing the task actually needs>").first().waitFor({ state: "visible", timeout: 20_000 });
```

- **Anchor on the task's element, not on load states.** `domcontentloaded` fires early on SPAs;
  `load` waits for images you may not need; `networkidle` is a **trap** on modern apps
  (analytics/websockets/polling keep the network busy forever — it times out and masks the real
  problem). Reserve `networkidle` for static/legacy multipage sites only.
- **Response-gated actions:** when a click triggers an API call, register
  `page.waitForResponse(predicate)` *before* the click and await both (R6). Predicate on URL
  **and** `resp.ok()` — a 500 also "responds".
- **Polling for non-DOM conditions:** a small `poll(fn, {timeout, interval})` helper (R7) covers
  "job status flipped", "file appeared", "game score changed". Exponential-ish intervals: start
  at ~5–10 % of expected duration.
- **Bounded sleeps:** allowed only for animation settling ≤ ~300 ms, with a comment naming the
  animation. Anything longer means you're missing a signal — find one.
- **SPA route changes** don't fire `goto`-style navigation; wait on the destination view's
  element, or on `page.waitForURL(/pattern/)` which handles history.pushState.

## §6 Network observation & interception rules

- **Observe freely on your own page:** `page.on('response')`, `page.on('requestfailed')`,
  `page.waitForResponse` — read-only, zero blast radius. Harvest JSON API payloads from
  responses instead of scraping DOM when the app has a clean XHR (R6 variant) — sturdier and cheaper.
- **Intercept only on your own page:** `page.route(...)` is scoped to your tab — acceptable for
  blocking third-party noise (analytics, ads) that slows automation (R8). Always
  `page.unrouteAll()` in teardown.
- **NEVER `context.route(...)` on the shared default context.** It would intercept the user's
  and other agents' tabs and outlives your task. This is a safety rule, not a style preference
  ([safety-rules.md](safety-rules.md) §5).
- **No request forgery:** don't rewrite request bodies/headers to impersonate app behavior on
  authenticated sites; observation and noise-blocking only. Mock-heavy work belongs in test
  suites (`playwright-test-automation`), not in the live authed browser.
- **HAR capture:** for debugging a gnarly flow, collect `{url, status, type}` tuples from
  `page.on('response')` into a JSONL artifact instead of full HAR (full HAR on an authed browser
  captures cookies/tokens — avoid; see safety-rules §6).

## §7 File downloads (three-tier strategy)

Downloads on a CDP-attached *real* Chrome are the least standardized part of this stack. Use the
tiers in order; each has a recipe.

- **Tier 1 — Playwright download event (R9, hedged):** register
  `page.waitForEvent('download')` before the triggering click; `download.saveAs(target)`.
  On attached real Chrome this works in current Playwright versions, but historically
  `download.path()`/`saveAs` had gaps over `connectOverCDP`. If `saveAs` throws or hangs → Tier 2.
- **Tier 2 — CDP `Browser.setDownloadBehavior` + directory watch (R10, hedged):** via
  `browser.newBrowserCDPSession()`, set
  `{ behavior: 'allow', downloadPath: '<abs path under out\\downloads>', eventsEnabled: true }`,
  trigger, then either consume `Browser.downloadWillBegin`/`Browser.downloadProgress`
  (state `completed`) or poll the directory. **Must reset** `{ behavior: 'default' }` in
  teardown — this is browser-global state on the user's Chrome.
- **Tier 3 — watch the real Downloads folder (R11, always works):** Chrome's default is
  `~\Downloads`. Snapshot the dir before the click, poll for a new file, wait for
  its `.crdownload` twin to disappear and size to stabilize, then **move** it to `out\downloads\`.
  Ugly but dependency-free.

Completion criteria regardless of tier: no `.crdownload` sibling, size stable across two polls
1 s apart, and (when format is known) the file parses — a 0-byte or HTML-error-page "CSV" is a
failure, not a success (E3).

## §8 File uploads

- Standard `<input type=file>` (even visually hidden): `locator.setInputFiles(absPath)` (R12).
- Drop-zone-only UIs: most frameworks still mount a hidden input —
  `page.locator('input[type=file]').setInputFiles(...)` first; synthetic `drop` event with a
  constructed `DataTransfer` as fallback (pattern in `playwright-test-automation` §Advanced).
- **Never** upload files outside the task's scope; never upload anything from `out\` containing
  another task's data. Absolute Windows paths; forward slashes are fine in Node.

## §9 Screenshots & visual verification

- **Primary loop (verified as agent-native):** `page.screenshot({ path })` →
  agent Reads the PNG → judges against the expectation → iterates. Full page:
  `{ fullPage: true }`; element: `locator.screenshot()`; region:
  `{ clip: await locator.boundingBox() }`.
- Naming: `out\<task>\shot-<step>-<HHmmss>.png`. Keep every iteration; they are the audit trail.
- **Stability before shooting:** wait for the anchor element, then ~150–300 ms for CSS
  transitions (commented bounded sleep is acceptable here), or wait for
  `document.fonts.ready` via evaluate when typography matters.
- **Programmatic diff (R14, hedged):** for tight iteration loops, a buffer-equality or
  coarse pixel-sample diff via `evaluate`/Node is enough to detect "changed at all";
  do not build a baseline-comparison system here — that's `toHaveScreenshot` territory in
  `playwright-test-automation`, and `ui-visual-fidelity-audit` owns aesthetic judgment.
- Mask/crop dynamic regions (clocks, avatars) by clipping to the region under test instead of
  full-page shots.
- **Privacy:** full-page shots of authed apps can capture emails, tokens in URLs, personal data.
  Keep under `out\`, never publish or upload; crop when sharing in reports (safety-rules §6).

## §10 Game & canvas testing

Canvas apps (HTML5 games, WebGL, PixiJS/Phaser/Three.js, Godot HTML5 exports) have **no DOM
inside the canvas** — locators see one `<canvas>` element and nothing else. Different toolkit:

### 10.1 Serving & loading
- Games must load over **http://**, not `file://` (module scripts, fetch, audio contexts fail on
  file). Serve local builds: `npx http-server -p 8080 .` or `python -m http.server 8080` in the
  build dir, then drive `http://localhost:8080` in your own tab. localhost is green-tier.
- Godot HTML5/itch-style embeds often nest the game in an **iframe** — get the frame via
  `page.frames()` / `frameLocator('iframe')` before anything else; input must target the frame's
  canvas.

### 10.2 Input
- **Focus first.** Click the canvas center once before any keyboard input — unfocused canvas
  swallows keys silently (top game-testing failure mode).
- **Held keys:** `page.keyboard.down('ArrowRight')` … `await page.waitForTimeout(ms)` …
  `page.keyboard.up('ArrowRight')` — games read key state per frame; a `press` (down+up in one
  tick) often registers as nothing. This is the sanctioned use of small sleeps: they express
  *hold duration*, not waiting.
- **Mouse in canvas coordinates:** compute from `canvas.boundingBox()` —
  `page.mouse.click(box.x + relX * box.width, box.y + relY * box.height)` with rel coords in
  0..1 so resizes don't break the script (R16).
- Trusted-event note from §3 applies: keyboard/mouse APIs produce `isTrusted` events; games that
  gate on user gestures (audio unlock, pointer lock) accept them. `dispatchEvent` usually fails.
- **Gamepad** is not emulatable via Playwright input APIs; test keyboard/mouse paths, note the gap.

### 10.3 Reading game state (in reliability order)
1. **Debug hooks (best):** if you control the game code, expose `window.__game = { score, state,
   entities, fps }` behind a `?test=1` flag and read via `evaluate`. Compose with
   `game-debugging` / dev-side skills to add hooks rather than divining pixels.
2. **DOM HUD:** many games render score/menus as DOM overlays — normal locators work on those.
3. **Screenshots:** `locator('canvas').screenshot()` captures via the compositor and works for
   **both** 2D and WebGL regardless of buffer settings — the default probe.
4. **Pixel reads via evaluate (R18):** 2D canvas — `getContext('2d').getImageData(...)`.
   **WebGL gotcha (verified pattern):** `toDataURL()`/`readPixels` outside the frame callback
   returns blank unless the context was created with `preserveDrawingBuffer: true`; when you
   can't change that, use the screenshot path (3) instead.

### 10.4 Performance & stability probes
- **FPS:** inject a `requestAnimationFrame` counter for N seconds via `evaluate` (R17); report
  min/avg. Note the hub Chrome is headful on a real desktop — background tabs are throttled, so
  bring your tab to front (`page.bringToFront()`) before sampling.
- **Errors:** collect `console`/`pageerror`/`requestfailed` from load onward (R19) — a game that
  "plays fine" while spraying per-frame errors fails review.
- **Long sessions:** watch for WebGL context loss (`webglcontextlost` listener via evaluate) and
  heap creep (`performance.memory.usedJSHeapSize` — Chrome-only, fine here) sampled per minute.
- **Determinism:** games are RNG + real-time; assert on *invariants* (score is a number and
  non-decreasing; player sprite moved after input; no errors; FPS ≥ threshold) rather than exact
  states. Fixed seeds require a debug hook (10.3.1).
- Full release verdicts (aesthetics, juice, loop completeness) are `web-game-release-review`'s
  job — this skill supplies its live-browser evidence: input probes, screenshots, FPS, console log.

## §11 Console, error & diagnostics collection

Attach collectors immediately after opening your page, assert at the end (full code R19):

- `page.on('console')` — filter `type() === 'error'`, keep an explicit ignore-list (favicon,
  ResizeObserver noise) so real errors aren't drowned.
- `page.on('pageerror')` — uncaught exceptions; almost always job-relevant.
- `page.on('requestfailed')` — include method + URL + `failure().errorText`.
- On any failure: screenshot + `page.content()` dump to `out\` **before** re-raising (R23) —
  unattended runs die silently otherwise.

## §12 Failure taxonomy → recovery matrix

| Symptom | Likely cause | Recovery |
|---------|--------------|----------|
| `connectOverCDP` ECONNREFUSED / fetch fail | Chrome not running / CDP off | `start.ps1` → retry once → `doctor.ps1` → report if still down |
| CDP up but `contexts()` empty or weird | Race during Chrome startup | wait 2 s, reconnect; then doctor |
| `Target closed` / `Target crashed` mid-task | Tab crashed (OOM, GPU) | close handle, fresh `newPage()`, re-navigate, resume from last checkpoint; second crash on same URL → report with artifacts |
| Navigation timeout | Slow site / wrong wait anchor | retry once with `domcontentloaded` + element anchor; capture screenshot on second failure |
| Element never appears | Selector drift / wrong page state / signed out | screenshot + DOM dump; check signed-in signals before blaming selectors (browser-connection: wrong-account and signed-out mimic "broken page") |
| Click does nothing | Overlay/consent dialog, unfocused canvas, wrong frame | screenshot; look for dialogs/cookie banners (dismiss within your tab is fine); games → refocus canvas |
| Download never completes | Tier mismatch / blocked | escalate Tier 1→2→3 (§7); check `chrome://downloads` is NOT the tool — stay in your tab; report if site requires interaction you can't verify |
| Signed out / login wall | Session expired | **STOP.** Report site + identity per `browser-connection`; human signs in via hub window. Never credentials/2FA |
| CAPTCHA / bot-wall | Site defense | **STOP.** Screenshot, report. Never bypass (safety-rules §4) |
| Lock file held & fresh | Another agent mid-flow on that host | wait (poll ≤ 5 min) or report; never delete a fresh lock |
| Playwright module not found | Wrong cwd | run from known-good cwd (§1) |
| Everything weird at once | Hub state drifted | `doctor.ps1 -Deep`, attach its output to your report; do not improvise browsers |

Retry policy: **one** automatic retry per failure class with a changed hypothesis; after that,
capture diagnostics and report. Blind retry loops on an authed browser are how agents historically
made messes on this machine.

## §13 Artifacts & logging conventions

```
$env:BROWSER_HUB\out\
  <job-slug>\
    shot-*.png            # every visual checkpoint
    dom-*.html            # failure DOM dumps
    net-*.jsonl           # response tuples when network-debugging
    downloads\            # relocated downloads (Tier 1–3)
    result.json           # machine-readable task outcome
    run.log               # one line per step: ts, action, outcome
```

Every task that changes anything or gathers evidence leaves `result.json` + at least one
screenshot. Clean up `downloads\` staging only; never delete other tasks' folders.

## §14 PowerShell orchestration snippets

Write-and-run a recipe (the standard invocation shape):

```powershell
$scriptDir = "~\.cursor\skills\grok-imagine\scripts"   # known-good playwright cwd
$tmp = Join-Path $env:TEMP ("cba-" + [guid]::NewGuid().ToString("N") + ".mjs")
Set-Content -LiteralPath $tmp -Value $mjsSource -Encoding UTF8      # UTF-8, no BOM issues for .mjs
Push-Location $scriptDir
try   { node $tmp; $code = $LASTEXITCODE }
finally { Pop-Location; Remove-Item -LiteralPath $tmp -ErrorAction SilentlyContinue }
if ($code -ne 0) { throw "recipe failed with exit $code" }
```

Serve a local game build:

```powershell
Push-Location "C:\path\to\game\build"
Start-Process -PassThru npx -ArgumentList "http-server","-p","8080","-s" | Tee-Object -Variable server
# ... drive http://localhost:8080 ... then:
Stop-Process -Id $server.Id   # your server, your process — narrow kill only
Pop-Location
```

Poll for a downloaded file:

```powershell
$dl = "~\Downloads"
$before = Get-ChildItem $dl -File | Select-Object -Expand Name
# ... trigger download in browser ...
do { Start-Sleep 1; $new = Get-ChildItem $dl -File | Where-Object { $_.Name -notin $before -and $_.Extension -ne ".crdownload" } } until ($new)
Move-Item $new.FullName "~\.cursor\browser-hub\out\<task>\downloads\"
```

## §15 Verified vs hedged log

| Claim | Status | Evidence / next check |
|-------|--------|------------------------|
| CDP 9222, UserData path, start/stop/doctor/status behavior | **verified** | browser-connection v3 (2026-07-15) |
| `attachHub` options `{url,newPage,ensureStart,siteLock}`, `closeOwnPage()`, `acquireSiteLock()` | **verified** | browser-connection SKILL + reference |
| Exact `attachHub` return shape | hedged | log `Object.keys()` on first use; update R1 |
| `browser.close()` after connectOverCDP disconnects without quitting Chrome | **verified** | browser-connection reference (bug log #3) |
| Trusted input via CDP Input domain | high-confidence | Chromium behavior; confirm on first game-gesture task |
| Tier-1 Playwright download over connectOverCDP | hedged | try first; fall to Tier 2/3 |
| `Browser.setDownloadBehavior` semantics + events | hedged | CDP protocol docs; reset to `default` after use |
| WebGL blank-read without `preserveDrawingBuffer` | high-confidence | standard WebGL semantics; screenshot path immune |
| Known-good playwright cwd (grok-imagine scripts) | **verified** | browser-connection SKILL |

On first live confirmation of a hedged row, flip it to verified with a date — same convention as
`grok-x-platform` reference §6.
