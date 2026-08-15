---
name: game-camera-system
version: 1.3.1
description: "Implements reactive Godot 4.x cameras: delta-scaled follow, trauma shake, room zones, SpringArm3D/orbit/FPS rigs, pop-free transitions, split-screen SubViewports, and XROrigin3D locomotion. Use when the view must react to gameplay. Not for static cameras, AnimationPlayer cinematics, OpenXR session/Quest export (game-xr-development), or the Camera2D/3D property cookbook (godot-camera-systems)."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## When to Use

Reach for this skill when the camera has to *react* to gameplay rather than sit still. Reactive cameras share a few hard problems — frame-rate independence, smooth handoffs, and bounded motion — and getting them wrong shows up immediately as jitter, motion sickness, or the player seeing past the edge of the level. Use it for:

- **Smooth follow** for 2D and 3D targets — when the camera should trail a moving subject without snapping or lagging.
- **Trauma-based screen shake** — when impacts need tactile feedback that scales with severity instead of a flat rattle.
- **Camera zones / rooms** — Metroidvania or Zelda-style bounded scrolling where each room constrains the view.
- **3D camera rigs** — third-person (`SpringArm3D`), orbit, and first-person, where occlusion and pitch limits matter.
- **Transitions** — blending between viewpoints (cutscene cameras, perspective swaps) without a visible pop.
- **Local multiplayer split-screen** using `SubViewport`s, where each player needs an independent view.
- **VR/AR rigs** via `XRServer` — where the headset, not your code, owns the camera transform.

### Do Not Use

- **Truly static cameras.** A `Camera2D`/`Camera3D` with a fixed transform needs no script. Adding follow logic just buys you a `_process` callback that does nothing useful.
- **Authored cinematic sequences.** Multi-track, branching cutscenes belong in `AnimationPlayer`/`AnimationTree` or a dedicated cutscene system. This skill handles point-to-point moves, not a timeline you scrub and key.
- **Low-level rendering overrides.** If you are bypassing the `Camera2D`/`Camera3D` nodes to drive the `RenderingServer` or a custom compositor directly, you are below the layer these node-based patterns operate on.
- **Per-physics-step coupling.** Prefer `_process` (or Godot 4.x physics interpolation) so the view stays smooth regardless of the physics tick rate. Only drop into `_physics_process` when the camera must be rigidly locked to a physics body — and then turn on physics interpolation so rendering still interpolates between ticks.
- **Networked / remote-controlled camera parameters.** Treat any transform or zoom value that arrives over the network as untrusted: clamp it to sane ranges and reject `NaN`/`inf`. A malicious or buggy peer can otherwise fling the view off-world or feed a `NaN` that silently poisons every later interpolation.

## Prerequisites

- **Godot 4.x** — all APIs, property names, and signals below are Godot 4.x. Godot 3.x has different `Camera2D` zoom semantics (larger zoom = zoomed out, inverted from 4.x).
- **C# nullable reference types** — the C# examples use `Node2D?`. Enable with `<Nullable>enable</Nullable>` in your `.csproj`; the null-checks still work without it, you just lose the compiler's help.
- **Windows host (PowerShell)** — file paths and commands assume a Windows development environment. Adapt path separators for macOS/Linux if needed.

## Procedure

The patterns below share three principles, because those are the things that separate a camera that "works on my machine" from one that holds up:

1. **Interpolate manually and frame-rate-independently.** Built-in smoothing is convenient but opaque; driving position in `_process` with a `delta`-scaled weight keeps motion identical at 30 and 240 FPS and leaves room for look-ahead and dead-zones.
2. **Validate inputs at the boundary.** Targets can be unassigned, signals can fire from the wrong body, and impact values can be `NaN`. Each script below fails loudly (a warning/error) instead of silently misbehaving.
3. **Hand off explicitly.** When switching active cameras, finish the blend *before* calling `make_current()`, so there is never a one-frame jump.

### Camera2D Properties That Matter (Godot 4.x)

These are the real, load-bearing `Camera2D` properties. The "why" column is the part that is easy to get wrong.

| Property | Type | Why it matters |
|---|---|---|
| `position_smoothing_enabled` | `bool` | Godot's built-in damper toward the target. Fine for a one-line prototype follow, but it has no look-ahead or dead-zone, so **disable it when you drive `global_position` yourself** — otherwise two smoothing passes fight and the motion feels rubbery. |
| `position_smoothing_speed` | `float` | Damping rate for the built-in damper (higher reaches the target faster). Only read when `position_smoothing_enabled` is `true`. |
| `rotation_smoothing_enabled` | `bool` | Same idea for rotation. Leave it **off** when you set `rotation` directly (e.g. screen-shake roll), or the damper will lag and smear the shake. |
| `ignore_rotation` | `bool` | Defaults to `true`, which makes the camera discard its own `rotation`. You must set it to `false` before applying screen-shake roll, or the roll is silently thrown away — a very common "my shake doesn't tilt" bug. |
| `drag_horizontal_enabled` / `drag_vertical_enabled` | `bool` | Enable a dead-zone so tiny target movements don't nudge the view. Cuts down jitter on a near-idle target and reduces motion sickness. |
| `drag_left_margin`, `drag_right_margin`, `drag_top_margin`, `drag_bottom_margin` | `float` (0–1) | Size of that dead-zone for each edge, as a fraction of the viewport (0 = no slack, 1 = the camera can drift a full half-view before it moves). |
| `limit_left/right/top/bottom` | `int` | Hard world boundaries in pixels so the camera never reveals the void outside the level. These are integers in Godot 4.x. |
| `zoom` | `Vector2` | Zoom factor; `Vector2(2, 2)` shows the world at 2× (objects look *larger*). Note this is inverted from Godot 3, where larger meant zoomed out. |
| `global_position` | `Vector2` | Absolute world position — the value you lerp when doing manual follow. |

