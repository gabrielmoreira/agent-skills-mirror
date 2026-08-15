---
name: game-godot-genre-shooter
version: 1.2.1
description: "Godot 4 FPS/TPS gunplay blueprint covering WeaponData resources, recoil and bloom, hitscan vs projectile, aim assist, client prediction, and hit registration. Use when building competitive shooters, battle royales, or tactical FPS in Godot 4. Not for platformers (game-godot-genre-platformer), engine-agnostic NPC AI (game-ai-behavior), GdUnit export CI (game-godot), or Unity/Unreal shooters."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Genre: Shooter (FPS/TPS)

Gunplay feel, responsive combat, and competitive balance define shooters. This skill provides production-ready architecture, code patterns, and hard rules for building competitive FPS/TPS games in Godot 4.x.

## When to Use

Use this skill when building competitive shooters, battle royales, or tactical FPS games requiring responsive combat. This blueprint covers weapon systems, recoil patterns, hitscan vs projectile, aim assist, multiplayer prediction, and gunplay feel for games like Call of Duty, Counter-Strike, Apex Legends, and Fortnite.

**Trigger keywords:** hitscan, recoil pattern, aim assist, client prediction, weapon archetype, projectile physics, hit registration, FPS, TPS, shooter, gunplay, bloom, spread, lag compensation, spray pattern.

## Prerequisites

- Godot 4.x (`.NET` or standard build) with `CharacterBody3D`, `PhysicsDirectSpaceState3D`, `Decal`, and `AnimationTree` nodes available.
- Project configured with physics layers set up for player, enemy, environment, and projectile collision masks.
- Windows host is primary (PowerShell). All paths assume `~\agent-skills\library\game-godot-genre-shooter\` as the skill root.
- For multiplayer: ENet (UDP) transport configured — never TCP.

## Procedure

### Core Loop

`Engage → Aim → Fire → Kill Confirm → Acquire Next`

### Available Scripts

Load these reference scripts when you need the corresponding systems:

1. **`scripts/advanced_weapon_controller.gd`** — Load when implementing recoil, bloom, and dual hitscan/projectile weapon systems with object pooling. This is the expert pattern for weapon feel.
2. **`scripts/shooter_patterns.gd`** — Load when implementing server-bypassing hitscan, random spread, or `ShapeCast3D`-based explosion queries. Reusable across weapon types.

### Step 1: Weapon System Architecture

Create a `Resource`-based `WeaponData` system so designers can balance weapons without touching code. Never hardcode weapon statistics inside logic.

```gdscript
# weapon.gd
extends Node3D
class_name Weapon

@export_group("Stats")
@export var damage: int = 20
@export var fire_rate: float = 0.1
@export var magazine_size: int = 30
@export var reload_time: float = 2.0
@export var range: float = 100.0
@export var collision_mask: int = 1

@export_group("Recoil")
@export var base_recoil: Vector2 = Vector2(0.5, 2.0)
@export var recoil_recovery_speed: float = 5.0
@export var max_spread: float = 5.0

@export_group("Type")
@export var is_hitscan: bool = true
@export var projectile_scene: PackedScene

var current_ammo: int = 30
var can_fire: bool = true
var current_recoil: Vector2 = Vector2.ZERO
var current_spread: float = 0.0

signal fired
signal reloaded
signal ammo_changed(current: int, max_ammo: int)

func _ready() -> void:
    current_ammo = magazine_size

func fire_hitscan() -> void:
    if not can_fire or current_ammo <= 0:
        return
    
    current_ammo -= 1
    ammo_changed.emit(current_ammo, magazine_size)
    
    var camera := get_viewport().get_camera_3d()
    if not camera:
        return
    var ray_origin := camera.global_position
    var ray_direction := -camera.global_basis.z
    
    ray_direction = apply_spread(ray_direction)
    
    var space := get_world_3d().direct_space_state
    var query := PhysicsRayQueryParameters3D.create(
        ray_origin,
        ray_origin + ray_direction * range
    )
    query.collision_mask = collision_mask
    
    var result := space.intersect_ray(query)
    if result:
        var hit_point: Vector3 = result.position
        var hit_normal: Vector3 = result.normal
        var hit_object: Object = result.collider
        
        spawn_impact_effect(hit_point, hit_normal)
        
        if hit_object.has_method("take_damage"):
            var hit_zone := determine_hit_zone(result)
            var final_damage := calculate_damage(damage, hit_zone)
            hit_object.take_damage(final_damage, hit_zone)
    
    apply_recoil()
    start_fire_cooldown()
    fired.emit()

