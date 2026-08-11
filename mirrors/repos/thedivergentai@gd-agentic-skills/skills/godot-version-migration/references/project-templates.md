# Migration notes: godot-project-templates

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `Object.get_meta_list` return type is `Array[StringName]` (was PackedStringArray).
- `WorkerThreadPool.wait_for_task_completion` now returns `Error`.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- `NOTIFICATION_NODE_RECACHE_REQUESTED` removed from Node.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- Binary serialization of scripted Objects/typed Arrays changed — re-test template Resource round-trips.
- `PackedByteArray` may use compact base64 storage; older editors may not open 4.3 resources with large byte arrays.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `@export_file` stores `uid://` paths from the Inspector (breaking vs `res://` expectations).
- `FileAccess.store_*` methods return `bool` success.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `Resource.duplicate(true)` deep-duplicates **only internal** resources; use `duplicate_deep(DEEP_DUPLICATE_ALL)` for old behavior.
- `ProjectSettings.add_property_info` warns on invalid/`usage` keys.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- TSCN gains unique node IDs (large VCS diffs on first 4.6 save — expected for scaffold scenes).
- New project defaults: **D3D12** on Windows; **Jolt** for 3D physics — document in FPS/3D template rows.
- `MeshInstance3D.skeleton` default is empty NodePath — enable compatibility setting if old parent-skeleton behavior needed.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- New projects default stretch **mode** `canvas_items` (was `disabled`); **aspect** `expand` (was `keep`) — override in template bootstrap if legacy behavior is required.
- **Asset Store** replaces **Asset Library** naming in the editor.
- Sky reflection roughness_layers default restored toward 8.
- `Object.is_class` takes `StringName`.
- Setting an element of a packed array property no longer calls the property setter for the whole array.
- Overrides of methods with typed returns must actually `return` (add `return null` if needed).
