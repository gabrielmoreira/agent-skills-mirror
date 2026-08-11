# Migration notes: godot-raycasting-queries

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `Area2D`/`Area3D.priority` type is `int` (was `float`) — audit pick/filter ordering when multiple Areas participate in queries.
- `PhysicsDirectSpaceState2D/3D.collide_shape()` return types changed — update overlap iteration (`Array[Vector2]` / `Array[Vector3]`).
- Viewports with physics picking enabled auto-mark `InputEvent`s handled — remove redundant manual event forwarding in mouse-pick ray tutorials.
- `Geometry3D.segment_intersects_convex` takes `Array[Plane]`.
- `Basis`/`Transform3D.looking_at` and `Node3D.look_at*` gain optional `use_model_front` — set when LOS rays should align to model forward, not -Z.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- **Mesh format upgrade** on open — regenerate convex/trimesh collision from upgraded mesh resources before shape queries rely on them.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- `PhysicsShapeQueryParameters3D.motion` is `Vector3` (was `Vector2`) — fix 3D cast/sweep motion vectors in `intersect_shape` and shapecast helpers.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `SoftBody3D.set_point_pinned()` gains optional `insert_at` — only affects 3D pin-query debug samples, not 2D ray workflows.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- Jolt: `physics/jolt_physics_3d/simulation/areas_detect_static_bodies` removed — `Area3D` overlap queries always include static bodies; filter with layers/masks in query parameters.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- **New projects default 3D physics engine to Jolt** — re-verify 3D ray/shapecast hit normals and tunneling behavior when switching engines mid-project.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- Jolt: `WorldBoundaryShape3D.plane.d` sign flipped — infinite boundary ray tests may miss until `d` is negated.
- Jolt: `Area3D` reports overlaps with `SoftBody3D` — layer/mask filters on overlap queries must account for soft bodies.
- `PhysicsServer2D.body_set_shape_as_one_way_collision()` direction is shape-relative — one-way platform ray/snaps may need updated floor normals in 2D query debug draws.
