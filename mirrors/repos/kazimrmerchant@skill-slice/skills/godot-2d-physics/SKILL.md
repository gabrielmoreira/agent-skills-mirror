---
name: godot-2d-physics
description: "Expert patterns for Godot 2D physics including collision layers/masks, Area2D triggers, raycasting, and PhysicsDirectSpaceState2D queries. Use when implementing collision detection, trigger zones, line-of-sight systems, or manual physics queries. Trigger keywords: CollisionShape2D, CollisionPolygon2D, collision_layer, collision_mask, set_collision_layer_value, set_collision_mask_value, Area2D, body_entered, body_exited, RayCast2D, force_raycast_update, PhysicsPointQueryParameters2D, PhysicsShapeQueryParameters2D, direct_space_state, move_and_collide, move_and_slide. Do not use Node2D scale on CollisionShape2D, coyote-time CharacterBody2D controllers (godot-characterbody-2d), or 3D PhysicsServer3D."
version: 1.0.1
---

# 2D Physics

Expert guidance for collision detection, triggers, and raycasting in Godot 2D.

## When to Use

Activate this skill when the user needs to:
- Set up collision layers and masks for 2D entities
- Implement trigger zones or Area2D-based detection
- Build raycasting systems (line-of-sight, ledge detection, vision cones)
- Perform manual physics queries via `PhysicsDirectSpaceState2D`
- Optimize physics for large entity counts (swarms, bullet hells)
- Debug collision issues, jitter, or tunneling
- Implement one-way platforms, custom gravity, or substepping

Trigger keywords: `CollisionShape2D`, `CollisionPolygon2D`, `collision_layer`, `collision_mask`, `set_collision_layer_value`, `set_collision_mask_value`, `Area2D`, `body_entered`, `body_exited`, `RayCast2D`, `force_raycast_update`, `PhysicsPointQueryParameters2D`, `PhysicsShapeQueryParameters2D`, `direct_space_state`, `move_and_collide`, `move_and_slide`.

## Prerequisites

- Godot 4.x project (Godot 4.7+ for one-way collision direction parameter)
- Working knowledge of GDScript and node-based scene composition
- Windows host primary (PowerShell). Paths use backslashes on Windows.

## NEVER Do

- **NEVER scale `CollisionShape2D` nodes** — Use the shape handles in the editor, NOT the Node2D scale property. Scaling causes unpredictable physics behavior and incorrect collision normals.
- **NEVER confuse `collision_layer` with `collision_mask`** — Layer = "What AM I?", Mask = "What do I DETECT?". Setting both to the same value is usually wrong.
- **NEVER multiply velocity by delta when using `move_and_slide()`** — `move_and_slide()` automatically includes timestep. Only multiply gravity/acceleration by delta.
- **NEVER forget `force_raycast_update()` for manual mid-frame raycasts** — Raycasts update once per physics frame. If you change `target_position`, you MUST force an update.
- **NEVER use `get_overlapping_bodies()` every frame** — It is expensive. Cache results with `body_entered`/`body_exited` signals instead.
- **NEVER modify `RigidBody2D` state directly in `_process`** — Use `_integrate_forces()` for safe, synchronized access to `PhysicsDirectBodyState2D`.
- **NEVER move `PhysicsBody2D` nodes in `_process()`** — Use `_physics_process()`. Moving bodies outside the physics step causes stutter and unreliable collision detection.
- **NEVER use `RigidBody2D` for 1000+ simple entities** — Use `PhysicsServer2D` to bypass node overhead for massive performance gains (swarms/bullets).
- **NEVER use `Area2D` for high-frequency blocking (bullets)** — Area signals can be delayed. Use `move_and_collide()` or `ShapeCast2D` for frame-perfect results.
- **NEVER ignore 'Physics Jitter' on high-refresh monitors** — Enable Physics Interpolation to prevent micro-stutter in motion.
- **NEVER scale collision shapes directly at runtime** — It causes major instability. Resize the shape resource (size/radius) instead.
- **NEVER use `set_deferred` for immediate physics transform logic** — It happens at the end of the frame. Use `force_raycast_update()` or `PhysicsServer2D` instead.
- **NEVER leave Continuous CD (CCD) enabled for slow objects** — It adds significant CPU overhead. Reserve it for high-speed projectiles to prevent tunneling.
- **NEVER use a single collision layer for all tiles/entities** — Separate layers (Ground, Walls, Enemies) to allow selective filtering via masks.
- **NEVER forget to free `PhysicsServer2D` RIDs manually** — They are not garbage collected and will leak memory permanently.

