# Migration notes: godot-platform-mobile

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

*No skill-relevant breaking changes for this hop.*

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- Mesh compression upgrade dialog — plan bandwidth for cellular downloads after upgrading `.mesh` assets.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- Android permissions are **not** auto-requested — use `OS.request_permission()` + `MainLoop.on_request_permissions_result` (see [android_runtime_permissions.gd](../scripts/android_runtime_permissions.gd)).
- `auto_translate` → **`auto_translate_mode`** — localized HUD may stop translating if children inherit DISABLED.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- Accelerometer/gyro **disabled by default** — enable sensors in Project Settings before [mobile_sensor_fusion.gd](../scripts/mobile_sensor_fusion.gd) patterns work on export.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- C# Android export requires **.NET 9**.
- `EditorExportPlatform.get_forced_export_files()` gains optional `preset` parameter.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- Android Gradle tree uses `src/main/java/...` — update custom JNI/Java plugin paths.
- Mobile Environment **glow** looks brighter after renderer rewrite — retune bloom before store screenshots.
- `EditorExportPreset.get_script_export_mode()` returns enum type.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- Built-in **virtual joystick** available — prefer over third-party touch plugins when remapping desktop controls.
- **HDR output** on iOS and supported Android panels — test tonemapping on real hardware, not editor-only.
- New project stretch defaults `canvas_items` + `expand` — re-check safe-area layouts on notched devices.
