# Plugin runtime

magpie's built-in plugins are the parts of magpie not everyone needs, each
one a package under `plugins/` that the user can switch off. The runtime in
`internal/pluginrt` keeps their registry, applies the ones that are on in the
order their services make, and disposes of what each registered when it is
turned off. `plugins.yml` says which are on. This page describes P0 (the
runtime, the file and the window's switch) and P1 (the window's kernel: a
plugin's page, its error boundary, the kit it draws with and its settings
form, with the Gateway page as the first plugin to draw its own page), and
P2 so far (a page moved out of the core whole: its code, styles and words,
starting with Sessions). OpenCode plugins (npm packages in
the plugin host) are a different thing; see
[provider and plugin ownership](provider-plugins.md) and
[gateway middleware](gateway-middleware.md).

## Responsibilities and boundaries

| Part | What it does | Source |
| --- | --- | --- |
| Registry | A plugin calls `pluginrt.Register(Manifest)` from `init`. `Registered` lists them by id; two with one id panic. `plugins/all` imports every plugin, and only `main.go` imports `plugins/all`, so core code and its tests run without any. | [`pluginrt.go`](../../internal/pluginrt/pluginrt.go), [`plugins/all/all.go`](../../plugins/all/all.go) |
| Manifest | `ID`, `API` (a caret range of the host API, `"^1"`; `pluginrt.API` is `"1.0"`), `Requires` and `Provides` (services), `Essential`, `Name`/`Sub` (English; the window translates them), `One`/`Many` (what is in use, of 1 or `{n}`), `InUse`, `Apply`, `Parts` (`{Slot, Key}`: the window's parts it is), `Defaults` (its config), `Settings` (a struct of its settings, made into `Defaults` and a schema at `Register`) and `Client` (its files in the window, under `internal/gui/assets/plugins/<id>/`: scripts, its `i18n.js` and a `.css`). | [`pluginrt.go`](../../internal/pluginrt/pluginrt.go) |
| Lifecycle | `Runtime.Reconcile(on, config)`. Off first: every plugin no longer wanted, and every one requiring a service one of those provided, is disposed newest first. Then on: each wanted plugin whose requirements are provided (by `Core`, `settings`, `providers`, `gateway`, `window`, or an active plugin) is applied, again and again until no more can be. States: `off`, `pending` (waiting for a service, logged), `active`, `failed` (Apply returned an error or panicked, or the API range doesn't match; what it registered before is undone), `disposed`. A failed plugin never stops the others. | [`pluginrt.go`](../../internal/pluginrt/pluginrt.go) |
| Ctx | What `Apply` gets: `OnDispose(f)`, `Contribute(slot, key)`, `Provide(name, v)` (withdrawn when it goes), `Service(name)`, and its composed `Config`. Disposers run in reverse, each one's panic logged and the rest still run. | [`pluginrt.go`](../../internal/pluginrt/pluginrt.go) |
| plugins.yml | `appdir.Config()/plugins.yml`: `preset` (`essentials` or `all`) and `plugins`, rows of `{id, enabled, config}` holding only what the user set. | [`config.go`](../../internal/pluginrt/config.go) |
| Settings schema | `SchemaOf(Settings)` makes a JSON Schema object of the struct, in its fields' order (`x-order`): each exported field with a json name is a setting, of `bool`, an int, `float64` or `string`, with tags `title` (English; the window translates it), `description`, `enum` (comma separated) and `min`/`max`. Its values are the defaults. A field a form can't draw, or a tag that doesn't parse, panics at `Register`. `Schema.Validate` takes a value only as the schema allows it (a JSON float64 or a YAML int for an integer); `SetConfig(id, config)` writes the user's row through it, and `Compose` leaves out a value edited into plugins.yml by hand that it doesn't allow, so the default stands. | [`schema.go`](../../internal/pluginrt/schema.go), [`config.go`](../../internal/pluginrt/config.go) |
| Built-in plugins | `groups`, `library`, `otel`, `sessions`, `warmups` (P0), and `gateway` (P1), the Gateway page, which is Essential and in use while a gateway key is there (`access.List`). Its one setting, `callsPage` (10, 20, 50 or 100; 20), is how many recent calls the page shows at a time. The other five aren't Essential. Each one's `InUse` counts what the user made with it: routing groups not Auto and not hidden, library items given to agents, a collector sent to, gateway conversations recorded, warm-ups and check-ins on. | [`plugins/`](../../plugins) |

The boundary is checked by `TestPluginsImportOnlyCore`: no package outside
`plugins/` imports one (but `main.go`, through `plugins/all`), a plugin never
imports another, and `plugins/all` imports every plugin folder. Plugins reach
each other only through services.

## The window's kernel (P1)

`internal/gui/assets/kernel.js` loads after `i18n.js` and before the
plugins' scripts and `app.js`, all classic scripts sharing one scope. It is
`window.magpie`:

- `magpie.plugin(id, setup)`: a plugin's script registers, and `setup` gets
  a context: `config` (from boot.js's `pluginConfig`, then Plugins ›
  Built-in), `onConfig(fn)`, `onDispose(fn)`, `slots.add(slot, part)` and
  `ui`.
- **Slots.** The one slot is `page`: a part `{key, html, loads, mount,
  …hooks}` becomes `<main class="view" id="view-<key>"
  data-feature="<plugin>">` where index.html's `<template data-slot="page">`
  is, at once, so app.js finds the page as it finds its own. app.js calls
  `magpie.start()` when it is set up, which mounts every page, and then each
  hook through `magpie.call(key, hook, …)`: `loading`, `draft` and `render`
  around `/api/providers` for a page that `loads: "providers"`, `open` when
  `show` opens it (a promise it gives back puts the reader back where they
  were once it settles), `relang` when the language changes on it.
  `title` is the page's header (English; `show` translates it).
  `magpie.pages()` adds the plugins' pages to the views `show` and
  `?view=` know.
- **Words.** A plugin's `i18n.js` calls `magpie.strings({zh, "zh-TW", ja,
  de})`, added to i18n.js's `I18N` before app.js translates anything. A key
  already there is logged and not taken. `tests/strings.cjs` reads them as
  the page does, for `gui-de`, `gui-ja`, `gui-zh-tw` and `i18n-keys`
  (no key in two files, every key of a plugin's file in all four
  languages).
- **Error boundary.** A hook that throws, or whose promise fails, is caught
  in `run`: logged with `[magpie] <plugin>: <key>.<hook>`, and the page is
  replaced by a card saying "This page stopped working", the error's message
  and Try again. Further hooks of a broken page do nothing, so nothing half
  drawn comes back, and the other pages go on. Try again puts the page's
  markup back, translates it, mounts it and runs the hook that broke with
  what it was given. A plugin whose `setup` throws is logged and has no page.
- **Kit** (`magpie.ui`): `el`, `button`, `toggle` (the switch Plugins uses,
  `role="switch"`), `menu` (the app's menu through `openProtoMenu`, never a
  native `<select>`), `row` (a settings row) and `form(schema, values,
  onChange)`: a switch for a boolean, a menu for an enum (numbers in the
  window's locale), a field for a number (kept to its range, `aria-invalid`
  when not) or text.
- **Settings.** Plugins › Built-in draws the rows of each plugin on, with a
  schema, from `ui.form` under its row (`.feat-set`), and a change posts
  `{id, config}`; `applyFeatures` hands each plugin's config to
  `magpie.configure`, which calls its `onConfig` only when it changed.

The Gateway page is `plugins/gateway` with `Client: keys.js, client.js`
(`internal/gui/assets/plugins/gateway/`): `keys.js` is the gateway-key
manager that was `caller-keys.js`, and `client.js` is the page's code that
was in app.js, ending in its `magpie.plugin("gateway", …)`. Still in
app.js and app.css: its styles, its sidebar and header buttons
(`data-feature="gateway"` in index.html), and `decideEntry`, which the model
info card shares. `TestBuiltinClientsLoaded` holds index.html to load every
plugin's `Client` script between kernel.js and app.js, and its stylesheet in
the head, each with its `?v=`.

## Pages moved out (P2)

Each page moves in a commit of its own, whole: its code into
`assets/plugins/<id>/client.js`, its styles beside it, and the words only it
says from i18n.js into its `i18n.js` (a key app.js, another page, index.html
or Go also says stays in i18n.js). It stays so after: `i18n-keys`' "a
plugin's words are its own" fails when anything outside a plugin's folder
says one of its words, which goes back to i18n.js.

- **Sessions** (`plugins/sessions`, `Client: i18n.js, sessions.css,
  client.js`): the page that was `sessions.js`, its markup all drawn by its
  code, so its part has no `html`. Its hooks: `open` and `relang` load it,
  and `reveal(s, e)` is the Usage page's way in (a session's row and All
  sessions, #752), called through `magpie.call("sessions", "reveal", …)`,
  so with no Sessions plugin it does nothing. Still in app.js: the Usage
  page's Sessions tab (`/api/sessions`) and Settings' session terminal row
  (`data-feature="sessions"`).
- **Library** (`plugins/library`, `Client: i18n.js, library.css,
  client.js`): the page that was `library.js`. Its code runs at `mount`
  only, where it wires its listeners (the dialog's backdrop and Escape,
  focus and visibility reading it again, its lists' scroll), since the
  script is in before app.js. Its hooks: `open` and `relang` read
  `/api/library`, `redraw` draws it again once the state says which agents
  are hidden, and `close`, `dirty` and `discard` are what `show()` asks
  before the reader leaves it. `window.loadLibrary`, `redrawLibrary`,
  `closeLibraryModal`, `libraryDirty` and `discardLibrary` are gone.

## Source of truth and composing

What a plugin runs with is composed field by field (`Compose`), each value
remembering its layer (`Source`):

1. `default`: every plugin on, its `Manifest.Defaults`;
2. `preset`: Essentials leaves every plugin not `Essential` off;
3. `user`: the rows of plugins.yml (`enabled`, and `config` merged into the
   defaults key by key, maps deeply);
4. `in use`: a plugin whose `InUse` is above 0 is on whatever the rows say,
   since off its things would go on working with nowhere to see them. An
   `InUse` error counts as in use.

`Composed.Chosen` is plugins.yml's say before step 4. `magpie plugin dump`
(`--json`) prints the composed list with each plugin's state and why.

## Runtime paths

- **Start** (`internal/cli/main.go`, after `settings.Migrate`):
  `pluginrt.Settle(!settings.RanBefore())` writes a first plugins.yml when
  there is none: `essentials` on a new install, `all` on a magpie that ran
  here before (one of `settings.ranBefore`'s files is there; one that can't
  be looked at counts as there), so an existing user keeps everything. Then
  `pluginrt.Refresh` makes the process's runtime and reconciles it. An error
  is printed and magpie starts.
- **Every read**: `Refresh` loads plugins.yml again, composes it and
  reconciles. The window's `/api/state`, `/api/plugins/builtin` and boot.js
  each call it (`builtinsState`), so a change made by the CLI shows on the
  next read.
- **Switch**: `Set(id, on)` (`POST /api/plugins/builtin`, `magpie plugin
  builtin on|off <id>`) writes the user's row; `SetPreset` the preset
  (`magpie plugin preset essentials|all`). Off is refused while the plugin
  is in use.
- **The window**: see [GUI app shell](gui-shell.md), "Built-in plugins".

## Failure and compatibility

- A plugins.yml that can't be read or doesn't parse, or names another
  preset, is an error, never an empty file. `Refresh` returns it and leaves
  the runtime as it was; before the first good read every plugin is on, as
  before plugins existed. `Set` and `SetPreset` refuse to write over it, the
  window says it above the list and disables every switch, and the CLI exits
  with it. The user fixes the file or removes it.
- Writes hold `filelock.Mutex` (`plugins.yml.lock`) against other magpies
  and a mutex in the process, are written whole (temp file, sync, rename),
  and keep the file they replace as `plugins.yml.bak`.
- A plugin written for another major API, or a newer minor, is `failed`
  with the reason; the rest run.
- A plugin's page whose code throws breaks only that page (the boundary
  above); a POST of a config the schema refuses is a 400 and writes nothing.
- A plugin's off is the window's alone: its page, sections and rows
  leave the window. The gateway, the TUI and the CLI serve the same either
  way, and nothing the user made is deleted. Davsync doesn't carry
  plugins.yml.

## Verification

- `go test ./internal/pluginrt/` (`TestReconcile`, `TestCompatible`,
  `TestPluginsImportOnlyCore`, `TestCompose`, `TestSettleAndSet`,
  `TestBrokenFileIsKept`), `go test ./internal/settings/ -run TestRanBefore`.
- `go test ./internal/pluginrt/ -run 'TestSchemaOf|TestValidate|TestSetConfig'`.
- `go test ./internal/gui/ -run 'TestBuiltin|TestBootSaysBuiltinsOff'`
  (`TestBuiltinConfig`, `TestBuiltinClientsLoaded`).
- `i18n-keys`, `gui-de`, `gui-ja`, `gui-zh-tw`, and a moved page's own
  tests (`sessions-*`, `session-*`, `sess-*`; `library-*`, `skill-*`,
  `mcp-*`, `found-skill-*`) in Chromium and WebKit.
- `internal/gui/tests/builtins.test.cjs` (the settings form) and
  `plugin-kernel.test.cjs` (the boundary, Try again, `callsPage` from
  boot.js and from a change) in Chromium and WebKit, every language, 1100,
  800 and 420 points; the Gateway page's own tests (`gateway-*`,
  `recent-calls-*`) unchanged.
- By hand, under a sandbox HOME: `magpie plugin builtin`, `magpie plugin
  builtin on groups`, `magpie plugin dump`, and a plugins.yml broken by hand.
