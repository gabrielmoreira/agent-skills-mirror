# Migration notes: godot-ui-theming

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 3.x → 4.0

Official: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html)

- Theme API: `get_stylebox` → `get_theme_stylebox`; checked/unchecked icon names.
- Fonts → `FontFile`; rebuild theme resources.
- Control offsets replace margins.

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `SubViewportContainer.mouse_filter` must be STOP/PASS for input to reach SubViewports embedded in themed HUD shells.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- Font fallback property structure changed — update Theme/default-font fallback chains.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- Default font outline color is black (was white) — rebalance outline-only Theme overrides.
- `auto_translate` deprecated for Node `auto_translate_mode` (inherit semantics).

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

*No skill-relevant breaking changes for this hop.*

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- CanvasItem/Font/TextLine draw APIs gain optional `oversampling`.
- `ProjectSettings.add_property_info` warns on invalid/`usage` keys — validate custom theme-related project settings.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- `Control.grab_focus` / `has_focus` gain hide-focus options.
- `PopupMenu.submenu_popup_delay` default 0.2 (was 0.3).

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- New projects default stretch `canvas_items` + aspect `expand` — retest Theme scale on legacy `viewport`/`keep` projects.
- **Control offset transform** for inspector-driven visual tweaks without relayout.
- `ResourceImporterDynamicFont.hinting` default changed to **3** — verify font crispness on target DPI.
- **GradientTexture2D** supports **conic** gradients in Theme icon/background recipes.
- `CanvasItem` no longer adds antialiasing feather that thickened lines — widen themed separator strokes if needed.
