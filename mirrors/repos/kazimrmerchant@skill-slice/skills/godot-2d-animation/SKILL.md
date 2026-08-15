---
name: godot-2d-animation
description: "Expert patterns for 2D animation in Godot 4.7+ using AnimatedSprite2D, AnimationPlayer, AnimationTree, and skeletal cutout rigs. Use when implementing sprite frame animations, procedural squash/stretch, cutout bone hierarchies, IK, frame-perfect timing, or GPU swarm animation. Trigger keywords: AnimatedSprite2D, SpriteFrames, animation_finished, animation_looped, frame_changed, frame_progress, set_frame_and_progress, cutout animation, skeletal 2D, Bone2D, procedural animation, animation state machine, advance(0). Not for deprecated AnimatedTexture, 3D root-motion BlendSpace trees (godot-animation-tree-mastery), or mixing AnimationPlayer tracks with code-driven AnimatedSprite2D."
version: 1.0.1
---

## When to Use

Activate this skill when the user needs to implement or debug any of the following in a Godot 4.7+ project:

- **Frame-based sprite animation** via `AnimatedSprite2D` and `SpriteFrames`.
- **Skeletal/cutout 2D animation** using `Bone2D`, `Skeleton2D`, and `AnimationPlayer`.
- **Procedural animation** such as squash/stretch, IK foot placement, or runtime bone retargeting.
- **Frame-perfect gameplay sync** — triggering SFX, VFX, hitboxes, or method calls on specific animation frames.
- **AnimationTree state machines** — blending, travel(), and locomotion graphs.
- **Tween lifecycle management** — safe interruption, property-fight prevention, looping.
- **GPU optimization** — MultiMeshInstance2D swarms, 2D mesh fill-rate optimization, shader-driven animation.
- **Pixel-art-specific issues** — snapping, filtering, centering artifacts.

Trigger keywords: `AnimatedSprite2D`, `SpriteFrames`, `animation_finished`, `animation_looped`, `frame_changed`, `frame_progress`, `set_frame_and_progress`, `cutout animation`, `skeletal 2D`, `Bone2D`, `procedural animation`, `animation state machine`, `advance(0)`.

## Prerequisites

