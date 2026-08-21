# langalpha desktop

Electron shell around the hosted web app. It is a **remote-URL wrapper**: the package
contains Electron, `src/`, two local pages and an entry URL, and nothing else. No web
bundle ships with it, so a web deploy never needs a desktop release. The two local
pages are the ones that have to work when the network does not: the OSS server picker
and the outage screen.

> Single source of truth for AI coding agents in `desktop/`. Edit here.

## Why Electron, not Tauri

Both were built and measured. On macOS the performance is comparable, so speed is not
what decided it: what is left is a straight trade of package size and idle memory, where
Tauri wins outright, against engine control and shell cost, where Electron does.

**Engine control is worth more here than it would be in a bundled app.** This wrapper
carries no web bundle, so under Tauri the rendering engine becomes whatever the user's
OS ships. WebView2 on Windows is Chromium and fine; macOS pins to that machine's
WKWebView and Linux to WebKitGTK, for a payload that deploys weekly and cannot be
version-matched to any of them. Electron puts one Chromium inside the package and moves
it on our schedule. For an app that shipped its own bundle this argument would be much
weaker, because engine and payload would be tested as a pair.

**The window chrome is the same point in miniature.** `-webkit-app-region` is a Chromium
property and the whole contract is built on it, five call sites in `web/` plus
`titleBarStyle`. Tauri's `data-tauri-drag-region` would put shell-specific markup into
`web/` for every browser user to download, and put a JS handler back in front of a
decision that is now pure CSS.

**The shell is cheap because it is JavaScript.** Roughly 2000 lines of URL classification
and window policy, with a suite in plain `node --test` over an `electron` stub and no
runtime needed. In Rust that is a toolchain in CI and on every self-hoster's machine, to
host logic that mostly decides whether a URL is ours.

This is the right call for this stage, not a permanent one. The thing that would move it
is the desktop app shipping its own bundle: engine and payload recouple, the argument
above loses most of its force, and ~90 MB of package and the idle memory become the
whole story.

## Commands

```bash
pnpm start                       # run the shell from source (oss defaults → localhost:5173)
pnpm test                        # node:test; pure logic only, no Electron runtime needed
pnpm run preview                 # the shell against a web build that has not deployed yet
pnpm run build                   # unpacked build into dist/<edition>/, fastest way to check packaging
pnpm run dist                    # real installers (dmg + zip on macOS)

DESKTOP_EDITION=saas \
DESKTOP_APP_ORIGIN=https://…  \
DESKTOP_PLATFORM_ORIGIN=https://… pnpm run dist  # a saas package
```

**`pnpm run preview` is how you see a change before it deploys.** A remote-URL shell
loads whatever is *live*, so every frame decision it makes is a reaction to the deployed
bundle rather than to the source in front of you: that is how the window buttons ended up
on the app's own logo, and it is where the console's second window was caught before it
reached anyone. It builds `web/`, serves it on loopback with the api streamed through to
a running stack, and launches the shell against it. `--web-env <file>` builds the
frontend the way another environment builds it and `--platform <origin>` runs the saas
edition, which together make a hosted preview a matter of pointing at a local pair:

```bash
# the console, in the layout production actually runs: at an origin root, not
# under /account/. Its dev default is the legacy same-host layout, and a console
# reachable only at a path prefix is one this shell cannot address, since it
# classifies by origin and nothing else.
VITE_ACCOUNT_PREFIX= VITE_BASE=/ VITE_APP_URL=http://localhost:5399 \
VITE_PLATFORM_URL=http://localhost:5178 VITE_COOKIE_DOMAIN=localhost \
pnpm dev --port 5178 --strictPort          # in the console's own web/

VITE_APP_ENTRY_PATH=/ VITE_PLATFORM_URL=http://localhost:5178 \
pnpm run preview -- --host localhost --web-env ../../web/.env \
  --platform http://localhost:5178 --backend http://127.0.0.1:8000
```

