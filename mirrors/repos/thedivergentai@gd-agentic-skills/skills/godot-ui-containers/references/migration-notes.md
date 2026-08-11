# Migration notes: godot-ui-containers

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 3.x → 4.0

Official: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html)

- `Control.margin` → `offset`; theme `get_stylebox` → `get_theme_stylebox`.
- `ToolButton` → `Button` with Flat; `TextureProgress` → `TextureProgressBar`.
- `PopupMenu` / button signals: verify `pressed` vs `button_up`/`button_down` renames.
- YSort node removed — use CanvasItem **Y Sort Enabled**.

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `SubViewportContainer.mouse_filter` must be STOP/PASS for input to reach SubViewports.
- Layered SubViewportContainers needing mouse input may need Area2D replacements.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- `PopupMenu` shortcut helpers gain `allow_echo`; `clear` gains `free_submenus`.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- Default font outline color is black (was white).
- `auto_translate` deprecated for Node `auto_translate_mode` (inherit semantics).
- `AcceptDialog` register/remove helpers take LineEdit/Button specifically.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

*No skill-relevant breaking changes for this hop.*

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- CanvasItem/Font/TextLine draw APIs gain optional `oversampling`.
- `TreeItem.add_button` gains `alt_text`.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- `Control.grab_focus` / `has_focus` gain hide-focus options.
- `FileDialog.add_filter` gains `mime_type`; `SplitContainer.clamp_split_offset` gains `priority_index`.
- `EditorFileDialog` file APIs moved onto `FileDialog` base; `add_side_menu` removed.
- `PopupMenu.submenu_popup_delay` default 0.2 (was 0.3).

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- `Control.accessibility_live` uses `AccessibilityServer.AccessibilityLiveMode`.
- **Control offset transform** — visual offset without breaking container layout constraints.
- **TextureRect** can tile **AtlasTexture** regions as repeating textures.
- `CanvasItem` no longer adds antialiasing feather that thickened lines — widen panel/separator strokes if visuals relied on it.
