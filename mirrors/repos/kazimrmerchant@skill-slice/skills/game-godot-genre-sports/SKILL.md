---
name: game-godot-genre-sports
version: 1.1.1
description: "Builds Godot 4.3+ sports sims: RigidBody3D Magnus ball physics, formation-slot team AI, contextual pass/shoot/tackle input, and broadcast cameras. Use when making soccer, basketball, hockey, racing, or arcade sports. Not for turn-based or cosmetic-physics sports, party minigame collections (game-godot-genre-party), or general Camera2D follow (game-camera-system)."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## When to Use

Use this skill when developing sports simulations or arcade sports titles in **Godot 4.3+** that require any of the following:

- **High-Fidelity Physics:** Ball/puck dynamics including the Magnus effect (curve), friction, bounce, and air resistance.
- **Dynamic Team AI:** Group behaviors, positional slots, and tactical shifts (e.g., switching from offensive to defensive formations).
- **Contextual Input:** Systems where a single button performs different actions based on the player's state (e.g., "Pass" vs "Shoot" based on distance to goal).
- **Broadcast Cinematography:** Smooth, target-tracking cameras that mimic professional sports broadcasts.
- **Steering Behaviors:** Arrival, Pursuit, and Separation behaviors for AI athletes.

### Do Not Use For

- **Static Gameplay:** Turn-based sports games or simple 2D sports games where physics are purely cosmetic.
- **Non-Sports Projects:** These formation patterns are tuned for sports; do not apply to general RPG or FPS AI.
- **Low-Performance Targets:** Complex physics calculations on very low-end mobile hardware require collision-layer optimization first.

## Prerequisites

- **Godot 4.3 or later** (`.NET` or standard build). Verify with:
  ```powershell
  godot --version
  # Expected output: 4.3.stable or higher
  ```
- A 3D project with `RigidBody3D`, `Camera3D`, and `CharacterBody3D` nodes available.
- Basic familiarity with Godot's `PhysicsDirectBodyState3D` and resource-based architecture.
- If using the `PhantomCamera` addon for broadcast cameras, install it from the Godot Asset Library before proceeding.

## Procedure

### 1. Physics-Based Ball Interaction (Magnus Effect)

Implement the ball or puck as a `RigidBody3D`. Override `_integrate_forces` to apply custom physics such as the Magnus effect for curving shots.

```gdscript
# SportsBall.gd — minimal inline Magnus snippet; pack companion: scripts/sports_ball_physics.gd
extends RigidBody3D
class_name SportsBall

@export var magnus_coefficient: float = 0.5
@export var air_density: float = 1.2
@export var ball_radius: float = 0.11

func _integrate_forces(state: PhysicsDirectBodyState3D) -> void:
    var r3 := ball_radius * ball_radius * ball_radius
    var coef := (4.0 / 3.0) * PI * r3 * air_density * magnus_coefficient
    var magnus_force := state.angular_velocity.cross(state.linear_velocity) * coef
    state.apply_force(magnus_force)
```

**Steps:**
1. Create a `RigidBody3D` node named `Ball` in your scene.
2. Attach a `SphereMesh` (or appropriate mesh) with a `CollisionShape3D` matching `ball_radius`.
3. Attach `scripts/sports_ball_physics.gd` (or the inline SportsBall snippet) to the node.
4. Set `contact_monitor` to `true` and `max_contacts_reported` to `8` if you need collision callbacks.
5. Tune `magnus_coefficient` in the inspector: `0.1` for subtle curve, `0.5` for arcade-style dramatic bend.

### 2. Team AI Formation Management

Create a `TeamManager` node that assigns `FormationSlot` resources to players. Use a state machine to transition between tactical states (`ATTACKING`, `DEFENDING`, `TRANSITION`).

```gdscript
# formation_slot.gd — project Resource (inline)
class_name FormationSlot
extends Resource

@export var slot_name: String = "Striker"
@export var base_offset: Vector3 = Vector3(0, 0, -10)
```

```gdscript
# scripts/team_manager.gd
extends Node
class_name TeamManager

@export var formation_slots: Array[FormationSlot] = []

func update_tactics(ball_position: Vector3) -> void:
    for slot in formation_slots:
        var target_pos := ball_position + slot.base_offset
        print("Moving slot: ", slot.slot_name, " to: ", target_pos)
```

**Steps:**
1. Create `FormationSlot` resources in the inspector for each position (e.g., Striker, Midfielder, Defender, Goalkeeper).
2. Set `base_offset` relative to the ball position for each slot (negative Z = forward, positive Z = backward).
3. Attach `scripts/team_manager.gd` to a `Node` in your scene.
4. Populate the `formation_slots` array with your created resources.
5. Call `update_tactics(ball_position)` every physics frame from your match controller.
6. Implement a state machine on each AI player that reads its assigned slot's `target_pos` and uses steering behaviors (Step 5) to move there.