`--host localhost` rather than the loopback literal is deliberate: cookies ignore
port, so a console on the same hostname shares a session with the preview the way
the two subdomains share one in production.

It keeps a user-data dir of its own, which is not tidiness: sharing the installed app's
would teach the *installed* app that its frontend reserves the window-button strip when
the build it actually loads may not, which is the bug it exists to catch.

**Say `pnpm run`, not `pnpm`, for anything that builds.** `pnpm <name>` falls back
to a script only when pnpm has no command of that name, and the failure when it
does is silent: this used to be `pnpm pack`, which quietly built a **tarball**
instead, left the previous artifact in the output tree, and exited 0. A verification run
against that stale artifact is what caught it.

**The `postinstall` line is load-bearing.** Electron 42 removed the package's own
postinstall, so `require('electron')` now downloads the binary lazily on first use.
Left alone that turns a missing download into a stall in the middle of whatever
first touched it; `install-electron` puts the fetch back at install time where a
failure is a failed install. It is also why `onlyBuiltDependencies` lists only
`sharp` now: neither electron nor electron-builder has a build script to approve.

Minimum supported macOS is **12**, raised by Electron 38.

## Two editions, one source

| | `oss` | `saas` |
|---|---|---|
| Entry on first run | the server picker | hosted sign-in, then wherever the platform sends them |
| Platform console | does not exist | shares the app window (see below) |
| Config | `config/default.json` (committed) | `config/build.json` (gitignored) |
| App name | `LangAlpha OSS` | `LangAlpha` |
| Bundle id | `ai.langalpha.desktop.oss` | `ai.langalpha.desktop` |
| URL scheme | `langalpha-oss://` | `langalpha://` |

`src/config.js` merges the two and refuses to start a `saas` build with no
`platformOrigin`: that build would open on the app and silently skip onboarding, which
is the one thing the edition exists to guarantee.

**The shell never decides whether a customer needs onboarding.** A SaaS first run enters
at the platform's *sign-in* page and the platform's own post-auth funnel routes from
there: to the app for an account that is set up, into the wizard for one that is not.
`reachedApp` is per-install state and only ever a shortcut past that round trip; reading
account state off it gets a returning user the wrong first screen,
being offered a downgrade from the plan they already pay for.

**The two editions are installable side by side, and all three identity strings
carry that.** The name is the load-bearing one: `app.getName()` is what
`getPath('userData')` is derived from, so a shared name is a shared `settings.json`
and the OSS build inherits whatever origin the hosted one last learned. Separate
bundle ids do not separate profiles. The scheme is the functional half; both editions
registering `langalpha://` leaves the OS to pick one, so a hosted magic link can open a
build pointed at localhost, which cannot redeem it.

`src/config.js` holds the table and is the only thing the *running* app reads, including
`app.setName(config.appName)` in `main.js`. Without that call Electron answers
`getName()` from the packaged `package.json`, not from the `CFBundleName`
electron-builder stamps, and a correctly-stamped bundle resolves the other edition's
profile. `scripts/build.mjs` holds the packaging half and rewrites `electron-builder.yml`
per edition; the committed base is the OSS identity, so an unset `DESKTOP_EDITION` builds
the self-hosted one. The two tables are asserted equal in the tests, because every
consumer only ever reads its own half.

**`config/build.json` is deployment configuration, not source.** Where a build points
is decided per package, so the origins are written from the environment at package time
and deleted again on an `oss` build: a tree that previously built `saas` cannot bake
those origins into an OSS package by accident.

**Nor do the two share an output directory** (`directories.output: dist/${EDITION}`).
The artifact filename carries the edition; nothing else written there does. The unpacked
bundle is named from `productName`, so both `.app`s land under one `mac-arm64`, and the
update manifests are `latest-mac.yml` and `latest.yml`, fixed names with no edition in
them at all, so whichever edition builds second overwrites the first's. `scripts/build.mjs`
then searches that same directory for what it just produced, which is where one tree
turns into a signing check verifying the other edition's stale bundle and a no-feed build
whose sweep strips the other edition's baked `app-update.yml`.

