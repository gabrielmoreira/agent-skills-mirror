# AGENTS.md

Instructions for coding agents (Claude Code, Codex, Gemini CLI, Cursor, Copilot and others) working in
this repository. People should start with [README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md);
this file repeats their rules in the form an agent needs, and links to them for the detail.

## First: which job are you doing?

| You were asked to | Do this |
|---|---|
| Clean up a TV: debloat it, install the launcher, push a theme | Read [PROMPT.md](PROMPT.md) and follow it exactly, on the real TV. Use the tools in `tools/` and the launcher in `launcher/` rather than writing new ones; the only file you need to change is `launcher/app/src/main/res/values/config.xml`, or a theme's `config.json`, for this TV. Do not edit the repo's docs, tests or other code, and do not open issues or pull requests unless the person asks you to. |
| Change this repo: a TV list, a fix, a translation, a theme, docs | Skip the next section and read on from [Repo map](#repo-map). |

### Cleaning a TV: the rules that are not negotiable

[PROMPT.md](PROMPT.md) is the procedure. Its safety rules, in brief:

- **Disable, never uninstall.** `pm disable-user --user 0`, one package per shell call. No
  `pm uninstall`, no root, nothing flashed. Every step must be undone by `tools/restore.sh`.
- **Back up first.** Package list, disabled list, `getprop` and settings into `backup/` before the first
  change. `tools/disable.sh` also writes its own record in `~/.cleanyourtv/`; keep the list you applied.
- **Leave alone what the TV needs to work:** the TV app and input services behind HDMI and the tuner,
  the input/source menu, remote and Bluetooth pairing, the on-screen keyboard, Play Store and Play
  Services. When a package name says nothing, read `dumpsys package <name>`, then ask.
- **Never disable Android's core packages:** the permission controller, package installer, ext
  services/shared and module metadata (`com.android.*` and `com.google.android.*`),
  `com.google.android.overlay.modules*`, `com.android.providers.*` (calendar, contacts, user dictionary
  and blocked numbers aside), `com.android.systemui`, `com.android.shell`, `com.android.phone`,
  `com.android.settings`, `com.android.tv.settings`, `android`. Without them Android may not boot (#884);
  `tools/disable.sh`, `disable.ps1` and `check.py --fix` refuse such a list, with no override.
- **Never start a factory or test package** (`com.cvte.tv.hkcfac`, `mediatek.factorymenu.ui` and the like),
  not even to look. On some boards that flips a factory-mode flag the shell cannot undo.
- **Keep the Home guard.** The stock launcher is disabled only after the new launcher is installed and
  confirmed as Home (`dumpsys activity activities | grep mFocusedApp`). On Google TV, check
  `dumpsys wifi | grep -o 'cname=[^ ]*'` before disabling setupwraith: if it owns the saved Wi-Fi
  network, disabling it takes the TV off Wi-Fi and ADB. `tools/disable.sh` and
  `launcher/build-and-install.sh` already enforce this. Use `FORCE_HOME=1` or `FORCE_SETUPWRAITH=1` only in
  the situation the script's own message describes, and only with the person's agreement.
  - On a CVTE board (any `com.cvte.*` package), leave its stock launcher (`com.cvte.tv.launcher.*`) enabled
    unless the `examples/` folder for that exact board disables it. Make the new launcher Home with
    `cmd package set-home-activity`, reboot once, and confirm Home and ADB come back before anything else.
    Don't enable a remote-key helper in the same pass: a JVC set hung on its boot animation with ADB gone
    after both were done before one reboot (#741).
- **Ask before anything the family uses.** Streaming apps, the voice assistant, Chromecast, Miracast and
  the firmware updater go into one checklist question; disable only what the person does not tick.
- **Disable in small batches** and screenshot between them (`tools/tv.py --screenshot shots/01.png`).
  Live TV, HDMI and some streaming apps give empty screenshots; that is the TV, not damage.
- **An injected key is not proof** for a remote button that goes through an accessibility helper: ask the
  person to press the real button. `am force-stop com.gathin.tvhome` switches those helpers off.
- **Close ADB afterwards.** USB debugging and Network/ADB debugging off, authorisations revoked, reboot,
  then `tools/adb-closed.py <tv ip>` must report the port closed. Port 5555 is plaintext.
- **Stop and say so** when the TV refuses: `pm disable-user` refused for every package, a sideload that
  fails verification, or an SDK below the launcher's `minSdk` 26. Do not retry in a loop, and do not lower
  `minSdk` or hand over an APK built elsewhere.

The person's backups (`backup/`), screenshots (`shots/`), notes (`work/`) and the ADB key
(`tools/adbkey/`) are listed in `.gitignore` and must never be committed. If the person wants to
share their TV's list afterwards, follow [Add a TV list](#add-a-tv-list) below.

## Repo map

| Path | What it is |
|---|---|
| `PROMPT.md` | The prompt people paste into their agent. Brand-neutral; safety rules live here. |
| `README.md` | Front page: quick start, supported TVs and the TV table, tools, launcher, restore, firmware updates, FAQ. `README.zh-CN.md` and `README.vi.md` are translations. |
| `CONTRIBUTING.md` | The contributor guide for people. "Where does my idea go?" is the routing table. |
| `SECURITY.md` | Private vulnerability reporting. |
| `SHOWCASE.md` | Projects built on this repo that live in their own repositories. |
| `CODE_OF_CONDUCT.md` | Includes the rule against publishing device identifiers, Wi-Fi names and IPs. |
| `examples/` | One folder per tested TV model: `debloat.txt`, sometimes a `README.md` and a `config.json`. Indexed in `examples/README.md`. |
| `docs/` | `docs/TROUBLESHOOTING.md`, `docs/REMOTE.md` (another home, over Tailscale), `docs/modules.md` and `docs/specs/card.md` (module cards), `docs/PRESS.md`, `docs/devices/` for models with notes but no tested list, and `docs/workflows/` for multi-step methods (see [Workflows](#workflows)). |
| `launcher/` | The reference launcher, package `com.gathin.tvhome`: plain Java, AndroidX RecyclerView and DynamicAnimation, `minSdk` 26, no `INTERNET` permission. |
| `themes/` | One folder per theme: `config.json`, a required `screenshot.jpg`, optional wallpapers. Keys are documented in `themes/README.md`. |
| `addons/` | Optional module-card apps, each its own Gradle project, never built into the launcher. |
| `tools/` | The ADB client and the scripts: `tv.py`, `b64push.py`, `relay.py` (guide: `tools/relay.md`), `disable.sh`, `restore.sh`, `recovery.py`, `check.py`, `privacy.py`, `theme.sh`, `adb-closed.py`, `bench.py`, `trace.py` and `trace_report.py` (guide: `tools/trace.md`, optional `tools/requirements-perf.txt`), `flamechart.py` (guide: `tools/flamechart.md`), `screendiff.py` (guide: `tools/screendiff.md`), `race_calendar.py`. Shell scripts have PowerShell twins (`disable.ps1` and the like). `readme_stats.py`, `readme_featured.py` and `readme_card.py` draw the README card. Each script's usage is in its first lines: read it before running it. |
| `tests/` | Python `unittest` suite: list format, README tables, press counts, themes, add-ons, the Home guard and the tools against fake TVs. |
| `.github/workflows/` | `ci.yml` (tests, launcher build, APK size gate), `addons.yml`, `maintainer-bot.yml`. |
| `.github/maintainer/MAINTAINER.md` | The review policy the maintainer and the PR bot apply. |
| `.github/pull_request_template.md` | The PR checklist. Fill it in. |

## Where a change goes

The core stays small on purpose. Pick the smallest home that fits (CONTRIBUTING, "Where does my idea go?"):

| The change | Where it goes |
|---|---|
| A TV list, a fix, a translation, docs, a tool fix | A pull request here |
| A small launcher switch that is off by default | A pull request here: see [the switch recipe](#add-an-off-by-default-launcher-switch) |
| A new look: colours, wallpaper, dock, columns, that existing config keys can carry | `themes/<name>/` |
| A widget or tile that can be its own small app | `addons/<name>/`, as a module card that never touches `launcher/` |
| A whole new launcher, a heavy restyle, a port to another platform, a lower `minSdk`, new permissions or network access, Fire TV Home takeover, a changed default for every TV | Your own repository, plus one row in `SHOWCASE.md` |
| Safety rules in `PROMPT.md`, the Home-safety logic in the scripts, protected packages, CI and workflows, the APK size gate | Open an issue for the maintainer; do not change it in a PR |

### What gets merged, sent back or closed

Every PR is reviewed by the maintainer and by a bot that applies `.github/maintainer/MAINTAINER.md`.
Read that file before a non-trivial PR; the verdicts are:

| Verdict | When |
|---|---|
| merge | Correct, in scope, tested where it matters. |
| merge-with-fix | One small mechanical change on merge: a missing README or examples row, a string missing in one or two locales, a stray file, an untested entry commented out. |
| rework | One real change needed: split a PR that bundles separable parts, rebase a code conflict, fold a second unit of an existing TV into its folder, turn a switch's default off. |
| theme, addon, showcase | A kind close or a move: the idea is good and belongs in that home. |
| hold | A maintainer decision, or a run on a real TV first. Changes to the Home or launch path (Home key, boot, return to Home, the install scripts) usually need one. |
| close | A duplicate, superseded, or against the base rule: no root, nothing uninstalled, you build it yourself. |

## Recipes

Run the tests after every recipe: `python3 -m unittest discover -s tests -v` (see [Before opening a PR](#before-opening-a-pr)).

### Add a TV list

1. Check `examples/README.md` first. The same product code and firmware as an existing folder is usually a
   second unit or a re-badge: add your notes to that folder instead of a new one.
2. Create `examples/<brand>-<model>/debloat.txt`, lower-case with hyphens. Copy the format of
   `examples/xiaomi-mi-tv-4a/debloat.txt`:
   - The first line is a comment with the exact model, Android version and firmware build
     (`tools/tv.py --probe` prints them).
   - Then the Apply and Undo lines, the stock launcher and Live TV package if they differ, and what was kept and why.
   - One package per line, grouped under a comment that names the group, with a trailing comment on anything
     non-obvious. No duplicates, nothing but package names outside comments.
3. List only packages you actually disabled and lived with for a few days. Note anything you re-enabled.
   Mark untested entries as comments.
4. Add one row to the table in `examples/README.md` (`` | `<folder>/` | TV | OS | Notes | ``) and one to the
   TV table in `README.md` (`| TV | OS |`). The TV cell must be the same text in both; `tests/test_examples.py`
   compares them.
5. Leave the counts alone (the `TV models` number in the card's alt text, the brand line): CI checks them only
   on `main`, and they are fixed up on merge.
6. A `README.md` for TV-specific notes and a `config.json` with the dock are welcome in the folder. Do not add
   install or restore scripts, Private DNS or AdGuard setup, or `pm uninstall` steps: the folder only
   disables, and `tools/disable.sh` and `tools/restore.sh` do the rest.

A model with notes but no several-day list goes in `docs/devices/<brand-model>.md`, with one line under the notes
list at the end of `examples/README.md`. A folder in `examples/` must have packages in it.

### Update an existing list

Keep the header accurate: add the second unit's model, firmware and region rather than replacing the first.
Explain each added or re-enabled package in a comment. A list that disables the firmware updater says why in the
header; keeping it enabled is preferred. `pm hide` or `pm block` needs the matching undo in the header. Edits to
someone else's list are judgement calls, so say in the PR which TV you tested on and for how long.

### Add a launcher translation

1. Create `launcher/app/src/main/res/values-<qualifier>/strings.xml` and translate every string in
   `launcher/app/src/main/res/values/strings.xml`, skipping the ones marked `translatable="false"`. Keep
   placeholders (`%1$s`, `%d`) and XML escapes intact.
2. Add the locale to `launcher/app/src/main/res/xml/locales_config.xml`.
3. Add the language to the Languages list in `README.md`.
4. To fix a missing string in existing locales, add it to every `values-*` folder you can, in the same order as
   the default `strings.xml`. A missing string falls back to English (`launcher/app/lint.xml`), but a new switch
   needs its strings in every locale.
5. Moving hard-coded text into resources is welcome; do not bundle unrelated build changes with it.
6. Build the launcher, set the TV's language (Android 13+: `tools/tv.py 'cmd locale set-app-locales com.gathin.tvhome --locales <tag>'`)
   and attach a screenshot. Right-to-left languages mirror the layout like Hebrew; `tests/test_hebrew_resources.py`
   checks that `layout-iw` keeps every view.

### Add an off-by-default launcher switch

The core takes a switch only if it changes nothing until a theme or `config.xml` turns it on:

1. Add the key to `launcher/app/src/main/res/values/config.xml` with a comment that says what it does and
   that a theme can set it, defaulting to off (`false`, `0` or the current behaviour).
2. Read it in `launcher/app/src/main/java/com/gathin/tvhome/Config.java`, from the resource and from the
   theme JSON, the way existing keys such as `show_stats` are read.
3. Add a row to the Keys table in `themes/README.md`.
4. If it adds a row to Launcher settings, put its strings in `launcher/app/src/main/res/values/strings.xml`
   and every `values-*` folder.
5. With the key off, nothing new runs: no receiver, no service, no write, no permission grant in the install
   script. The bot checks this in the diff, not in the description.
6. Add a JVM unit test under `launcher/app/src/test/java/com/gathin/tvhome/` for any logic that can be tested
   without a TV.
7. Keep it small: a switch should cost a few hundred bytes to about 1 KB of APK. Build and check the size
   gate; the gate is hard.
8. Verify on a real TV with the switch on and off, D-pad from every edge, and attach screenshots.

Anything TV-specific goes in `config.xml` or a theme, not in code. A bug fix that corrects wrong behaviour needs
no switch. No new dependencies in `launcher/app/build.gradle` without an issue first.

### Add a theme

1. Create `themes/<name>/config.json` using only keys from the table in `themes/README.md`;
   `themes/default/config.json` is the starting point.
2. Add `wallpaper.jpg` or a `wallpapers/` folder if it uses them: dark, 1920x1080, under about 300 KB each,
   and art you have the right to use.
3. Push it to a real TV with `tools/theme.sh themes/<name>` and take `screenshot.jpg` of Home with the focus
   on the dock: a JPEG at 1280x720 (16:9), at most 300 KB. Not a mock-up, not an emulator.
   `tests/test_themes.py` fails without it.
4. Add a row to the table in `themes/README.md` showing the screenshot, like the others.
5. A look that needs a new key is a launcher switch first, in its own PR.

### Add an add-on

1. Create `addons/<name>/` as its own Gradle project (`settings.gradle` and an `app` module), with its own
   package name.
2. It talks to the launcher only through the module-card contract (`docs/modules.md`, `docs/specs/card.md`).
   Nothing under `launcher/` changes, and `launcher/` never mentions `addons/`. If the idea needs a launcher
   change, it is not an add-on: open an issue.
3. Its `README.md` has a Permissions section listing every permission and why, plus any network access or
   background service. No telemetry without an opt-in, no ads, your own art.
4. Add one row to the table in `addons/README.md` linking `<name>/`, with the TV it was tested on.
5. No APKs in the repo. `tests/test_addons.py` checks all of this; `.github/workflows/addons.yml` builds the
   add-ons that changed with `./gradlew --no-daemon assembleRelease`.

### Add a showcase row

1. Add one row to the section of `SHOWCASE.md` that fits (home screens, forks, screensavers and add-ons,
   tools, other platforms), and the project under its TV brand in "Find a project by TV brand".
2. Keep each cell to one line: what it is, what it was built and tested on, and the author.
3. The project is open source with a link people can read and build, says which TV it was tested on, collects
   nothing beyond what its README says, and is yours or listed with the author's blessing.
4. Put a screenshot in the PR description; it is linked from the row.

### Add a press entry

1. Add a row `| Outlet | [Headline](<url>) | Date |` to the right country section of `docs/PRESS.md`, in the
   headline's own language. The link must open and show the article: no syndicated copies, no auto-generated
   listings, nothing that cannot be checked.
2. Update the counts in all four places `tests/test_press_counts.py` checks: the `docs/PRESS.md` intro line,
   its index line, the README card's alt text ("and N more: N articles from N countries") and `MORE` in
   `tools/readme_featured.py`. If you cannot redraw `docs/featured.png` and `docs/card.jpg` with
   `tools/readme_featured.py` and `tools/readme_card.py`, say so in the PR.

### Docs and troubleshooting notes

- `docs/TROUBLESHOOTING.md` is grouped under headings (Connecting, Working on the TV, then one per larger
  problem). An entry is a bullet that opens with the symptom in bold, then the cause and the fix, naming the
  TV model and firmware it was seen on.
- A fix for something your agent got stuck on usually belongs in `PROMPT.md` as one extra sentence, kept
  brand-neutral. Brand-specific knowledge goes in `examples/` or `docs/devices/`. Changes to the safety rules
  themselves go to the maintainer.
- Several tests pin facts in `docs/devices/` notes, `PROMPT.md` and `docs/TROUBLESHOOTING.md` (the
  `tests/test_*_note.py` files). If you reword one of those passages, run the suite and keep the fact.
- Docs and the README stay in step: a new list, theme, add-on or tool gets its row where the others are.

## Workflows

Multi-step methods in `docs/workflows/`. Read the one that fits before you start; each opens with when to
use it and links the tool guides it needs.

- [`perf-ab.md`](docs/workflows/perf-ab.md): measure performance improvements or regressions from a launcher
  change, with traces, a report and flame charts.

## Before opening a PR

| Check | Command or rule |
|---|---|
| Tests, as CI runs them | `python3 -m unittest discover -s tests -v` after `python3 -m venv tools/venv` and `tools/venv/bin/pip install -r tools/requirements.txt`. On `main`, CI sets `CLEANYOURTV_STRICT=1`, which also checks the README's TV-model count. |
| Launcher, if you touched `launcher/` | JDK 17, Android SDK platform 34, build-tools 34.0.0. In `launcher/`: `./gradlew --no-daemon testReleaseUnitTest lintRelease assembleRelease`. Lint must stay at zero errors. |
| APK size gate | `launcher/app/build/outputs/apk/release/app-release.apk` must be under 491,520 B (480 KB). Linux: `stat -c %s`, macOS: `stat -f %z`. |
| README rows | A new list has its row in `README.md` and `examples/README.md`; a theme in `themes/README.md`; an add-on in `addons/README.md`. |
| One topic per PR | A TV list never rides inside a launcher feature PR. A device's list plus small fixes for that same device can be one PR. |
| Tested on | Say which TV, Android version and firmware you tested on, in the PR template's "Tested on" line. |
| Real TV | Launcher changes are verified on a real TV, not only the emulator: `tools/tv.py --screenshot shots/after.png DPAD_DOWN`. D-pad from every edge (Up, Down, Left, Right). A button handled by an accessibility helper needs a press on the real remote, and a force-stop of the launcher switches the helpers off (`docs/TROUBLESHOOTING.md`). |
| Screenshots | Every visual change has a screenshot from the TV in the PR description. A performance claim has numbers, for example from `tools/bench.py`. |
| Stray files | No files that nothing links to: screenshots belong in the PR description, not the tree. |

## Hard rules

Never do these in a PR:

- **No prebuilt APKs or binaries** in the repo, not even as CI artifacts. People build from source.
- **No uninstalling.** No `pm uninstall` in a list or a script. `pm hide` or `pm block` only with the matching
  undo written in the list header.
- **No network in the launcher:** no `INTERNET` permission, no network features, no analytics or telemetry, no
  background services or polling, no blur or video. It targets TVs with 1 GB of RAM.
- **No new launcher dependencies** without discussing them in an issue first.
- **No changes to the safety rules** in `PROMPT.md`, the Home guard and other safety checks in
  `tools/disable.sh`, `tools/check.py` and `launcher/build-and-install.sh`, or the list of packages the TV
  needs, without the maintainer.
- **No changing a default for every TV.** New behaviour is off until a theme or `config.xml` turns it on.
- **Firmware updaters are better left enabled** (commented out in the list); a list that disables one says
  why in its header.
- **No Private DNS or AdGuard setup, and no install or restore scripts, inside a list folder.** The README
  already has the optional DNS extra; a note that Private DNS works on that TV is fine.
- **No secrets or identifiers** in commits, lists or screenshots: no IP addresses, Wi-Fi names, account emails,
  serial numbers, Android IDs, MAC addresses or ADB keys. Use `<tv ip>` or `192.168.1.50` in docs.
- **Don't edit `.github/workflows/`** or the APK size gate in a normal PR. A PR whose main content is a new CI
  workflow that builds or publishes releases is closed.
- **Don't open factory or test menus** on a TV to see what they do. Factory packages may be disabled, never
  launched.
- **No root, no getting around app-store protection, no private builds** others cannot reproduce from this repo.
- **No extras added to the PROMPT flow** beyond debloating and the launcher.
- **Don't relax `minSdk`** (26) or the launcher's permissions; those are forks for `SHOWCASE.md`.

## Privacy and screenshots

- The launcher's top bar shows the Wi-Fi network name, and a theme's `greeting_name` shows a name. Blur
  Wi-Fi names, people's names and cities, or crop them out, before a screenshot goes anywhere public.
- Never commit or post TV Settings screenshots that show accounts, email addresses or device names.
- `tools/tv.py --probe`, `getprop` and backups contain the serial number and device names. Quote only the model,
  Android version and firmware build.
- Keep session files in `backup/`, `shots/` and `work/`, which git ignores.

## Commit and PR style

- Titles are `area: what changed`, in plain words, with the issue in parentheses when there is one:
  `examples: add Epson LS800 laser projector (Askey HA90, Amlogic), Android TV 14`,
  `docs: an HDMI row opens any app that claims the channel MIME type (#805)`,
  `Launcher: show_inputs_pill, to hide the Inputs pill`. The area is the folder or file the change is in:
  `examples`, `Launcher`, `docs`, `tools`, `tests`, `themes`, `addons`, `SHOWCASE`, `README`, `Press`.
- The body is one or two sentences on what changed and the TV it was tried on, then the template's checklist.
  `Fixes #N` or `Closes #N` when it resolves an issue.
- One topic per PR. Small is fine. Be kind in reviews.
- Contributions are released under the repo's MIT licence.

## Where to ask

| For | Where |
|---|---|
| "Does it work on my TV?" and other questions | [GitHub Discussions](https://github.com/Gathin23/cleanyourtv/discussions) |
| Bugs and TV lists | Issues, with the templates in `.github/ISSUE_TEMPLATE/` |
| An idea that needs a launcher change, a new dependency, a tool replacement | An issue first, before the PR |
| A security problem in the prompt, tools, launcher or a list | Privately, as [SECURITY.md](SECURITY.md) describes. Never in a public issue. |
