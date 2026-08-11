# Migration notes: godot-inventory-system

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `SubViewportContainer.mouse_filter` must be STOP/PASS for input to reach SubViewports (3D preview panes).
- Layered SubViewportContainers needing mouse input may need Area2D replacements.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- `PopupMenu` shortcut helpers gain `allow_echo`; `clear` gains `free_submenus` (context split/stack menus).
- GraphEdit/GraphNode API moves — only if crafting trees use visual graphs.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- Scripted Object / typed Array binary serialization changes — verify Item/Inventory Resource round-trips.
- Large `PackedByteArray` storage format may not open in older editors.
- Default font outline color is black (was white) — retune slot count/quantity labels.
- `auto_translate` deprecated for Node `auto_translate_mode` (inherit semantics).

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `@export_file` stores `uid://` paths from the Inspector — resolve UIDs in icon/effect Resource paths.
- `FileAccess.store_*` methods return `bool` success — handle stash save failures.
- `Curve` enforces `min_value`/`max_value`.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `Resource.duplicate(true)` deep-duplicates **only internal** resources; use `duplicate_deep(DEEP_DUPLICATE_ALL)` when cloning full item stacks with external refs.
- CanvasItem/Font/TextLine draw APIs gain optional `oversampling`.
- `TreeItem.add_button` gains `alt_text` (equipment slot actions).

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- First save in 4.6 rewrites scenes with unique node IDs — expect large diffs on inventory UI scenes.
- `Control.grab_focus` / `has_focus` gain hide-focus options (drag/drop focus rings).
- `PopupMenu.submenu_popup_delay` default 0.2 (was 0.3).

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- Confirm project stretch mode and `AudioStreamPlayer.area_mask` after opening in 4.7.
- Re-validate Resource pipelines after packed-array setter and typed-return GDScript changes (stack counts, proc bindings).
- `CanvasItem` no longer adds antialiasing feather that thickened lines — widen slot border strokes if needed.
