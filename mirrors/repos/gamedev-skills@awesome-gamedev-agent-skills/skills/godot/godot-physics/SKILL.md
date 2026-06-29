---
name: godot-physics
description: >
  Use Godot 4.x physics bodies and detection in 2D and 3D: RigidBody, StaticBody,
  Area, and CharacterBody; collision layers vs masks; contact/overlap signals; and
  raycasts (RayCast nodes and direct space-state queries). Use when configuring
  collision layers/masks, detecting overlaps with Area2D/Area3D, applying forces to a
  RigidBody, or casting rays in a Godot project (.tscn with physics bodies).
license: Apache-2.0
compatibility: Godot 4.3+
metadata:
  engine: godot
  category: godot
  difficulty: intermediate
---

# Godot Physics (4.x, 2D + 3D)

Pick the right physics body, wire up collision layers/masks, detect overlaps, and cast
rays. Concepts apply to both 2D and 3D (swap the `2D`/`3D` suffix). Targets
**Godot 4.3+**.

## When to use

- Use when choosing between body types, setting collision layers/masks so the right
  things collide, detecting overlaps (triggers, hurtboxes) with `Area`, applying
  forces/impulses to a `RigidBody`, or casting rays for line-of-sight/ground checks.

**When *not* to use:** kinematic character controllers (`move_and_slide`) →
`godot-2d-movement`; tile collision setup → `godot-tilemap`; tuning the *feel* of physics
(timestep, mass, jitter) → `physics-tuning`.

## Core workflow

1. **Choose the body type:**
   - `StaticBody` — never moves (floors, walls). Collides, no simulation.
   - `RigidBody` — fully simulated (gravity, forces, bouncing). Don't set its
     `position` directly; apply forces/impulses or set `linear_velocity`.
   - `CharacterBody` — script-driven kinematic (see `godot-2d-movement`).
   - `Area` — detects overlaps and can apply gravity/damping; no solid collision.
   Every body needs a `CollisionShape` (or `CollisionPolygon`) child.
2. **Configure layers and masks.** A body is *on* its **layers** and *scans for* its
   **masks**. Two bodies interact only if one's layer is in the other's mask. Name layers
   in Project Settings > Layer Names for clarity.
3. **Detect overlaps** with `Area` signals (`body_entered`, `area_entered`).
4. **Drive RigidBodies with forces/impulses**, or override `_integrate_forces` for full
   control.
5. **Cast rays** with a `RayCast2D/3D` node (polled each frame) or a one-shot space-state
   query from code.

## Patterns

### 1. Collision layers vs masks (set from code)

```gdscript
# Player is on layer 1, scans layers 2 (walls) and 3 (enemies).
func _ready() -> void:
    set_collision_layer_value(1, true)    # I am on layer 1
    set_collision_mask_value(2, true)     # I collide with things on layer 2
    set_collision_mask_value(3, true)     # ...and layer 3
    # Bit-field forms also exist: collision_layer = 1; collision_mask = 0b110
```

### 2. Area2D as a trigger / hurtbox

```gdscript
extends Area2D                            # e.g. a damage zone

func _ready() -> void:
    body_entered.connect(_on_body_entered)
    area_entered.connect(_on_area_entered)

func _on_body_entered(body: Node2D) -> void:
    if body.has_method("take_damage"):
        body.take_damage(10)

func _on_area_entered(area: Area2D) -> void:
    print("Overlapped area: ", area.name)
```

### 3. Applying force and impulse to a RigidBody3D

```gdscript
extends RigidBody3D

func push(direction: Vector3) -> void:
    apply_central_impulse(direction * 8.0)     # instantaneous velocity change

func _physics_process(_delta: float) -> void:
    apply_central_force(Vector3.FORWARD * 4.0) # continuous force (per tick)
    # Never set `position` on a RigidBody to move it; use forces/impulses or
    # set linear_velocity. Use freeze=true if you must hold it in place.
```

### 4. Raycast two ways

```gdscript
# A) RayCast2D node: enable it, then poll after physics has updated.
@onready var ray: RayCast2D = $RayCast2D    # set target_position in the editor

func _physics_process(_delta: float) -> void:
    if ray.is_colliding():
        var hit := ray.get_collider()
        var point := ray.get_collision_point()

# B) One-shot query from code (no node needed).
func ground_under(global_from: Vector2) -> Dictionary:
    var space := get_world_2d().direct_space_state
    var query := PhysicsRayQueryParameters2D.create(global_from, global_from + Vector2(0, 64))
    query.collision_mask = 1                 # only layer 1
    return space.intersect_ray(query)        # {} if nothing hit, else collider/position/normal
```

## Pitfalls

- **Layer vs mask confusion** is the #1 bug. Layer = "what I am"; mask = "what I look
  for". For A to detect B, B's layer must be in A's mask. Detection can be one-directional.
- **Moving a RigidBody by `position`** fights the solver and causes tunneling/jitter.
  Use impulses/forces, set `linear_velocity`, or `freeze` it. To teleport, set position
  and zero the velocities inside `_integrate_forces`.
- **`Area` doesn't fire** when neither monitoring nor monitorable is set, or layers/masks
  don't overlap. `monitoring` must be on for the Area to detect; `monitorable` lets others
  detect it.
- **RayCast2D/3D read stale or no data** if `enabled` is false, or if you read it before
  physics updated — read in `_physics_process`, and call `force_raycast_update()` after
  moving it within the same tick.
- **Forgetting a `CollisionShape`** (or leaving it empty) means the body never collides.
- **Fast objects tunnel** through thin walls; enable **continuous CD** on the RigidBody
  (`continuous_cd`) or use a raycast-based check.
- **`intersect_ray` excludes its own body?** Pass `query.exclude = [self.get_rid()]` (an
  `Array[RID]`, not an array of nodes) to skip self-hits.

## References

- For `_integrate_forces`, joints, one-way collision, `PhysicsServer` direct access,
  shape queries (`intersect_shape`), and 3D `move_and_collide`, read
  `references/bodies-and-queries.md`.

## Related skills

- `godot-2d-movement` — kinematic `CharacterBody2D` controllers.
- `godot-tilemap` — tile collision shapes and their layers.
- `physics-tuning` — engine-agnostic feel: timestep, mass, drag, CCD.
- `godot-3d-essentials` — 3D scene setup these bodies live in.
