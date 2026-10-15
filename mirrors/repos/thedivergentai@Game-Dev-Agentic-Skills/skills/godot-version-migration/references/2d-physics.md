# Migration notes: godot-2d-physics

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 3.x → 4.0

Official: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html)

- `KinematicBody2D` → `CharacterBody2D`; `move`/`move_and_slide` APIs changed — rewrite character controllers.
- `RigidBody2D` / `Area2D` signal and layer naming unchanged in spirit but audit `body_entered` vs legacy enter signals from 2.x leftovers.
- `RectangleShape2D.extents` → `size` (full size, not half-extents).
- Bullet was never 2D-default; still re-test after 3→4 converter renames.

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `Area2D.priority` type is `int` (was `float`) — audit serialized scenes and comparisons that stored fractional priorities.
- `PhysicsDirectSpaceState2D.collide_shape()` return type changed to `Array[Vector2]` (was `Array[PackedVector2Array]`) — update shape-overlap snippets that iterated nested arrays.
- Viewports with physics picking enabled now auto-mark `InputEvent`s handled — remove redundant manual pick forwarding in ray/shape query tutorials.
- `PathFollow2D.lookahead` removed — replace path-following samples with current `PathFollow2D` progress/rotation APIs.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

*No skill-relevant breaking changes for this hop.*

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

*No skill-relevant breaking changes for this hop.*

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

*No skill-relevant breaking changes for this hop.*

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

*No skill-relevant breaking changes for this hop.*

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

*No skill-relevant breaking changes for this hop.*

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- `PhysicsServer2D.body_set_shape_as_one_way_collision()` adds optional `direction` relative to the shape — pass the platform normal (e.g. `Vector2.UP.rotated(shape_rotation)`) instead of assuming global up.
- `CollisionShape2D` one-way collision direction is shape-relative — re-test tile and StaticBody one-way platforms after upgrade; rotate the shape or set direction explicitly for angled one-ways.
