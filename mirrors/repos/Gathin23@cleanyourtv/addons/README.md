# Add-ons

Small, optional Android TV apps that plug into the launcher as a **module card**, kept in this repo
so they are easy to find, build and review. The launcher in [`launcher/`](../launcher/) never
depends on them: it is built, tested and size-checked without this folder, so an add-on can't make
the core bigger or change how it behaves. You install an add-on only if you want it.

## Add-ons

| Add-on | What it does | Author | Tested on | Permissions |
|---|---|---|---|---|
| [Frigate Glance](frigate-glance/) | Frigate camera pop-ups over whatever is playing | [NickLD](https://github.com/NickLD) | TCL 65Q650G | overlay, accessibility (card keys), network, foreground service |
| [Capacity Stats](capacity-stats/) | Available/total and used/total RAM; available/total storage | [lionlev21](https://github.com/lionlev21) | Android TV 12 (model private) | None |
| [Weather](weather/) | The weather for one city: now, US air quality and the next three days, from Open-Meteo (no key) | [@Sumyabazar1](https://github.com/Sumyabazar1) | Hisense SmartTV 4K FFM (lushan), Google TV 12 | `INTERNET` |
| [Photo Prints](photo-prints/) | Your own photos as a screensaver: dated prints dealt in on a time-of-day sky, and a card that starts the slideshow | [@shivamsingh262](https://github.com/shivamsingh262) | Sony BRAVIA KD-65X82L (Google TV 12) | None |
| [Photo screensaver](photo-screensaver/) | Your own pictures and MP4 clips as the TV's screensaver and as a card, slowly zooming and crossfading (20 s each by default); optional time, photo dates, prints on a sky and weather | [JorickGU](https://github.com/JorickGU) | TCL 43P69K (Google TV 12) | `INTERNET` and coarse location, only with the weather option on |
| [Prayer Times](prayer-times/) | Today's prayer times for one city from Aladhan (no key), the next prayer with a countdown, Gregorian and Hijri dates | [@majnioui](https://github.com/majnioui) | Xiaomi TV (MiTV-MOOR2), Google TV 11 | `INTERNET` |
| [TV Hub](tv-hub/) | One live-TV guide for M3U/XMLTV playlists, Dispatcharr and HDHomeRun tuners, with a Media3 player and shortcuts to installed live-TV apps | [@maxhayim](https://github.com/maxhayim) | MOKA R8G (Android TV 14) | `INTERNET` |
| [Headphones](headphones/) | Bluetooth headphones made easy: where the sound goes, paired pairs with battery, a pairing shortcut, and a quiet guard that pauses and mutes the speakers when headphones drop | [@maxhayim](https://github.com/maxhayim) | MOKA R8G (Android 14) | Bluetooth (paired devices only) |

A widget, an info tile, a storage or smart-home card: if it can live as its own small app, it can live
here. See the rules below.

## How an add-on works

An add-on is a normal Android TV app with its own Gradle project in `addons/<name>/`. It declares a
card with the existing module-card contract: the how-to is [`docs/modules.md`](../docs/modules.md)
and the spec is [`docs/specs/card.md`](../docs/specs/card.md). The launcher finds the card, asks the
TV owner once, and shows it as a tile with the add-on's label, caption and glow colour. Nothing else
connects the two.

Build one (JDK 17, Android SDK 34, as for the launcher):

```bash
cd addons/<name> && ./gradlew assembleRelease
TV_HOST=<tv ip> tools/venv/bin/python -I tools/tv.py --push addons/<name>/app/build/outputs/apk/release/app-release.apk /data/local/tmp/addon.apk
TV_HOST=<tv ip> tools/venv/bin/python -I tools/tv.py 'pm install -r /data/local/tmp/addon.apk; rm -f /data/local/tmp/addon.apk'
```

## Rules

- **Its own app.** One folder per add-on, `addons/<name>/`, with its own Gradle project
  (`settings.gradle`, `app/`), its own package name and its own README.
- **Only through the module-card spec.** An add-on never edits anything under `launcher/`, and
  `launcher/` never references `addons/`. If your idea needs a change inside the launcher, it isn't
  an add-on. Open an issue first instead.
- **No prebuilt APKs** in the repo. People build from source, as with the launcher.
- **Permissions up front.** The add-on's README lists every permission it asks for and why, plus
  any network access or background service. The rules in [`docs/modules.md`](../docs/modules.md)
  apply: no telemetry without an opt-in, no ads, your own art.
- **Tested on a real TV.** Say which one in the README and in the table above.
- **The author maintains it.** Issues about an add-on are assigned to its author. An add-on that
  breaks on current Android TV versions, or goes unmaintained, may be removed. Its history stays in
  git, and you can keep it going in a fork listed in [`SHOWCASE.md`](../SHOWCASE.md).

## Adding one

Open a pull request that adds `addons/<name>/` and one row to the table above. The core CI is not
blocked by add-ons: a separate workflow builds whatever changed under `addons/`, and
`tests/test_addons.py` checks the folder rules (own Gradle project, a README with a Permissions
section, no APKs, a row in this table) and that the launcher never includes or references this folder.