## Godot 4.7: 2D Physics Updates

- `body_set_shape_as_one_way_collision` adds **direction** parameter — set relative to shape orientation for one-way platforms.
- `CollisionShape2D` supports one-way collision **direction relative to the shape** (not just global up).

## Available Scripts

> **MANDATORY**: Read the script matching your use case before implementation. Load from `scripts/` relative to this skill directory.

| Script | When to Load |
|--------|-------------|
| `scripts/collision_setup.gd` | Setting up collision layers/masks programmatically with named constants and debug visualization |
| `scripts/physics_query_cache.gd` | Eliminating redundant `PhysicsDirectSpaceState2D` queries via frame-based caching |
| `scripts/custom_physics.gd` | Non-standard gravity, forces, or manual stepping for `CharacterBody2D` |
| `scripts/physics_queries.gd` | Line-of-sight, ground detection, or area scanning via `PhysicsDirectSpaceState2D` |
| `scripts/physics_server_swarm.gd` | Thousands of moving objects (bullet hells, swarms) via low-level `PhysicsServer2D` |
| `scripts/substepping_logic.gd` | High-velocity projectiles needing manual sub-stepping for frame-perfect collision |
| `scripts/safe_rigidbody_state.gd` | Thread-safe `RigidBody2D` modification via `_integrate_forces` (teleport, custom impulses) |
| `scripts/physics_direct_query.gd` | Lightweight environment sensing via `PhysicsDirectSpaceState2D` without `RayCast2D` nodes |
| `scripts/collision_bitmask_helper.gd` | Managing complex collision layers/masks using bitwise Enums and helpers |
| `scripts/raycast_vision_stack.gd` | AI vision system reusing a single `RayCast2D` to check multiple angles per frame |
| `scripts/shapecast_aoe.gd` | AOE detection via `ShapeCast2D` with instant collision info (no Area2D signal lag) |
| `scripts/custom_gravity_override.gd` | Localized gravity zones (water, space, wind) and manual character-weight simulation |
| `scripts/collision_debouncer.gd` | Preventing signal spam when multi-shape bodies enter triggers |
| `scripts/jitter_interpolation_fix.gd` | Smooth character movement on high-refresh-rate monitors |
| `scripts/physics_server_direct_body.gd` | Direct `PhysicsServer2D` RID management for peak performance in massive simulations |
| `scripts/move_and_collide_precision.gd` | Expert bounce and friction logic for precision-critical movement |
| `scripts/continuous_collision_detection.gd` | Advanced CCD management for preventing bullet tunneling at extreme velocities |
| `scripts/performance_batch_mover.gd` | Optimized batch movement for multiple static/animatable bodies with riders-aware logic |

## Procedure

### 1. Collision Layers & Masks (Bitmask Deep Dive)

**Mental model:**
- `collision_layer` (32 bits): "What broadcast channels am I transmitting on?"
- `collision_mask` (32 bits): "What broadcast channels am I listening to?"

```gdscript
# Example: Player vs Enemy
# Player:
#   layer = 0b0001 (Channel 1: "I am a player")
#   mask  = 0b0110 (Channels 2+3: "I listen for enemies and walls")
# Enemy:
#   layer = 0b0010 (Channel 2: "I am an enemy")
#   mask  = 0b0101 (Channels 1+3: "I listen for players and walls")
```

**Bitmask helpers:**