- **Godot 4.7+** (stable, 2026-06-18). Consult the [Godot 4.7 migration guide](https://docs.godotengine.org/en/4.7/tutorials/migrating/upgrading_to_godot_4.7.html) when upgrading from 4.6.
- **NEVER** assume 4.6 defaults (stretch mode, audio `area_mask`, RichTextLabel percent flags) without checking 4.7 migration notes.
- Windows host is primary (PowerShell). Keep path separators as `res://` inside Godot; use backslash `\` only for OS-level file operations outside the engine.

## NEVER Do (Hard Rules)

1. **NEVER use `AnimatedTexture`** — Deprecated, highly inefficient in modern renderers, may be removed in future Godot versions. Use `AnimatedSprite2D` or `AnimationPlayer` instead.
2. **NEVER allow Tweens to fight over the same property** — The last-created Tween forcibly takes priority. Always assign your Tween to a variable and call `kill()` on the previous instance before creating a new one.
3. **NEVER process kinematic movement outside the physics tick** — If `AnimationPlayer` moves a `CharacterBody2D`, set its callback mode to **Physics**. Animating physics bodies during Idle (render) frames breaks fixed-timestep interpolation and causes stutter.
4. **NEVER use `animation_finished` for looping animations** — The signal only fires on non-looping animations. Use `animation_looped` instead.
5. **NEVER call `play()` and expect instant state changes** — `AnimatedSprite2D` applies `play()` on the next process frame. Call `advance(0)` immediately after `play()` for synchronous property updates (e.g., changing animation + `flip_h` simultaneously).
6. **NEVER set `frame` directly when preserving animation progress** — Setting `frame` resets `frame_progress` to `0.0`. Use `set_frame_and_progress(frame, progress)` to maintain smooth transitions when swapping animations mid-frame.
7. **NEVER forget to cache `@onready var anim_sprite`** — The node-lookup getter is surprisingly slow in hot paths like `_physics_process()`. Always use `@onready`.
8. **NEVER mix `AnimationPlayer` tracks with code-driven `AnimatedSprite2D`** — Choose one animation authority per sprite. Mixing causes flickering and state conflicts.
9. **NEVER use paper-thin skeletons for deformation** — 2D meshes require balanced vertex density. If a mesh deforms poorly, increase vertex count near joints in the Mesh2D editor.

## Available Scripts (MANDATORY Loading)

> **Rule**: Read the appropriate script from `scripts/` before implementing the corresponding pattern. Each script contains verified, engine-accurate code for Godot 4.7+.

| Script | When to Load |
|--------|-------------|
| `scripts/animation_sync.gd` | Syncing gameplay events (SFX/VFX/hitboxes) to animation frames via method tracks or signals. |
| `scripts/animation_state_sync.gd` | Frame-perfect state-driven animation with transition queueing for responsive characters. |
| `scripts/shader_hook.gd` | Animating `ShaderMaterial` uniforms via `AnimationPlayer` property tracks (hit flash, dissolve, instance uniforms). |
| `scripts/procedural_squash_stretch.gd` | Physics-driven deformation — `lerp` logic for impact squashes and directional stretches. |
| `scripts/skeleton_2d_rig_helper.gd` | Programmatic rig management — FABRIK/CCDIK stack tuning, runtime bone rest-pose updates. |
| `scripts/animation_tree_step.gd` | `AnimationNodeStateMachinePlayback.travel()` for multi-state A* transitions. |
| `scripts/one_frame_sync_fix.gd` | Eliminating the "One-Frame Glitch" via `advance(0)` alongside `flip_h` or property changes. |
| `scripts/gpu_mesh_optimizer.gd` | Converting large sprites to 2D meshes to bypass GPU fill-rate bottlenecks. |
| `scripts/multimesh_swarm_anim.gd` | Offloading animation (sine waves, flight patterns) to GPU vertex shader for thousands of entities. |
| `scripts/tween_lifecycle_manager.gd` | Safe `Tween` orchestration — interruption cleanup, property-fight prevention. |

## Procedure

### 1. Choose the Right Animation Tool

| Scenario | Recommended Node | Expert Insight |
|----------|------------------|----------------|
| Isolated frame-by-frame spritesheets | **AnimatedSprite2D** | Simple, but cannot animate non-visual properties, transforms, or trigger external methods. |
| Cutout, non-visual sync, audio/particles | **AnimationPlayer** | Required for multi-sprite transforms, 2D mesh deformations, method/particle sync. |
| Complex state machines, blending, locomotion | **AnimationTree** | Drives an underlying `AnimationPlayer`; does not hold animations itself. |
| Procedural, dynamic, fire-and-forget UI/fx | **Tween** | Runtime-calculated targets; lightweight; designed to be created and discarded. |
| Swarms of thousands of entities | **MultiMeshInstance2D + Shader** | Bypasses node system; movement computed on GPU vertex shader. |

### 2. AnimatedSprite2D Signal Wiring

Use `animation_looped` for repeating animations; `animation_finished` **only** for one-shots.

```gdscript
extends CharacterBody2D

@onready var anim: AnimatedSprite2D = $AnimatedSprite2D

func _ready() -> void:
    anim.animation_looped.connect(_on_loop)
    anim.animation_finished.connect(_on_finished)
    anim.play("run")

func _on_loop() -> void:
    emit_particle_effect("dust")

func _on_finished() -> void:
    anim.play("idle")
```

### 3. Frame-Perfect Event Triggering via `frame_changed`

```gdscript
extends AnimatedSprite2D

signal attack_hit
signal footstep

const EVENT_FRAMES := {
    "attack": {3: "attack_hit", 7: "attack_hit"},
    "run": {2: "footstep", 5: "footstep"}
}

func _ready() -> void:
    frame_changed.connect(_on_frame_changed)

func _on_frame_changed() -> void:
    var events := EVENT_FRAMES.get(animation, {})
    if frame in events:
        emit_signal(events[frame])
```

### 4. Fix the One-Frame Glitch with `advance(0)`

When updating both animation and sprite properties simultaneously, `play()` defers to the next frame. Force immediate sync:

```gdscript
# ❌ BAD: Glitches for 1 frame
func change_direction(dir: int) -> void:
    anim.flip_h = (dir < 0)
    anim.play("run")  # Applied NEXT frame

# ✅ GOOD: Force immediate sync
func change_direction(dir: int) -> void:
    anim.flip_h = (dir < 0)
    anim.play("run")
    anim.advance(0)  # Force immediate update
```

> **Load `scripts/one_frame_sync_fix.gd`** before implementing this pattern.

### 5. Smooth Mid-Animation Transitions with `set_frame_and_progress()`

```gdscript
func swap_skin(new_skin: String) -> void:
    var current_frame := anim.frame
    var current_progress := anim.frame_progress
    anim.sprite_frames = load("res://skins/%s.tres" % new_skin)
    anim.play(anim.animation)
    anim.set_frame_and_progress(current_frame, current_progress)
```

### 6. Procedural Squash & Stretch

```gdscript
extends CharacterBody2D

@onready var sprite: Sprite2D = $Sprite2D
var _base_scale := Vector2.ONE

func _physics_process(delta: float) -> void:
    var prev_velocity := velocity
    move_and_slide()

    if not is_on_floor() and is_on_floor():
        var impact_strength := clamp(abs(prev_velocity.y) / 800.0, 0.0, 1.0)
        _squash_and_stretch(Vector2(1.0 + impact_strength * 0.3, 1.0 - impact_strength * 0.3))
    elif velocity.y < -200:
        sprite.scale = _base_scale.lerp(Vector2(0.9, 1.1), delta * 5.0)
    else:
        sprite.scale = sprite.scale.lerp(_base_scale, delta * 10.0)

func _squash_and_stretch(target_scale: Vector2) -> void:
    var tween := create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
    tween.tween_property(sprite, "scale", target_scale, 0.08)
    tween.tween_property(sprite, "scale", _base_scale, 0.12)
```

> **Load `scripts/procedural_squash_stretch.gd`** before implementing physics-driven deformation.

### 7. Cutout Animation with Bone2D Skeleton

Node hierarchy:

```
Player (Node2D)
  └─ Skeleton2D
      ├─ Bone2D (Root - Torso)
      │   ├─ Sprite2D (Body)
      │   └─ Bone2D (Head)
      │       └─ Sprite2D (Head)
      ├─ Bone2D (ArmLeft)
      │   └─ Sprite2D (Arm)
      └─ Bone2D (ArmRight)
          └─ Sprite2D (Arm)
```

Key bone rotations in `AnimationPlayer` using tracks like:
- `Skeleton2D/Bone2D:rotation`
- `Skeleton2D/Bone2D/Bone2D2:rotation` (head)
- `Skeleton2D/Bone2D3:rotation` (arm left)

**Why Bone2D over manual parenting?** FK/IK support, easier rigging and weight painting, better animation retargeting integration.

### 8. AnimationTree State Machine Travel

```gdscript
extends CharacterBody2D

@onready var animation_tree: AnimationTree = $AnimationTree
@onready var state_machine: AnimationNodeStateMachinePlayback = animation_tree.get("parameters/playback")

func _ready() -> void:
    state_machine.start("idle")

func _physics_process(_delta: float) -> void:
    if velocity.length() > 0:
        state_machine.travel("run")
    else:
        state_machine.travel("idle")
```

> **Load `scripts/animation_tree_step.gd`** before implementing multi-state A* transitions.

### 9. Safe Tween Lifecycle Management

```gdscript
extends Node2D

var _tween: Tween

func animate_damage_flash() -> void:
    if _tween:
        _tween.kill()
    _tween = create_tween()
    _tween.set_loops(3)
    _tween.tween_property($Sprite2D, "modulate", Color.RED, 0.1).set_trans(Tween.TRANS_SINE)
    _tween.tween_property($Sprite2D, "modulate", Color.WHITE, 0.1).set_trans(Tween.TRANS_SINE)
```

> **Load `scripts/tween_lifecycle_manager.gd`** before implementing rapid tween orchestration.

### 10. Animation-Frame Data Extractor (Method/Value Tracks)

`SpriteFrames` is strictly visual. Use `AnimationPlayer` Value Tracks or Call Method Tracks to decouple logical metadata from visual frames.

```gdscript
class_name AnimationDataExtractor extends CharacterBody2D

@export var current_spawn_offset: Vector2 = Vector2.ZERO:
    set(value):
        current_spawn_offset = value
        _update_spawn_point()

@onready var anim_player: AnimationPlayer = $AnimationPlayer
@onready var spawn_marker: Marker2D = $SpawnMarker

func _ready() -> void:
    anim_player.play("attack_shoot")

func _update_spawn_point() -> void:
    spawn_marker.position = current_spawn_offset

func spawn_projectile(damage: int, specific_offset: Vector2) -> void:
    var projectile = PROJECTILE_SCENE.instantiate()
    projectile.damage = damage
    projectile.position = global_position + specific_offset
    get_parent().add_child(projectile)
```

> **Load `scripts/animation_sync.gd`** before implementing method-track or signal-driven sync.

### 11. Procedural IK Foot Placement (TwoBoneIK)

1. Add a `SkeletonModificationStack2D` to your `Skeleton2D`.
2. Add a `SkeletonModification2DTwoBoneIK` to the stack.
3. Assign target bones (e.g., UpperLeg and LowerLeg).
4. Point `target_nodepath` to a `Marker2D` (IK Target).

```gdscript
class_name ProceduralWalker2D extends Node2D

@onready var skeleton: Skeleton2D = $Skeleton2D
@onready var ik_target_left_foot: Marker2D = $IKTargets/LeftFootTarget
@onready var floor_raycast: RayCast2D = $RayCasts/LeftFootRay

func _ready() -> void:
    var mod_stack: SkeletonModificationStack2D = skeleton.get_modification_stack()
    if mod_stack:
        mod_stack.enabled = true
        mod_stack.enable_all_modifications(true)

func _physics_process(_delta: float) -> void:
    floor_raycast.force_raycast_update()
    if floor_raycast.is_colliding():
        ik_target_left_foot.global_position = floor_raycast.get_collision_point()
    else:
        ik_target_left_foot.position = Vector2(0, 50)
```

> **Load `scripts/skeleton_2d_rig_helper.gd`** before tuning FABRIK/CCDIK stacks or updating bone rest poses at runtime.

### 12. SpriteFrames Memory Optimization

```gdscript
# ✅ GOOD: Share SpriteFrames resource across instances
const SHARED_FRAMES := preload("res://characters/player_frames.tres")

func _ready() -> void:
    anim_sprite.sprite_frames = SHARED_FRAMES

# ❌ BAD: Each instance loads separately — duplicates in memory
func _ready() -> void:
    anim_sprite.sprite_frames = load("res://characters/player_frames.tres")
```

### 13. Async Sprite-Sheet Loading (VRAM Management)

```gdscript
class_name SpriteSheetMemoryManager extends Node

@onready var animated_sprite: AnimatedSprite2D = $AnimatedSprite2D
var _pending_path: String = ""
var _target_anim: StringName = &"heavy_attack"

func load_high_res_anim(path: String) -> void:
    _pending_path = path
    ResourceLoader.load_threaded_request(_pending_path)
    set_process(true)

func _process(_delta: float) -> void:
    var status = ResourceLoader.load_threaded_get_status(_pending_path)
    if status == ResourceLoader.THREAD_LOAD_LOADED:
        var tex: Texture2D = ResourceLoader.load_threaded_get(_pending_path)
        _apply_to_frames(tex)
        set_process(false)

func _apply_to_frames(tex: Texture2D) -> void:
    var frames: SpriteFrames = animated_sprite.sprite_frames
    if not frames.has_animation(_target_anim):
        frames.add_animation(_target_anim)
    frames.add_frame(_target_anim, tex)
    animated_sprite.play(_target_anim)

func unload_high_res_anim() -> void:
    var frames: SpriteFrames = animated_sprite.sprite_frames
    if frames.has_animation(_target_anim):
        frames.clear(_target_anim)
```

### 14. GPU Fill-Rate Optimization with 2D Meshes

Sprites with large transparent areas (tree leaves, wings) waste GPU fill rate. Convert a `Sprite2D` into a `MeshInstance2D` to generate a 2D polygon that tightly hugs opaque pixels.

> **Load `scripts/gpu_mesh_optimizer.gd`** before implementing this architectural pattern.

### 15. MultiMesh Swarm Animation

For thousands of entities (bats, fish, particles), offload animation logic to the GPU vertex shader via `MultiMeshInstance2D`.

> **Load `scripts/multimesh_swarm_anim.gd`** before implementing GPU-driven swarm animation.

### 16. Pixel Art Centering & Filtering

```gdscript
# Solution 1: Disable centering
anim_sprite.centered = false
anim_sprite.offset = Vector2.ZERO

# Solution 2: Enable global pixel snapping (Project Settings)
# rendering/2d/snap/snap_2d_vertices_to_pixel = true
# rendering/2d/snap/snap_2d_transforms_to_pixel = true
```

For texture filtering, in the Import tab for each texture:
- **Filter**: Nearest (for pixel art)
- **Mipmaps**: Off (prevents blending at distance)

Or globally in Project Settings:
```
rendering/textures/canvas_textures/default_texture_filter = Nearest
```

### 17. Hybrid Cutout + Cel Animation

Use `AnimationPlayer` to rig a 2D skeleton and animate bones (cutout), while simultaneously keyframing `texture` or `frame` properties of specific child sprites. This enables efficient transform-based body animation with selective hand-shape or facial-expression swapping via traditional cel animation.

## Pitfalls

- **`animation_finished` on looping animations**: Signal never fires. Use `animation_looped`.
- **One-frame glitch on `flip_h` + `play()`**: `play()` defers to next frame. Always call `advance(0)` after.
- **Setting `frame` resets `frame_progress`**: Use `set_frame_and_progress(frame, progress)` to preserve progress.
- **Tween property fights**: Last-created Tween wins. Always `kill()` previous Tween references.
- **AnimationPlayer moving CharacterBody2D on Idle frame**: Breaks physics interpolation. Set callback mode to Physics.
- **AnimatedTexture usage**: Deprecated and inefficient. Never use.
- **Mixing AnimationPlayer tracks with code-driven AnimatedSprite2D**: Causes flickering and state conflicts. Pick one authority.
- **Paper-thin 2D meshes**: Deform poorly. Increase vertex density near joints.
- **Per-instance `load()` of SpriteFrames**: Duplicates memory. Use `preload` and share the resource.
- **Pixel art blur**: Ensure Nearest filtering and pixel snapping enabled.

## Verification

1. **Signal wiring check** — Verify `animation_looped` (not `animation_finished`) is connected for looping animations:
   ```gdscript
   # In _ready(), confirm connection:
   assert(anim.animation_looped.is_connected(_on_loop))
   ```

2. **One-frame sync check** — After `play()` + property change, confirm `advance(0)` was called:
   ```gdscript
   anim.play("run")
   anim.advance(0)
   # Verify: anim.animation == "run" and sprite properties are current THIS frame
   ```

3. **Tween safety check** — Confirm previous Tween is killed before creating new one:
   ```gdscript
   if _tween:
       _tween.kill()
   _tween = create_tween()
   ```

4. **Physics callback mode** — In the AnimationPlayer inspector, confirm **Callback Mode → Process** is set to **Physics** for any track animating a `CharacterBody2D`.

5. **SpriteFrames sharing** — Confirm all instances reference the same resource:
   ```gdscript
   assert(anim_sprite.sprite_frames == SHARED_FRAMES)
   ```

6. **Pixel snapping** — In Project Settings, verify:
   - `rendering/2d/snap/snap_2d_vertices_to_pixel = true`
   - `rendering/2d/snap/snap_2d_transforms_to_pixel = true`

7. **IK stack enabled** — Confirm at runtime:
   ```gdscript
   var mod_stack = skeleton.get_modification_stack()
   assert(mod_stack and mod_stack.enabled)
   ```

## Related Skills

- **Master Skill**: `godot-master` (`../godot-master/SKILL.md`) — overarching Godot 4.7 patterns and cross-system guidance.
