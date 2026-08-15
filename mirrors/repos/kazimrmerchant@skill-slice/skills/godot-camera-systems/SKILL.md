---
name: godot-camera-systems
description: "Controls Godot Camera2D/Camera3D follow: position_smoothing, trauma shake on offset, drag_margin deadzones, look-ahead, SpringArm3D, and split-screen viewports. Use when the user wants a player camera, cinematic PathFollow, or RemoteTransform decoupling. Trigger: camera_limits, limit_smoothed, look_at. Not for GridMap/CSG world layout or AnimationPlayer tracks as the camera rig. Never snap global_position to the target every frame or parent the camera to a high-speed physics body."
version: 1.0.1
---

## When to Use
Use this skill when implementing 2D/3D camera control, smooth following (lerp, position_smoothing), camera shake (trauma system), screen shake with frequency parameters, deadzone/drag for platformers, look-ahead prediction, and camera transitions. Ideal for player cameras, cinematic sequences, or multi-camera systems.

## Prerequisites
- Target engine: **Godot 4.7+** (stable, 2026-06-18).
- Consult the [Godot 4.7 migration guide](https://docs.godotengine.org/en/4.7/tutorials/migrating/upgrading_to_godot_4.7.html) when upgrading projects from 4.6.
- **NEVER** assume 4.6 defaults (stretch mode, audio area_mask, RichTextLabel percent flags) without checking 4.7 migration notes.

## Procedure

### 1. Load Required Scripts
**MANDATORY**: Read the relevant script from `scripts/` before implementing camera behaviors.
- Load `scripts/camera_shake_trauma_pro.gd` when implementing advanced noise-based screenshake (Trauma system) for organic, non-jittery explosions and impacts.
- Load `scripts/cinematic_framing_logic.gd` when managing Rule of Thirds and Lead Room in code for high-quality cinematic composition.
- Load `scripts/camera_state_machine.gd` when managing transitions between 'Follow', 'Static', and 'Cinematic' camera states with Tweens.
- Load `scripts/minimap_viewport_manager.gd` when optimizing SubViewports for Mini-maps and UI overlays to reduce render updates.
- Load `scripts/split_screen_setup.gd` when building dynamic split-screen architecture for local multiplayer, handling viewport stretching and audio listeners.
- Load `scripts/remote_transform_decoupling.gd` when decoupling camera position from player rotation/scale using `RemoteTransform2D` for high-speed stability.
- Load `scripts/zoom_damping_controller.gd` when implementing non-linear, smooth zoom logic with tactical overview bounds and mouse-wheel support.
- Load `scripts/spring_lerp_camera_3d.gd` when building a physics-stable 3D follow camera using spring-mass interpolation to reduce follow-latency jitter.
- Load `scripts/first_person_sway.gd` when adding procedural 8-figure head bob and weapon sway logic for immersive First-Person systems.
- Load `scripts/deadzone_drag_margins.gd` when managing platformer-specific deadzones using code to control follow-margins and drag-center behavior.

### 2. Camera2D Basics & Smoothing
```gdscript
extends Camera2D

@export var target: Node2D
@export var follow_speed := 5.0

func _process(delta: float) -> void:
    if target:
        global_position = global_position.lerp(
            target.global_position,
            follow_speed * delta
        )

func _ready() -> void:
    # Built-in smoothing
    position_smoothing_enabled = true
    position_smoothing_speed = 5.0
```

### 3. Camera Limits
```gdscript
extends Camera2D

func _ready() -> void:
    # Constrain camera to level bounds
    limit_left = 0
    limit_top = 0
    limit_right = 1920
    limit_bottom = 1080
    
    # Smooth against limits
    limit_smoothed = true
```

### 4. Camera Shake (Offset-based)
```gdscript
extends Camera2D

var shake_amount := 0.0
var shake_decay := 5.0

func _process(delta: float) -> void:
    if shake_amount > 0:
        shake_amount = max(shake_amount - shake_decay * delta, 0)
        offset = Vector2(
            randf_range(-shake_amount, shake_amount),
            randf_range(-shake_amount, shake_amount)
        )
    else:
        offset = Vector2.ZERO

func shake(intensity: float) -> void:
    shake_amount = intensity

# Usage:
$Camera2D.shake(10.0)  # Screen shake on explosion
```

### 5. Zoom Controls
```gdscript
extends Camera2D

@export var zoom_speed := 0.1
@export var min_zoom := 0.5
@export var max_zoom := 2.0

func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventMouseButton:
        if event.button_index == MOUSE_BUTTON_WHEEL_UP:
            zoom_in()
        elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
            zoom_out()

func zoom_in() -> void:
    zoom = zoom.move_toward(Vector2.ONE * max_zoom, zoom_speed)

func zoom_out() -> void:
    zoom = zoom.move_toward(Vector2.ONE * min_zoom, zoom_speed)
```

### 6. Look-Ahead Camera
```gdscript
extends Camera2D

@export var look_ahead_distance := 50.0
@export var target: CharacterBody2D

func _process(delta: float) -> void:
    if target:
        var look_ahead := target.velocity.normalized() * look_ahead_distance
        global_position = target.global_position + look_ahead
```

### 7. Split-Screen (Multiple Cameras)
```gdscript
# Player 1 Camera
@onready var cam1: Camera2D = $Player1/Camera2D

# Player 2 Camera
@onready var cam2: Camera2D = $Player2/Camera2D

func _ready() -> void:
    # Split viewport
    cam1.anchor_mode = Camera2D.ANCHOR_MODE_DRAG_CENTER
    cam2.anchor_mode = Camera2D.ANCHOR_MODE_DRAG_CENTER
```

### 8. Camera3D Patterns
#### Third-Person Camera
```gdscript
extends Camera3D

@export var target: Node3D
@export var distance := 5.0
@export var height := 2.0
@export var rotation_speed := 3.0

var rotation_angle := 0.0

func _process(delta: float) -> void:
    if not target:
        return
    
    rotation_angle += Input.get_axis("camera_left", "camera_right") * rotation_speed * delta
    
    var offset := Vector3(
        sin(rotation_angle) * distance,
        height,
        cos(rotation_angle) * distance
    )
    
    global_position = target.global_position + offset
    look_at(target.global_position, Vector3.UP)
```

#### First-Person Camera
```gdscript
extends Camera3D

@export var mouse_sensitivity := 0.002
@export var max_pitch := deg_to_rad(80)

var pitch := 0.0

func _ready() -> void:
    Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _input(event: InputEvent) -> void:
    if event is InputEventMouseMotion:
        get_parent().rotate_y(-event.relative.x * mouse_sensitivity)
        pitch -= event.relative.y * mouse_sensitivity
        pitch = clamp(pitch, -max_pitch, max_pitch)
        rotation.x = pitch
```

### 9. Camera Transitions & Cinematic Cameras
```gdscript
# Smooth camera position change
func move_to_position(target_pos: Vector2, duration: float = 1.0) -> void:
    var tween := create_tween()
    tween.tween_property(self, "global_position", target_pos, duration)
    tween.set_ease(Tween.EASE_IN_OUT)
    tween.set_trans(Tween.TRANS_CUBIC)

# Camera path following
extends Path2D

@onready var path_follow: PathFollow2D = $PathFollow2D
@onready var camera: Camera2D = $PathFollow2D/Camera2D

func play_cutscene(duration: float) -> void:
    var tween := create_tween()
    tween.tween_property(path_follow, "progress_ratio", 1.0, duration)
    await tween.finished
```

### 10. Expert Camera Architectures
#### Camera Framing Box (Multi-Target Framing)
```gdscript
class_name FramingBoxCamera2D extends Camera2D
## Dynamically zooms and pans to frame multiple targets.

@export var targets: Array[Node2D] = []
@export var margin: float = 100.0
@export var min_zoom: float = 0.5
@export var max_zoom: float = 2.0

func _physics_process(_delta: float) -> void:
    if targets.is_empty(): return
    
    var rect := Rect2(targets[0].global_position, Vector2.ZERO)
    for target in targets:
        rect = rect.expand(target.global_position)
    
    rect = rect.grow(margin)
    global_position = rect.get_center()
    
    var screen_size := get_viewport_rect().size
    var zoom_x := screen_size.x / rect.size.x
    var zoom_y := screen_size.y / rect.size.y
    var target_zoom := clampf(min(zoom_x, zoom_y), min_zoom, max_zoom)
    
    zoom = Vector2.ONE * target_zoom
```

#### Camera Raycasting (Occlusion Aware)
```gdscript
class_name OcclusionAwareCamera3D extends Camera3D
## Prevents camera clipping via manual physics space raycasting.

@export var target: Node3D
@export var ideal_distance: float = 5.0

func _physics_process(_delta: float) -> void:
    if not target: return
    
    var space_state := get_world_3d().direct_space_state
    var desired_pos := target.global_position + (Vector3.BACK * ideal_distance)
    
    var query := PhysicsRayQueryParameters3D.create(target.global_position, desired_pos)
    query.exclude = [target.get_rid()]
    
    var result: Dictionary = space_state.intersect_ray(query)
    
    if not result.is_empty():
        global_position = result.position + result.normal * 0.2
    else:
        global_position = desired_pos
        
    look_at(target.global_position)
```

#### Screenshake Audit (Trauma Decay Profiler)
```gdscript
class_name TraumaDebugger extends Node2D
## Visualizes the decay curve of a trauma-based shake system.

@export var camera: ProceduralScreenShake
var _history: PackedFloat32Array = []

func _process(_delta: float) -> void:
    if not camera: return
    
    _history.append(camera.get_current_trauma())
    if _history.size() > 200: _history.remove_at(0)
    queue_redraw()

func _draw() -> void:
    var width := 400.0
    var height := 100.0
    var step := width / 200.0
    
    for i in range(1, _history.size()):
        var p1 := Vector2(i * step, height - (_history[i-1] * height))
        var p2 := Vector2((i+1) * step, height - (_history[i] * height))
        draw_line(p1, p2, Color.YELLOW, 2.0)
```

## Pitfalls
- **NEVER use `global_position = target.global_position` every frame** — Instant position matching causes jittery movement. Use `lerp()` or `position_smoothing_enabled = true`.
- **NEVER use `offset` for permanent camera positioning** — `offset` is for shake, sway, or temporary recoil effects only. Use `position` for permanent framing to avoid logic conflicts.
- **NEVER forget `limit_smoothed = true` for `Camera2D`** — Hard boundaries cause jarring visual stops. Smoothing against limits ensures a professional feel.
- **NEVER enable multiple `Camera2D` nodes in the same viewport simultaneously** — Only the last enabled camera takes precedence. Explicitly disable inactive cameras.
- **NEVER use `SpringArm3D` without a collision mask** — It will clip through terrain and walls. Set it to the world/environment layer.
- **NEVER implement screen shake by randomizing `position` directly** — This overwrites follow-logic. Use `offset` or a dedicated Trauma/Noise system to Layer shake over the follow-position.
- **NEVER parent the Camera directly to a high-speed physics body** — Physics stutter or parent rotation will cause motion sickness. Use `RemoteTransform2D/3D` with rotation sync disabled for a stable view.
- **NEVER use `look_at()` in 3D without a fallback for the 'Up' vector** — If the target is directly above/below, the camera will flip wildly. Use guards or `Quaternion` math for vertical tracking.
- **NEVER rely on `SubViewport` defaults for Mini-maps** — Viewports are expensive; explicitly set `render_target_update_mode` to `UPDATE_WHEN_VISIBLE` or a fixed lower framerate to save GPU.
- **NEVER use linear interpolation for Zoom** — It feels 'robotic'. Use exponential lerp or a `Tween` with `TRANS_CUBIC` for a more natural tactical feel.

## Verification
1. Verify camera smoothing by checking `position_smoothing_enabled` is `true` and `position_smoothing_speed` is set appropriately in the inspector or code.
2. Verify camera limits by checking `limit_left`, `limit_top`, `limit_right`, `limit_bottom`, and `limit_smoothed` are configured correctly.
3. Verify screen shake by ensuring `offset` is used for shake calculations instead of `position`.
4. Verify 3D occlusion by checking `SpringArm3D` collision mask or `intersect_ray` query excludes the target.
5. Verify split-screen by checking only one `Camera2D` is enabled per viewport.

## Related skills
- Master Skill: [godot-master](../godot-master/SKILL.md)
