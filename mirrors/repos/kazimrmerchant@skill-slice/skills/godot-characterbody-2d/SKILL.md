---
name: godot-characterbody-2d
description: "Implements CharacterBody2D locomotion: move_and_slide, coyote_time, jump_buffer, variable jump height, 8-way/tank top-down, one-way platforms, and wall cling. Use when the user wants player, NPC, or enemy 2D movement feel. Trigger: is_on_floor, get_slide_collision, floor_snap_length. Not for RigidBody2D simulation or Area2D/RayCast2D query work (godot-2d-physics). Never multiply velocity by delta before move_and_slide, and never treat CharacterBody3D here."
version: 1.0.1
---

## Overview
Expert guidance for player-controlled 2D movement using Godot's physics system. Covers platformer mechanics, top-down movement, collision handling, and state machines.

## When to Use
- Use for player characters (platformer, top-down, side-scroller)
- Use for NPCs with custom movement logic
- Use for enemies with non-physics-based movement
- Trigger keywords: CharacterBody2D, move_and_slide, is_on_floor, coyote_time, jump_buffer, velocity, get_slide_collision, one_way_platforms, state_machine.

## Prerequisites
- Godot 4.x project (Godot 4.7 compatible)
- Windows host (PowerShell) primary environment
- Scripts located in `scripts/` directory relative to this skill

## Procedure
1. **Load Foundation Script**: Before implementing any platformer mechanics, read `scripts/expert_physics_2d.gd` for the complete platformer foundation (coyote time, jump buffering, smooth acceleration/friction, sub-pixel stabilization).
2. **Implement Basic Platformer Controller**:
   - Apply gravity only if `not is_on_floor()`.
   - Handle jump input.
   - Get input direction and apply movement using `move_toward` for acceleration/friction.
   - Call `move_and_slide()`.
3. **Add Advanced Mechanics**: Load the corresponding script from `scripts/` before implementing:
   - Coyote Time & Jump Buffering: `scripts/frame_perfect_coyote_time.gd`
   - Slope/Stair Snapping: `scripts/slope_stair_snapping.gd`
   - Variable Jump Height: `scripts/variable_jump_height.gd`
   - Wall Slide/Jump: `scripts/wall_slide_jump_refined.gd` or `scripts/wall_jump_controller.gd`
   - Dash: `scripts/dash_state_controller.gd` or `scripts/dash_controller.gd`
   - Sub-pixel Rounding: `scripts/subpixel_movement_rounding.gd`
   - Character Pooling: `scripts/performance_character_pooling.gd`
   - Impulse/Knockback: `scripts/impulse_response_handler.gd`
   - Aerial Drift: `scripts/aerial_drift_acceleration.gd`
   - Ceiling Bonk: `scripts/ceiling_bonk_detection.gd`
4. **Top-Down Movement**:
   - 8-Directional: Use `Input.get_vector` and normalize for diagonal movement. Accelerate/friction using `velocity.move_toward`.
   - Tank Controls: Rotate using `Input.get_axis` and move forward/backward using `transform.x`.
5. **Collision Handling**:
   - Detect floor/walls/ceiling using `is_on_floor()`, `is_on_wall()`, `is_on_ceiling()`.
   - Iterate `get_slide_collision_count()` and use `get_slide_collision(i)` for collision info (collider, normal).
   - One-Way Platforms: Check `Input.is_action_pressed("move_down")` and increment `position.y` slightly to pass through.
6. **State Machine Implementation**:
   - Use an `enum` for states (IDLE, RUNNING, JUMPING, FALLING, DASHING).
   - Match state in `_physics_process` and call corresponding state functions.

## Examples

### Basic Platformer Controller
```gdscript
extends CharacterBody2D

const SPEED := 300.0
const JUMP_VELOCITY := -400.0

var gravity: int = ProjectSettings.get_setting("physics/2d/default_gravity")

func _physics_process(delta: float) -> void:
    if not is_on_floor():
        velocity.y += gravity * delta
    
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = JUMP_VELOCITY
    
    var direction := Input.get_axis("move_left", "move_right")
    
    if direction:
        velocity.x = direction * SPEED
    else:
        velocity.x = move_toward(velocity.x, 0, SPEED)
    
    move_and_slide()
```

