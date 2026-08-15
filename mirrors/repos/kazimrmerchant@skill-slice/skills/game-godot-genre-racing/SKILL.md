---
name: game-godot-genre-racing
version: 1.1.1
description: "Blueprints Godot 4 racing: VehicleBody3D and VehicleWheel3D, sequential checkpoints, rubber-banding AI, drift-boost, speed-FOV camera, lap UI, and ghost cars. Use when building arcade, kart, or sim racers, time trials, or track vehicle physics. Not for Godot MultiplayerAPI/RPC (networking-multiplayer) or non-racing vehicle sandboxes. Do not use for 2D platformers or other genre chairs."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Overview
Expert blueprint for racing games balancing physics, competition, and sense of speed.

## When to Use
Use this skill when building any racing game genre including:
- Arcade racers (Need for Speed, Burnout style)
- Kart racing games (Mario Kart style)
- Realistic racing simulators (Assetto Corsa, Gran Turismo style)
- Time trial / ghost car systems
- Multiplayer competitive racing
- Any game requiring vehicle physics, checkpoint systems, AI opponents, drift mechanics, or racing UI

### Core Loop
1. **Race**: Player controls a vehicle on a track.
2. **Compete**: Player overtakes opponents or beats the clock.
3. **Upgrade**: Player earns currency/points to buy parts/cars.
4. **Tune**: Player adjusts vehicle stats (grip, acceleration).
5. **Master**: Player learns track layouts and optimal lines.

### Skill Chain
| Phase | Skills | Purpose |
|-------|--------|---------|
| 1. Physics | `physics-bodies`, `vehicle-wheel-3d` | Car movement, suspension, collisions |
| 2. AI | `navigation`, `steering-behaviors` | Opponent pathfinding, rubber-banding |
| 3. Input | `input-mapping` | Analog steering, acceleration, braking |
| 4. UI | `progress-bars`, `labels` | Speedometer, lap timer, minimap |
| 5. Feel | `camera-shake`, `godot-particles` | Speed perception, tire smoke, sparks |

## Prerequisites
- Godot 4.x project with 3D setup.
- Input actions mapped: `right`, `left`, `forward`, `back` (or equivalent analog axes).
- Basic understanding of `VehicleBody3D` and `VehicleWheel3D`.

## Procedure

### 1. Vehicle Controller Setup
1. Create a `VehicleBody3D` node.
2. Attach `VehicleWheel3D` nodes for each wheel.
3. Load `scripts/arcade_vehicle_physics.gd` when implementing high-performance arcade handling with custom gravity, air control, and friction-slip drifting.
4. Load `scripts/raycast_suspension.gd` when configuring spring/damper models for raycast wheels with configurable stiffness.
5. Implement steering and engine force:
```gdscript
# car_controller.gd
extends VehicleBody3D

@export var max_torque: float = 300.0
@export var max_steering: float = 0.4

func _physics_process(delta: float) -> void:
    steering = lerp(steering, Input.get_axis("right", "left") * max_steering, 5 * delta)
    engine_force = Input.get_axis("back", "forward") * max_torque
```

### 2. Checkpoint System
1. Place `Area3D` nodes sequentially along the track.
2. Load `scripts/lap_tracker.gd` for high-precision lap management with sequential checkpoint logic.
3. Load `scripts/racing_checkpoint.gd` for indexed trigger gate modular track-based lap progression.
4. Implement validation:
```gdscript
# checkpoint_manager.gd
extends Node

var checkpoints: Array[Area3D] = []
var current_checkpoint_index: int = 0
signal lap_completed

func _on_checkpoint_entered(body: Node3D, index: int) -> void:
    if index == current_checkpoint_index + 1:
        current_checkpoint_index = index
    elif index == 0 and current_checkpoint_index == checkpoints.size() - 1:
        complete_lap()

func complete_lap() -> void:
    current_checkpoint_index = 0
    lap_completed.emit()
```