func apply_spread(base_direction: Vector3) -> Vector3:
    var spread_angle := deg_to_rad(current_spread)
    var random_offset := Vector2(
        randf_range(-spread_angle, spread_angle),
        randf_range(-spread_angle, spread_angle)
    )
    return base_direction.rotated(Vector3.UP, random_offset.x).rotated(Vector3.RIGHT, random_offset.y)

func spawn_impact_effect(pos: Vector3, normal: Vector3) -> void:
    var decal = Decal.new()
    get_tree().root.add_child(decal)
    decal.global_position = pos
    decal.look_at(pos + normal, Vector3.UP if abs(normal.y) < 0.99 else Vector3.FORWARD)
    
    var timer = get_tree().create_timer(10.0)
    timer.timeout.connect(decal.queue_free)

func apply_recoil() -> void:
    current_recoil += base_recoil

func start_fire_cooldown() -> void:
    can_fire = false
    var timer = get_tree().create_timer(fire_rate)
    timer.timeout.connect(func(): can_fire = true)

func determine_hit_zone(result: Dictionary) -> String:
    if "headshot" in result.collider.name.to_lower():
        return "head"
    elif "chest" in result.collider.name.to_lower():
        return "chest"
    return "body"

func calculate_damage(base: int, zone: String) -> int:
    match zone:
        "head": return int(base * 2.5)
        "chest": return int(base * 1.0)
        _: return int(base * 0.8)
```

### Step 2: Choose Hitscan vs Projectile

**Hitscan (Instant Hit):** Use for pistols, ARs, snipers. See `fire_hitscan()` above. Provides instant feedback, minimal network traffic (only fire event sent).

**Projectile (Physical Bullet):** Use for rockets, grenades, arrows. Requires object pooling — never instantiate and `free()` hundreds of projectile nodes.

```gdscript
# projectile.gd
extends CharacterBody3D
class_name Projectile

@export var speed := 100.0
@export var damage := 20
@export var gravity_affected := true
@export var lifetime := 5.0

var direction: Vector3 = Vector3.FORWARD
var shooter: Node3D

func _ready() -> void:
    var timer = get_tree().create_timer(lifetime)
    timer.timeout.connect(queue_free)

func _physics_process(delta: float) -> void:
    if gravity_affected:
        velocity.y -= 9.8 * delta
    
    velocity = direction * speed
    var collision := move_and_collide(velocity * delta)
    
    if collision:
        var collider := collision.get_collider()
        if collider != shooter and collider.has_method("take_damage"):
            collider.take_damage(damage)
        spawn_impact(collision.get_position(), collision.get_normal())
        queue_free()

func spawn_impact(pos: Vector3, normal: Vector3) -> void:
    var decal = Decal.new()
    get_tree().root.add_child(decal)
    decal.global_position = pos
    decal.look_at(pos + normal, Vector3.UP if abs(normal.y) < 0.99 else Vector3.FORWARD)
    var timer = get_tree().create_timer(5.0)
    timer.timeout.connect(decal.queue_free)
```

**Weapon type decision tree:**
- Pistol/AR: Hitscan (instant feedback)
- Rocket/Grenade: Projectile with gravity
- Sniper: Hitscan with tracer visual
- Shotgun: Multiple hitscan rays (5-8 pellets), effective range <10m

### Step 3: Implement the Three-Layer Recoil System

Three recoil types must work together: **visual recoil** (camera kick), **pattern offset** (learnable spray), and **spread bloom** (accuracy penalty).

```gdscript
class_name RecoilSystem
extends Node

var visual_recoil: Vector2 = Vector2.ZERO
var pattern_offset: Vector2 = Vector2.ZERO
var spread_bloom: float = 0.0

@export var recoil_pattern: Array[Vector2]
var pattern_index: int = 0

