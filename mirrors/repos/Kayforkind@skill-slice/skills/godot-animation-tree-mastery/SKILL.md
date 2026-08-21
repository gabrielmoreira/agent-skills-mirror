---
name: godot-animation-tree-mastery
description: "Blends Godot AnimationTree graphs: AnimationNodeStateMachine travel, BlendSpace2D/1D, BlendTree Add2/Blend2 layers, advance_expression, OneShot, and tree root_motion. Use when the user wants 5+ character states, 8-way blend_position, or upper/lower-body masks. Trigger: transition_request, StateMachine playback. Not for UI/cutscene/prop AnimationPlayer timelines or SpriteFrames. Do not use AnimationPlayer.play() while the tree is active."
version: 1.0.1
---

# AnimationTree Mastery

Expert guidance for Godot's advanced animation blending and state machines. Covers Godot 4.x (including 4.7 changes).

## When to Use

Use this skill when building complex character animation systems in Godot that require any of the following:

- **StateMachine** with 5+ states and transition logic (idle, walk, run, jump, attack, hurt, etc.)
- **BlendSpace2D** for directional (X+Y) movement blending (8-way walk/run, strafe)
- **BlendSpace1D** for single-axis speed blending (walk → run by speed)
- **BlendTree** for layered animations (upper-body aim + lower-body walk)
- **Root motion** extraction through AnimationTree
- **Sub-StateMachines** for hierarchical state management (Grounded → Airborne)
- **Sync Groups** for keeping multi-layer animations aligned
- **OneShot** nodes for reactive animations (recoil, hit reactions)
- **TimeScale** for bullet-time or haste effects

Trigger keywords: `AnimationTree`, `AnimationNodeStateMachine`, `BlendSpace2D`, `BlendSpace1D`, `BlendTree`, `transition_request`, `blend_position`, `advance_expression`, `AnimationNodeAdd2`, `AnimationNodeBlend2`, `root_motion`.

**Use AnimationPlayer only** for: simple state swaps, UI animations, cutscenes, props. If a character has fewer than 5 states and no directional blending, AnimationTree is overkill.

## Prerequisites

- Godot 4.x project (Godot 4.7+ for latest API changes noted below)
- An `AnimationPlayer` node with imported animations (idle, walk, run, etc.)
- Basic familiarity with Godot's Animation panel and AnimationTree editor
- Windows host with PowerShell (primary development environment)

### Godot 4.7 Specific Changes

- `LookAtModifier3D.relative` default is now **false** (was true in 4.6).
- Blend space `add_blend_point` accepts an optional **name** parameter for labeled blend points.

## NEVER Do (Hard Rules)

These are lived rules verified against real Godot projects. Violating them causes jitter, conflicts, or performance degradation.

1. **NEVER call `play()` on AnimationPlayer when using AnimationTree** — AnimationTree controls the player. Directly calling `play()` causes conflicts and jitter. Use `set("parameters/transition_request")` or `travel()` instead.
2. **NEVER forget to set `active = true`** — AnimationTree is inactive by default. Animations won't play until `$AnimationTree.active = true`.
3. **NEVER use absolute paths for parameter access** — Use relative paths like `"parameters/StateMachine/transition_request"`. This ensures compatibility when nodes move in the hierarchy.
4. **NEVER leave `auto_advance` enabled for interactive states** — It causes immediate transitions. Use it only for automated sequences like combo chains or death-to-respawn.
5. **NEVER use `BlendSpace2D` for 1D blending** — Blending only speed? Use `BlendSpace1D`. Blending only two states? Use `Blend2`. `BlendSpace2D` is specifically for X+Y directional inputs (strafe).
6. **NEVER update AnimationTree parameters every frame without a guard** — Setting parameters via `set()` every frame regardless of change causes cache invalidation and potential stutter. Check equality first.
7. **NEVER use deep, nested `BlendTrees` for simple logic** — Every layer adds CPU overhead. If logic can be handled in a `StateMachine` or a simple script-driven `Blend2`, do it there.
8. **NEVER forget to handle `await get_tree().process_frame` when updating parameters synchronously** — Sometimes the tree needs one frame to reconcile state before the next parameter change takes effect.
9. **NEVER rely on `auto_advance` for long cutscenes** — If an animation is interrupted, `auto_advance` can put the character in a broken state. Use `Method Tracks` to signal state completion instead.
10. **NEVER use `Sync` groups for animations with wildly different lengths** — It forces one animation to play at an extreme speed. Use `TimeScale` or separate layers for mismatching cycles.

## Available Scripts

> **MANDATORY**: Read the appropriate script before implementing the corresponding pattern. Each script is located under `scripts/` in the skill directory.