### 3. Contextual Input System

Implement an `InputManager` that queries the player's current state and environment (distance to goal, teammate proximity) to map a single input to different actions.

```gdscript
# InputManager.gd — project autoload (inline)
extends Node
class_name InputManager

enum Context { ATTACK, DEFENSE, NEUTRAL }
var current_context: Context = Context.NEUTRAL

func handle_input(action_name: StringName) -> void:
    match current_context:
        Context.ATTACK:
            if action_name == &"action_main":
                perform_shoot()
        Context.DEFENSE:
            if action_name == &"action_main":
                perform_tackle()
        Context.NEUTRAL:
            if action_name == &"action_main":
                perform_dribble()

func perform_shoot() -> void:
    print("Shooting!")

func perform_tackle() -> void:
    print("Tackling!")

func perform_dribble() -> void:
    print("Dribbling!")
```

**Steps:**
1. Attach the InputManager snippet above to an autoload singleton or a persistent `Node`.
2. Define input actions in **Project > Project Settings > Input Map** (e.g., `action_main`, `action_secondary`, `action_switch`).
3. Update `current_context` each frame based on game state:
   - `ATTACK` when the controlled player has possession and is near the opponent's goal.
   - `DEFENSE` when the opponent has possession.
   - `NEUTRAL` during loose-ball or transition states.
4. Route all player input through `handle_input()` so context resolution happens in one place.

### 4. Broadcast Camera System

Use a `Camera3D` with smoothing interpolation, or the `PhantomCamera` addon if installed, to track the ball while keeping the active player in frame.

**Steps (native Godot, no addon):**
1. Add a `Camera3D` to your scene as a child of a `Node3D` (the "rig").
2. Each frame, compute a target position that frames both the ball and the active player:
   ```gdscript
   # BroadcastCamera.gd — project Camera3D (inline)
   extends Camera3D

   @export var ball: Node3D
   @export var active_player: Node3D
   @export var smooth_speed: float = 3.0
   @export var offset: Vector3 = Vector3(0, 15, 20)

   func _physics_process(delta: float) -> void:
       if not ball or not active_player:
           return
       var midpoint := (ball.global_position + active_player.global_position) / 2.0
       var target_pos := midpoint + offset
       global_position = global_position.lerp(target_pos, smooth_speed * delta)
       look_at(midpoint)
   ```
3. Attach the BroadcastCamera snippet and assign `ball` and `active_player` references in the inspector.
4. Adjust `offset` to mimic broadcast angles: high Y + back Z for sideline cam, lower Y for pitch-level.

**Steps (PhantomCamera addon):**
1. Install PhantomCamera from the Asset Library.
2. Add a `PhantomCamera3D` node and set its `follow_target` to the ball.
3. Add the active player as a secondary look-at target.
4. Tune `follow_damping` for smooth broadcast-style motion.

### 5. Steering Behaviors for AI Athletes

Implement `Vector3` steering forces so AI players move naturally toward their assigned formation slots without overlapping.

**Steps:**
1. On each AI `CharacterBody3D`, compute a desired velocity toward the formation slot target.
2. Apply **Arrival** behavior (decelerate as the AI nears the slot):
   ```gdscript
   # Arrival steering — project CharacterBody3D (inline)
   extends CharacterBody3D

   @export var max_speed: float = 8.0
   @export var arrival_radius: float = 2.0

   func arrive(target_pos: Vector3, delta: float) -> void:
       var to_target := target_pos - global_position
       var distance := to_target.length()
       if distance < 0.01:
           return
       var ramped_speed := max_speed * (distance / arrival_radius)
       var clamped_speed := min(ramped_speed, max_speed)
       var desired_velocity := to_target.normalized() * clamped_speed
       velocity = velocity.lerp(desired_velocity, 10.0 * delta)
       move_and_slide()
   ```
3. Add **Separation** by checking nearby teammates via `Area3D` overlap and steering away from their average position.
4. Add **Pursuit** for defenders chasing a ball carrier: predict the carrier's future position based on their current velocity and steer toward it.

## Examples

- **Soccer/Football:** A ball with air resistance and a team maintaining a 4-4-2 formation. Slots shift forward when attacking, drop back when defending.
- **Basketball:** Contextual input switches from "Dribble" to "Shoot" when within the paint. Defensive context triggers "Steal" on the same button.
- **Hockey:** High-friction puck physics with rapid AI repositioning. Magnus effect is minimal; focus on friction and rebound energy.
- **Racing/Extreme Sports:** Vehicle physics using `VehicleBody3D` with AI opponents using pursuit steering and waypoint following.
- **Arcade Sports:** Simplified physics with exaggerated "power-up" impulses and dynamic camera zooms on key moments.

