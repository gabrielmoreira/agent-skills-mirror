# Migration notes: godot-genre-educational

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `SubViewportContainer.mouse_filter` must be STOP/PASS for input to reach SubViewports.
- Layered SubViewportContainers needing mouse input may need Area2D replacements.
- `CodeEdit.add_code_completion_option` gains `location`; Tree `edit_selected` gains `force_edit`.
- `Object.get_meta_list` return type is `Array[StringName]` (was PackedStringArray).
- `WorkerThreadPool.wait_for_task_completion` now returns `Error`.
- `Basis`/`Transform3D.looking_at` and `Node3D.look_at*` gain optional `use_model_front`.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- `PopupMenu` shortcut helpers gain `allow_echo`; `clear` gains `free_submenus`.
- GraphEdit: `arrange_nodes_button_hidden` → `show_arrange_button`; snap props renamed; `get_zoom_hbox` → `get_menu_hbox`.
- GraphNode: large API move to `GraphElement`; connection query methods removed; `comment`/`show_close` removed.
- `NOTIFICATION_NODE_RECACHE_REQUESTED` removed from Node.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- If the genre uses TileMap, migrate to TileMapLayer nodes before relying on layer APIs.
- If the genre ships multiplayer, upgrade all peers to 4.3 together (SceneMultiplayer protocol).
- Default font outline color is black (was white).
- `auto_translate` deprecated for Node `auto_translate_mode` (inherit semantics).
- `AcceptDialog` register/remove helpers take LineEdit/Button specifically.
- Binary serialization of scripted Objects/typed Arrays changed — re-test save/load of custom Resources.
- `PackedByteArray` may use compact base64 storage; older editors may not open 4.3 resources with large byte arrays.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `GraphEdit.connect_node` gains `keep_alive`; `frame_rect_changed` uses `Rect2`.
- `@export_file` stores `uid://` paths from the Inspector (breaking vs `res://` expectations).
- `FileAccess.store_*` methods return `bool` success.
- `Curve` enforces `min_value`/`max_value` — adjust curves that used points outside `[0, 1]`.
- `OS.read_string_from_stdin` requires `buffer_size`.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- CanvasItem/Font/TextLine draw APIs gain optional `oversampling`.
- `TreeItem.add_button` gains `alt_text`.
- `Resource.duplicate(true)` deep-duplicates **only internal** resources; use `duplicate_deep(DEEP_DUPLICATE_ALL)` for old behavior.
- `Node.get_rpc_config` renamed to `get_node_rpc_config`.
- `JSONRPC.set_scope` replaced by `set_method`.
- `ProjectSettings.add_property_info` warns on invalid/`usage` keys.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- Retune Environment glow/fog if the genre leans on bloom-heavy looks.
- `Control.grab_focus` / `has_focus` gain hide-focus options.
- `FileDialog.add_filter` gains `mime_type`; `SplitContainer.clamp_split_offset` gains `priority_index`.
- `EditorFileDialog` file APIs moved onto `FileDialog` base; `add_side_menu` removed.
- `PopupMenu.submenu_popup_delay` default 0.2 (was 0.3).
- TSCN gains unique node IDs (large VCS diffs on first 4.6 save — expected).
- `FileAccess.get_as_text` drops `skip_cr` parameter.
- `Performance.add_custom_monitor` gains optional `type`.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- Confirm project stretch mode and AudioStreamPlayer area_mask after opening in 4.7.
- `Control.accessibility_live` uses `AccessibilityServer.AccessibilityLiveMode`.
- `TreeItem.select` gains `set_as_cursor`.
- `CanvasItem` no longer adds antialiasing feather that thickened lines — widen strokes if visuals relied on it.
- `Object.is_class` takes `StringName`.
- Setting an element of a packed array property no longer calls the property setter for the whole array.
- Overrides of methods with typed returns must actually `return` (add `return null` if needed).
- New projects default stretch `canvas_items` + aspect `expand` (was `disabled`/`keep`).
