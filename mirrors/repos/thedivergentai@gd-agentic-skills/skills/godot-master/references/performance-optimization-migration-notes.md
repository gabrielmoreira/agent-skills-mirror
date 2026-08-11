# Migration notes: godot-performance-optimization

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 3.x → 4.0

Official: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html)

- 4.x baseline memory/binary size higher — re-measure budgets.
- 2D HDR off by default — overbright modulate; enable HDR 2D if needed (later 4.2+ setting).
- Servers renamed (`VisualServer`→`RenderingServer`, physics 2D/3D servers).
- Multithreading API changes — rewrite workers before claiming perf wins.

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `Object.get_meta_list` return type is `Array[StringName]` (was PackedStringArray).
- `WorkerThreadPool.wait_for_task_completion` now returns `Error`.
- `RenderingServer.global_shader_parameter_get_list` / RD shader version lists return `Array[StringName]`.
- `RenderingDevice.draw_list_begin` storage_textures typed as `Array[RID]`.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- `NOTIFICATION_NODE_RECACHE_REQUESTED` removed from Node.
- **Mesh format** upgrade — use Project → Tools → Upgrade Mesh Surfaces; Restart & Upgrade prevents downgrade.
- ImporterMesh/MeshDataTool/SurfaceTool compression flag widths → `uint64`.
- RenderingDevice BarrierMask enum values changed.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- Binary serialization of scripted Objects/typed Arrays changed — re-test save/load of custom Resources.
- `PackedByteArray` may use compact base64 storage; older editors may not open 4.3 resources with large byte arrays.
- **Reverse Z** depth — update custom shaders (depth compare, `POSITION.z` assumptions).
- Decal modulate converted sRGB→linear — visuals change.
- RenderingDevice barrier/draw_list API simplified (post_barrier params removed).

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `@export_file` stores `uid://` paths from the Inspector (breaking vs `res://` expectations).
- `FileAccess.store_*` methods return `bool` success.
- `Curve` enforces `min_value`/`max_value` — adjust curves that used points outside `[0, 1]`.
- `RenderingDevice.draw_list_begin` signature overhauled (params removed + breadcrumb).
- `Shader` default texture parameter types use `Texture` / `TextureLayered`.
- `VisualShaderNodeVec4Constant` input type → Vector4 — recreate constants.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `Resource.duplicate(true)` deep-duplicates **only internal** resources; use `duplicate_deep(DEEP_DUPLICATE_ALL)` for old behavior.
- `Node.get_rpc_config` renamed to `get_node_rpc_config`.
- `ProjectSettings.add_property_info` warns on invalid/`usage` keys.
- `RenderingServer.instance_reset_physics_interpolation` / `instance_set_interpolated` removed.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- TSCN gains unique node IDs (large VCS diffs on first 4.6 save — expected).
- `Performance.add_custom_monitor` gains optional `type`.
- Glow default blend **Screen** (brighter) — retune Environment glow; Mobile glow rewrite looks different.
- Volumetric fog blending brighter — reduce density/energy.
- New project defaults: D3D12 on Windows; Jolt for 3D physics — document for templates/benchmark baselines.
- `MeshInstance3D.skeleton` default is empty NodePath — enable compatibility setting if old parent-skeleton behavior needed.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- New projects default stretch `canvas_items` + aspect `expand` (was `disabled`/`keep`) — note vs legacy viewport stretch in UI perf sections.
- `Object.is_class` takes `StringName`.
- Setting an element of a packed array property no longer calls the property setter for the whole array.
- Overrides of methods with typed returns must actually `return` (add `return null` if needed).
- `Texture2D.get_format()` unified on base class — use when teaching format-specific import/shader pipelines.
- Prefer **AreaLight3D** for rectangular soft lights; HDR output available on major platforms.