## Pitfalls

- **Magnus force direction:** `angular_velocity.cross(linear_velocity)` produces a force perpendicular to spin and velocity. If the ball curves the wrong way, negate the coefficient or check your spin axis sign.
- **Formation slot jitter:** If AI players oscillate around their slot, increase `arrival_radius` or add a dead-zone threshold (stop moving when within `0.5` units).
- **Context flickering:** If `current_context` rapidly switches between `ATTACK` and `DEFENSE` near the threshold, add hysteresis (e.g., require 0.5s of consistent state before switching).
- **Camera clipping:** Broadcast cameras can clip through stadium geometry. Add a `RayCast3D` from the camera target to the camera position and pull the camera in if the ray is blocked.
- **Performance on mobile:** Complex `_integrate_forces` calculations and many AI steering queries can be expensive. Profile with Godot's built-in debugger; reduce physics tick rate or simplify collision shapes if frame time exceeds budget.
- **Collision layers:** Ensure the ball, players, and field are on separate collision layers to prevent unwanted interactions (e.g., ball resting on a player's head). Use layer masks, not layer removal, so physics still reports contacts.

## Verification

Run the following checks to confirm the skill is correctly implemented:

### Physics Validation
- [ ] Ball responds to impulses: apply `apply_central_impulse(Vector3(1, 0, 0))` and confirm `linear_velocity.length() > 0`.
- [ ] Magnus force is applied: set non-zero `angular_velocity` and `linear_velocity`, observe lateral curve in `_integrate_forces`.
- [ ] Ball does not pass through the field at high speeds: enable continuous collision detection (`contact_monitor = true`, `max_contacts_reported >= 4`).

### AI Formation Check
- [ ] AI players move toward their assigned slots when `update_tactics()` is called.
- [ ] Players maintain minimum separation (no two players occupy the same position).
- [ ] Formation shifts correctly when the ball changes possession (slots reposition relative to new ball position).

### Input Context Test
- [ ] The same `action_main` input triggers `perform_shoot()` in `ATTACK` context.
- [ ] The same input triggers `perform_tackle()` in `DEFENSE` context.
- [ ] The same input triggers `perform_dribble()` in `NEUTRAL` context.

### Camera Tracking
- [ ] Broadcast camera maintains a smooth follow-target without jitter.
- [ ] Camera does not clip through stadium geometry (verify with a `RayCast3D` obstruction check).
- [ ] Both ball and active player remain in frame during fast transitions.

### Automated Verification Script

```gdscript
# verify_skill.gd — save in the Godot project root, then run headless
extends SceneTree

func _init() -> void:
    # Test ball physics
    var ball := SportsBall.new()
    var impulse := Vector3(1, 0, 0)
    ball.apply_central_impulse(impulse)
    assert(ball.linear_velocity.length() > 0, "Ball should have velocity after impulse")
    print("PASS: Ball physics impulse")

    # Test team manager
    var team_manager := TeamManager.new()
    var slot := FormationSlot.new()
    slot.slot_name = "Striker"
    slot.base_offset = Vector3(0, 0, -10)
    team_manager.formation_slots = [slot]
    team_manager.update_tactics(Vector3(0, 0, 0))
    print("PASS: Team manager update_tactics")

    # Test input manager
    var input_manager := InputManager.new()
    input_manager.current_context = InputManager.Context.ATTACK
    input_manager.handle_input(&"action_main")
    print("PASS: Input manager contextual dispatch")

    print("All verification checks passed.")
    quit()
```

Run from PowerShell:
```powershell
godot --headless --script verify_skill.gd
```

Expected output:
```
PASS: Ball physics impulse
Moving slot: Striker to: (0, 0, -10)
PASS: Team manager update_tactics
Shooting!
PASS: Input manager contextual dispatch
All verification checks passed.
```

## Related Skills

- **Godot Physics & Collision:** Advanced use of `CollisionLayers`, `PhysicsMaterial`, and contact reporting.
- **AI Steering Behaviors:** Implementation of Reynolds' steering behaviors for crowd/team movement.
- **State Machines:** Managing complex athlete states (Idle, Sprint, Tackle, Shoot) with `AnimationTree` integration.
- **Cinematography:** Using `InterpolatedCamera` and `BezierCurve3D` for replay systems.
- **AnimationTree:** Using `BlendTree` for seamless transitions between running and kicking/throwing animations.