| Script | When to Load |
|--------|-------------|
| `scripts/sync_parameter_manager.gd` | Before writing any code that sets AnimationTree parameters every frame. Provides guarded setters to prevent redundant updates and GPU cache churn. |
| `scripts/reactive_oneshot_vfx.gd` | When implementing `AnimationNodeOneShot` for high-priority reactive animations (recoil, blinks, hit reactions). |
| `scripts/dynamic_timescale_control.gd` | When implementing runtime playback speed manipulation (bullet-time, haste multipliers). |
| `scripts/advanced_transition_masking.gd` | When implementing procedural bone filtering (masking) for `Add2`/`Blend2` nodes to separate upper/lower body. |
| `scripts/statemachine_travel_code.gd` | When implementing programmatic `travel()` and `start()` control via `AnimationNodeStateMachinePlayback`. |
| `scripts/blendtree_logic_mixing.gd` | When building complex `BlendTree` mixing patterns for interactive combat layers. |
| `scripts/root_motion_animtree_sync.gd` | When implementing 3D CharacterBody root motion extraction optimized for AnimationTree. |
| `scripts/sync_group_layering.gd` | When using Sync Groups to keep multi-layered animations (walk + reload) aligned. |
| `scripts/nested_tree_architecture.gd` | When building hierarchical State Machines with nested node parameter paths. |
| `scripts/runtime_tree_debugging.gd` | When debugging current states, transition paths, and blend values in real-time. |

## Procedure

### Step 1: Scene Setup

```
CharacterBody2D or CharacterBody3D
  ├─ AnimationPlayer (has: idle, walk, run, jump, land)
  ├─ AnimationTree
  │   └─ Root: AnimationNodeStateMachine (assigned in editor)
  └─ VisibleOnScreenNotifier3D (optional, for perf optimization)
```

1. Add an `AnimationPlayer` node and ensure all needed animations are imported/created.
2. Add an `AnimationTree` node as a sibling.
3. In the AnimationTree inspector, set `anim_player` NodePath to point to the `AnimationPlayer`.
4. Assign a root node (e.g., `AnimationNodeStateMachine`) via `tree_root`.
5. Set `active = true` in code or in the inspector.

### Step 2: StateMachine Pattern (Basic)

Create state nodes in the AnimationTree editor (Idle, Walk, Run, Jump, Land), each referencing the corresponding AnimationPlayer animation. Add transitions between them with advance conditions or auto-advance.

```gdscript
@onready var anim_tree: AnimationTree = $AnimationTree
@onready var state_machine: AnimationNodeStateMachinePlayback = anim_tree.get("parameters/StateMachine/playback")

func _ready() -> void:
    anim_tree.active = true

func _physics_process(delta: float) -> void:
    var velocity := get_velocity()

    if is_on_floor():
        if velocity.length() < 10:
            state_machine.travel("Idle")
        elif velocity.length() < 200:
            state_machine.travel("Walk")
        else:
            state_machine.travel("Run")
    else:
        if velocity.y < 0:
            state_machine.travel("Jump")
        else:
            state_machine.travel("Land")
```

### Step 3: Transition Conditions (Advance Expressions)

In the AnimationTree editor, add a transition (e.g., Idle → Walk) and set its **Advance Condition** to a boolean parameter like `is_walking`. Then drive it from code:

```gdscript
anim_tree.set("parameters/conditions/is_walking", true)

# Damage transition example — reset each frame, set on event
anim_tree.set("parameters/conditions/is_damaged", false)

func take_damage() -> void:
    anim_tree.set("parameters/conditions/is_damaged", true)
    # Transition to "Hurt" state fires immediately
```

### Step 4: Auto-Advance (Combo Chains)

In the AnimationTree editor, add a transition (e.g., Attack1 → Attack2) and enable **Auto Advance** (no condition needed). Call `state_machine.travel("Attack1")` in code. When Attack1 finishes, it automatically transitions to Attack2, then to Idle.

Use auto-advance **only** for: attack combos, death → respawn, short automated sequences. Never for interactive states or long cutscenes.

### Step 5: BlendSpace2D (8-Way Directional Movement)

In the AnimationTree editor, create a `BlendSpace2D` node and add blend points at directional positions:

| Position | Animation |
|----------|-----------|
| (0, -1) | walk_up |
| (0, 1) | walk_down |
| (-1, 0) | walk_left |
| (1, 0) | walk_right |
| (-1, -1) | walk_up_left |
| (1, -1) | walk_up_right |
| (-1, 1) | walk_down_left |
| (1, 1) | walk_down_right |
| (0, 0) | idle (center) |

