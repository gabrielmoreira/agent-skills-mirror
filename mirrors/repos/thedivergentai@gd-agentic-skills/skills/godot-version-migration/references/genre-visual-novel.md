# Migration notes: godot-genre-visual-novel

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `SubViewportContainer.mouse_filter` must be STOP/PASS for input to reach SubViewports (character portrait layers).
- Layered SubViewportContainers needing mouse input may need Area2D replacements.
- `RichTextLabel.push_list` gains `bullet`; `push_paragraph` gains justification/tab_stops optionals.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- `RichTextLabel.add_image` gains `key`, `pad`, `tooltip`, `size_in_percent` optionals.
- `PopupMenu` shortcut helpers gain `allow_echo`; `clear` gains `free_submenus`.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- If the genre uses TileMap, migrate to `TileMapLayer` nodes before relying on layer APIs.
- If the genre ships multiplayer, upgrade all peers to 4.3 together (`SceneMultiplayer` protocol).
- Default font outline color is black (was white) — retune dialogue/nameplate themes.
- `auto_translate` deprecated for Node `auto_translate_mode` (inherit semantics) — verify localized choice menus.
- `RichTextLabel.push_meta` gains `underline_mode`.
- `AcceptDialog` register/remove helpers take LineEdit/Button specifically.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `RichTextLabel.push_meta` gains `tooltip`; `set_table_column_expand` gains `shrink`.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `add_image`/`update_image`: `size_in_percent` replaced by `width_in_percent` and `height_in_percent` — set both for inline CG/sprite sizing.
- CanvasItem/Font/TextLine draw APIs gain optional `oversampling`.
- `TreeItem.add_button` gains `alt_text` (choice/history lists).

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- Retune Environment glow/fog if the genre leans on bloom-heavy looks (title screens, dream sequences).
- `Control.grab_focus` / `has_focus` gain hide-focus options — useful for auto-advance vs keyboard focus.
- `PopupMenu.submenu_popup_delay` default 0.2 (was 0.3).

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- Confirm project stretch mode and `AudioStreamPlayer.area_mask` after opening in 4.7.
- `width_in_percent`/`height_in_percent` → `width_unit`/`height_unit` with `RichTextLabel.ImageUnit` — migrate inline CG/sprite tags.
- `ImageUpdateMask.UPDATE_WIDTH_IN_PERCENT` → `UPDATE_WIDTH_UNIT`.
- `add_image`/`update_image` width/height are `float` — **NEVER** pass bool percent flags.
- `CanvasItem` no longer adds antialiasing feather that thickened lines — widen dialogue box strokes if borders looked bolder.
