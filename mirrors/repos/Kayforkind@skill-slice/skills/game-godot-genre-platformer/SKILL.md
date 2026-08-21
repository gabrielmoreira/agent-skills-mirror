---
name: game-godot-genre-platformer
version: 1.1.1
description: "Implements Godot 4.3+ 2D platformers: CharacterBody2D coyote time, jump buffering, variable jump height, squash/stretch juice, checkpoints, collectibles, and assist options. Use when building a precision platformer or debugging floaty jumps and tunneling. Trigger: platformer, coyote_time, jump_buffer, game_feel. Not for party/minigame collections, top-down or 3D movement, or Metroidvania world maps."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Overview

A production-grade design and implementation guide for 2D platformer games in Godot 4.3+. Covers the full stack: movement feel, camera design, level pacing, visual juice, checkpoint systems, and accessibility. Grounded in proven design patterns from Celeste, Hollow Knight, Super Meat Boy, and Mario.

**Core Loop:** `Jump → Navigate Obstacles → Reach Goal → Next Level`

**Skill Chain:** `godot-project-foundations` → `godot-characterbody-2d` → `godot-input-handling` → `animation` → `sound-manager` → `tilemap-setup` → `camera-2d`

## When to Use

Activate this skill when the user is:

- Building a 2D platformer in Godot 4.3+ (keywords: **platformer**, **precision_movement**)
- Implementing responsive jump mechanics (keywords: **coyote_time**, **jump_buffer**)
- Polishing movement feel and visual juice (keywords: **game_feel**, **squash_stretch**)
- Designing levels, checkpoints, or difficulty curves (keywords: **level_design**)
- Setting up collectible systems, assist modes, or remappable controls
- Debugging floaty jumps, tunneling collisions, or unresponsive controls

**Do NOT use for:** Metroidvania world design (use `godot-genre-metroidvania`), top-down movement, or 3D platformers without adaptation.

## Prerequisites

- **Godot 4.3+** — `CharacterBody2D` and `move_and_slide()` are required; `KinematicBody2D` is removed.
- **Skill chain loaded:** Ensure `godot-project-foundations` and `godot-characterbody-2d` skills are available before starting.
- **Windows host (PowerShell):** All CLI commands assume PowerShell. Path separator is `\`.
- **Project structure:** A Godot project with `res://` root, `scripts/` directory, and `test/` directory for headless verification.

## Procedure

### 1. Set Up the Player Controller

Load [scripts/advanced_platformer_controller.gd](scripts/advanced_platformer_controller.gd) as the base controller. This file provides a professional-grade `CharacterBody2D` with coyote time, jump buffering, and variable jump height integrated.

**Key constants to tune:**

```gdscript
const MOVE_SPEED := 200.0
const JUMP_VELOCITY := -400.0
const JUMP_RELEASE_MULTIPLIER := 0.5
const COYOTE_TIME := 0.1        # 100 ms grace period
const JUMP_BUFFER_TIME := 0.15  # 150 ms input queue
const GRAVITY := 980.0
const FALL_GRAVITY_MULTIPLIER := 1.5
const MAX_FALL_SPEED := 600.0
const AIR_ACCEL := 800.0
```

### 2. Implement Coyote Time

Load [scripts/coyote_timer.gd](scripts/coyote_timer.gd) for standalone grace-period logic. Integrate into `_physics_process`:

```gdscript
var coyote_timer: float = 0.0

func _physics_process(delta: float) -> void:
    if is_on_floor():
        coyote_timer = COYOTE_TIME
    else:
        coyote_timer = max(0.0, coyote_timer - delta)

    if Input.is_action_just_pressed("jump") and coyote_timer > 0.0:
        velocity.y = JUMP_VELOCITY
        coyote_timer = 0.0
```

### 3. Implement Jump Buffering

Load [scripts/jump_buffer.gd](scripts/jump_buffer.gd) for input-queue logic:

```gdscript
var jump_buffer: float = 0.0

func _physics_process(delta: float) -> void:
    if Input.is_action_just_pressed("jump"):
        jump_buffer = JUMP_BUFFER_TIME
    else:
        jump_buffer = max(0.0, jump_buffer - delta)

    if is_on_floor() and jump_buffer > 0.0:
        velocity.y = JUMP_VELOCITY
        jump_buffer = 0.0
```

### 4. Implement Variable Jump Height

Load [scripts/variable_jump.gd](scripts/variable_jump.gd) for velocity-cutoff on button release:

```gdscript
func _physics_process(delta: float) -> void:
    if Input.is_action_just_released("jump") and velocity.y < 0.0:
        velocity.y *= JUMP_RELEASE_MULTIPLIER
```