### Advanced Platformer with Coyote Time & Jump Buffer
```gdscript
extends CharacterBody2D

const SPEED := 300.0
const JUMP_VELOCITY := -400.0
const ACCELERATION := 1500.0
const FRICTION := 1200.0
const AIR_RESISTANCE := 200.0

const COYOTE_TIME := 0.1
var coyote_timer := 0.0

const JUMP_BUFFER_TIME := 0.1
var jump_buffer_timer := 0.0

var gravity: int = ProjectSettings.get_setting("physics/2d/default_gravity")

func _physics_process(delta: float) -> void:
    if not is_on_floor():
        velocity.y += gravity * delta
        coyote_timer -= delta
    else:
        coyote_timer = COYOTE_TIME
    
    if Input.is_action_just_pressed("jump"):
        jump_buffer_timer = JUMP_BUFFER_TIME
    else:
        jump_buffer_timer -= delta
    
    if jump_buffer_timer > 0 and coyote_timer > 0:
        velocity.y = JUMP_VELOCITY
        jump_buffer_timer = 0
        coyote_timer = 0
    
    if Input.is_action_just_released("jump") and velocity.y < 0:
        velocity.y *= 0.5
    
    var direction := Input.get_axis("move_left", "move_right")
    
    if direction:
        velocity.x = move_toward(velocity.x, direction * SPEED, ACCELERATION * delta)
    else:
        var friction_value := FRICTION if is_on_floor() else AIR_RESISTANCE
        velocity.x = move_toward(velocity.x, 0, friction_value * delta)
    
    move_and_slide()
```

### 8-Directional Top-Down
```gdscript
extends CharacterBody2D

const SPEED := 200.0
const ACCELERATION := 1500.0
const FRICTION := 1000.0

func _physics_process(delta: float) -> void:
    var input_vector := Input.get_vector("move_left", "move_right", "move_up", "move_down")
    
    if input_vector != Vector2.ZERO:
        velocity = velocity.move_toward(input_vector * SPEED, ACCELERATION * delta)
    else:
        velocity = velocity.move_toward(Vector2.ZERO, FRICTION * delta)
    
    move_and_slide()
```

### Top-Down with Rotation (Tank Controls)
```gdscript
extends CharacterBody2D

const SPEED := 200.0
const ROTATION_SPEED := 3.0

func _physics_process(delta: float) -> void:
    var rotate_direction := Input.get_axis("rotate_left", "rotate_right")
    rotation += rotate_direction * ROTATION_SPEED * delta
    
    var move_direction := Input.get_axis("move_backward", "move_forward")
    velocity = transform.x * move_direction * SPEED
    
    move_and_slide()
```

### Collision Handling
```gdscript
func _physics_process(delta: float) -> void:
    move_and_slide()
    
    for i in get_slide_collision_count():
        var collision := get_slide_collision(i)
        if collision.get_collider().is_in_group("bouncy"):
            velocity = velocity.bounce(collision.get_normal())
```

### One-Way Platforms
```gdscript
func _physics_process(delta: float) -> void:
    if Input.is_action_pressed("move_down") and is_on_floor():
        position.y += 1
    
    velocity.y += gravity * delta
    move_and_slide()
```

### State Machine
```gdscript
extends CharacterBody2D

enum State { IDLE, RUNNING, JUMPING, FALLING, DASHING }

var current_state := State.IDLE
var dash_velocity := Vector2.ZERO
const DASH_SPEED := 600.0
const DASH_DURATION := 0.2
var dash_timer := 0.0

func _physics_process(delta: float) -> void:
    match current_state:
        State.IDLE: _state_idle(delta)
        State.RUNNING: _state_running(delta)
        State.JUMPING: _state_jumping(delta)
        State.FALLING: _state_falling(delta)
        State.DASHING: _state_dashing(delta)

func _state_idle(delta: float) -> void:
    velocity.x = move_toward(velocity.x, 0, FRICTION * delta)
    if Input.is_action_pressed("move_left") or Input.is_action_pressed("move_right"):
        current_state = State.RUNNING
    elif Input.is_action_just_pressed("jump"):
        current_state = State.JUMPING
    move_and_slide()

func _state_dashing(delta: float) -> void:
    dash_timer -= delta
    velocity = dash_velocity
    if dash_timer <= 0:
        current_state = State.IDLE
    move_and_slide()
```

