# Migration notes: godot-composition-apps

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `SubViewportContainer.mouse_filter` must be STOP/PASS for embedded editor panes.
- `Object.get_meta_list()` returns `Array[StringName]`.
- `WorkerThreadPool.wait_for_task_completion()` returns **`Error`** — handle failures in background import jobs.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- `GraphEdit` / `GraphNode` API moves (see dialogue graph notes) — update composable node-tool UIs.
- `NOTIFICATION_NODE_RECACHE_REQUESTED` removed.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- `auto_translate_mode` inherit semantics — tool UI strings may need explicit locale nodes.
- Binary serialization of custom `Resource` components changed — re-test saved workspace layouts.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `@export_file` stores `uid://` paths — component graphs referencing files by `res://` string need UID resolution.
- `FileAccess.store_*()` returns **`bool`** — check failures when persisting app layouts to `user://`.
- `Curve` enforces min/max — remap animation curves used in UI tweens.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `Resource.duplicate(true)` deep-copies internal resources only — use `duplicate_deep(DEEP_DUPLICATE_ALL)` when cloning nested component trees.
- `ProjectSettings.add_property_info()` stricter validation for plugin-declared settings.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- `EditorFileDialog` APIs moved to `FileDialog` — update `@tool` composition editors.
- TSCN unique node IDs — first save after upgrade produces large diffs in tool scenes.
- `FileAccess.get_as_text()` drops `skip_cr` parameter.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- New project stretch defaults `canvas_items` + `expand` — dockable tool UIs may need anchor pass.
- Packed array element assignment no longer triggers property setter — reactive UI binding via typed arrays needs audit.
- Typed-return overrides must explicitly `return` — fix `@tool` scripts with typed `_get()`/`_set()`.
- `Control.accessibility_live` enum — expose live regions in accessible tool palettes.
