# Migration notes: godot-3d-world-building

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `MeshInstance3D.create_multiple_convex_collisions` optional `settings` — update procedural collision-from-mesh recipes.
- `Node3D.look_at` / `look_at_from_position` gain optional `use_model_front`.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- **Mesh format** upgrade — use Project → Tools → Upgrade Mesh Surfaces; Restart & Upgrade prevents downgrade.
- ImporterMesh/MeshDataTool/SurfaceTool compression flag widths → `uint64`.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- `Skeleton3D.add_bone` returns `int32`; `bone_pose_changed` → `skeleton_updated` — fix rigged prop attachment in levels.
- Binary serialization of scripted Objects/typed Arrays changed — re-test save/load of custom level/chunk Resources.
- `PackedByteArray` may use compact base64 storage; older editors may not open 4.3 resources with large byte arrays.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- CSG uses Manifold — **non-manifold** CSG booleans unsupported; use MeshInstance3D for quads, planes, and open meshes.
- `@export_file` stores `uid://` paths from the Inspector — level tools expecting `res://` must resolve UIDs.
- `FileAccess.store_*` methods return `bool` success — handle failures in procedural save/export helpers.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- GLTF/BLEND/FBX naming version for non-joint nodes in skeletons — set Import dock Naming Version for kitbash assets.
- `Resource.duplicate(true)` deep-duplicates **only internal** resources; use `duplicate_deep(DEEP_DUPLICATE_ALL)` when cloning level Resource graphs.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- `MeshInstance3D.skeleton` default empty NodePath — explicit skeleton paths required for skinned kit pieces.
- TSCN gains unique node IDs (large VCS diffs on first 4.6 save — expected for level scenes).

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- **Path3D** snap-to-colliders for placing spline points on geometry.
- **3D vertex snapping** with vertex/origin base setting (editor B key workflow).
- Prefer **AreaLight3D** for built-in rectangular area lights in blockout scenes.
- `EditorSceneFormatImporter` import constants live under `ImportFlags` enum — update custom import tooling.