```gdscript
func _physics_process(delta: float) -> void:
    var input := Input.get_vector("left", "right", "up", "down")
    anim_tree.set("parameters/Movement/blend_position", input)
    # input = (0.5, -0.5) → blends walk_right and walk_up
```

### Step 6: BlendSpace1D (Speed Blending)

For walk → run transitions along a single axis:

```gdscript
# BlendSpace1D setup:
#   Position 0.0: walk
#   Position 1.0: run

func _physics_process(delta: float) -> void:
    var speed := velocity.length()
    var max_speed := 400.0
    var blend_value := clamp(speed / max_speed, 0.0, 1.0)
    anim_tree.set("parameters/SpeedBlend/blend_position", blend_value)
```

### Step 7: BlendTree (Layered Animations)

For upper-body + lower-body layering (e.g., aim while walking):

1. Set root to `BlendTree`.
2. Add `Walk` (lower body) and `Aim` (upper body) animation nodes.
3. Add an `Add2` node combining Walk and Aim.
4. Enable `filter_enabled` on the Add2 node.
5. Set filters: only enable upper body bones for the Aim input.

No code needed — BlendTree auto-combines. Just ensure animations are assigned.

### Step 8: Blend2 (Dynamic Crossfade)

```gdscript
# Root → BlendTree → Blend2
#   Input A: idle
#   Input B: attack

var blend_amount := 0.0

func _process(delta: float) -> void:
    blend_amount += delta
    blend_amount = clamp(blend_amount, 0.0, 1.0)
    anim_tree.set("parameters/IdleAttackBlend/blend_amount", blend_amount)
    # 0.0 = 100% idle, 0.5 = 50/50, 1.0 = 100% attack
```

### Step 9: Root Motion with AnimationTree

```gdscript
# Enable in AnimationTree inspector or code:
anim_tree.root_motion_track = NodePath("CharacterBody3D/Skeleton3D:Root")

func _physics_process(delta: float) -> void:
    var root_motion := anim_tree.get_root_motion_position()
    # Apply to character position (not velocity directly)
    global_position += root_motion.rotated(rotation.y)
    # For CharacterBody3D with move_and_slide:
    velocity = root_motion / delta
    move_and_slide()
```

**Load `scripts/root_motion_animtree_sync.gd` before implementing root motion** for the optimized extraction pattern.

### Step 10: Sub-StateMachines

For hierarchical state management:

```
Root → StateMachine
  ├─ Grounded (Sub-StateMachine)
  │   ├─ Idle
  │   ├─ Walk
  │   └─ Run
  └─ Airborne (Sub-StateMachine)
      ├─ Jump
      ├─ Fall
      └─ Glide
```

```gdscript
var sub_state = anim_tree.get("parameters/Grounded/playback")
sub_state.travel("Run")
```

**Load `scripts/nested_tree_architecture.gd` before building nested state machines** for the full parameter path management pattern.

### Step 11: TimeScale (Slow Motion)

```gdscript
anim_tree.set("parameters/TimeScale/scale", 0.5)  # 50% speed
# Useful for: bullet time, hurt/stun, charge-up animations
```

**Load `scripts/dynamic_timescale_control.gd`** for the full runtime manipulation pattern.

### Step 12: Sync Between Animations

To prevent foot slide when switching walk → run:

1. In the AnimationTree editor, select the transition (Walk → Run).
2. Enable the **Sync** checkbox.

Godot automatically syncs animation playback positions so feet stay grounded during the transition.

**Load `scripts/sync_group_layering.gd`** for multi-layer sync group setup. Never use Sync groups for animations with wildly different lengths.

### Step 13: Performance Optimization

Disable AnimationTree for off-screen entities:

```gdscript
extends VisibleOnScreenNotifier3D

func _ready() -> void:
    screen_exited.connect(_on_screen_exited)
    screen_entered.connect(_on_screen_entered)

func _on_screen_exited() -> void:
    $AnimationTree.active = false

func _on_screen_entered() -> void:
    $AnimationTree.active = true
```

For massive scenes, swap the entire `tree_root` resource between a complex "Hero" tree and a simplified "Crowd" tree:

```gdscript
class_name AnimationComplexityManager extends Node3D

@export var hero_tree: AnimationRootNode
@export var crowd_tree: AnimationRootNode

@onready var anim_tree: AnimationTree = $AnimationTree
@onready var visibility: VisibleOnScreenNotifier3D = $VisibleOnScreenNotifier3D

func _ready() -> void:
    visibility.screen_entered.connect(func(): anim_tree.tree_root = hero_tree)
    visibility.screen_exited.connect(func(): anim_tree.tree_root = crowd_tree)
```

## Expert Patterns

### Animation-Event-Dispatcher

Decouple animation frames from gameplay logic by using a generalized dispatcher that passes metadata through signals.