func apply_recoil(weapon: Weapon) -> void:
    visual_recoil.y += weapon.base_recoil.y * randf_range(0.8, 1.2)
    visual_recoil.x += weapon.base_recoil.x * randf_range(-1.0, 1.0)
    
    if pattern_index < recoil_pattern.size():
        pattern_offset += recoil_pattern[pattern_index]
        pattern_index += 1
    
    spread_bloom = min(spread_bloom + 0.5, weapon.max_spread)

func recover_recoil(delta: float, recovery_speed: float) -> void:
    visual_recoil = visual_recoil.lerp(Vector2.ZERO, recovery_speed * delta)
    pattern_offset = pattern_offset.lerp(Vector2.ZERO, recovery_speed * delta)
    spread_bloom = lerp(spread_bloom, 0.0, recovery_speed * delta)
    
    if visual_recoil.length() < 0.01:
        pattern_index = 0

func get_spread_direction(base_direction: Vector3) -> Vector3:
    var spread_angle := deg_to_rad(spread_bloom)
    var random_offset := Vector2(
        randf_range(-spread_angle, spread_angle),
        randf_range(-spread_angle, spread_angle)
    )
    return base_direction.rotated(Vector3.UP, random_offset.x).rotated(Vector3.RIGHT, random_offset.y)
```

### Step 4: Add Aim Assist (Controller Support)

Implement friction (slowdown near targets) and magnetism (subtle pull toward targets). Only activate within `assist_angle` and `assist_range`.

```gdscript
class_name AimAssist
extends Node3D

@export var assist_range := 50.0
@export var assist_angle := 15.0
@export var friction_strength := 0.3
@export var magnetism_strength := 0.1

func apply_aim_assist(look_input: Vector2, camera: Camera3D) -> Vector2:
    var target := find_closest_target(camera)
    if not target:
        return look_input
    
    var to_target := target.global_position - camera.global_position
    var camera_forward := -camera.global_basis.z
    var angle := rad_to_deg(camera_forward.angle_to(to_target.normalized()))
    
    if angle > assist_angle:
        return look_input
    
    var friction := 1.0 - (friction_strength * (1.0 - angle / assist_angle))
    look_input *= friction
    
    var target_screen_pos := camera.unproject_position(target.global_position)
    var screen_center := get_viewport().get_visible_rect().size / 2
    var pull_direction := (target_screen_pos - screen_center).normalized()
    look_input += pull_direction * magnetism_strength * (1.0 - angle / assist_angle)
    
    return look_input

func find_closest_target(camera: Camera3D) -> Node3D:
    var closest: Node3D = null
    var closest_angle := assist_angle
    
    for target in get_tree().get_nodes_in_group("enemies"):
        if target is Node3D:
            var to_target := target.global_position - camera.global_position
            var angle := rad_to_deg((-camera.global_basis.z).angle_to(to_target.normalized()))
            
            if angle < closest_angle and to_target.length() < assist_range:
                if has_line_of_sight(camera.global_position, target.global_position):
                    closest = target
                    closest_angle = angle
    
    return closest

func has_line_of_sight(from: Vector3, to: Vector3) -> bool:
    var space = get_world_3d().direct_space_state
    var query = PhysicsRayQueryParameters3D.create(from, to)
    var result = space.intersect_ray(query)
    if result:
        return result.collider.is_in_group("enemies")
    return false
```

### Step 5: Polish Weapon Feel

#### Camera Effects

```gdscript
# weapon_effects_controller.gd
extends Node3D

@export var camera: Camera3D
@export var muzzle_flash: GeometryInstance3D
@export var reload_time: float = 2.0
@export var magazine_size: int = 30

var can_fire: bool = true
var can_aim: bool = true
var current_ammo: int = 30

func on_weapon_fired() -> void:
    camera_shake(0.1, 0.05)
    
    if camera:
        camera.fov += 2.0
        await get_tree().create_timer(0.05).timeout
        camera.fov -= 2.0
    
    if muzzle_flash:
        muzzle_flash.visible = true
        await get_tree().create_timer(0.02).timeout
        muzzle_flash.visible = false

func camera_shake(duration: float, magnitude: float) -> void:
    if not camera:
        return
    var initial_offset = camera.h_offset
    var time_elapsed = 0.0
    while time_elapsed < duration:
        camera.h_offset = initial_offset + randf_range(-magnitude, magnitude)
        await get_tree().process_frame
        time_elapsed += get_process_delta_time()
    camera.h_offset = initial_offset

