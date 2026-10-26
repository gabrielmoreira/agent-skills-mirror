# HY320 Projector — CleanYourTV Setup

## Device
- **Model**: HY320 projector (t950s_be311, Google-certified Android TV)
- **Android**: 13 (SDK 33)
- **Firmware**: be311-13 TQ2A.20250729 06:21:20.E1
- **Resolution**: 1280x720, 213dpi

## What was done
1. **Debloated 24 packages** — ad services, app stores, background junk, unused preloaded apps
2. **Installed Apple TV-style launcher** (com.gathin.tvhome) with dock: Netflix, YouTube, Wave IPTV, MX Player
3. **Set launcher as default home**, disabled stock launcher (com.htc.htclauncherhighenglishd08)
4. **Enabled AdGuard Private DNS** for ad blocking

## Re-enable an app
```sh
TV_HOST=<tv ip> tools/venv/bin/python tools/tv.py 'pm enable --user 0 <package>'
```

## Restore everything (undo the debloat)
```sh
TV_HOST=<tv ip> tools/restore.sh examples/hy320/debloat.txt
```

## Rebuild and reinstall the launcher
```sh
cd launcher
JAVA_HOME=/opt/homebrew/opt/openjdk@17 ANDROID_HOME=/opt/homebrew/share/android-commandlinetools \
  TV_HOST=<tv ip> bash build-and-install.sh
```

## Change dock apps or order
Edit `launcher/app/src/main/res/values/config.xml`, the `dock_apps` array, then rebuild.
Or push a theme: edit `examples/hy320/config.json` and run:
```sh
TV_HOST=<tv ip> tools/theme.sh examples/hy320/config.json
```

## Change wallpaper
Set `wallpaper: true` in config.json and add a wallpaper image, or use a theme folder under `themes/`.

AdGuard Private DNS works on this TV.

## Firmware note: HOME.JM
This projector's firmware routes the Home key through a custom `android.intent.category.HOME.JM`
category (from the JM launcher that was preloaded). The launcher's AndroidManifest.xml was updated
to include this category in its HOME intent filter. If you rebuild from a clean checkout, that
change must be re-applied or the Home key will go to FallbackHome instead of the launcher.

## Security
This TV has `ro.adb.secure` unset, meaning port 5555 accepts any device on the network without
a prompt. ADB was left open during setup. When done, turn off USB debugging and Network/ADB
debugging on the TV (Settings > Developer Options), revoke USB debugging authorisations, and
reboot. Verify with:
```sh
tools/adb-closed.py <tv ip>
```