### 3. Race Manager
1. Create a high-level state machine for race states (COUNTDOWN, RACING, FINISHED).
2. Use `await` for async countdown timers.
```gdscript
# race_manager.gd
extends Node

enum State { COUNTDOWN, RACING, FINISHED }
var current_state: State = State.COUNTDOWN
var elapsed_time: float = 0.0

func start_race() -> void:
    await countdown()
    current_state = State.RACING

func _process(delta: float) -> void:
    if current_state == State.RACING:
        elapsed_time += delta

func countdown() -> void:
    var count = 3
    while count > 0:
        await get_tree().create_timer(1.0).timeout
        count -= 1
```

### 4. AI & Competition
1. Load `scripts/spline_ai_controller.gd` when implementing professional racing AI using Path3D predictive steering and rubber-banding logic.
2. Load `scripts/slipstream_handler.gd` when adding drafting zones with relative dot-product checks for speed boosts.
3. Implement rubber-banding to keep races competitive:
```gdscript
class_name RubberBandingSystem extends Node

@export var player_vehicle: VehicleBody3D
@export var base_speed: float = 120.0

func update_ai_speed(ai_car: VehicleBody3D) -> void:
    if not is_instance_valid(player_vehicle):
        return
        
    var dist = ai_car.global_position.distance_to(player_vehicle.global_position)
    var ai_is_ahead = ai_car_is_ahead_of_player(ai_car, player_vehicle)
    
    if ai_is_ahead:
        ai_car.max_speed = base_speed * 0.9
    else:
        ai_car.max_speed = base_speed * 1.1

func ai_car_is_ahead_of_player(ai_car: VehicleBody3D, player: VehicleBody3D) -> bool:
    var forward_dir = -player.global_transform.basis.z.normalized()
    var to_ai = (ai_car.global_position - player.global_position).normalized()
    return forward_dir.dot(to_ai) > 0.0
```

### 5. Drifting & Boost Mechanics
1. Implement drift by reducing friction or applying sideways force.
2. Load `scripts/arcade_vehicle_controller.gd` for an alternative tight, raycast-based vehicle movement model for non-physics karts.
3. Implement Drift-Boost (Mini-Turbo) by accumulating charge and applying `apply_central_impulse()`:
```gdscript
class_name DriftBoostSystem extends Node

@export var vehicle: VehicleBody3D
var drift_charge: float = 0.0
const BOOST_MULTIPLIER = 1000.0
var is_drifting: bool = false

func _physics_process(delta: float) -> void:
    if not is_instance_valid(vehicle):
        return
        
    if is_drifting:
        drift_charge += delta
    elif drift_charge > 0.0:
        execute_boost()

func execute_boost() -> void:
    if is_instance_valid(vehicle):
        var boost_force := -vehicle.global_transform.basis.z * (drift_charge * BOOST_MULTIPLIER)
        vehicle.apply_central_impulse(boost_force)
    drift_charge = 0.0
```

### 6. Visuals, Audio, & UI
1. Load `scripts/skid_mark_emitter.gd` when implementing conditional tire-slip trail systems for persistent visual feedback.
2. Load `scripts/engine_audio_controller.gd` for RPM-to-pitch audio synthesis for engine revving and gear shifts.
3. Load `scripts/minimap_icon_projector.gd` for 3D-to-2D bridge for projecting racers onto a localized UI.
4. Load `scripts/force_feedback_router.gd` for haptic and rumble management based on terrain and collisions.
5. Load `scripts/ghost_recorder.gd` for binary transform serialization for lightweight ghost car playback.
6. Attach `GPUParticles3D` to wheels for tire smoke, toggling `emitting` based on `wheel.get_skidinfo() < 0.5`.
7. Use `SubViewport` for rear-view mirror or minimap texture.
8. Use `Doppler` effect on `AudioListener` for realistic passing sounds.

## Pitfalls

