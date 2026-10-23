# TCL Q7C (G08, Google TV, Android 14), European firmware

TCL Q7C QD-Mini LED, device `G08`, model "Smart TV Pro", product `G08_4K_GB`, firmware `UTT2.250416.001 AU02`,
MediaTek `tcl9618`, about 2.4 GB RAM. The same firmware build as the 85RM7L list and the same G08 board as the
C755, QM6K and 75T7 (US) lists. Set up on Ethernet in Austria. Both halves work on this set: the debloat list and the
Clean Your TV launcher as Home.

| File | What it is |
|---|---|
| `debloat.txt` | The 37 packages that were disabled, grouped and commented |
| `config.json` | Dock, hidden TCL tiles, Live TV app, the Settings and YouTube buttons; push it with `tools/theme.sh` |
| `65q7d-pro-home.png` | Home on the second unit, a TCL 65Q7D Pro (see [Second unit](#second-unit-65q7d-pro-greece-wi-fi)) |

**How much testing is behind it:** one set, from 21 October 2026. The first 35 packages were disabled in five batches
and survived a reboot. launcherx and setupwraith were disabled afterwards, for the new launcher. YouTube, Live TV,
the HDMI list in the Inputs menu, the Input, Settings and YouTube buttons, and D-pad navigation were checked on the
TV.

All commands run from the repo root with the TV's IP in `TV_HOST`. USB debugging must be on while you run them.
On this set, switching it on opens port 5555 by itself. Wireless debugging cannot be switched on over Ethernet,
and it is not needed.

## Install

The order matters: setupwraith goes while Google TV's home still owns Home, then `build-and-install.sh` starts the
new launcher and only then disables launcherx. `disable.sh` skips launcherx on the first run (its Home guard), which
is what you want here.

```bash
FORCE_SETUPWRAITH=1 TV_HOST=<tv-ip> tools/disable.sh examples/tcl-q7c-google-tv/debloat.txt
INPUT_KEY_SERVICE=1 HOME_KEY_SERVICE=1 TV_HOST=<tv-ip> launcher/build-and-install.sh
TV_HOST=<tv-ip> tools/theme.sh examples/tcl-q7c-google-tv
```

`FORCE_SETUPWRAITH=1` is only for a set on Ethernet with no saved Wi-Fi: there `dumpsys wifi` shows no network
owner, and `disable.sh` then plays safe and skips setupwraith. On Wi-Fi, run
`tools/tv.py "dumpsys wifi | grep -o 'cname=[^ ]*'"` first. If the network belongs to setupwraith, forget it and
join it again in Settings before you disable the wizard.

`build-and-install.sh` needs JDK 17 for Gradle 8.9. On a Mac where `java_home -v 17` answers with a newer JDK, pass
`JAVA_HOME` explicitly.

## Undo everything

```bash
TV_HOST=<tv-ip> tools/restore.sh examples/tcl-q7c-google-tv/debloat.txt com.google.android.apps.tv.launcherx
```

## Remote buttons

Every button on this remote arrives as scancode 240 (`KEY_UNKNOWN`). TCL's `TclKeyLayoutMap` tells them apart by HID
usage and turns them into keycodes, so map them by keycode (scancode entries would all collide). Found with
`logcat -v time` while pressing the real buttons: look for `InputReader ... TIDD: keyCode=`.

| Button | Keycode | Without Google TV's home | Here |
|---|---|---|---|
| Home | 3 | works | |
| Input | 178 (`KEYCODE_TV_INPUT`) | works: TCL draws its own source panel (`com.tcl.suspension`) | |
| Settings (gear) | 83 (`KEYCODE_NOTIFICATION`) | does nothing (it was launcherx's dashboard) | `settings_key_keycodes: [83]`, `HOME_KEY_SERVICE=1` |
| YouTube | 190 (`KEYCODE_BUTTON_3`) | does nothing | `app_keys: 190:com.google.android.youtube.tv`, `INPUT_KEY_SERVICE=1` |
| Netflix | 4062 | does nothing | left unmapped (Netflix is off) |
| Prime Video | 4099 | does nothing | left unmapped |
| TCL Channel | 4020 | does nothing | left unmapped |
| (app button) | 4057 | does nothing | left unmapped |
| (app button) | 4141 | does nothing | left unmapped |
| Mic | 84 (`KEYCODE_SEARCH`) | with katniss off, opens the Play Store search | |

The YouTube button sends 190 here. The G09 list maps 4065 for its YouTube button, so check yours. Re-pass both
`*_KEY_SERVICE=1` flags on every reinstall: a reinstall drops the services from the accessibility list.

## Notes for this set

- **Check that ADB is really closed when you are done.** Here the USB debugging switch in Developer options
  did not take: `settings get global adb_enabled` still said `1`, and port 5555 was still open after a reboot.
  `tools/tv.py 'settings put global adb_enabled 0'` closed it. The connection drops mid-command, so a non-zero exit is
  expected. Then revoke the authorisations on the TV, reboot, and check with `tools/adb-closed.py <tv-ip>`
  ("Connection refused").
- The UI runs at a 1920×1080 override on the 3840×2160 panel, at 60 Hz: the only display mode Android
  offers. This is the stock setting, not something the launcher changed.
- The Inputs menu lists the HDMI-CEC device names (here "Soundbar · HDMI 1", "PC · HDMI 2") from the TV input
  framework, plus Live TV (`com.tcl.tv`).
- Screenshots of Live TV and HDMI come back empty (0 bytes). `dumpsys activity activities | grep topResumedActivity`
  shows `com.tcl.tv/com.tcl.player.TVActivity`.
- Ambient mode (`dreamx`) was left enabled. Whether its screensaver still works with launcherx off was not checked.

## Second unit: 65Q7D Pro (Greece, Wi-Fi)

One owner's session on 2026-10-22, following [`PROMPT.md`](../../PROMPT.md) on Windows 11 with the repo's
tools (upstream `4c55533`, launcher 2.6). The firmware is the same build as the Q7C above (`G08_4K_GB`, `AU02`),
so `debloat.txt` here is the list to run; this section records the deltas and what differed on this unit. The
packages were applied in five batches with `tools/disable.sh` and checked after one reboot, but they have **not**
been lived with for several days, so nothing was added to `debloat.txt` beyond two header lines naming this unit.

![Reference launcher on the TCL 65Q7D Pro, five-tile dock, rotating wallpaper (greeting name and Wi-Fi name blurred)](65q7d-pro-home.png)

### Identify the firmware

| Field | Observed value |
|---|---|
| Retail model | `65Q7D Pro` (Q7D Pro SQD-Mini LED, 2026), supplied by the owner; not exposed by `ro.product.model` |
| `ro.product.manufacturer` / `ro.product.brand` | `TCL` / `TCL` |
| `ro.product.model` | `Smart TV Pro` |
| `ro.product.name` / `ro.product.device` | `G08_4K_GB` / `G08` |
| Android / SDK | `14` / `34`, Google TV |
| `ro.build.display.id` | `tcl9618-user 14 UTT2.250416.001 AU02 release-keys` |
| `ro.build.fingerprint` | `TCL/G08_4K_GB/G08:14/UTT2.250416.001/AU02:user/release-keys` |
| `ro.software.version_id` | `V8-T653T01-LF1V641` |
| Security patch | `2025-12-05` |
| `ro.hardware` / `ro.board.platform` | `mt5896` / `merak` |
| `ro.adb.secure` | `1` |

`G08_4K_GB` + `AU02` is the pair the Q7C, 85RM7L and 55C745 lists were applied on. The stock launcher is
`com.google.android.apps.tv.launcherx` and the Live TV player is `com.tcl.tv`
(`com.tcl.player.TVActivity`), as on the Q7C.

### Connecting: Wireless debugging only, and its port moves

The Q7C notes above say USB debugging opens port 5555 by itself. **Not on this unit.** With USB debugging on,
5555 kept answering `Connection refused` (the TV was reachable at the same IP). What worked was Developer
options > Wireless debugging, with Google's platform-tools `adb`:

```sh
adb mdns services                       # lists _adb-tls-pairing._tcp while the pairing dialog is open
adb pair <tv ip>:<pairing port> <six-digit code>
adb connect <tv ip>:<connect port>
adb -s <tv ip>:<connect port> tcpip 5555   # now tools/tv.py and the scripts work on 5555
```

- The first time, `adb mdns services` listed both `_adb-tls-pairing._tcp` and `_adb-tls-connect._tcp`. After a
  reboot only the pairing service was advertised, and the connect port had to be read from the TV's
  Wireless debugging screen.
- After the reboot that screen said "IP address and port: unavailable" while pairing still succeeded. Switching
  Wireless debugging off and on again brought the address back.
- `adb tcpip 5555` restarts adbd, so the connect port shown on the TV changes afterwards. Both the new port
  and 5555 worked.
- Forgetting and re-joining the Wi-Fi network (needed for setupwraith, next section) switched Wireless debugging off,
  and a reboot closed 5555. Each time a new pairing code was needed. Plan for three or four pairings in one
  session.
- On Windows, clone the repo to a short path. In a deeply nested folder, `git clone` left files unchecked-out
  and `pip install -r tools/requirements.txt` failed on a `cryptography` file path longer than 260 characters.

### setupwraith owned the Wi-Fi network in use

`tools/tv.py "dumpsys wifi" | grep -o 'cname=[^ ]*'` showed the saved network the TV was connected to with
`cname=com.google.android.tungsten.setupwraith` (a second, older saved network belonged to
`android.uid.system:1000`). The owner forgot the network in Settings and joined it again. After that its
creator was `com.android.tv.settings`, not `android.uid.system` as on the
[QM751G](../../docs/devices/tcl-75qm751g-qm7.md). setupwraith then owned no network, and `tools/disable.sh` disabled it without
`FORCE_SETUPWRAITH`. Wi-Fi stayed up, and the TV kept the same IP.

Order used, as in the Q7C README: setupwraith first, while launcherx still owned Home, then
`STOCK_LAUNCHER=com.google.android.apps.tv.launcherx INPUT_KEY_SERVICE=1 HOME_KEY_SERVICE=1
launcher/build-and-install.sh`, which started the new launcher, disabled launcherx and reported
`Home now resolves to com.gathin.tvhome/.MainActivity`. `mFocusedApp` confirmed it.

### The list as applied

29 packages in five batches, with a screenshot after each. Home, Live TV (`topResumedActivity` =
`com.tcl.tv/com.tcl.player.TVActivity`) and YouTube were checked between batches. launcherx was disabled by
`build-and-install.sh`, not from the list.

```text
# TCL promo, push messages, content rows and store demo
com.tcl.messagebox
com.tcl.esticker
com.tcl.exhibit
com.tcl.tv.tclhome_passive
com.tcl.waterfall.overseas
com.tcl.channelplus
com.tcl.usercenter
com.tcl.guard

# Telemetry, diagnostics and Android 14 ad / privacy services
com.tcl.logkit
com.google.android.feedback
com.android.tv.feedbackconsent
com.android.adservices.api
com.android.ondevicepersonalization.services
com.android.federatedcompute.services

# Extras nobody asked for
com.tcl.ocean.instructions
com.tcl.repairguide
com.android.printspooler
com.google.android.syncadapters.calendar
com.google.android.onetimeinitializer
com.google.android.play.games

# Off by the owner's choice
com.google.android.katniss              # Assistant; the mic button then opens the Play Store search
com.google.android.apps.mediashell      # Chromecast receiver
com.tcl.miracast
com.tcl.magiconnectfree
com.tcl.smartalexa
com.google.android.youtube.tvmusic      # was already disabled before the session
com.tcl.ui_mediaCenter
com.tcl.hearaid
com.tcl.t_solo

# Second Home claimant, after re-joining the Wi-Fi network in Settings
com.google.android.tungsten.setupwraith
```

Compared with the Q7C list:

| Q7C entry | Here |
|---|---|
| `com.tcl.airplay2`, `com.mediatek.AirplayAPK`, `com.mediatek.airplaydaemon` | Kept: the owner uses AirPlay |
| `com.tcl.UpdatePeripheral` | Kept: a TCL soundbar and subwoofer are connected, and this updates their firmware |
| `com.netflix.ninja`, `com.amazon.amazonvideo.livingroom` | Already disabled by the owner before the session; left as they were |
| `com.netflix.tokenmanager` | Left enabled (installed) |
| `com.google.android.videos` | Not installed on this preload |
| (not in the Q7C list) `com.google.android.apps.mediashell` | Off by choice. The Q7C keeps Chromecast |

Everything the Q7C header leaves alone was left alone here too, including `com.tcl.ttvs`, `com.tcl.eva`,
`com.tcl.tv`, `com.tcl.tvinput`, `com.tcl.suspension` and the firmware updater. `com.tcl.factory.view` is
installed and was not opened.

### Remote buttons, and the volume repeat they cost

The helpers were installed with `INPUT_KEY_SERVICE=1 HOME_KEY_SERVICE=1`, with the Q7C keycodes
(`settings_key_keycodes` `[83]`, `app_keys` `190:com.google.android.youtube.tv`). The owner pressed the real
buttons: **Home, Input, the gear and the YouTube button all worked.**

**Holding Volume + on the TCL remote moved the volume one step per press**, with both helpers bound. This is the
symptom in [the G09 key-repeat note](../../docs/devices/tcl-55p71b-g09-key-repeat.md), now seen on a G08 Google TV 14 build. Only
the "both helpers on" state was tried. The owner kept the helpers, because the soundbar's own remote still
ramps the volume continuously. Someone without a soundbar may prefer `"key_filter": false` or no helpers, and
give up the gear and YouTube buttons instead.

### Launcher config used

Pushed with `tools/theme.sh` (`greeting_name` left out here):

```json
{
  "columns": 5,
  "rows_below_dock": 0,
  "dock_apps": ["com.tcl.tv", "com.apple.atve.androidtv.appletv", "org.xbmc.kodi", "com.wbd.stream",
                "com.google.android.youtube.tv", "tunein.player", "com.windscribe.vpn"],
  "hidden_apps": ["com.tcl.dashboard", "com.tcl.partnercustomizer", "com.tcl.suspension", "com.tcl.gallery"],
  "live_tv_package": "com.tcl.tv",
  "app_labels": ["com.tcl.tv=Live TV", "com.wbd.stream=HBO Max"],
  "settings_key_keycodes": [83],
  "app_keys": ["190:com.google.android.youtube.tv"],
  "cinematic_home": false,
  "wallpaper": true,
  "wallpaper_rotation_minutes": 60
}
```

- With seven dock apps and `columns` 7, the tiles were small. `columns` 5 made them larger. The two extra
  dock apps then lead the grid row under the dock, which `rows_below_dock` 0 keeps mostly off screen until
  Down is pressed.
- `cinematic_home` was tried first. With a wallpaper it covers almost all of the picture with the focused
  app's colour. With it off, the wallpaper shows and the ambient glow still tints it in the focused app's
  colour.
- The `wallpapers/` collection was six 1920×1080 JPEGs drawn locally, 55 to 250 KB each. The
  collection loaded and showed one picture. An hourly change was not watched.

### Reboot and closing ADB

After one reboot, `pm list packages -d` returned the same 33 packages as before it: the 29 above, launcherx, and
the three disabled before the session. Nothing came back. HOME still resolved to `com.gathin.tvhome/.MainActivity`,
and `enabled_accessibility_services` still listed `InputKeyService` and `HomeKeyService`.

To close: `tools/tv.py 'settings put global adb_wifi_enabled 0'`, then `'settings put global adb_enabled 0'`.
The connection dropped during these two writes, and `tools/adb-closed.py <tv ip>` then reported 5555 closed. The owner revoked the USB debugging authorisations,
removed the paired computer, switched Wireless debugging and USB debugging off, and rebooted. Afterwards:

- `tools/adb-closed.py` reported `Connection refused`, and `adb mdns services` listed no ADB service.
- A full TCP scan of the TV found 6465, 6466, 6467, 6553, 7000 (AirPlay, kept), 16794 and 45011 open. 16794 and
  45011 accept a TCP connection, but `adb connect` to them stayed `offline`, so they are not ADB. Both were
  already open while debugging was on.

### Test limits

- One set, one firmware, one session and one reboot. Nothing here has been lived with for several days.
- HDMI inputs, the tuner, channel scanning, AirPlay, the Netflix/Prime/app buttons and the microphone button were
  not tested after the list. Live TV and YouTube were opened, not watched for long.
- Standby/wake, a cold boot from mains, and a firmware update are untested.
- The volume repeat was measured with both helpers bound only. No bisect, and no `key_filter` false run.