```gdscript
# GOOD: Use helper functions for clarity
func setup_player_collision() -> void:
    set_collision_layer_value(1, true)
    set_collision_mask_value(2, true)  # enemies
    set_collision_mask_value(3, true)  # world

# GOOD: Bit shift for programmatic layer math
func enable_layers(base_layer: int, count: int) -> void:
    var mask := 0
    for i in range(count):
        mask |= (1 << (base_layer + i - 1))
    collision_mask = mask

# BAD: Hardcoded bitmasks without documentation
collision_mask = 0b110110  # What does this mean?!
```

**Common patterns:**

```gdscript
# Projectile that hits enemies but ignores other projectiles
extends Area2D

func _ready() -> void:
    set_collision_layer_value(4, true)   # Layer 4: "Projectiles"
    set_collision_mask_value(2, true)    # Mask Layer 2: "Enemies"
```

### 2. Area2D Expert Patterns

**Problem: Duplicate triggers on multi-collision-shape Area2D**

`body_entered` fires multiple times if an `Area2D` has multiple `CollisionShape2D` children. Track unique bodies:

```gdscript
extends Area2D

var _active_bodies := {}  # Use dict as Set

func _ready() -> void:
    body_entered.connect(_on_body_entered)
    body_exited.connect(_on_body_exited)

func _on_body_entered(body: Node2D) -> void:
    if body not in _active_bodies:
        _active_bodies[body] = true
        print("First entrance!")  # Fires once

func _on_body_exited(body: Node2D) -> void:
    _active_bodies.erase(body)
```

**Damage-over-time with immunity frames:**

```gdscript
extends Area2D

@export var damage_per_tick := 5
@export var tick_rate := 0.5
var _damage_timers := {}

func _ready() -> void:
    body_entered.connect(_on_body_entered)
    body_exited.connect(_on_body_exited)

func _on_body_entered(body: Node2D) -> void:
    if body.has_method("take_damage"):
        _damage_timers[body] = 0.0  # Immediate first tick

func _on_body_exited(body: Node2D) -> void:
    _damage_timers.erase(body)

func _process(delta: float) -> void:
    for body in _damage_timers.keys():
        _damage_timers[body] -= delta
        if _damage_timers[body] <= 0.0:
            body.take_damage(damage_per_tick)
            _damage_timers[body] = tick_rate
```

### 3. RayCast2D Advanced Usage

**Dynamic raycast rotation (enemy vision):**

```gdscript
extends CharacterBody2D

@onready var vision_ray: RayCast2D = $VisionRay

func can_see_target(target: Node2D) -> bool:
    var direction := global_position.direction_to(target.global_position)
    vision_ray.target_position = direction * 300
    vision_ray.force_raycast_update()  # CRITICAL: Update mid-frame
    if vision_ray.is_colliding():
        return vision_ray.get_collider() == target
    return false
```

**Multi-raycast ledge detection:**

```gdscript
extends CharacterBody2D

@onready var floor_front: RayCast2D = $FloorCheckFront
@onready var floor_back: RayCast2D = $FloorCheckBack

func at_ledge() -> bool:
    return floor_front.is_colliding() and not floor_back.is_colliding()

func _physics_process(_delta: float) -> void:
    if at_ledge() and is_on_floor():
        velocity.x *= -1
```

**Raycast exclusions:**

```gdscript
func _ready() -> void:
    $RayCast2D.add_exception(self)
    $RayCast2D.add_exception($Weapon)

# Reset exclusions
$RayCast2D.clear_exceptions()
```

### 4. PhysicsDirectSpaceState2D (Manual Queries)

**Point query — click detection:**

```gdscript
func get_body_at_mouse() -> Node2D:
    var mouse_pos := get_global_mouse_position()
    var space := get_world_2d().direct_space_state
    var query := PhysicsPointQueryParameters2D.new()
    query.position = mouse_pos
    query.collide_with_areas = false
    query.collision_mask = 0b11111111
    var results := space.intersect_point(query, 1)
    if results.is_empty():
        return null
    return results[0].collider
```

**Shape cast — AOE attack:**