func on_weapon_reloaded() -> void:
    can_fire = false
    can_aim = false
    
    if has_node("AnimationPlayer"):
        get_node("AnimationPlayer").play("reload")
        
    await get_tree().create_timer(reload_time).timeout
    
    current_ammo = magazine_size
    can_fire = true
    can_aim = true
```

#### Audio Layering

Never use a single `AudioStreamPlayer` for gunfire. Use layered audio: mechanical + shot + reverb tail.

```gdscript
# audio_layering.gd
extends Node

@export var fire_audio_player: AudioStreamPlayer
@export var mechanical_player: AudioStreamPlayer
@export var tail_player: AudioStreamPlayer

@export var fire_sounds: Array[AudioStream]
@export var tail_sound: AudioStream
@export var mechanical_sound: AudioStream

func play_fire_audio() -> void:
    if fire_sounds.is_empty():
        return
    var shot := fire_sounds.pick_random()
    fire_audio_player.stream = shot
    fire_audio_player.play()
    
    mechanical_player.stream = mechanical_sound
    mechanical_player.play()
    
    await get_tree().create_timer(0.1).timeout
    tail_player.stream = tail_sound
    tail_player.play()
```

### Step 6: Implement Multiplayer Client Prediction

Never trust the client for hit registration. Use server-authoritative validation with lag compensation. Never synchronize every bullet over the network — use client-side prediction for visual tracers and only send the initial fire event.

```gdscript
# CLIENT: Instant feedback, no waiting for server
func fire_client() -> void:
    play_effects_immediate()
    local_hitscan_visual()
    rpc_id(1, "server_validate_shot", camera.global_transform)

# SERVER: Authoritative damage
@rpc("any_peer")
func server_validate_shot(shooter_transform: Transform3D) -> void:
    var hit = perform_server_hitscan(shooter_transform)
    if hit and is_valid_shot(hit):
        rpc("confirm_hit", hit.victim_id, hit.damage)
```

### Step 7: Advanced Meta-Systems

#### Spray-Pattern Editor (Recoil Math)

Use Godot's custom `Resource` system for data-driven recoil patterns editable in the Inspector.

```gdscript
class_name WeaponRecoilPattern extends Resource

@export var spray_points: Array[Vector2] = []
@export var horizontal_variance: float = 0.1
@export var vertical_variance: float = 0.1

func get_recoil_at(shot_index: int) -> Vector2:
    if spray_points.is_empty(): return Vector2.ZERO
    var base := spray_points[shot_index % spray_points.size()]
    return base + Vector2(randf() * horizontal_variance, randf() * vertical_variance)
```

#### Lag-Compensation (Server Rewinding)

Store player position history in a ring buffer. When a shot is fired, the server rewinds target colliders to historical positions based on the client's timestamp, performs the raycast, and restores them. Always perform the raycast in a single frame and immediately restore transforms to prevent physics glitches.

```gdscript
class_name LagCompensator extends Node

var _history: Array[Dictionary] = []
const MAX_BACKTRACK_MS = 200

func _physics_process(_delta: float) -> void:
    _history.append({"time": Time.get_ticks_msec(), "transform": owner.global_transform})
    if _history.size() > 60:
        _history.pop_front()

func backtrack_to(timestamp: int) -> void:
    var best_match = _history[0]
    for entry in _history:
        if abs(entry.time - timestamp) < abs(best_match.time - timestamp):
            best_match = entry
    owner.global_transform = best_match.transform
```

#### ShapeCast3D Explosion

Query an explosion volume without node overhead using `PhysicsDirectSpaceState3D.intersect_shape()`.

```gdscript
class_name ExplosionQuery extends Node3D

func execute_explosion(radius: float) -> Array[Dictionary]:
    var space_state := get_world_3d().direct_space_state
    var sphere := SphereShape3D.new()
    sphere.radius = radius
    
    var query := PhysicsShapeQueryParameters3D.new()
    query.shape = sphere
    query.transform = global_transform
    query.collision_mask = 1

    return space_state.intersect_shape(query, 32)
