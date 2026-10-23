# TCL 43S450F-CA (TCL S4 Fire TV Edition, Fire OS 8.1.8.5)

TCL 43" S4 Fire TV Edition, Amazon model `AFTDEC012E`, codename `ginza`, Fire OS 8.1.8.5 (RS8185/3885) on
Android 11 (SDK 30), MediaTek, ATSC tuner, 1.8 GB RAM. Canadian set with the UI in Spanish. Done over Wi-Fi
on 21 October 2026 with `tools/tv.py` (adb-shell, no adb binary; port 5555 opens as soon as ADB debugging is
on, no pairing). The first TCL Fire TV Edition list here; same firmware line as `amazon-fire-tv-stick-4k-2023/`
and `hisense-fire-tv-aftcibfbd1/`.

| File | What it is |
|---|---|
| `debloat.txt` | The 45 packages that were disabled, grouped and commented, plus the 7 that Fire OS protects |

All commands run from the repo root with the TV's IP in `TV_HOST`.

## What worked and what did not

**Debloat: yes.** Telemetry, ACR, ad bidding and sponsored rows, Fire TV Channels, Shopping, demo content,
popups, Amazon Photos, Kids, miniTV, Silk, tutorials, other-Amazon-device setup, the Matter controller, the
screensaver, and the unused streaming apps (Crave, Paramount+, Max, Apple TV). Applied in four batches with a
screenshot after each, then rebooted: all 45 stayed disabled, Home, YouTube and Live TV settings open.
Seven packages are protected (`Cannot disable a protected package`), the same set as the Stick 4K 2023 list:
device.metrics, device.logmanager, device.crashmanager, diode, usagestats.proxy, ftvads.deeplinking, tv.csapp.

**Launcher: no.** This is Fire OS, not Google TV. `com.amazon.tv.launcher` owns Home at priority 950 and is a
protected package, so `launcher/build-and-install.sh` does not apply. The hero banner at the top of Home is
the launcher's own feed and stays; the recommendation rows under it are gone once `media.recommendations`
and `kso.blackbird` are off.

## Apply and undo

```
TV_HOST=<tv ip> tools/disable.sh examples/tcl-43s450f-ca/debloat.txt
TV_HOST=<tv ip> tools/restore.sh examples/tcl-43s450f-ca/debloat.txt com.amazon.tv.launcher
TV_HOST=<tv ip> tools/tv.py "pm enable --user 0 com.cbs.ca"      # one app back
```

## Notes

- Alexa voice was kept on this set, so none of the Alexa helpers that return at every boot on other Fire OS 8
  sets (`vizzini` and friends) were in the list; nothing came back after the reboot.
- The favourites bar on Home keeps tiles for apps that are now disabled (Max, Internet, Photos, Kids+) and
  placeholders (DAZN, Twitch): highlight one, press the ☰ button and remove it.
- Settings > Preferences > Privacy Settings (device and app usage data, interest-based ads) and Featured
  Content autoplay are account-synced toggles: turn them off in the menu, not with `settings put`.
- Closing ADB from the shell: `settings put global adb_enabled 0` closes port 5555 at once (the connection
  drops, as expected). A backgrounded `nohup ... reboot` dies with the shell session on this firmware, so
  reboot from the TV's menu afterwards.
- Kept on purpose: Prime Video, Amazon Music, Luna, Alexa, AirPlay, Miracast, DIAL casting, OTA updates,
  Live TV and the tuner, Tubi, Pluto TV, Netflix, YouTube, Spotify and the owner's own sideloads.
