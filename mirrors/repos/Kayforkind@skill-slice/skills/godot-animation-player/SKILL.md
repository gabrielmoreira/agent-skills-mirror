---
name: godot-animation-player
description: "Drives Godot AnimationPlayer timelines: value/method/audio/bezier tracks, RESET tracks, root_motion, queue/blend_times, and CALL_MODE_DISCRETE callbacks. Use when the user wants cutscenes, UI transitions, prop playback, or procedural track_insert_key. Trigger: animation_finished, animation_set_next, seek. Not for AnimationTree BlendSpace2D/StateMachine locomotion and not AnimatedSprite2D SpriteFrames. Never use CALL_MODE_CONTINUOUS for one-shot method tracks."
version: 1.0.1
---

## When to Use
Use this skill for timeline-based keyframe animations, cutscenes, character animations, complex UI transitions, root motion extraction, and procedural animation generation in Godot 4.7. Trigger keywords: AnimationPlayer, Animation, track_insert_key, root_motion, animation_finished, RESET_track, call_mode, animation_set_next, queue, blend_times.

## Prerequisites
- Godot 4.7 project.
- Ensure `AnimationPlayer` node is present in the scene.
- Read the appropriate script from `scripts/` before implementing the corresponding pattern (see Procedure).

## Procedure

### 1. Track Types Deep Dive
#### Value Tracks (Property Animation)
```gdscript
# Animate ANY property: position, color, volume, custom variables
var anim := Animation.new()
anim.length = 2.0

# Position track
var pos_track := anim.add_track(Animation.TYPE_VALUE)
anim.track_set_path(pos_track, ".:position")
anim.track_insert_key(pos_track, 0.0, Vector2(0, 0))
anim.track_insert_key(pos_track, 1.0, Vector2(100, 0))
anim.track_set_interpolation_type(pos_track, Animation.INTERPOLATION_CUBIC)

# Color track (modulate)
var color_track := anim.add_track(Animation.TYPE_VALUE)
anim.track_set_path(color_track, "Sprite2D:modulate")
anim.track_insert_key(color_track, 0.0, Color.WHITE)
anim.track_insert_key(color_track, 2.0, Color.TRANSPARENT)

$AnimationPlayer.add_animation("fade_move", anim)
$AnimationPlayer.play("fade_move")
```

#### Method Tracks (Function Calls)
```gdscript
# Call functions at specific timestamps
var method_track := anim.add_track(Animation.TYPE_METHOD)
anim.track_set_path(method_track, ".")  # Path to node

# Insert method calls
anim.track_insert_key(method_track, 0.5, {
    "method": "spawn_particle",
    "args": [Vector2(50, 50)]
})

anim.track_insert_key(method_track, 1.5, {
    "method": "play_sound",
    "args": ["res://sounds/explosion.ogg"]
})

# CRITICAL: Set call mode to DISCRETE
anim.track_set_call_mode(method_track, Animation.CALL_MODE_DISCRETE)

# Methods must exist on target node:
func spawn_particle(pos: Vector2) -> void:
    # Spawn particle at position
    pass

func play_sound(sound_path: String) -> void:
    $AudioStreamPlayer.stream = load(sound_path)
    $AudioStreamPlayer.play()
```

#### Audio Tracks
```gdscript
# Synchronize audio with animation
var audio_track := anim.add_track(Animation.TYPE_AUDIO)
anim.track_set_path(audio_track, "AudioStreamPlayer")

# Insert audio playback
var audio_stream := load("res://sounds/footstep.ogg")
anim.audio_track_insert_key(audio_track, 0.3, audio_stream)
anim.audio_track_insert_key(audio_track, 0.6, audio_stream)  # Second footstep

# Set volume for specific key
anim.audio_track_set_key_volume(audio_track, 0, 1.0)  # Full volume
anim.audio_track_set_key_volume(audio_track, 1, 0.7)  # Quieter
```

#### Bezier Tracks (Custom Curves)
```gdscript
# For smooth, custom interpolation curves
var bezier_track := anim.add_track(Animation.TYPE_BEZIER)
anim.track_set_path(bezier_track, ".:custom_value")

# Insert bezier points with handles
anim.bezier_track_insert_key(bezier_track, 0.0, 0.0)
anim.bezier_track_insert_key(bezier_track, 1.0, 100.0,
    Vector2(0.5, 0),    # In-handle
    Vector2(-0.5, 0))   # Out-handle

# Read value in _process
func _process(delta: float) -> void:
    var value := $AnimationPlayer.get_bezier_value("custom_value")
    # Use value for custom effects
```

### 2. Root Motion Extraction
```gdscript
# Scene structure:
# CharacterBody3D (root)
#   ├─ MeshInstance3D
#   │   └─ Skeleton3D
#   └─ AnimationPlayer

# AnimationPlayer setup:
@onready var anim_player: AnimationPlayer = $AnimationPlayer

func _ready() -> void:
    # Enable root motion (point to root bone)
    anim_player.root_motion_track = NodePath("MeshInstance3D/Skeleton3D:root")
    anim_player.play("walk")

func _physics_process(delta: float) -> void:
    # Extract root motion
    var root_motion_pos := anim_player.get_root_motion_position()
    var root_motion_rot := anim_player.get_root_motion_rotation()
    var root_motion_scale := anim_player.get_root_motion_scale()
    
    # Apply to CharacterBody3D
    var transform := Transform3D(basis.rotated(basis.y, root_motion_rot.y), Vector3.ZERO)
    transform.origin = root_motion_pos
    global_transform *= transform
    
    # Velocity from root motion
    velocity = root_motion_pos / delta
    move_and_slide()
```