```gdscript
func damage_nearby_enemies(center: Vector2, radius: float, damage: int) -> void:
    var space := get_world_2d().direct_space_state
    var query := PhysicsShapeQueryParameters2D.new()
    var circle := CircleShape2D.new()
    circle.radius = radius
    query.shape = circle
    query.transform = Transform2D(0.0, center)
    query.collision_mask = 0b0010  # Layer 2: Enemies
    var hits := space.intersect_shape(query)
    for hit in hits:
        var enemy: Node2D = hit.collider
        if enemy.has_method("take_damage"):
            enemy.take_damage(damage)
```

**Ray cast — instant hit weapon:**

```gdscript
func fire_hitscan_weapon(from: Vector2, direction: Vector2, max_range: float) -> void:
    var space := get_world_2d().direct_space_state
    var query := PhysicsRayQueryParameters2D.create(from, from + direction * max_range)
    query.exclude = [self]
    query.collision_mask = 0b0010  # Enemies
    var result := space.intersect_ray(query)
    if result:
        var hit_enemy: Node2D = result.collider
        var hit_point: Vector2 = result.position
        spawn_hit_effect(hit_point)
        if hit_enemy.has_method("take_damage"):
            hit_enemy.take_damage(25)
```

### 5. Decision Tree: Choosing a Collision Method

| Use Case | Method | Why |
|----------|--------|-----|
| Continuous trigger zone | `Area2D` + signals | Memory of what's inside, signals are efficient |
| One-time pickup (coin) | `Area2D` + `queue_free()` on enter | Simple, automatic cleanup |
| Line-of-sight check | `RayCast2D` | Efficient, built-in |
| Click-to-select units | `PhysicsPointQueryParameters2D` | Single query, no permanent node |
| AOE spell | `PhysicsShapeQueryParameters2D` | One-shot query, flexible shape |
| Instant-hit weapon | `PhysicsRayQueryParameters2D` | Hitscan, no projectile physics |
| Platformer ground check | `RayCast2D` or raycast down | Precise ledge detection |
| High-frequency bullet blocking | `move_and_collide()` or `ShapeCast2D` | Frame-perfect, no signal lag |
| 1000+ simple entities | `PhysicsServer2D` | Bypasses node overhead |

### 6. Expert Techniques

**Physics-server batching (low-level swarms):**

Load `scripts/physics_server_swarm.gd` before implementing. Core pattern:

```gdscript
class_name PhysicsBatchManager extends Node

var _bodies: Array[RID] = []

func create_bullet_swarm(count: int) -> void:
    for i in range(count):
        var body := PhysicsServer2D.body_create()
        PhysicsServer2D.body_set_mode(body, PhysicsServer2D.BODY_MODE_KINEMATIC)
        PhysicsServer2D.body_set_space(body, get_world_2d().space)
        _bodies.append(body)

func _physics_process(_delta: float) -> void:
    for body in _bodies:
        var t := PhysicsServer2D.body_get_state(body, PhysicsServer2D.BODY_STATE_TRANSFORM)
        PhysicsServer2D.body_set_state(body, PhysicsServer2D.BODY_STATE_TRANSFORM, t.translated(Vector2.RIGHT * 5.0))
```

**Multi-shape sync (compound RID bodies):**

```gdscript
func _ready() -> void:
    _body = PhysicsServer2D.body_create()
    var circle := PhysicsServer2D.circle_shape_create()
    PhysicsServer2D.shape_set_data(circle, 20.0)
    PhysicsServer2D.body_add_shape(_body, circle, Transform2D.IDENTITY)

    var box := PhysicsServer2D.rectangle_shape_create()
    PhysicsServer2D.shape_set_data(box, Vector2(10, 50))
    PhysicsServer2D.body_add_shape(_body, box, Transform2D.IDENTITY.translated(Vector2(30, 0)))
```

**Collision visual debugger (runtime gizmos):**

