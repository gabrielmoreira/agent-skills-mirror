# Migration notes: godot-save-load-systems

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 3.x → 4.0

Official: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html)

- `File`/`Directory` → `FileAccess`/`DirAccess` (often static APIs).
- `ResourceSaver.save` argument order swapped (`resource`, `path`).
- Time via `Time` singleton (not OS); JSON helpers differ from 3.x Dictionary.to_json patterns.
- Keep **save schema** versioning separate from **engine** hops — still bump save version when fields change.

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

*No skill-relevant breaking changes for this hop.*

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

*No skill-relevant breaking changes for this hop.*

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- Scripted Object / typed `Array` binary serialization changed — round-trip all save `Resource` schemas.
- Large `PackedByteArray` compact storage may not open in older editors — avoid downgrading save files.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `FileAccess.store_var()` / `store_buffer()` return **`bool`** — handle write failures; never assume success.
- `@export_file` Inspector values may store `uid://` — resolve UIDs when loading designer-assigned default save paths.
- `Curve` enforces configured min/max — remapping curves in save-slot metadata may clamp unexpectedly.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `Resource.duplicate(true)` deep-copies **internal** resources only — use `duplicate_deep(DEEP_DUPLICATE_ALL)` when cloning save templates with external sub-resources.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- TSCN unique node IDs on first 4.6 save — do not key saves on ephemeral node instance ids from `.tscn` order.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- Packed array element assignment no longer invokes custom setters — typed-array save caches may stop emitting change signals.
- Typed-return overrides must explicitly `return` — audit save-manager methods with typed returns.
