# Migration notes: godot-resource-data-patterns

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 3.x → 4.0

Official: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html)

- ResourceSaver argument order; FileAccess static open patterns.
- `Shortcut` spelling; `ShortCut` → `Shortcut`.
- Reimport textures/meshes; ArrayMesh break.

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

*No skill-relevant breaking changes for this hop.*

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

*No skill-relevant breaking changes for this hop.*

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- Scripted Object / typed Array binary serialization changes — verify Resource round-trips and save bundles.
- Large `PackedByteArray` storage format may not open in older editors.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `@export_file` stores `uid://` paths from the Inspector — scripts expecting `res://` strings must resolve UIDs or use `@export_file_path` (4.5+).
- `FileAccess.store_*` methods return `bool` success — add error checks to custom serializers.
- `Curve` enforces `min_value`/`max_value` — clamp runtime curve edits for data-driven tables.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `Resource.duplicate(true)` deep-duplicates **only internal** resources; use `duplicate_deep(DEEP_DUPLICATE_ALL)` for full external subgraph clones.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- First save in 4.6 rewrites scenes with unique node IDs.
- Scene unique IDs change diffs — migrate save schemas if they keyed on old node identity assumptions.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- Packed array element assignment no longer triggers whole-property setter — audit data-binding Resources using typed arrays.
- Typed-return overrides require an explicit `return` statement in custom Resource subclasses.
