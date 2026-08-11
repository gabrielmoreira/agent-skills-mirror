# Migration notes: godot-adapt-mobile-to-desktop

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

*No skill-relevant breaking changes for this hop.*

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- Mesh compression upgrade particularly affects mobile bandwidth — plan mesh upgrade dialog carefully.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- Android permissions are **not** auto-requested — use `OS.request_permission` + `MainLoop.on_request_permissions_result`.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- Android sensors off by default for exports that relied on them.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- C# Android export requires **.NET 9** (other platforms still .NET 8+).
- `EditorExportPlatform.get_forced_export_files` gains optional `preset`.
- `add_property_info` validates keys more loudly.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- Mobile renderer glow rewrite looks different — retune Environment.
- Android export template source layout matches Android Studio (`src/main/java/...`) — update custom Java patches.
- `EditorExportPreset.get_script_export_mode` returns enum type.
- New project defaults: D3D12 on Windows; Jolt for 3D physics — document for templates.
- `MeshInstance3D.skeleton` default is empty NodePath — enable compatibility setting if old parent-skeleton behavior needed.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- Prefer built-in virtual joystick over third-party touch plugins where possible.
- Asset Library workflow → **Asset Store** in editor — update docs/tooling that pointed at old Asset Library UX.
- `EditorSceneFormatImporter` import constants live under `ImportFlags` enum.
- New project stretch defaults `canvas_items` + `expand`.
- Sky reflection roughness_layers default restored toward 8.