### 3. Animation Sequences & Queueing
```gdscript
# Play animations in sequence
@onready var anim: AnimationPlayer = $AnimationPlayer

func play_attack_combo() -> void:
    anim.play("attack_1")
    await anim.animation_finished
    anim.play("attack_2")
    await anim.animation_finished
    anim.play("idle")

# Or use queue:
func play_with_queue() -> void:
    anim.play("attack_1")
    anim.queue("attack_2")
    anim.queue("idle")  # Auto-plays after attack_2
```

#### Blend Times
```gdscript
# Smooth transitions between animations
anim.play("walk")

# 0.5s blend from walk → run
anim.play("run", -1, 1.0, 0.5)  # custom_blend = 0.5

# Or set default blend
anim.set_default_blend_time(0.3)  # 0.3s for all transitions
anim.play("idle")
```

### 4. RESET Track Pattern
```gdscript
# Create RESET animation with default values
var reset_anim := Animation.new()
reset_anim.length = 0.01  # Very short

var track := reset_anim.add_track(Animation.TYPE_VALUE)
reset_anim.track_set_path(track, "Sprite2D:position")
reset_anim.track_insert_key(track, 0.0, Vector2(0, 0))  # Default position

track = reset_anim.add_track(Animation.TYPE_VALUE)
reset_anim.track_set_path(track, "Sprite2D:modulate")
reset_anim.track_insert_key(track, 0.0, Color.WHITE)  # Default color

anim_player.add_animation("RESET", reset_anim)

# AnimationPlayer automatically plays RESET when scene loads
# IF "Reset on Save" is enabled in AnimationPlayer settings
```

### 5. Procedural Animation Generation
```gdscript
# Create bounce animation programmatically
func create_bounce_animation() -> void:
    var anim := Animation.new()
    anim.length = 1.0
    anim.loop_mode = Animation.LOOP_LINEAR
    
    # Position track (Y bounce)
    var track := anim.add_track(Animation.TYPE_VALUE)
    anim.track_set_path(track, ".:position:y")
    
    # Generate sine wave keyframes
    for i in range(10):
        var time := float(i) / 9.0  # 0.0 to 1.0
        var value := sin(time * TAU) * 50.0  # Bounce height 50px
        anim.track_insert_key(track, time, value)
    
    anim.track_set_interpolation_type(track, Animation.INTERPOLATION_CUBIC)
    $AnimationPlayer.add_animation("bounce", anim)
    $AnimationPlayer.play("bounce")
```

### 6. Advanced Patterns
#### Play Animation Backwards
```gdscript
# Play animation in reverse (useful for closing doors, etc.)
anim.play("door_open", -1, -1.0)  # speed = -1.0 = reverse

# Pause and reverse
anim.pause()
anim.play("current_animation", -1, -1.0, false)  # from_end = false
```

#### Animation Callbacks (Signal-Based)
```gdscript
# Emit custom signal at specific frame
func _ready() -> void:
    $AnimationPlayer.animation_finished.connect(_on_anim_finished)

func _on_anim_finished(anim_name: String) -> void:
    match anim_name:
        "attack":
            deal_damage()
        "die":
            queue_free()
```

#### Seek to Specific Time
```gdscript
# Jump to 50% through animation
anim.seek(anim.current_animation_length * 0.5)

# Scrub through animation (cutscene editor)
func _input(event: InputEvent) -> void:
    if event is InputEventMouseMotion and scrubbing:
        var normalized_pos := event.position.x / get_viewport_rect().size.x
        anim.seek(anim.current_animation_length * normalized_pos)
```

### 7. Performance Optimization
#### Disable When Off-Screen
```gdscript
extends VisibleOnScreenNotifier2D

func _ready() -> void:
    screen_exited.connect(_on_screen_exited)
    screen_entered.connect(_on_screen_entered)

func _on_screen_exited() -> void:
    $AnimationPlayer.pause()

func _on_screen_entered() -> void:
    $AnimationPlayer.play()
```

### 8. Expert Patterns
#### Shared-Animation-Library
```gdscript
class_name SharedAnimationManager extends Node

@export var shared_library: AnimationLibrary
@onready var anim_player: AnimationPlayer = $AnimationPlayer

func _ready() -> void:
    # 1. Inject the shared library under a unique key
    anim_player.add_animation_library(&"shared_human", shared_library)
    
    # 2. Access animations using the 'library/animation' syntax
    anim_player.play(&"shared_human/walk")
```

