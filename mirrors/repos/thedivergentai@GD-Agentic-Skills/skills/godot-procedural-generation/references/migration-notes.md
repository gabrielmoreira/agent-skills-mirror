# Migration notes: godot-procedural-generation

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `PathFollow2D.lookahead` removed — update 2D spline followers on generated paths.
- `MeshInstance3D.create_multiple_convex_collisions` optional `settings` — retune runtime mesh collider baking.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- **Mesh format** upgrade — use Project → Tools → Upgrade Mesh Surfaces on generated/imported meshes.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- **TileMap layers → `TileMapLayer` nodes** — migrate tile-based chunk/world generators before relying on layer APIs.
- `Skeleton3D.add_bone` returns `int32`; pose update signal rename.
- **Reverse Z** depth — update custom terrain/splat shaders comparing depth.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- CSG uses Manifold — **non-manifold** meshes unsupported; bake proc meshes to `MeshInstance3D` instead of CSG booleans.
- `FileAccess.store_*` methods return `bool` success — handle chunk save failures.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `TileMapLayer.get_coords_for_body_rid` less precise with physics chunking — set `physics_quadrant_size = 1` for tile-collision debug of generated worlds.
- GLTF/BLEND/FBX naming version for non-joint nodes in skeletons — set Import dock Naming Version for instanced props.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- Retune Environment glow/fog if the genre leans on bloom-heavy looks (biome fog, cave lighting).
- `MeshInstance3D.skeleton` default empty; SpringBone enums moved to `SkeletonModifier3D`.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- Confirm project stretch mode and `AudioStreamPlayer.area_mask` after opening in 4.7.
- **Path3D snap-to-colliders** for spline-based road/river generation on terrain colliders.
- Jolt: `WorldBoundaryShape3D.plane.d` sign convention flipped — negate infinite floor/ceiling used in heightfield bounds.