### Expert Architectures

#### Wall Cling (Variable Friction)
```gdscript
class_name WallClingController extends CharacterBody2D

@export var wall_friction: float = 0.15
@export var gravity: float = 980.0

func _physics_process(delta: float) -> void:
    if not is_on_floor():
        velocity.y += gravity * delta
        if is_on_wall() and velocity.y > 0:
            velocity.y *= wall_friction
    move_and_slide()
```

#### Animation-Driven Movement (Root Motion)
```gdscript
class_name RootMotionController2D extends CharacterBody2D

@export var animation_tree: AnimationTree

func _physics_process(delta: float) -> void:
    var root_motion: Vector3 = animation_tree.get_root_motion_position()
    var motion_2d := Vector2(root_motion.x, root_motion.z)
    velocity = motion_2d / delta
    move_and_slide()
```

#### Game-Feel Profiler (Jump Arcs)
```gdscript
class_name GameFeelProfiler extends Node2D

@export var character: CharacterBody2D
var _points: PackedVector2Array = []

func _process(_delta: float) -> void:
    if not character: return
    _points.append(character.global_position - global_position)
    if _points.size() > 100: _points.remove_at(0)
    queue_redraw()

func _draw() -> void:
    if _points.size() < 2: return
    draw_polyline(_points, Color.CYAN, 2.0, true)
    draw_line(_points[-1], _points[-1] + character.velocity * 0.1, Color.YELLOW, 3.0)
```

## Pitfalls
- **NEVER use `RigidBody2D` for standard player controllers** — RigidBody is for physics-simulated objects. For responsive, feel-driven player movement, always use `CharacterBody2D`.
- **NEVER multiply `velocity` by `delta` before `move_and_slide()`** — `move_and_slide()` handles delta internally. Manual multiplication makes movement framerate-dependent.
- **NEVER use `global_position` updates for movement** — Use `velocity` and `move_and_slide()`. Direct position updates bypass collision detection and floor snapping.
- **NEVER ignore the return value of `move_and_slide()`** — While optional, checking `is_on_floor()` or `get_last_motion()` immediately after is critical for state logic.
- **NEVER rely on default `floor_snap_length` for fast stair-climbing** — Default snapping is too small for high-velocity characters. Use custom raycast-based stair logic for smooth transitions.
- **NEVER apply gravity while `is_on_floor()` is true** — Constant downward force on the floor can cause "micro-jitter" or prevent floor-snap from working correctly. Reset `velocity.y` to 0 or a small constant.
- **NEVER use `Area2D` for ground detection** — Real collisions (rays/shapecasts) are more precise. `is_on_floor()` is highly optimized; only augment it if necessary.
- **NEVER forget Ceiling Bonk detection** — If you don't reset `velocity.y` to 0 when `is_on_ceiling()`, the player will "float" against the ceiling until gravity pulls them down.
- **NEVER use high-precision physics for pixel art visuals** — Keep physics math high-precision, but round your Sprite nodal positions in `_process` to avoid visual sub-pixel jitter.
- **NEVER use `queue_free()` on characters every frame** — Use object pooling for bullets or enemies to avoid SceneTree performance spikes.
- **Character slides on slopes**: Increase friction.
- **Character stutters on moving platforms**: Enable platform snap and add `get_platform_velocity()` to velocity.
- **Double jump exploit**: Track if jump was used with a boolean flag.

## Verification
1. **Check Gravity Application**: Ensure `velocity.y` is not increasing while `is_on_floor()` is true.
2. **Check Delta Usage**: Search codebase for `velocity * delta` before `move_and_slide()` — this should not exist.
3. **Check Ceiling Bonk**: Verify `velocity.y = 0` is set when `is_on_ceiling()` is true.
4. **Run Project**: Execute `godot --path .` in PowerShell to verify no runtime errors and character moves correctly.

## Related skills
- Master Skill: [godot-master](../godot-master/SKILL.md)
