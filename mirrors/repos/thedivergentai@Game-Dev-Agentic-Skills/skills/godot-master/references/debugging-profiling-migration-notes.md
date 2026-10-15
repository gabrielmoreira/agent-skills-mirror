# Migration notes: godot-debugging-profiling

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 3.x → 4.0

Official: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html)

- `VisualServer` → `RenderingServer`; render info getter renamed.
- Debugger/monitors still apply — re-bind custom monitors after API renames.
- Threading: `Thread.start` Callable form; `is_active` → `is_alive`.

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `Object.get_meta_list` return type is `Array[StringName]` (was PackedStringArray).
- `WorkerThreadPool.wait_for_task_completion` now returns `Error`.
- `Basis`/`Transform3D.looking_at` and `Node3D.look_at*` gain optional `use_model_front`.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- `NOTIFICATION_NODE_RECACHE_REQUESTED` removed from Node.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- Binary serialization of scripted Objects/typed Arrays changed — re-test save/load of custom Resources.
- `PackedByteArray` may use compact base64 storage; older editors may not open 4.3 resources with large byte arrays.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `@export_file` stores `uid://` paths from the Inspector (breaking vs `res://` expectations).
- `FileAccess.store_*` methods return `bool` success.
- `Curve` enforces `min_value`/`max_value` — adjust curves that used points outside `[0, 1]`.
- `OS.read_string_from_stdin` requires `buffer_size`.
- `@export_file` Inspector assignments become `uid://` — scripts expecting `res://` strings must resolve UIDs or use `@export_file_path` (4.5+).

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `Resource.duplicate(true)` deep-duplicates **only internal** resources; use `duplicate_deep(DEEP_DUPLICATE_ALL)` for old behavior.
- `Node.get_rpc_config` renamed to `get_node_rpc_config`.
- `JSONRPC.set_scope` replaced by `set_method`.
- `ProjectSettings.add_property_info` warns on invalid/`usage` keys.
- `add_property_info` validates keys more loudly.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- TSCN gains unique node IDs (large VCS diffs on first 4.6 save — expected).
- `FileAccess.get_as_text` drops `skip_cr` parameter.
- `Performance.add_custom_monitor` gains optional `type`.
- New project defaults: D3D12 on Windows; Jolt for 3D physics — document for templates.
- `MeshInstance3D.skeleton` default is empty NodePath — enable compatibility setting if old parent-skeleton behavior needed.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- `Object.is_class` takes `StringName`.
- Setting an element of a packed array property no longer calls the property setter for the whole array.
- Overrides of methods with typed returns must actually `return` (add `return null` if needed).
- New projects default stretch `canvas_items` + aspect `expand` (was `disabled`/`keep`).
- New project stretch defaults `canvas_items` + `expand`.
- Sky reflection roughness_layers default restored toward 8.
- Packed array element assignment no longer triggers whole-property setter.
- Typed-return overrides require an explicit return statement.