Separate outputs do **not** make the two editions safe to build at the same time. Both
still write `config/build.json` and `.electron-builder.resolved.yml`, one copy each at
fixed paths, so two concurrent packages race over the origins and the identity and can
produce a correctly named artifact carrying the other edition's configuration. Build them
one after the other. For the same reason `scripts/make-release-index.mjs` takes one
edition's output directory and refuses a parent holding several.

## Layout

| File | Purpose |
|---|---|
| `src/index.js` | the packaged entry: turns a require-time crash into a dialog instead of a silent death |
| `src/main.js` | windows, IPC, lifecycle, and carrying out what `policy` decided |
| `src/policy.js` | what the shell decides: entry URL, where a navigation belongs. **Pure** — it may not write the store or open anything |
| `src/origins.js` | what counts as ours: **by origin, never by path** |
| `src/oauth.js` | system-browser OAuth, intercepted (below) |
| `src/deeplink.js` | `langalpha://` scheme, for magic links clicked with the app closed |
| `src/preload.js` | the renderer bridge: version, platform, `setTheme`, `openExternal`, `savePdf` |
| `src/pdf.js` | renders the calling window to a PDF the user picks a home for; allowlists the options the page may set |
| `src/downloads.js` | gives a download a visible ending, since a frameless window has no download shelf |
| `src/notify.js` | the dock bounce that says a file landed |
| `src/outage.js` | what replaces a blank window when the network does not answer |
| `src/updater.js` | auto-update, gated on a feed actually existing |
| `src/probe.js` | "is anything answering", shared by the picker and the outage page |
| `src/store.js` | a few scalars in a JSON file: `serverUrl`, `reachedApp`, `appChrome`, `platformChrome`, `theme` |
| `setup/` | the OSS server picker, in its own window with its own preload |
| `outage/` | the outage page, a local file so it renders when nothing else can |
| `test/` | `node:test` over the pure logic, with an `electron` module stub |

## One frame per app

Hiding the titlebar hands the top strip of the window to the page. That is only safe
for a page that takes it: both SPAs reserve a 38px drag region for the macOS window
buttons, and a page that does not leaves the buttons sitting on its own header **and**
the window with no drag region anywhere, which means it cannot be moved at all.

**Each SPA declares its region in `index.html`, not in its bundle** (`#window-drag`,
shown by a `desktop-mac` class the same document stamps from the bridge). Two reasons,
both learned the hard way. It has to hold on every route: langalpha's used to live in
the sidebar, so a logged-out window reserved nothing, the probe below recorded "this
build does not reserve", and the next launch came up with a plain titlebar. And it has
to hold when the bundle is the thing that failed, since a window showing a dead build
is still a window the user has to be able to move. Where a sidebar exists it also
carries a matching 38px spacer, so the app's own header starts below the buttons
rather than under them.

**Once the bundle is up, the band widens past that corner.** Each SPA's
`styles/chrome.css` turns its frame into a titlebar under `html.desktop-mac`: the
sidebar's spacer carries the drag itself, `[data-chrome~="drag"]` marks the header
rows, and `.chrome-drag-strip` gives a column with no header of its own a 38px band
in place of its top padding. Interactive elements and documents declare `no-drag`,
because a drag region swallows the mouse for everything inside it. **None of this is
testable from Playwright**: its mouse events are CDP synthesized and never reach the
hit test that owns `-webkit-app-region`, and posting real CoreGraphics events needs
macOS Accessibility permission. Changes here are checked by dragging the window.

**So the frame is feature-detected, not assumed.** After each app load the shell asks the
page whether anything under the buttons is a drag region (`DRAG_PROBE`, hit-testing three
points along the strip) and remembers the answer in `appChrome`; window creation reads it.
An unmounted page returns `null`, which is not "no" and is not recorded. `titleBarStyle`
is fixed at construction, so a changed answer applies on the next launch rather than
recreating a window that may have a turn streaming in it.

