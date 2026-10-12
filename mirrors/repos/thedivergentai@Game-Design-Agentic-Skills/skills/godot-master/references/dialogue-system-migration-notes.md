# Migration notes: godot-dialogue-system

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `SubViewportContainer.mouse_filter` must be STOP/PASS for portrait layers receiving clicks.
- `CodeEdit.add_code_completion_option()` gains `location`; `Tree.edit_selected()` gains `force_edit`.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- `GraphEdit`: `arrange_nodes_button_hidden` → `show_arrange_button`; snap props renamed; `get_zoom_hbox()` → `get_menu_hbox()`.
- `GraphNode` APIs moved to **`GraphElement`** — update [dialogue_graph_editor.gd](../scripts/dialogue_system_dialogue_graph_editor.gd) tooling.
- `PopupMenu.clear()` gains `free_submenus` — dialogue debug menus with nested choices.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- Default font outline color **black** (was white) — retheme BBCode dialogue boxes.
- `auto_translate` → **`auto_translate_mode`** — line keys may stop auto-translating nested choice buttons.
- `AcceptDialog` register/remove helpers require `LineEdit`/`Button` types specifically.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `GraphEdit.connect_node()` gains `keep_alive` — long-lived dialogue graph editor sessions.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `RichTextLabel.add_image()` / `update_image()`: `size_in_percent` split into **`width_in_percent`** and **`height_in_percent`** — set both for portrait sizing.
- `TreeItem.add_button()` gains `alt_text` for accessible choice lists.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- `Control.grab_focus()` / `has_focus()` gain hide-focus options — keyboard/gamepad choice navigation.
- `EditorFileDialog` file APIs moved to `FileDialog` base — update `@tool` graph editor import/export.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- `RichTextLabel` ImageUnit: `width_in_percent`/`height_in_percent` → **`width_unit`/`height_unit`** — migrate inline portrait tags in [typebox_effect.gd](../scripts/dialogue_system_typebox_effect.gd) helpers.
- `Control.accessibility_live` uses `AccessibilityServer.AccessibilityLiveMode` — screen-reader choice UI.
- `CanvasItem` line antialiasing feather removed — widen dialogue box borders if they looked thicker before.