### Physics & Handling
- NEVER use a rigid camera attachment; strictly use a **Smooth Follow** pattern with `lerp()` to prevent motion sickness.
- NEVER prioritize realism over fun; strictly increase **Gravity Scale** (2x-3x) and keep friction high for responsive arcade feel.
- NEVER use `VehicleBody3D` default settings for karts; strictly rewrite suspension using Raycasts or custom spring/damper models.
- NEVER apply steering torque directly to mass; strictly use a steering curve factored by lateral velocity.
- NEVER calculate suspension without a damper model; strictly include damping to prevent eternal oscillation (bouncing).
- NEVER ignore the **Center of Mass** property; strictly offset it downward to ensure stability during high-speed turns.
- NEVER multiply engine force by `delta`; it is an integrated force in the physics solver.
- NEVER rely on `is_action_pressed()` for manual gear shifting; strictly use `is_action_just_pressed()` for single-tap accuracy.

### AI & Competition
- NEVER use static AI speeds; strictly use **Rubber-Banding** to keep races competitive based on player distance.
- NEVER run AI pathfinding across the entire track every frame; strictly use a "Look-Ahead" point on a spline/path.
- NEVER ignore racing **Checkpoints**; strictly enforce sequential `Area3D` validation to prevent track shortcuts.
- NEVER use standard `Area3D` for slipstreaming without a **Dot Product** check to ensure the player is directly behind.

### Visuals & Audio
- NEVER skip "Sense of Speed" effects; strictly implement dynamic **FOV scaling**, motion blur, and high-speed camera shake.
- NEVER update minimap transforms for static elements in `_process()`; strictly update dynamic racers only.
- NEVER serialize ghost cars as mass transform lists; strictly store positions/quaternions at fixed intervals.
- NEVER use constant pitch for engine sounds; strictly map RPM or engine load to `pitch_scale`.
- NEVER spawn particles for skid marks every frame; strictly use **Trail3D** or procedural strips for low-cost persistence.
- NEVER use standard Strings for surface detection; strictly use `StringName` (e.g., `&"asphalt"`).

### Security & Deprecation
- NEVER expose raw file paths when saving ghost data; always sanitize and use `FileAccess` with the `User` directory to avoid path traversal.
- NEVER rely on the deprecated `yield()` for async; use `await` with `Callable` or `Signal` as shown in the Race Manager.
- NEVER store sensitive player telemetry in plain text; encrypt or hash if transmitting over network.

## Verification
- [ ] Verify VehicleBody3D center of mass is offset downward for stability
- [ ] Confirm gravity scale is set to 2.0-3.0 for arcade feel
- [ ] Test checkpoint system prevents shortcuts (sequential validation)
- [ ] Verify rubber-banding AI adjusts speed based on player distance
- [ ] Confirm drift mechanic reduces lateral friction and provides exit boost
- [ ] Test camera uses smooth follow (lerp) not rigid attachment
- [ ] Verify FOV scales with speed for sense of speed
- [ ] Confirm engine audio pitch maps to RPM/engine load
- [ ] Test ghost recorder uses binary serialization (PackedVector3Array)
- [ ] Verify skid marks use Trail3D not per-frame particles
- [ ] Confirm minimap only updates dynamic elements in _process()
- [ ] Test slipstream uses dot product for behind-check
- [ ] Verify suspension includes damper model (no eternal oscillation)
- [ ] Confirm steering uses curve factored by lateral velocity
- [ ] Test gear shifting uses is_action_just_pressed() not is_action_pressed()
- [ ] Ensure no deprecated `yield()` calls remain in scripts
- [ ] Validate all file I/O uses sanitized paths within `user://` directory

## Related skills
- [godot-master](../godot-master/SKILL.md) - Master Godot skill reference
- `physics-bodies` - RigidBody3D, VehicleBody3D physics fundamentals
- `vehicle-wheel-3d` - Wheel configuration, suspension tuning
- `navigation` - Path3D, NavigationServer for AI pathfinding
- `steering-behaviors` - Seek, flee, arrival for AI movement
- `input-mapping` - Analog input handling for steering/acceleration
- `progress-bars` - Speedometer, fuel gauge, boost meter UI
- `labels` - Lap timer, position counter, sector times
- `camera-shake` - Impact, rumble, high-speed shake effects
- `godot-particles` - Tire smoke, sparks, dust trails