This is the same rule as the bridge: **feature-detected, never version-detected**. The
shell releases on a slow cadence and the app deploys continuously, so a shell that only
works against the newest frontend would be a shell that has to ship with every web
deploy. It also means a packaged shell run against an older deployed build is merely
plainer, never broken.

The console is asked the same question separately (`platformChrome`), because it is a
separate app on its own deploy cadence. **It shares the main window by default**, the way
"Usage & Plan" is a plain same-tab link in the browser and the console carries its own
way back; a second window would be the shell inventing a journey the product does not
have. The exception is the one combination that cannot work: a main window with no
titlebar showing a page that reserves no strip. That, and only that, gets a
standard-titlebar window of its own, and it stops the day the console reserves a strip.

`classify()` routes it: a navigation to the app from a console window returns
`app-window`, one to the console from the main window returns `platform-window` only in
that exception, and everything else is a plain `allow`. On `will-navigate` the
handoff also closes the window that was left behind (a top-level navigation out is the
user leaving it), while `setWindowOpenHandler` does not, because the page that opened it
is still using the one it has.

## OAuth

Google refuses OAuth inside an embedded webview (`disallowed_useragent`, and a
user-agent spoof does not get around it), so the authorize URL has to open in the real
browser and the code has to come back over a loopback listener.

The shell does this **generically, without either SPA knowing**. It catches the
authorize navigation, swaps `redirect_to` for `http://127.0.0.1:<port>/callback`, and
when the code arrives sends the window that started the flow to the `redirect_to` it
originally asked for, with the code appended.

Three things are load-bearing:

- **The exchange happens in the renderer, never in main.** The PKCE verifier lives in
  that renderer's cookie jar and never leaves it. That is also what makes the loopback
  hop safe: anything else listening on the port gets a code it cannot redeem.
- **Only 8788/8789/8790 work.** Supabase matches `redirect_to` as an exact string, so
  every port has to be in its Redirect URLs allowlist.
- **The interception mechanic is indirect.** `setWindowOpenHandler` returns `deny`, so
  `window.open` returns `null` and the SPA takes its existing popup-blocked fallback: a
  same-tab navigation to the authorize URL, which `will-navigate` then catches. If an
  SPA ever drops that fallback, sign-in breaks here with no error on the web side.

`begin()` refuses any flow whose `redirect_to` is not one of our origins. Without that
the shell would drive its own window wherever a crafted authorize URL pointed, carrying
a code the user had just authorized.

## When the network does not answer

A remote-URL shell shows whatever the network gives it, and a failed load gives it
a blank window. That is the one failure mode this architecture buys, so it has a
real screen. Two paths reach it, and the second is easy to miss:

- `did-fail-load` on the main frame, for transport failures.
- `did-navigate` with a status of 500 or more. **A 502 from an edge is a
  successful load of an error body**, so it never fires `did-fail-load`, and
  without this the user is left looking at the CDN's page with no way back.

Anything under 500 belongs to the app: a 404 is a route, a 401 is a login.

The page reports four distinct situations, because the useful advice differs:
`offline` (this machine has no connection), `captive-portal` (the wifi wants a
sign-in), `unreachable` (we could not connect), and `server-error` (it answered,
badly). A server that answered is never reported as the user being offline, or
they spend the outage debugging their router.

**`net.isOnline()` alone cannot separate the first three.** Its `false` is
reliable; its `true` is documented as *inconclusive*, and a hotel or airport
portal is precisely the case that returns true. So when the machine looks online
and we still could not get there, `captive.js` probes
`http://cp.cloudflare.com/generate_204` and treats anything but a 204 as a
portal. **The cleartext scheme is the mechanism, not an oversight**: a portal can
only intercept plaintext, and over HTTPS the request fails in a way that is
indistinguishable from the host being down. A portal is only ever claimed on
positive evidence, and the probe is skipped for loopback or LAN targets so a
self-hoster never causes an outbound request. Cost is bounded to that one branch;
offline and 5xx still render instantly.