### 1. Smooth Follow (2D, with Look-Ahead)

We disable the built-in damper and interpolate in `_process` for two reasons: the motion becomes independent of the physics tick, and we can *lead* the camera in the direction of travel so the player sees more of where they're going. The look-ahead is itself eased, and gated behind a movement dead-zone, so a jittering idle target doesn't make the view wander.

**GDScript (Godot 4.x):**

```gdscript
extends Camera2D
## Frame-rate-independent follow camera with velocity-based look-ahead.
## A backing variable (_target) is used so the property setter can re-snap the
## camera without recursing into itself.

var _target: Node2D = null

## Node the camera chases. Assign in the inspector or via set_target().
@export var target: Node2D:
    get:
        return _target
    set(value):
        _target = value
        if is_inside_tree() and _target != null:
            _snap_to_target()

## Gap-closing rate. Must be > 0; higher is snappier.
@export var follow_speed: float = 8.0
## How far ahead of the target to bias the view, in pixels.
@export var look_ahead_distance: float = 80.0
## How quickly the look-ahead offset eases toward the movement direction.
@export var look_ahead_speed: float = 4.0
## Ignore per-frame target moves smaller than this (pixels) to avoid idle drift.
@export var movement_deadzone: float = 0.5

var _look_ahead_offset: Vector2 = Vector2.ZERO
var _previous_target_pos: Vector2 = Vector2.ZERO

func _ready() -> void:
    # We interpolate manually, so turn off the built-in damper to avoid two
    # smoothing passes stacking on top of each other.
    position_smoothing_enabled = false

    if follow_speed <= 0.0:
        push_warning("SmoothFollowCamera: follow_speed should be > 0; the camera will not move until it is.")
    if _target == null:
        push_warning("SmoothFollowCamera: no target assigned; set 'target' in the inspector or call set_target().")
        return
    _snap_to_target()

## Assign or clear the follow target at runtime (routes through the setter).
func set_target(new_target: Node2D) -> void:
    target = new_target

## Jump instantly to the target — used on spawn/teleport so the first frame does
## not slide the camera across the whole level.
func _snap_to_target() -> void:
    if _target == null:
        return
    _previous_target_pos = _target.global_position
    _look_ahead_offset = Vector2.ZERO
    global_position = _target.global_position

func _process(delta: float) -> void:
    # delta is 0 on the first frame and while paused; nothing to integrate then.
    if _target == null or delta <= 0.0:
        return

    # Estimate target velocity from this frame's position delta.
    var move_delta: Vector2 = _target.global_position - _previous_target_pos
    _previous_target_pos = _target.global_position

    # Only lead the view when the target is genuinely moving.
    var desired_ahead: Vector2 = Vector2.ZERO
    if move_delta.length() > movement_deadzone:
        desired_ahead = move_delta.normalized() * look_ahead_distance

    # Clamp the lerp weight to [0, 1] so a lag spike (large delta) cannot
    # overshoot the target.
    var ahead_t: float = clampf(look_ahead_speed * delta, 0.0, 1.0)
    _look_ahead_offset = _look_ahead_offset.lerp(desired_ahead, ahead_t)

    var desired_pos: Vector2 = _target.global_position + _look_ahead_offset
    var follow_t: float = clampf(maxf(follow_speed, 0.0) * delta, 0.0, 1.0)
    global_position = global_position.lerp(desired_pos, follow_t)
```

**C# (Godot 4.x):**

```csharp
using Godot;

/// <summary>
/// Frame-rate-independent 2D follow camera with velocity-based look-ahead.
/// Drives position manually in _Process so motion is decoupled from the physics
/// tick and supports look-ahead and a movement dead-zone.
/// </summary>
public partial class SmoothFollowCamera : Camera2D
{
    private Node2D? _target;

    /// <summary>Node the camera chases. May be null until assigned.</summary>
    [Export]
    public Node2D? Target
    {
        get => _target;
        set => SetTarget(value);
    }

    /// <summary>Gap-closing rate; must be &gt; 0. Higher is snappier.</summary>
    [Export] public float FollowSpeed { get; set; } = 8.0f;

    /// <summary>How far ahead of the target to bias the view (pixels).</summary>
    [Export] public float LookAheadDistance { get; set; } = 80.0f;

    /// <summary>Easing rate for the look-ahead offset.</summary>
    [Export] public float LookAheadSpeed { get; set; } = 4.0f;

    /// <summary>Ignore per-frame target moves smaller than this (pixels).</summary>
    [Export] public float MovementDeadzone { get; set; } = 0.5f;

    private Vector2 _lookAheadOffset = Vector2.Zero;
    private Vector2 _previousTargetPos = Vector2.Zero;

    public override void _Ready()
    {
        // Manual interpolation — disable the built-in damper so the two don't stack.
        PositionSmoothingEnabled = false;

        if (FollowSpeed <= 0.0f)
            GD.PushWarning("SmoothFollowCamera: FollowSpeed should be > 0; the camera will not move until it is.");
        if (_target == null)
        {
            GD.PushWarning("SmoothFollowCamera: no target assigned; set Target in the inspector or call SetTarget().");
            return;
        }
        SnapToTarget();
    }

    /// <summary>Assign or clear the follow target and re-snap to it.</summary>
    public void SetTarget(Node2D? newTarget)
    {
        _target = newTarget;
        if (!IsInsideTree() || _target == null)
            return;
        SnapToTarget();
    }

    private void SnapToTarget()
    {
        if (_target == null)
            return;
        _previousTargetPos = _target.GlobalPosition;
        _lookAheadOffset = Vector2.Zero;
        GlobalPosition = _target.GlobalPosition;
    }

    public override void _Process(double delta)
    {
        if (_target == null || delta <= 0.0)
            return;

        float dt = (float)delta;

        Vector2 moveDelta = _target.GlobalPosition - _previousTargetPos;
        _previousTargetPos = _target.GlobalPosition;

        Vector2 desiredAhead = Vector2.Zero;
        if (moveDelta.Length() > MovementDeadzone)
            desiredAhead = moveDelta.Normalized() * LookAheadDistance;

        // Clamp the lerp weight so a large delta (lag spike) cannot overshoot.
        float aheadT = Mathf.Clamp(LookAheadSpeed * dt, 0.0f, 1.0f);
        _lookAheadOffset = _lookAheadOffset.Lerp(desiredAhead, aheadT);

        Vector2 desiredPos = _target.GlobalPosition + _lookAheadOffset;
        float followT = Mathf.Clamp(Mathf.Max(FollowSpeed, 0.0f) * dt, 0.0f, 1.0f);
        GlobalPosition = GlobalPosition.Lerp(desiredPos, followT);
    }
}
```