#### Animation-Event-Signaling
```gdscript
class_name AnimationSignaler extends Node

## Emitted when the animation reaches a marked event key
signal animation_event(event_type: String)

## Generic receiver for AnimationPlayer Method Tracks
func emit_event(event_type: String) -> void:
    animation_event.emit(event_type)

# Setup in AnimationPlayer:
# 1. Add Method Track pointing to this node
# 2. Keyframe: method="emit_event", args=["spawn_footstep_vfx"]
# 3. Other systems connect to 'animation_event' signal
```

#### Animation-Budget-Manager
```gdscript
class_name AnimationBudgetManager extends Node3D

@onready var anim_player: AnimationPlayer = $AnimationPlayer
@onready var visibility_notifier: VisibleOnScreenNotifier3D = $VisibleOnScreenNotifier3D

func _ready() -> void:
    # 1. Disable automatic engine processing
    anim_player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL

func _process(delta: float) -> void:
    # 2. Cull updates for off-screen entities
    if not visibility_notifier.is_on_screen():
        return
        
    # 3. Manually step the animation forward
    # Optional: Throttle updates (e.g., only call every 2nd frame) for distant entities
    anim_player.advance(delta)
```

### 9. Available Scripts (Load Before Use)
> **MANDATORY**: Read the appropriate script before implementing the corresponding pattern.

- **[method_track_logic.gd](scripts/method_track_logic.gd)**: Load when implementing logic triggers using `CALL_MODE_DISCRETE` for high-precision hitbox and state management.
- **[runtime_anim_lib_swapper.gd](scripts/runtime_anim_lib_swapper.gd)**: Load when managing multiple `AnimationLibrary` resources (Stances, Weapons) on a single `AnimationPlayer`.
- **[dynamic_shader_animation.gd](scripts/dynamic_shader_animation.gd)**: Load when animating shader uniforms (e.g., dissolve, glow) in sync with timeline keyframes.
- **[procedural_track_modifier.gd](scripts/procedural_track_modifier.gd)**: Load for runtime modification of existing tracks (e.g., jump height tweaking) without creating new Animation resources.
- **[reset_track_orchestrator.gd](scripts/reset_track_orchestrator.gd)**: Load for forced, immediate state resets across complex multi-track node setups.
- **[bezier_curve_extraction.gd](scripts/bezier_curve_extraction.gd)**: Load when extracting numeric data from Bezier tracks at runtime to drive procedural VFX or physics.
- **[active_animation_culler.gd](scripts/active_animation_culler.gd)**: Load for performance optimization using `VisibleOnScreenNotifier` to disable `AnimationPlayer.active`.
- **[root_motion_physics_sync.gd](scripts/root_motion_physics_sync.gd)**: Load for expert 3D CharacterBody motion extraction using `get_root_motion_position`.
- **[character_part_swapper_tracks.gd](scripts/character_part_swapper_tracks.gd)**: Load for character customization (equipment/slots) managed entirely through Animation timeline tracks.
- **[precise_audio_sync.gd](scripts/precise_audio_sync.gd)**: Load for perfectly timed SFX using `TYPE_AUDIO` tracks with volume, pitch, and start-offset control.

## Pitfalls
- **NEVER forget RESET tracks** — Without a RESET track, animated properties don't restore to initial values when changing scenes. Create RESET animation with all default states.
- **NEVER use `Animation.CALL_MODE_CONTINUOUS` for function calls** — This calls the method EVERY frame during the keyframe. Use `CALL_MODE_DISCRETE` (calls once) to avoid logic spam.
- **NEVER animate resource properties directly** — Animating `material.albedo_color` creates embedded resources that bloat file size. Store the material in a variable or use `instance uniform` instead.
- **NEVER use `animation_finished` for looping animations** — This signal doesn't fire for looped animations. Use `animation_looped` or check `current_animation` in `_process()`.
- **NEVER hardcode animation names as strings across large codebases** — Use constants or enums. Typos cause silent failures.
- **NEVER use `seek()` without `update=true` for same-frame logic** — If you need properties to update immediately (e.g., for physics checks), you MUST set the `update` parameter to `true`.
- **NEVER leave unnecessary AnimationPlayers `active`** — If an entity is off-screen and its animation is purely visual (no logic tracks), set `active = false` to save significant CPU/GPU processing.
- **NEVER change `AnimationLibrary` content while it is playing** — This causes immediate crashes or undefined transform states. Stop the player or wait for the `finished` signal before swapping libraries.
- **NEVER rely on `speed_scale` for long-term synchronization** — For multiplayer or rhythm games, use `seek()` with a global time reference to prevent frame-drift.

## Verification
1. Check if animation exists before playing:
```gdscript
if anim.has_animation("walk"):
    anim.play("walk")
else:
    push_error("Animation 'walk' not found!")
```
2. Verify Method Track Call Mode:
```gdscript
var method_track_idx := anim.find_track(".:method_name", Animation.TYPE_METHOD)
# Ensure it is DISCRETE
assert(anim.track_get_call_mode(method_track_idx) == Animation.CALL_MODE_DISCRETE)
```
3. Verify RESET animation is present:
```gdscript
assert(anim.has_animation("RESET"), "RESET animation missing!")
```

## Related skills
- Master Skill: [godot-master](../godot-master/SKILL.md)
