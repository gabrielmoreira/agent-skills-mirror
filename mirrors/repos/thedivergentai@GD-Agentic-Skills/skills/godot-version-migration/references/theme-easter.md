# Migration notes: godot-theme-easter

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `SubViewportContainer.mouse_filter` must be STOP/PASS for input to reach SubViewports.
- Layered SubViewportContainers needing mouse input may need Area2D replacements.
- `CodeEdit.add_code_completion_option` gains `location`; Tree `edit_selected` gains `force_edit`.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- `PopupMenu` shortcut helpers gain `allow_echo`; `clear` gains `free_submenus`.
- GraphEdit: `arrange_nodes_button_hidden` → `show_arrange_button`; snap props renamed; `get_zoom_hbox` → `get_menu_hbox`.
- GraphNode: large API move to `GraphElement`; connection query methods removed; `comment`/`show_close` removed.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- Default font outline color is black (was white).
- `auto_translate` deprecated for Node `auto_translate_mode` (inherit semantics).
- `AcceptDialog` register/remove helpers take LineEdit/Button specifically.
- If the genre uses TileMap, migrate to TileMapLayer nodes before relying on layer APIs.
- If the genre ships multiplayer, upgrade all peers to 4.3 together (SceneMultiplayer protocol).

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `GraphEdit.connect_node` gains `keep_alive`; `frame_rect_changed` uses `Rect2`.

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
- Retune Environment glow/fog if the genre leans on bloom-heavy looks.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- `Control.accessibility_live` uses `AccessibilityServer.AccessibilityLiveMode`.
- `TreeItem.select` gains `set_as_cursor`.
- `CanvasItem` no longer adds antialiasing feather that thickened lines — widen strokes if visuals relied on it.
- Confirm project stretch mode and AudioStreamPlayer area_mask after opening in 4.7.