### 2. Screen Shake (Trauma-Based)

A single `trauma` value in `[0, 1]` is raised on impacts and decays over time. The *visible* shake is `trauma²`, not `trauma`, because a linear mapping feels mushy at the low end — squaring keeps small hits subtle while big hits read as violent. Two boundary cases are handled explicitly: `add_trauma` rejects non-finite input (so a bad gameplay calculation can't lock the camera into permanent shake), and `ignore_rotation` is turned off so the roll actually applies.

**GDScript (Godot 4.x):**

```gdscript
extends Camera2D
## Trauma-based screen shake driven by FastNoiseLite. Sampling a continuous noise
## field (instead of random offsets) keeps the motion coherent frame to frame
## rather than a harsh per-frame jitter.

## Maximum positional shake in pixels at full trauma, per axis.
@export var max_offset: Vector2 = Vector2(20.0, 15.0)
## Maximum roll in degrees at full trauma.
@export var max_roll_degrees: float = 3.0
## Trauma lost per second. Higher = snappier recovery.
@export var decay_rate: float = 1.5
## Noise scroll speed. Higher = buzzier shake; lower = a slow sway.
@export var noise_speed: float = 60.0

var _trauma: float = 0.0
var _noise: FastNoiseLite
var _noise_time: float = 0.0

func _ready() -> void:
    # Camera2D ignores its own rotation by default, which would silently swallow
    # the roll below. Opt back in so the shake can tilt the view.
    ignore_rotation = false

    _noise = FastNoiseLite.new()
    _noise.noise_type = FastNoiseLite.TYPE_SIMPLEX
    _noise.seed = randi()
    # Fractal layering gives the shake a richer, less repetitive texture.
    _noise.fractal_type = FastNoiseLite.FRACTAL_FBM
    _noise.frequency = 0.25

## Add an impact. `amount` is clamped into [0, 1]; non-finite values are rejected
## so a NaN from gameplay math cannot trap the camera in permanent shake.
func add_trauma(amount: float) -> void:
    if not is_finite(amount):
        push_error("add_trauma: amount must be a finite number, got %s" % str(amount))
        return
    _trauma = clampf(_trauma + maxf(amount, 0.0), 0.0, 1.0)

func _process(delta: float) -> void:
    if _trauma <= 0.0:
        # Fully recovered — guarantee the view is left perfectly centered.
        offset = Vector2.ZERO
        rotation = 0.0
        return

    _trauma = maxf(_trauma - decay_rate * delta, 0.0)
    _noise_time += delta * noise_speed

    # Square trauma for a non-linear, more natural ramp.
    var shake: float = _trauma * _trauma

    # Sample the field at separated coordinates so each axis is independent;
    # noise in [-1, 1] makes the shake move both ways around the center.
    offset = Vector2(
        max_offset.x * shake * _noise.get_noise_2d(_noise_time, 0.0),
        max_offset.y * shake * _noise.get_noise_2d(0.0, _noise_time)
    )
    rotation = deg_to_rad(max_roll_degrees) * shake * _noise.get_noise_2d(_noise_time, _noise_time)
```

**C# (Godot 4.x):**

```csharp
using Godot;

/// <summary>
/// Trauma-based screen shake. A trauma value in [0, 1] is raised on impacts and
/// decays over time; visible shake is trauma squared so light hits stay subtle
/// and heavy hits read as violent.
/// </summary>
public partial class ScreenShakeCamera : Camera2D
{
    [Export] public Vector2 MaxOffset { get; set; } = new Vector2(20f, 15f);
    [Export] public float MaxRollDegrees { get; set; } = 3.0f;
    [Export] public float DecayRate { get; set; } = 1.5f;
    [Export] public float NoiseSpeed { get; set; } = 60.0f;

    private float _trauma;
    private float _noiseTime;
    private FastNoiseLite _noise = null!;

    public override void _Ready()
    {
        // Camera2D ignores its own rotation by default; opt in so roll is visible.
        IgnoreRotation = false;

        _noise = new FastNoiseLite
        {
            NoiseType = FastNoiseLite.NoiseTypeEnum.Simplex,
            Seed = (int)GD.Randi(),
            FractalType = FastNoiseLite.FractalTypeEnum.Fbm,
            Frequency = 0.25f,
        };
    }

    /// <summary>Add an impact. <paramref name="amount"/> is clamped to [0, 1];
    /// non-finite values are rejected to avoid locking the camera in shake.</summary>
    public void AddTrauma(float amount)
    {
        if (!float.IsFinite(amount))
        {
            GD.PushError($"AddTrauma: amount must be finite, got {amount}.");
            return;
        }
        _trauma = Mathf.Clamp(_trauma + Mathf.Max(amount, 0f), 0f, 1f);
    }

    public override void _Process(double delta)
    {
        if (_trauma <= 0f)
        {
            Offset = Vector2.Zero;
            Rotation = 0f;
            return;
        }

        float dt = (float)delta;
        _trauma = Mathf.Max(_trauma - DecayRate * dt, 0f);
        _noiseTime += dt * NoiseSpeed;

        float shake = _trauma * _trauma;
        Offset = new Vector2(
            MaxOffset.X * shake * _noise.GetNoise2D(_noiseTime, 0f),
            MaxOffset.Y * shake * _noise.GetNoise2D(0f, _noiseTime)
        );
        Rotation = Mathf.DegToRad(MaxRollDegrees) * shake * _noise.GetNoise2D(_noiseTime, _noiseTime);
    }
}
```

### 3. Camera Zones / Rooms

For room-based games, each room is an `Area2D` carrying the camera limits for that room. When the player enters, we *tween* the active camera's `limit_*` values rather than snapping them — a snap reads as a jarring jump at every doorway. Driving the limits (instead of moving the camera) means your existing follow script keeps working untouched; it simply gets clamped to the new bounds.

**GDScript (Godot 4.x):**

```gdscript
## CameraZone.gd — attach to an Area2D, one per room, sized to the room.
extends Area2D

@export var limit_left: int = 0
@export var limit_right: int = 320
@export var limit_top: int = 0
@export var limit_bottom: int = 180

## Seconds to ease the limits to the new room. ~0.3–0.5s reads as smooth without
## feeling sluggish.
@export var transition_time: float = 0.4

## Group the triggering body must belong to. Restricting this stops enemies or
## projectiles from hijacking the camera bounds.
@export var trigger_group: StringName = &"player"

func _ready() -> void:
    # Fail loudly on a misconfigured zone rather than silently never firing.
    if limit_right <= limit_left or limit_bottom <= limit_top:
        push_error("CameraZone '%s': limits are inverted or zero-area (l=%d r=%d t=%d b=%d)."
            % [name, limit_left, limit_right, limit_top, limit_bottom])
    body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node2D) -> void:
    if not body.is_in_group(trigger_group):
        return

    var cam: Camera2D = body.get_viewport().get_camera_2d()
    if cam == null:
        push_warning("CameraZone '%s': no active Camera2D in the viewport; cannot apply limits." % name)
        return

    var tween: Tween = create_tween()
    tween.set_parallel(true)
    tween.set_ease(Tween.EASE_IN_OUT)
    tween.set_trans(Tween.TRANS_SINE)
    tween.tween_property(cam, "limit_left", limit_left, transition_time)
    tween.tween_property(cam, "limit_right", limit_right, transition_time)
    tween.tween_property(cam, "limit_top", limit_top, transition_time)
    tween.tween_property(cam, "limit_bottom", limit_bottom, transition_time)
```

**C# (Godot 4.x):**

```csharp
// CameraZone.cs — attach to an Area2D, one per room.
using Godot;

public partial class CameraZone : Area2D
{
    [Export] public int LimitLeft { get; set; } = 0;
    [Export] public int LimitRight { get; set; } = 320;
    [Export] public int LimitTop { get; set; } = 0;
    [Export] public int LimitBottom { get; set; } = 180;

    /// <summary>Seconds to ease the limits to the new room.</summary>
    [Export] public float TransitionTime { get; set; } = 0.4f;

    /// <summary>Group the triggering body must belong to.</summary>
    [Export] public StringName TriggerGroup { get; set; } = "player";

    public override void _Ready()
    {
        if (LimitRight <= LimitLeft || LimitBottom <= LimitTop)
            GD.PushError($"CameraZone '{Name}': limits are inverted or zero-area (l={LimitLeft} r={LimitRight} t={LimitTop} b={LimitBottom}).");

        BodyEntered += OnBodyEntered;
    }

    private void OnBodyEntered(Node2D body)
    {
        if (!body.IsInGroup(TriggerGroup))
            return;

        var cam = body.GetViewport().GetCamera2D();
        if (cam == null)
        {
            GD.PushWarning($"CameraZone '{Name}': no active Camera2D in the viewport; cannot apply limits.");
            return;
        }

        var tween = CreateTween();
        tween.SetParallel(true);
        tween.SetEase(Tween.EaseType.InOut);
        tween.SetTrans(Tween.TransitionType.Sine);
        tween.TweenProperty(cam, "limit_left", LimitLeft, TransitionTime);
        tween.TweenProperty(cam, "limit_right", LimitRight, TransitionTime);
        tween.TweenProperty(cam, "limit_top", LimitTop, TransitionTime);
        tween.TweenProperty(cam, "limit_bottom", LimitBottom, TransitionTime);
    }
}
```

### 4. 3D Camera Rigs

Three rigs are covered here: third-person (`SpringArm3D`), orbit, and first-person. For extra SpringArm3D / orbit / first-person variants, load `references/camera3d-patterns.md`.

#### Third-Person (SpringArm3D)

The `SpringArm3D` handles collision retraction — it shortens the arm when geometry is between the camera and the target, preventing the camera from clipping through walls.

**Scene tree:**
```
PlayerRoot (CharacterBody3D)
├── VisualMesh (MeshInstance3D)
└── SpringArm3D (spring_length = 4, collision_mask = world)
    └── Camera3D (current = true)
```

**GDScript (Godot 4.x):**

```gdscript
extends SpringArm3D
## Third-person spring arm that follows a target and rotates with mouse/gamepad input.

@export var target: Node3D
@export var rotation_speed: float = 0.005
@export var min_pitch: float = deg_to_rad(-60.0)
@export var max_pitch: float = deg_to_rad(20.0)

func _process(delta: float) -> void:
    if target == null:
        return
    global_position = target.global_position

func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
        rotate_y(-event.relative.x * rotation_speed)
        var pitch = rotation.x - event.relative.y * rotation_speed
        pitch = clampf(pitch, min_pitch, max_pitch)
        rotation.x = pitch
```

**C# (Godot 4.x):**

```csharp
using Godot;

public partial class ThirdPersonSpringArm : SpringArm3D
{
    [Export] public Node3D? Target { get; set; }
    [Export] public float RotationSpeed { get; set; } = 0.005f;
    [Export] public float MinPitch { get; set; } = Mathf.DegToRad(-60f);
    [Export] public float MaxPitch { get; set; } = Mathf.DegToRad(20f);

    public override void _Process(double delta)
    {
        if (Target == null) return;
        GlobalPosition = Target.GlobalPosition;
    }

    public override void _UnhandledInput(InputEvent @event)
    {
        if (@event is InputEventMouseMotion mouse && Input.MouseMode == Input.MouseModeEnum.Captured)
        {
            RotateY(-mouse.Relative.X * RotationSpeed);
            float pitch = Rotation.X - mouse.Relative.Y * RotationSpeed;
            Rotation = new Vector3(Mathf.Clamp(pitch, MinPitch, MaxPitch), Rotation.Y, Rotation.Z);
        }
    }
}
```

#### Orbit Camera

A camera that orbits a fixed point at a configurable radius, with pitch clamped to avoid gimbal lock at the poles.

**GDScript (Godot 4.x):**

```gdscript
extends Camera3D
## Orbit camera: rotates around a pivot point with yaw/pitch and radius.

@export var pivot: Node3D
@export var orbit_speed: float = 0.005
@export var min_pitch: float = deg_to_rad(-80.0)
@export var max_pitch: float = deg_to_rad(80.0)
@export var radius: float = 6.0

var _yaw: float = 0.0
var _pitch: float = 0.0

func _process(delta: float) -> void:
    if pivot == null:
        return
    var offset := Vector3.ZERO
    offset.x = cos(_pitch) * sin(_yaw) * radius
    offset.y = sin(_pitch) * radius
    offset.z = cos(_pitch) * cos(_yaw) * radius
    global_position = pivot.global_position + offset
    look_at(pivot.global_position)

func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
        _yaw -= event.relative.x * orbit_speed
        _pitch = clampf(_pitch - event.relative.y * orbit_speed, min_pitch, max_pitch)
```

**C# (Godot 4.x):**

```csharp
using Godot;

public partial class OrbitCamera : Camera3D
{
    [Export] public Node3D? Pivot { get; set; }
    [Export] public float OrbitSpeed { get; set; } = 0.005f;
    [Export] public float MinPitch { get; set; } = Mathf.DegToRad(-80f);
    [Export] public float MaxPitch { get; set; } = Mathf.DegToRad(80f);
    [Export] public float Radius { get; set; } = 6.0f;

    private float _yaw;
    private float _pitch;

    public override void _Process(double delta)
    {
        if (Pivot == null) return;
        Vector3 offset = Vector3.Zero;
        offset.X = Mathf.Cos(_pitch) * Mathf.Sin(_yaw) * Radius;
        offset.Y = Mathf.Sin(_pitch) * Radius;
        offset.Z = Mathf.Cos(_pitch) * Mathf.Cos(_yaw) * Radius;
        GlobalPosition = Pivot.GlobalPosition + offset;
        LookAt(Pivot.GlobalPosition);
    }

    public override void _UnhandledInput(InputEvent @event)
    {
        if (@event is InputEventMouseMotion mouse && Input.MouseMode == Input.MouseModeEnum.Captured)
        {
            _yaw -= mouse.Relative.X * OrbitSpeed;
            _pitch = Mathf.Clamp(_pitch - mouse.Relative.Y * OrbitSpeed, MinPitch, MaxPitch);
        }
    }
}
```

#### First-Person Camera

The camera is a child of the player's `CharacterBody3D` head bone or a dedicated `Node3D` at eye height. Pitch is clamped and applied to the camera only, not the player body.

**GDScript (Godot 4.x):**

```gdscript
extends Camera3D
## First-person camera: yaw rotates the player body, pitch tilts the camera only.

@export var mouse_sensitivity: float = 0.002
@export var min_pitch: float = deg_to_rad(-89.0)
@export var max_pitch: float = deg_to_rad(89.0)

func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
        # Yaw: rotate the parent (player body).
        get_parent().rotate_y(-event.relative.x * mouse_sensitivity)
        # Pitch: rotate the camera only, clamped.
        rotation.x = clampf(rotation.x - event.relative.y * mouse_sensitivity, min_pitch, max_pitch)
```

**C# (Godot 4.x):**

```csharp
using Godot;

public partial class FirstPersonCamera : Camera3D
{
    [Export] public float MouseSensitivity { get; set; } = 0.002f;
    [Export] public float MinPitch { get; set; } = Mathf.DegToRad(-89f);
    [Export] public float MaxPitch { get; set; } = Mathf.DegToRad(89f);

    public override void _UnhandledInput(InputEvent @event)
    {
        if (@event is InputEventMouseMotion mouse && Input.MouseMode == Input.MouseModeEnum.Captured)
        {
            GetParent().RotateY(-mouse.Relative.X * MouseSensitivity);
            Rotation = new Vector3(
                Mathf.Clamp(Rotation.X - mouse.Relative.Y * MouseSensitivity, MinPitch, MaxPitch),
                Rotation.Y,
                Rotation.Z
            );
        }
    }
}
```

### 5. Camera Transitions (Pop-Free)

When switching between cameras, the blend must finish *before* `make_current()` is called, or there is a one-frame pop. The pattern: tween the outgoing camera's position/rotation to the incoming camera's transform, `await` the tween's `finished` signal, then call `make_current()` on the incoming camera.

**GDScript (Godot 4.x):**

```gdscript
extends Node
## Transition manager that blends from the active camera to a target camera
## before switching `current`, avoiding a one-frame pop.

@export var transition_time: float = 0.5

func transition_to(target_cam: Camera2D) -> void:
    var current_cam: Camera2D = get_viewport().get_camera_2d()
    if current_cam == null or current_cam == target_cam:
        target_cam.make_current()
        return

    # Snapshot the target's transform so the outgoing camera can move to it.
    var target_pos := target_cam.global_position
    var target_zoom := target_cam.zoom

    var tween := create_tween()
    tween.set_ease(Tween.EASE_IN_OUT)
    tween.set_trans(Tween.TRANS_SINE)
    tween.tween_property(current_cam, "global_position", target_pos, transition_time)
    tween.parallel().tween_property(current_cam, "zoom", target_zoom, transition_time)

    # Wait for the blend to finish, THEN switch current — no pop.
    await tween.finished
    target_cam.make_current()
```

**C# (Godot 4.x):**

```csharp
using Godot;

public partial class CameraTransitionManager : Node
{
    [Export] public float TransitionTime { get; set; } = 0.5f;

    public async void TransitionTo(Camera2D targetCam)
    {
        var currentCam = GetViewport().GetCamera2D();
        if (currentCam == null || currentCam == targetCam)
        {
            targetCam.MakeCurrent();
            return;
        }

        Vector2 targetPos = targetCam.GlobalPosition;
        Vector2 targetZoom = targetCam.Zoom;

        var tween = CreateTween();
        tween.SetEase(Tween.EaseType.InOut);
        tween.SetTrans(Tween.TransitionType.Sine);
        tween.TweenProperty(currentCam, "global_position", targetPos, TransitionTime);
        tween.Parallel().TweenProperty(currentCam, "zoom", targetZoom, TransitionTime);

        // Wait for the blend to finish, THEN switch current — no pop.
        await ToSignal(tween, Tween.SignalName.Finished);
        targetCam.MakeCurrent();
    }
}
```

### 6. Local Multiplayer Split-Screen

Each player gets their own `SubViewport` with an independent world and camera. The `SubViewport` sizes must update on window resize.

**Scene tree:**
```
HBoxContainer            — fills the screen
├── SubViewportContainer (player 1 side, stretch = true)
│   └── SubViewport (P1Viewport)
│       ├── Player1 (CharacterBody2D/3D)
│       └── Camera2D/3D (child of Player1, current = true)
└── SubViewportContainer (player 2 side, stretch = true)
    └── SubViewport (P2Viewport)
        ├── Player2 (CharacterBody2D/3D)
        └── Camera2D/3D (child of Player2, current = true)
```

**Per-`SubViewport` settings and why:**

| Property | Value | Reason |
|---|---|---|
| `own_world_3d` | `true` (3D only) | Gives each player a separate physics world so they don't see each other's culled geometry oddly. |
| `audio_listener_enable_2d` / `audio_listener_enable_3d` | `true` on **one** viewport only | Two active listeners double up positional audio; pick the primary player's viewport. |
| `transparent_bg` | `false` | Avoids needless alpha blending between the two halves. |
| `handle_input_locally` | `false` | Let the root scene route input to the right player instead of each viewport grabbing it. |

**GDScript (Godot 4.x):**

```gdscript
# SplitScreenSetup.gd — attach to the root of the split-screen scene.
extends Node

@export var player_scene: PackedScene
@export var left_viewport_path: NodePath
@export var right_viewport_path: NodePath

var _left_viewport: SubViewport
var _right_viewport: SubViewport

func _ready() -> void:
    if player_scene == null:
        push_error("SplitScreenSetup: player_scene is not assigned.")
        return

    _left_viewport = get_node_or_null(left_viewport_path)
    _right_viewport = get_node_or_null(right_viewport_path)
    if _left_viewport == null or _right_viewport == null:
        push_error("SplitScreenSetup: one or both SubViewport paths are invalid.")
        return

    _spawn_player(_left_viewport, 0)
    _spawn_player(_right_viewport, 1)

    get_tree().root.size_changed.connect(_resize_viewports)
    _resize_viewports()

func _spawn_player(viewport: SubViewport, device_index: int) -> void:
    var player: Node = player_scene.instantiate()
    viewport.add_child(player)
    if player.has_method("set_device"):
        player.set_device(device_index)

func _resize_viewports() -> void:
    var window_size: Vector2i = DisplayServer.window_get_size()
    var half := Vector2i(window_size.x / 2, window_size.y)
    _left_viewport.size = half
    _right_viewport.size = half
```

**C# (Godot 4.x):**

```csharp
// SplitScreenSetup.cs — attach to the root of the split-screen scene.
using Godot;

public partial class SplitScreenSetup : Node
{
    [Export] public PackedScene? PlayerScene { get; set; }
    [Export] public NodePath LeftViewportPath { get; set; } = default!;
    [Export] public NodePath RightViewportPath { get; set; } = default!;

    private SubViewport? _leftViewport;
    private SubViewport? _rightViewport;

    public override void _Ready()
    {
        if (PlayerScene == null)
        {
            GD.PushError("SplitScreenSetup: PlayerScene is not assigned.");
            return;
        }

        _leftViewport = GetNodeOrNull<SubViewport>(LeftViewportPath);
        _rightViewport = GetNodeOrNull<SubViewport>(RightViewportPath);
        if (_leftViewport == null || _rightViewport == null)
        {
            GD.PushError("SplitScreenSetup: one or both SubViewport paths are invalid.");
            return;
        }

        SpawnPlayer(_leftViewport, 0);
        SpawnPlayer(_rightViewport, 1);

        GetTree().Root.SizeChanged += ResizeViewports;
        ResizeViewports();
    }

    private void SpawnPlayer(SubViewport viewport, int deviceIndex)
    {
        if (PlayerScene == null)
            return;
        Node player = PlayerScene.Instantiate<Node>();
        viewport.AddChild(player);
        // The method name must match the player script (snake_case for GDScript).
        if (player.HasMethod("set_device"))
            player.Call("set_device", deviceIndex);
    }

    private void ResizeViewports()
    {
        if (_leftViewport == null || _rightViewport == null)
            return;
        Vector2I windowSize = DisplayServer.WindowGetSize();
        var half = new Vector2I(windowSize.X / 2, windowSize.Y);
        _leftViewport.Size = half;
        _rightViewport.Size = half;
    }
}
```

> **Load `references/split-screen.md`** when you need the full scene-tree walkthrough, input routing details, or four-player layouts.

### 7. VR / XR Rig (`XRServer`)

In XR the headset owns the camera transform, so the rule flips: **do not lerp, shake, or `look_at` the `XRCamera3D` directly** — that fights head tracking and causes motion sickness. Move the `XROrigin3D` instead (teleport/locomotion), and let the runtime drive the camera. Initialization is also defensive: if OpenXR isn't present we fall back to flatscreen rather than crash.

**XR scene tree:**
```
VRCameraRig (Node3D)
└── XROrigin3D            — move THIS for locomotion, not the camera
    ├── XRCamera3D        — driven by the headset
    ├── LeftController (XRController3D)
    └── RightController (XRController3D)
```

**GDScript (Godot 4.x):**

```gdscript
## VRCameraRig.gd — attach to the root. Children: XROrigin3D > XRCamera3D (+ controllers).
extends Node3D

var _xr_interface: XRInterface

func _ready() -> void:
    _xr_interface = XRServer.find_interface("OpenXR")
    if _xr_interface == null:
        push_warning("VRCameraRig: OpenXR interface not found; running in flatscreen mode.")
        return
    if not _xr_interface.is_initialized():
        if not _xr_interface.initialize():
            push_error("VRCameraRig: failed to initialize OpenXR.")
            return
    # Route rendering through the headset.
    get_viewport().use_xr = true
    # The headset drives frame pacing, so disable the desktop vsync.
    DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
```

**C# (Godot 4.x):**

```csharp
// VRCameraRig.cs — attach to the root. Children: XROrigin3D > XRCamera3D (+ controllers).
using Godot;

public partial class VRCameraRig : Node3D
{
    private XRInterface? _xrInterface;

    public override void _Ready()
    {
        _xrInterface = XRServer.FindInterface("OpenXR");
        if (_xrInterface == null)
        {
            GD.PushWarning("VRCameraRig: OpenXR interface not found; running in flatscreen mode.");
            return;
        }
        if (!_xrInterface.IsInitialized() && !_xrInterface.Initialize())
        {
            GD.PushError("VRCameraRig: failed to initialize OpenXR.");
            return;
        }
        GetViewport().UseXr = true;
        DisplayServer.WindowSetVsyncMode(DisplayServer.VSyncMode.Disabled);
    }
}
```

## Pitfalls

- **Two smoothing passes stacking.** If you drive `global_position` manually but leave `position_smoothing_enabled = true`, Godot's built-in damper and your manual lerp fight each other. The motion feels rubbery and laggy. Always disable `position_smoothing_enabled` when doing manual follow.
- **`ignore_rotation = true` silently swallowing screen-shake roll.** `Camera2D` ignores its own `rotation` by default. If you apply shake roll without setting `ignore_rotation = false`, the roll is silently thrown away. This is the most common "my shake doesn't tilt" bug.
- **Godot 3 vs 4 zoom inversion.** In Godot 3, larger `zoom` values meant zoomed out. In Godot 4.x, `Vector2(2, 2)` means 2× zoom (objects look larger). If you port a Godot 3 project, invert your zoom values.
- **`limit_*` values are integers in Godot 4.x.** Passing floats silently truncates. Set them as `int` in your exports.
- **Camera zone `trigger_group` not restricted.** If you don't check `body.is_in_group(trigger_group)`, any physics body entering the `Area2D` (enemies, projectiles, debris) will hijack the camera bounds.
- **Inverted or zero-area camera zone limits.** If `limit_right <= limit_left` or `limit_bottom <= limit_top`, the camera locks up. The scripts above fail loudly with `push_error` on this misconfiguration.
- **One-frame pop on camera switch.** Calling `make_current()` before the blend tween finishes causes a visible jump. Always `await tween.finished` before switching `current`.
- **Pitch not clamped on 3D rigs.** If pitch reaches exactly ±90°, `look_at()` produces a degenerate forward vector (gimbal lock). Clamp to ±89° or ±80° to stay safe.
- **`SpringArm3D` collision mask not set.** Without the correct collision mask, the arm never detects walls and the camera clips through geometry.
- **Doubled positional audio in split-screen.** If both `SubViewport`s have `audio_listener_enable_2d/3d = true`, positional audio plays twice. Enable it on exactly one viewport (the primary player's).
- **Split-screen `SubViewport` sizes not updating on window resize.** If you don't connect to `size_changed`, the viewports keep their initial size and the split looks wrong after the user resizes the window.
- **Moving `XRCamera3D` directly in VR.** Lerping, shaking, or `look_at`-ing the XR camera fights head tracking and causes motion sickness. Move `XROrigin3D` for locomotion; let the headset drive the camera.
- **`NaN`/`inf` from gameplay math poisoning trauma.** If `add_trauma` receives a `NaN` (e.g., from a division by zero in damage calculation), `_trauma` becomes `NaN` and the shake never decays. The scripts above reject non-finite input with `push_error`.
- **Network-supplied camera parameters not validated.** Any transform or zoom value arriving over the network must be range-clamped and `NaN`/`inf`-checked before use. A malicious or buggy peer can fling the view off-world or poison interpolation.
- **Lerp weight not clamped to [0, 1].** On a lag spike, `delta` can be large enough that `speed * delta > 1.0`, causing the lerp to overshoot the target. Always `clampf(weight, 0.0, 1.0)`.

## Verification

Run through this checklist after implementing any camera system from this skill:

1. **Camera2D limits match level bounds** — verify `limit_left/right/top/bottom` are set so the view never shows the void outside the map. Check in the editor by dragging the camera to each edge.
2. **Smooth follow is frame-rate-independent** — confirm the follow script runs in `_process` with a `delta`-scaled, clamped lerp weight. Test by temporarily capping the FPS (`Engine.max_fps = 30`) and then restoring it; the motion should feel identical.
3. **Screen shake resets cleanly** — after `_trauma` reaches 0, verify `offset = Vector2.ZERO` and `rotation = 0.0`. Confirm `ignore_rotation = false` so the roll is actually visible.
4. **`add_trauma()` rejects bad input** — call `add_trauma(NAN)` and `add_trauma(inf)` in a test; verify the error is pushed and `_trauma` stays unchanged.
5. **`add_trauma()` clamps to 1.0** — call `add_trauma(5.0)`; verify `_trauma` is `1.0`, not `5.0`.
6. **`SpringArm3D` collision mask is set** — place a wall between the camera and the target; verify the arm retracts instead of clipping through.
7. **Pitch is clamped on every 3D rig** — on the orbit rig, verify pitch stops at `max_pitch`/`min_pitch` and never reaches ±90°. On the first-person rig, verify the same.
8. **Transitions are pop-free** — trigger a camera transition; verify the outgoing camera moves to the target transform, *then* `make_current()` is called. No one-frame jump should be visible.
9. **Split-screen `SubViewport` sizes update on resize** — resize the window; verify both viewports resize to half-width. Confirm `size_changed` is connected.
10. **Exactly one audio listener in split-screen** — verify only one `SubViewport` has `audio_listener_enable_2d/3d = true`.
11. **VR rig does not move `XRCamera3D`** — in the XR rig, confirm only `XROrigin3D` is moved by code. The `XRCamera3D` transform must be left to the headset.
12. **VR falls back to flatscreen** — run without an OpenXR runtime; verify the warning is pushed and the game continues in flatscreen mode rather than crashing.
13. **Network parameters are validated** — if any camera parameter arrives over the network, verify it is range-clamped and `NaN`/`inf`-checked before use.

## Related Skills

- **player-controller** — owns movement input; the first-person rig here plugs into its `CharacterBody3D`.
- **state-machine** — drive camera modes (follow vs. cutscene vs. aim) as explicit states so transitions are predictable.
- **godot-optimization** — camera frustum/visibility culling, relevant once you have multiple `SubViewport`s.
- **physics-system** — physics interpolation, the right answer when a camera must track a physics body smoothly.
- **2d-essentials** — parallax backgrounds that read the same `Camera2D` you set up here.
- **math-essentials** — the `lerp`/`smoothstep`/clamp building blocks every interpolation above relies on.
- **tween-animation** — richer `Tween` easing for cinematic camera moves.