### 5. Implement Ground Movement

Load [scripts/player_ground_controller.gd](scripts/player_ground_controller.gd) for instant ground response and slope-aware snapping:

```gdscript
func _physics_process(delta: float) -> void:
    var input_dir := Input.get_axis("move_left", "move_right")
    if is_on_floor():
        velocity.x = input_dir * MOVE_SPEED
    else:
        velocity.x = move_toward(velocity.x, input_dir * MOVE_SPEED, AIR_ACCEL * delta)
```

### 6. Apply Gravity (Frame-Rate Independent)

```gdscript
func apply_gravity(delta: float) -> void:
    var grav := GRAVITY
    if velocity.y > 0.0:
        grav *= FALL_GRAVITY_MULTIPLIER
    velocity.y = min(velocity.y + grav * delta, MAX_FALL_SPEED)
```

### 7. Call `move_and_slide()` — Do NOT Multiply by Delta

```gdscript
func _physics_process(delta: float) -> void:
    apply_gravity(delta)
    # ... input handling ...
    move_and_slide()  # No delta multiplication — internalized
```

### 8. Set Up Camera with Look-Ahead

Load [scripts/platformer_camera.gd](scripts/platformer_camera.gd) for smoothing and look-ahead:

```gdscript
extends Camera2D

@export var look_ahead_distance := 100.0
@export var look_ahead_speed := 3.0
@export var target_path: NodePath
var target: CharacterBody2D
var target_offset := Vector2.ZERO

func _ready() -> void:
    if target_path:
        target = get_node(target_path) as CharacterBody2D

func _process(delta: float) -> void:
    if not is_instance_valid(target):
        return
    var player_velocity: Vector2 = target.velocity
    var desired_offset := player_velocity.normalized() * look_ahead_distance
    target_offset = target_offset.lerp(desired_offset, look_ahead_speed * delta)
    offset = target_offset
```

### 9. Add Squash and Stretch (Visual Juice)

Apply on jump and land events. Ensure the visual node's pivot is at the character's feet (bottom center):

```gdscript
class_name GameFeelHelper extends Node

func apply_squash_and_stretch(visual_node: Node2D, target_scale: Vector2, duration: float) -> void:
    var tween := visual_node.create_tween()
    tween.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
    tween.tween_property(visual_node, "scale", target_scale, duration)
    tween.tween_property(visual_node, "scale", Vector2.ONE, duration)
```

### 10. Add Particle Trails

```gdscript
class_name SpeedTrail extends GPUParticles2D

func toggle_trail(active: bool) -> void:
    emitting = active
    lifetime = 0.5
    one_shot = false
```

### 11. Set Up Moving Platforms

Load [scripts/synchronized_platform.gd](scripts/synchronized_platform.gd). Use `AnimatableBody2D` (NOT `CharacterBody2D`) with `sync_to_physics` enabled:

```gdscript
extends AnimatableBody2D
# sync_to_physics = true (set in inspector or code)
```

For descending platforms, set `platform_on_leave = PLATFORM_ON_LEAVE_ADD_UPWARD_VELOCITY` to preserve jump impulse.

### 12. Set Up Wall Slide and Ledge Grab

- Load [scripts/wall_slide_sensor.gd](scripts/wall_slide_sensor.gd) for nodeless wall detection via physics raycasts.
- Load [scripts/ledge_grab_sensor.gd](scripts/ledge_grab_sensor.gd) for `PhysicsShapeQuery`-based ledge detection without `Area2D` nodes.

Use `is_on_wall()` and `get_wall_normal()` for wall-jump direction.

### 13. Set Up Fast Projectiles with CCD

Load [scripts/fast_projectile_ccd.gd](scripts/fast_projectile_ccd.gd). Enable `CCD_MODE_CAST_RAY` to prevent tunneling:

```gdscript
# On RigidBody2D or physics body
# Set continuous_cd mode to CCD_MODE_CAST_RAY in inspector
```

### 14. Set Up Custom Collision Sliding

Load [scripts/custom_collision_slider.gd](scripts/custom_collision_slider.gd) for manual sliding response at high speeds where discrete collision fails.

### 15. Sync Animations with Physics State

Load [scripts/platformer_animation_sync.gd](scripts/platformer_animation_sync.gd). Use `StringName` for state keys and avoid `!` in AnimationTree expressions:

```gdscript
# Use: is_walking == false
# NOT: !is_walking
# Use: &"jumping" (StringName) instead of "jumping" (String)
```

### 16. Build Levels with TileMapLayer

