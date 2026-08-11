# Migration notes: godot-genre-shooter-fps

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `Area3D.priority` type is `int` (was `float`) — audit hitbox/trigger ordering.
- `PhysicsDirectSpaceState3D.collide_shape` returns `Array[Vector3]`.
- `Geometry3D.segment_intersects_convex` takes `Array[Plane]`.
- `MeshInstance3D.create_multiple_convex_collisions` optional `settings`.
- `Node3D.look_at` / `look_at_from_position` gain `use_model_front` — retune weapon/ADS aim helpers.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- **Mesh format** upgrade — use Project → Tools → Upgrade Mesh Surfaces on weapon/environment meshes.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- If the genre uses TileMap, migrate to `TileMapLayer` nodes before relying on layer APIs.
- If the genre ships multiplayer, upgrade all peers to 4.3 together (`SceneMultiplayer` protocol).
- `PhysicsShapeQueryParameters3D.motion` is `Vector3` (was `Vector2`) — fix hitscan/sweep queries.
- **Reverse Z** depth — update custom scope/post shaders and decal blood overlays.
- `Skeleton3D.add_bone` returns `int32`; pose update signal rename.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- CSG uses Manifold — **non-manifold** meshes unsupported; use `MeshInstance3D` for blocking volumes and planes.
- `SoftBody3D.set_point_pinned` gains optional `insert_at`.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `Node.get_rpc_config` → `get_node_rpc_config` — audit weapon/fire RPC configs.
- Jolt: `physics/jolt_physics_3d/simulation/areas_detect_static_bodies` removed — Areas always report static overlaps; filter via layers/masks.
- GLTF/BLEND/FBX naming version for non-joint nodes in skeletons — set Import dock Naming Version for old weapon rigs.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- Retune Environment glow/fog if the genre leans on bloom-heavy looks (muzzle flash, lens dirt).
- New projects default 3D physics engine to **Jolt** — existing projects keep prior setting; verify Jolt differences before shipping.
- `MeshInstance3D.skeleton` default empty; SpringBone enums moved to `SkeletonModifier3D`.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- Confirm project stretch mode and `AudioStreamPlayer.area_mask` after opening in 4.7.
- `AudioStreamPlayer.area_mask` default is **0** — set mask for room/zone weapon reverb and footstep buses.
- Jolt: `WorldBoundaryShape3D.plane.d` sign convention flipped vs 4.6 — negate if kill planes moved.
- Jolt: `SoftBody3D` default mass is 1 kg for the body — retune gore/ragdoll stiffness/damping.
- Prefer **AreaLight3D** for soft rectangular muzzle/portal lights without GI hacks.