```gdscript
class_name CollisionVisualDebugger extends Node2D

var _last_collision: KinematicCollision2D

func update_debug_info(collision: KinematicCollision2D) -> void:
    _last_collision = collision
    queue_redraw()

func _draw() -> void:
    if not _last_collision: return
    var hit_pos := to_local(_last_collision.get_position())
    var normal := _last_collision.get_normal()
    draw_circle(hit_pos, 5.0, Color.RED)
    draw_line(hit_pos, hit_pos + normal * 30.0, Color.GREEN, 2.0)
```

## Pitfalls

1. **Raycasts in `_ready()` always return false** — Physics isn't initialized yet. Wait for `await get_tree().physics_frame` before querying.

2. **Area2D not detecting CharacterBody2D** — `CharacterBody2D` has `collision_layer = 0` by default. Explicitly set a layer:
   ```gdscript
   func _ready() -> void:
       collision_layer = 0b0001  # Layer 1: Player
   ```

3. **Raycast hitting backfaces** — Raycasts hit both front and back of collision shapes. For one-way raycasting, use `Area2D` monitoring instead.

4. **Always-on raycasts for rarely-used checks** — Disable when idle:
   ```gdscript
   func check_vision() -> bool:
       $OptionalRaycast.enabled = true
       $OptionalRaycast.force_raycast_update()
       var sees := $OptionalRaycast.is_colliding()
       $OptionalRaycast.enabled = false
       return sees
   ```

5. **Scaling `CollisionShape2D` via Node2D scale** — Causes incorrect normals and unpredictable behavior. Always use shape resource dimensions.

6. **Multiplying velocity by delta with `move_and_slide()`** — Double-applies timestep. Only gravity/acceleration should use delta.

7. **Forgetting to free `PhysicsServer2D` RIDs** — They are NOT garbage collected. Always call `PhysicsServer2D.free_rid(rid)` on cleanup.

8. **CCD enabled for slow objects** — Significant CPU overhead. Only enable for high-speed projectiles.

9. **Physics jitter on high-refresh monitors** — Enable Physics Interpolation in project settings or via `physics_interpolation_mode`.

## Verification

1. **Check collision layer/mask assignment at runtime:**
   ```gdscript
   print("Layer: ", collision_layer, " Mask: ", collision_mask)
   print("Layer 1 enabled: ", get_collision_layer_value(1))
   print("Mask 2 enabled: ", get_collision_mask_value(2))
   ```

2. **Verify raycast is updating mid-frame:**
   ```gdscript
   vision_ray.target_position = direction * 300
   vision_ray.force_raycast_update()
   print("Colliding: ", vision_ray.is_colliding())
   print("Collider: ", vision_ray.get_collider())
   ```

3. **Verify PhysicsDirectSpaceState2D query returns expected results:**
   ```gdscript
   var space := get_world_2d().direct_space_state
   var query := PhysicsPointQueryParameters2D.new()
   query.position = get_global_mouse_position()
   query.collision_mask = 0b11111111
   var results := space.intersect_point(query)
   print("Hit count: ", results.size())
   for r in results:
       print("Hit: ", r.collider.name)
   ```

4. **Confirm physics runs in `_physics_process`, not `_process`:**
   ```gdscript
   func _physics_process(delta: float) -> void:
       # Movement code here
       pass
   ```

5. **Verify RID cleanup for PhysicsServer2D bodies:**
   ```gdscript
   func _exit_tree() -> void:
       for body in _bodies:
           PhysicsServer2D.free_rid(body)
       _bodies.clear()
   ```

6. **Check for duplicate Area2D triggers (multi-shape):**
   ```gdscript
   func _on_body_entered(body: Node2D) -> void:
       print("body_entered: ", body.name, " active_count: ", _active_bodies.size())
   ```

## Reference

- [Godot Docs: PhysicsServer2D](https://docs.godotengine.org/en/stable/classes/class_physicsserver2d.html)
- [Godot Docs: KinematicCollision2D](https://docs.godotengine.org/en/stable/classes/class_kinematiccollision2d.html)

## Related

- Master Skill: [godot-master](../godot-master/SKILL.md)