`ERR_NETWORK_CHANGED (-21)` gets one silent retry before any of this, because it
is what switching access point or raising a VPN looks like from here. The retry is
released only by a `did-finish-load`; anything softer is a reload loop on a dead
network.

It retries on a widening backoff and recovers on its own. Each attempt probes
first, so a failed retry does not flash the app's loading screen and bounce back.
An `online` listener fires an immediate retry the moment the OS reports the link
back, so reconnecting wifi recovers the window with no click.

**This covers load-time failure only.** `did-fail-load` needs a navigation, so a
drop that happens while the app is already running never reaches the shell: the
SPA's own fetches and SSE stream fail and it owns that experience. That is
deliberate — replacing a running app with a full-screen outage page on one failed
request would be worse than the disease — but it means "the network died mid-turn"
is a question about `web/`, not about this directory.

Its controls reach the main process, so they are kept off every remote page:
`preload.js` exposes `langalphaOutage` only when `location.protocol === 'file:'`,
and the main process independently refuses those channels unless the window
really is showing the page.

## Updates

A build learns where to look in one of two ways, and needs exactly one:

- `app-update.yml`, written into the package by electron-builder when a `publish`
  target existed at build time. This is the normal path.
- `updateFeed` in the desktop config, which overrides it.

`electron-builder.yml` carries `publish: null` because where a build looks for
updates is deployment configuration, not source: the feed arrives as
`DESKTOP_UPDATE_FEED` and `scripts/build.mjs` rewrites the config for that one
build. **Supplying a feed is what makes electron-builder emit `latest-*.yml` at
all.** Without it there is no manifest, and a build with no manifest installs
perfectly and then never updates, which is why the build script fails hard when a
feed was set but no manifest came out. That guard caught its own case the first time it ran.

Distribution has two halves: the GitHub release is where a person downloads the
app, and the feed host is the only thing an installed app reads. Publishing one
without the other is a silent no-op.

The workflow in this repository builds the OSS edition only, and ships it feed-less
and unsigned. The hosted edition is built by a separate pipeline that holds the
signing certificates and the key to the feed host; it consumes this directory but
does not live in it, because a public repository is the wrong place to keep a
credential that can replace the binary every installed app runs. Both editions are
the same source, so a change here reaches both, and `scripts/` is shared: nothing
under it is dead code merely because this repository's own workflow does not call
it.

Applying a macOS update needs a Developer ID signature, which does not exist yet.
Everything up to that point is verified: the packaged app fetches its baked-in
feed, recognises a newer version, downloads it and verifies the sha512.

## Conventions

- **Classify by origin, not by path.** A path like `/account` only identifies the
  account console in dev, where a proxy stitches both SPAs onto one host; in production
  they are separate origins.
- **The window background must equal `--color-bg-page`.** Electron cannot remove the
  gap between frame and paint during a live resize, only match its colour, which is why
  the page pushes its resolved theme down through `setTheme`. If `tokens.css`
  `--background` moves, move `src/theme.js` with it.
- **The bridge is feature-detected, never version-detected.** The shell updates on a
  slow cadence while the web app deploys continuously, so a new web build must never
  require a new shell.
- **Nothing auth-related is exposed to the page.** The shell drives sign-in itself, so
  neither SPA needs, or gets, a way to.
- **A sandboxed preload cannot require arbitrary files.** Its resolver is limited to a
  few Electron built-ins, and a throw there takes the whole bridge down silently. The
  shell version travels as a command-line switch for this reason.
- **Packaging resources live in `resources/`, not `build/`.** The repo-root
  `.gitignore` has a Python `build/` rule that silently swallows it.

## Status

macOS is built and verified, including the outage page and the update path up to
the signature check. Windows and Linux targets are declared in
`electron-builder.yml` and run in CI, but have not been exercised by hand.

Nothing has shipped a feed yet, so no released build can update itself until
`DESKTOP_UPDATE_FEED` is set and the artifacts are uploaded there.