Use `TileMapLayer` (NOT individual `Sprite2D` nodes) for level geometry — optimized collision and rendering.

**Teaching Trilogy pattern:**
1. **Introduction** — Safe environment to learn mechanic
2. **Challenge** — Apply mechanic with moderate risk
3. **Twist** — Combine with other mechanics or time pressure

**Pacing flow:**
```
Easy → Easy → Medium → CHECKPOINT → Medium → Hard → CHECKPOINT → Boss
```

**Visual language:**
- Safe platforms: distinct color/texture
- Hazards: red/orange tints, spikes, glow effects
- Collectibles: bright, animated, particle effects
- Secrets: subtle environmental hints

### 17. Implement Checkpoint System

```gdscript
class_name Checkpoint extends Area2D

@export var checkpoint_id: StringName

func _ready() -> void:
    body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node2D) -> void:
    if body.is_in_group("player"):
        var save_manager = get_node_or_null("/root/SaveManager")
        if save_manager:
            save_manager.current_checkpoint_pos = global_position
            save_manager.last_checkpoint_id = checkpoint_id
        play_activation_effects()

func play_activation_effects() -> void:
    var sprite = get_node_or_null("Sprite2D")
    if sprite and sprite.has_meta("active_color"):
        sprite.modulate = sprite.get_meta("active_color")
```

### 18. Implement Accessibility Options

- **Assist mode:** Toggleable reduced gravity, infinite coyote time, slower hazards
- **Remappable controls:** Use Godot InputMap API; expose in settings menu
- **Color-blind safe palettes:** Avoid red/green-only hazard indicators
- **Screen shake toggle:** Some players experience motion sickness

### 19. Sub-Genre Adaptation

| Sub-Genre | Key Traits |
|-----------|-----------|
| **Precision** (Celeste, Meat Boy) | Instant respawn, no acceleration, checkpoints every few seconds, death = learning |
| **Collectathon** (Mario 64, Banjo) | Hub worlds, ability unlocks, backtracking, collectible-gated progression |
| **Puzzle** (Limbo, Inside) | Slow pacing, environmental puzzles, physics mechanics, atmospheric storytelling |
| **Metroidvania** (Hollow Knight) | Use `godot-genre-metroidvania` skill — ability-gated exploration, interconnected map |

### 20. Polish Checklist

- [ ] Dust particles on land/run
- [ ] Screen shake on heavy landings
- [ ] Squash/stretch animations on jump and land
- [ ] Sound effects for every action (jump, land, wall-slide)
- [ ] Death and respawn animations
- [ ] Checkpoint visual/audio feedback
- [ ] Accessible difficulty options (assist mode)
- [ ] Remappable controls on all input devices

## Pitfalls

### Physics & Movement Feel — HARD RULES

1. **NEVER** multiply velocity by `delta` before `move_and_slide()` — the method internalizes the timestep.
2. **NEVER** skip Coyote Time (~0.1s) — jumps feel unresponsive when walking off ledges without it.
3. **NEVER** ignore Jump Buffering (~0.15s) — players expect to jump the instant they touch ground if they pressed early.
4. **NEVER** use fixed jump height — strictly implement Variable Jump Height (cut velocity on release).
5. **NEVER** forget to scale gravity by `delta` before adding to velocity — gravity is an acceleration and must be frame-rate independent.
6. **NEVER** rely on discrete collision for high-speed movement — strictly use `CCD_MODE_CAST_RAY` to prevent tunneling.
7. **NEVER** use `move_and_collide()` for standard traversal — it lacks slope/stair handling of `move_and_slide()`.
8. **NEVER** check coyote or buffer timers using exact equality (`== 0.0`) — strictly use `is_equal_approx()` or `>= 0.0`.
9. **NEVER** use `KinematicBody2D` — removed in Godot 4.3. Always use `CharacterBody2D` with its built-in `move_and_slide()`.
10. **NEVER** load external scripts or resources from untrusted URLs at runtime — use `ResourceLoader.load_threaded_request()` with verified paths only.

### Polish & Level Design — HARD RULES

11. **NEVER** use linear camera snapping — strictly use Camera Smoothing or `lerp()` to prevent motion sickness.
12. **NEVER** skip Squash and Stretch on jump/land — movement feels weightless without these visual juice cues.
13. **NEVER** create Blind Jumps — strictly use camera look-ahead or zoom triggers to reveal landing zones.
14. **NEVER** use individual `Sprite2D` nodes for level geometry — strictly use `TileMapLayer` for optimized collision and rendering.
15. **NEVER** use complex/concave `CollisionShape2D` for the player — strictly favor primitive shapes (Capsule/Rectangle) for stability.
16. **NEVER** enable `process_mode = PROCESS_MODE_IDLE` on physics-critical nodes — always keep `PROCESS_MODE_PHYSICS` for deterministic behavior.