```

## Pitfalls

### Gunplay & Hit Registration — HARD RULES

1. **NEVER** use `_process()` for hit detection; strictly use **`_physics_process()`** to maintain frame-rate independent accuracy (aiming/firing are physics events).
2. **NEVER** apply recoil solely to the weapon model transform; strictly apply it to **Camera Rotation (kick)** and **Weapon Bloom (spread)**.
3. **NEVER** use `Area3D` overlap for high-speed hit detection; strictly use **`PhysicsDirectSpaceState3D.intersect_ray()`** for 100x better performance.
4. **NEVER** trust the client for hit registration in multiplayer; strictly use **Server-Authoritative** validation using lag compensation (rewinding).
5. **NEVER** synchronize every bullet over the network; strictly use **Client-Side Prediction** for visual tracers and only send the initial "Fire" event.
6. **NEVER** forget to exclude the player's own RID from hitscan raycasts; strictly use **`add_exception()`** to prevent shots colliding with the weapon barrel.
7. **NEVER** use exact floating-point equality (`==`) for bullet damage or health; strictly use **`is_equal_approx()`** to mitigate precision loss.

### Performance & Architecture — HARD RULES

8. **NEVER** hardcode weapon statistics (Damage, Recoil) inside logic; strictly use **Resource-based WeaponData** for rapid balancing.
9. **NEVER** use a single `AudioStreamPlayer` for gunfire; strictly use **Layered Audio** (Mechanical + Shot + Reverb Tail) for punchy feedback.
10. **NEVER** instantiate and `free()` hundreds of projectile nodes; strictly use **Object Pooling** or the `PhysicsServer3D` API for stability.
11. **NEVER** use `Sprite3D` for bullet impacts on surfaces; strictly use the **Decal** node for conforming, perspective-correct projection.
12. **NEVER** use absolute pixel positioning for crosshairs; strictly rely on **Anchors & RectCenter** to ensure accuracy across resolutions.
13. **NEVER** scale `CollisionShape3D` non-uniformly; strictly scale the **Internal Shape Resource** to maintain valid physics calculations.
14. **NEVER** use TCP for multiplayer shooter synchronization; strictly use **ENet (UDP)** with unreliable transfer modes to avoid latency spikes.

### Common Feel Problems & Expert Fixes

- **Weak bullet impact** → Triple-layer audio (shot + tail + mechanical) + screen shake + blood VFX + damage number.
- **Guns feel identical** → Unique recoil patterns (SMG: tight vertical, AK: strong horizontal kick).
- **No skill ceiling** → Learnable spray patterns (CS:GO style), not pure RNG spread.
- **Controller aim frustration** → Friction (0.3 slowdown near targets) + subtle 0.1 magnetism.

### Godot-Specific Tips

1. **Raycasts**: Use `PhysicsRayQueryParameters3D` with proper layer masks.
2. **Projectiles**: `CharacterBody3D` or `RigidBody3D` depending on physics needs.
3. **Audio**: Multiple `AudioStreamPlayer3D` for layered gun sounds.
4. **Animations**: `AnimationTree` for weapon state machines (idle, aim, fire, reload).

## Verification

- [ ] Verify all weapon scripts compile without errors in Godot 4.x.
- [ ] Test hitscan raycasts exclude player collision correctly via `add_exception()`.
- [ ] Validate recoil recovery resets `pattern_index` to 0 when `visual_recoil.length() < 0.01`.
- [ ] Confirm aim assist only activates within `assist_angle` (15°) and `assist_range` (50m).
- [ ] Test client prediction visual effects match server-authoritative results.
- [ ] Verify lag compensation history buffer restores transforms after rewind (single-frame raycast).
- [ ] Check explosion `ShapeCast3D` returns correct colliders within radius (test with 32 max results).
- [ ] Run multiplayer test with 100ms simulated latency to validate prediction.
- [ ] Confirm `_physics_process()` is used for all hit detection — not `_process()`.
- [ ] Verify `is_equal_approx()` is used for all damage/health float comparisons.
- [ ] Confirm ENet (UDP) transport is configured — never TCP.
- [ ] Verify `Decal` nodes are used for bullet impacts — not `Sprite3D`.

## Related skills

- [godot-master](../godot-master/SKILL.md)