```gdscript
class_name AnimationEventDispatcher extends Node

signal animation_event(event_name: String, metadata: Variant)

func dispatch_event(event_name: String, metadata: Variant) -> void:
    animation_event.emit(event_name, metadata)

# Workflow:
# 1. Add Method Track to animation (e.g., "walk")
# 2. Keyframe: method="dispatch_event", args=["footstep", "stone"]
# 3. Audio manager listens to signal and plays correct 'stone' SFX
```

### Procedural-In-Place-Rotation

Use a `BlendTree` to blend turning animations based on rotation input for natural stationary turns.

```gdscript
# Root -> BlendTree
#   └─ TurnBlend (AnimationNodeBlend2)
#       ├─ Input 0: Idle
#       └─ Input 1: TurnRight

func _physics_process(delta: float) -> void:
    var turn_input := Input.get_axis("left", "right")
    var blend_amount := abs(turn_input)
    anim_tree.set("parameters/TurnBlend/blend_amount", blend_amount)
    rotate_y(-turn_input * turn_speed * delta)
```

## Pitfalls

1. **Animation not playing**: AnimationTree is inactive by default. Always set `anim_tree.active = true` in `_ready()`.
2. **Transition not firing**: Check (1) is `advance_condition` set correctly? (2) is transition priority correct? (3) is `auto_advance` enabled unintentionally?
3. **Blend not smooth**: Increase transition `xfade_time` to 0.1–0.3s.
4. **Jitter/stutter from parameter spam**: Setting parameters every frame without equality checks causes cache invalidation. Use guarded setters — load `scripts/sync_parameter_manager.gd`.
5. **Broken state after interruption**: `auto_advance` on long sequences can leave characters in broken states. Use Method Tracks to signal completion instead.
6. **Foot slide on walk→run**: Enable **Sync** on the transition between synced animations.
7. **Sync group speed mismatch**: Never group animations with wildly different lengths — one will play at extreme speed. Use `TimeScale` or separate layers.
8. **Synchronous parameter race**: Sometimes the tree needs one frame to reconcile. Use `await get_tree().process_frame` between rapid parameter changes.
9. **Using BlendSpace2D for 1D**: If only blending speed, use `BlendSpace1D`. If only blending two states, use `Blend2`. BlendSpace2D is for X+Y directional inputs only.
10. **Deep nested BlendTrees**: Every layer adds CPU overhead. Move simple logic to StateMachine or script-driven Blend2.

## Verification

### Check AnimationTree is Active

```gdscript
func _ready() -> void:
    assert($AnimationTree.active == true, "AnimationTree must be active to play animations")
```

### Print Current State and Blend Position

```gdscript
func _process(delta: float) -> void:
    var current_state = anim_tree.get("parameters/StateMachine/current_state")
    print("Current state: ", current_state)

    var blend_pos = anim_tree.get("parameters/Movement/blend_position")
    print("Blend position: ", blend_pos)
```

### Verify No Direct play() Calls

Search your codebase for direct `AnimationPlayer.play()` calls that conflict with AnimationTree:

```powershell
# From project root in PowerShell:
Select-String -Path "*.gd" -Pattern "\.play\(" | Where-Object { $_.Line -match "AnimationPlayer" }
```

If any results appear in scripts that also use AnimationTree, remove the `play()` call and replace with `travel()` or `transition_request`.

### Verify Root Motion Track

```gdscript
func _physics_process(delta: float) -> void:
    var rm := anim_tree.get_root_motion_position()
    if rm.length() > 0.0:
        print("Root motion this frame: ", rm)
```

### Verify Parameter Guard Pattern

```gdscript
# Correct pattern — check equality before setting
var _last_blend_pos: Vector2 = Vector2.ZERO

func _physics_process(delta: float) -> void:
    var input := Input.get_vector("left", "right", "up", "down")
    if input != _last_blend_pos:
        anim_tree.set("parameters/Movement/blend_position", input)
        _last_blend_pos = input
```

### Decision Matrix: AnimationPlayer vs AnimationTree

| Feature | AnimationPlayer Only | AnimationTree |
|---------|---------------------|---------------|
| Simple state swap | ✅ `play("idle")` | ❌ Overkill |
| Directional movement | ❌ Complex | ✅ BlendSpace2D |
| State machine (5+ states) | ❌ Messy code | ✅ StateMachine |
| Layered animations | ❌ Manual blending | ✅ BlendTree |
| Root motion | ✅ Possible | ✅ Built-in |
| Transition blending | ❌ Manual | ✅ Auto |

## Related Skills

- Master Skill: `godot-master` — see `../godot-master/SKILL.md` for overarching Godot patterns and cross-references.
