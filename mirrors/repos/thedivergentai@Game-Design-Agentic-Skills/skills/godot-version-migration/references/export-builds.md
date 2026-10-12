# Migration notes: godot-export-builds

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 3.x → 4.0

Official: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html)

- Export presets / feature tags need re-validation on 4.0.
- C#: Mono → .NET 6; mobile/web export support historically incomplete — verify target platforms.
- No GLES2 — use Compatibility (GLES3) for old GPUs; binary size larger than 3.x.
- Re-run export after each later 4.x hop that touches platforms.

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

*No skill-relevant breaking changes for this hop.*

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- Mesh format upgrade dialog on project open — re-export mobile/desktop builds after upgrading compressed meshes.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- Android permissions are **not** auto-granted from export presets — call `OS.request_permission()` and handle `MainLoop.on_request_permissions_result`.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- Android accelerometer/gyro **off by default** — enable under Project Settings → Input Devices → Sensors before shipping motion-aware exports.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- C# Android export targets **.NET 9** (other C# platforms remain .NET 8+).
- `EditorExportPlatform.get_forced_export_files()` gains optional `preset` — update custom export plugins that enumerate forced files.
- `ProjectSettings.add_property_info()` validates keys more strictly — fix invalid export-plugin property metadata.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- Android export template Java sources moved to `android/build/src/main/java/...` (Android Studio layout) — patch custom Gradle/Java integrations.
- `EditorExportPreset.get_script_export_mode()` now returns an enum — adjust headless export scripts comparing ints.
- New Windows projects default **D3D12**; new 3D projects default **Jolt** — smoke-test CI matrix against your pinned backends.
- Mobile renderer glow rewrite — retune Environment before comparing mobile export sizes/screenshots.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- Editor **Asset Store** replaces Asset Library naming — update release runbooks that reference addon install UX.
- `EditorSceneFormatImporter` constants moved under `ImportFlags` enum — fix custom import/export tooling.
- Verify per-platform **HDR viewport** settings in export presets (desktop/mobile) after upgrading templates.
- New project stretch defaults `canvas_items` + `expand` — regression-test UI scale in exported builds, not only editor.