### Architecture & Performance — HARD RULES

17. **NEVER** use `CharacterBody2D` for simple moving platforms — strictly use `AnimatableBody2D` and enable `sync_to_physics`.
18. **NEVER** ignore `platform_on_leave` for descending platforms — use `PLATFORM_ON_LEAVE_ADD_UPWARD_VELOCITY` to preserve jump impulse.
19. **NEVER** disable `recovery_as_collision` on the player character — required for correct floor snapping reports.
20. **NEVER** use `!` (NOT) operator in AnimationTree expressions — strictly use `is_walking == false`.
21. **NEVER** use standard `String` for high-frequency state checks — strictly use `StringName` (e.g., `&"jumping"`).
22. **NEVER** load heavy level chunks synchronously — strictly use `ResourceLoader.load_threaded_request()` to prevent frame stutters.
23. **NEVER** rely on legacy `yield()` for timers — replace with `await get_tree().create_timer()` (Godot 4.3+).

### Common Design Pitfalls

| Pitfall | Solution |
|---------|----------|
| Floaty jumps | Increase gravity, especially on descent (`FALL_GRAVITY_MULTIPLIER`) |
| Imprecise landings | Add coyote time and visual landing feedback |
| Unfair deaths | Ensure hazards are clearly visible before encountered |
| Blind jumps | Camera look-ahead or zoom out during falls |
| Boring mid-game | Introduce new mechanics every 2-3 levels |

## Verification

Run the following checks on Windows (PowerShell):

### 1. Run Test Suite

```powershell
godot --headless -s test/run.gd
```

Expected: All tests pass with exit code 0.

### 2. Verify Core Mechanics

- [ ] Coyote time: Walk off ledge, press jump within 100ms — character jumps. Press after 100ms — no jump.
- [ ] Jump buffering: Press jump 150ms before landing — character jumps immediately on land. Press earlier — no buffered jump.
- [ ] Variable jump height: Tap jump — short hop. Hold jump — full height. Release mid-rise — velocity cut by `JUMP_RELEASE_MULTIPLIER`.
- [ ] Camera smoothing: No linear snapping; `lerp()` or smoothing enabled. No motion sickness on extended play.

### 3. Verify Anti-Patterns Absent

Run static analysis or grep for forbidden patterns:

```powershell
# Check for delta multiplication before move_and_slide
Select-String -Path "scripts\*.gd" -Pattern "move_and_slide\(\s*\*\s*delta"
# Should return no matches

# Check for KinematicBody2D usage
Select-String -Path "scripts\*.gd" -Pattern "KinematicBody2D"
# Should return no matches

# Check for yield() usage
Select-String -Path "scripts\*.gd" -Pattern "\byield\("
# Should return no matches

# Check for String instead of StringName in state checks
Select-String -Path "scripts\*.gd" -Pattern '== "jumping"'
# Should return no matches (use &"jumping" instead)
```

### 4. Verify Checkpoint Persistence

- [ ] Trigger checkpoint, transition scenes, return — position and ID persisted.
- [ ] Restart game — checkpoint data loaded from save.

### 5. Verify Accessibility

- [ ] Assist mode toggles reduced gravity / infinite coyote time.
- [ ] Remappable controls work on keyboard, gamepad, and touch.
- [ ] Screen shake toggle functions.

### 6. Performance Profiling

- [ ] Particle trails and squash/stretch render without spikes — profile at 60 FPS minimum.
- [ ] Level chunk loading via `ResourceLoader.load_threaded_request()` — no frame stutters.
- [ ] Physics tick rate: consider 120 Hz (`engine/physics/common/physics_fps`) for smoother movement.

### 7. Playtest

- [ ] Sample levels follow difficulty curve and pacing guidelines.
- [ ] No blind jumps — all landing zones visible via camera look-ahead.
- [ ] Cross-reference feel against Celeste / Hollow Knight for consistency.

## Related Skills

- [godot-master](../godot-master/SKILL.md) — Master skill index
- `godot-project-foundations` — Project setup and conventions
- `godot-characterbody-2d` — CharacterBody2D deep dive
- `godot-input-handling` — Input mapping and action handling
- `animation` — AnimationTree and tween patterns
- `sound-manager` — Audio bus and SFX management
- `tilemap-setup` — TileMapLayer configuration
- `camera-2d` — Camera2D smoothing and limits
- `godot-genre-metroidvania` — Metroidvania-specific design patterns
