# Migration notes: godot-physics-3d

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 3.x → 4.0

Official: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html)

- Default 3D physics: Bullet removed → GodotPhysics; expect different contacts/joints — re-tune.
- `KinematicBody` → `CharacterBody3D`; `Spatial` physics helpers → `Node3D` tree.
- Shape resources: `BoxShape`→`BoxShape3D`, `PlaneShape`→`WorldBoundaryShape3D`, `RayShape`→`SeparationRayShape3D`.
- CSG/`VoxelGI` `extents` → `size` with halved numeric values.

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `Area3D.priority` type is `int` (was `float`) — audit gravity-well / trigger priority comparisons in skill examples.
- `PhysicsDirectSpaceState3D.collide_shape()` returns `Array[Vector3]` — update overlap iteration in shapecast and direct-query snippets.
- Viewports with physics picking enabled auto-mark `InputEvent`s handled — drop manual pick-event forwarding in 3D ray/pick tutorials.
- `Geometry3D.segment_intersects_convex` takes `Array[Plane]` — fix convex cast helpers that passed a single plane array incorrectly.
- `MeshInstance3D.create_multiple_convex_collisions` accepts optional `settings` — use when retuning generated collision hulls after import.
- `PathFollow2D.lookahead` removed (2D paths in mixed scenes); `Basis`/`Transform3D.looking_at` and `Node3D.look_at*` gain optional `use_model_front`.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- **Mesh format upgrade** dialog on project open — re-import or run Project → Tools → Upgrade Mesh Surfaces before relying on legacy `.mesh` collision sources.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- `PhysicsShapeQueryParameters3D.motion` is `Vector3` (was `Vector2`) — fix 3D sweep/shapecast examples that copy-pasted 2D motion vectors.
- **Reverse Z** depth convention flipped — custom debug shaders drawing contact normals or depth comparisons may need updated math (see official Reverse Z article).
- `Skeleton3D.add_bone` returns `int32`; pose update signal renamed — update ragdoll setup snippets that assumed old return/signal names.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `SoftBody3D.set_point_pinned()` gains optional `insert_at` — pass ordered pin indices when building cloth attachment lists procedurally.
- **Manifold CSG** required — non-manifold CSG booleans fail; use `MeshInstance3D` trimesh/convex colliders for planes and quads used in world-building.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- Jolt: project setting `physics/jolt_physics_3d/simulation/areas_detect_static_bodies` **removed** — `Area3D` always reports static overlaps; filter with layers/masks instead of that toggle.
- GLTF/BLEND/FBX **Naming Version** for non-joint skeleton nodes — set Import dock version for older rigged collision sources.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- **New projects default 3D physics engine to Jolt** — existing projects keep prior setting; compare Godot Physics vs Jolt before shipping ragdoll/vehicle/soft-body samples.
- `MeshInstance3D.skeleton` default is empty `NodePath` (was implicit parent) — assign skeleton path explicitly in skinned collision/ragdoll scenes.
- SpringBone-related enums moved to `SkeletonModifier3D` — update ragdoll/blend tooling that referenced old enum locations.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- Jolt: `WorldBoundaryShape3D.plane.d` **sign convention flipped** vs 4.6 — negate `d` on infinite floor/ceiling boundaries if colliders shifted after upgrade.
- Jolt: `SoftBody3D` default total mass is **1 kg** (not 0 → per-point auto mass) — retune `linear_stiffness`, `damping_coefficient`, and pin attachments in soft-body presets.
- Jolt: `Area3D` now reports overlaps with `SoftBody3D` — adjust collision layers/masks or you get surprise overlap signals on trigger volumes.
