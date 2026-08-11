# Migration notes: godot-adapt-desktop-to-mobile

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

*No skill-relevant breaking changes for this hop.*

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- Mesh compression upgrade — mobile download size jumps if desktop meshes were uncompressed.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- Android permissions require explicit `OS.request_permission()` — desktop-origin projects often miss VIBRATE/storage prompts.
- `auto_translate_mode` inherit semantics — HUD strings may stop translating after port.
- Default font outline color **black** — retheme dialogue/HUD copied from desktop.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- Motion sensors off by default — enable before porting tilt/gyro desktop prototypes.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- C# Android export requires **.NET 9** when shipping C# mobile builds.
- `ProjectSettings.add_property_info()` stricter validation for mobile-specific settings.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- Mobile renderer glow rewrite — retune bloom when downscaling desktop HDR looks.
- Android `src/main/java/...` layout — update any JNI bridges added during port.
- New Windows dev machines default D3D12 — keep desktop iteration separate from mobile renderer choice.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- Built-in **virtual joystick** — replace desktop keyboard hints with native touch controls.
- New stretch defaults `canvas_items` + `expand` — re-run safe-area and orientation layout tests.
- **HDR mobile output** — verify tonemapping when adapting desktop color grading.
