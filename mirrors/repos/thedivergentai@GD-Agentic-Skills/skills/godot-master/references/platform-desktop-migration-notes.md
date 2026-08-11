# Migration notes: godot-platform-desktop

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

*No skill-relevant breaking changes for this hop.*

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

*No skill-relevant breaking changes for this hop.*

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

*No skill-relevant breaking changes for this hop.*

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

*No skill-relevant breaking changes for this hop.*

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `ProjectSettings.add_property_info()` validates keys more loudly — fix desktop settings-menu custom project settings.
- `EditorExportPlatform.get_forced_export_files()` gains optional `preset` for Steam/Epic packaging hooks.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- New Windows projects default **D3D12** rendering driver — verify fullscreen/window modes and GPU selection on player machines.
- New 3D projects default **Jolt** physics — desktop games using Godot Physics may need explicit project setting.
- `EditorExportPreset.get_script_export_mode()` returns enum — update headless Steam depot scripts.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- `InputEvent.DEVICE_ID_MOUSE` / `DEVICE_ID_KEYBOARD` replace magic `0` — fix rebinding code that assumed device id zero is always keyboard.
- **HDR output** on Windows, macOS, and Linux (Wayland) — expose toggle in [desktop_settings_persistent.gd](../scripts/platform_desktop_desktop_settings_persistent.gd) flows.
- New project stretch defaults `canvas_items` + `expand` — test multi-monitor DPI scaling after upgrade.
- Sky reflection `roughness_layers` default restored toward **8** — may change IBL look in 3D desktop titles.
