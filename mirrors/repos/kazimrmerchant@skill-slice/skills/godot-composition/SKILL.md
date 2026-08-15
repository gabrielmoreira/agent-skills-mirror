---
name: godot-composition
description: "Enforces Godot Has-A composition: selfish worker nodes, a logic-free orchestrator, signals-up/methods-down, and @export/%UniqueNames wiring. Use when the user wants to split player, NPC, or weapon systems out of a god-class inheritance chain. Trigger: Entity-Component, HealthComponent, child-node StateMachine. Not a scene-split chair (godot-scene-organization) and not the Health/Hitbox node kit (godot-component-system). Never deep-inherit features or let a component type-check its parent Player script."
version: 1.0.1
---

## Overview

This skill enforces **Composition over Inheritance** ("Has-a" vs "Is-a") in Godot 4.7+. In Godot, Nodes **are** components. A complex entity (Player) is an Orchestrator managing specialized Worker Nodes (Components).

**Golden Rules:**
1. **Single Responsibility**: One script = One job.
2. **Encapsulation**: Components are "selfish." They handle internal logic but don't know *who* owns them.
3. **The Orchestrator**: The root script (e.g., `player.gd`) does **no logic**. It only manages state and passes data between components.
4. **Decoupling**: Components communicate via **Signals** (up) and **Methods** (down).

## When to Use

- Designing player controllers, NPCs, enemies, or weapons in Godot 4.7+.
- Building complex gameplay systems that need to scale (RPGs, Platformers, Shooters).
- Refactoring deep inheritance chains into reusable component-based architecture.
- Triggered by keywords: Entity-Component, ECS, Gameplay, Actors, NPCs, Enemies, Weapons, Hitboxes, Game Loop, Level Design.

## Prerequisites

- **Godot 4.7+** (stable, 2026-06-18). Consult the [Godot 4.7 migration guide](https://docs.godotengine.org/en/4.7/tutorials/migrating/upgrading_to_godot_4.7.html) when upgrading from 4.6.
- **NEVER** assume 4.6 defaults (stretch mode, audio area_mask, RichTextLabel percent flags) without checking 4.7 migration notes.
- Windows host is primary (PowerShell). Scripts live in this skill's `scripts/` folder when present.

## Procedure

### 1. Identify Entity Responsibilities

Break a complex entity into single-responsibility components before writing any code.

| Component | Responsibility | Script Reference |
|---|---|---|
| Input | Read hardware state, store it, do NOT act | `scripts/` custom |
| Movement | Manipulate physics body, handle velocity/gravity | `scripts/velocity_component.gd` |
| Health | Manage HP, clamp values, signal changes | `scripts/health_component.gd` |
| HitBox | Intercept damage, delegate to HealthComponent | `scripts/hit_box_component.gd` |
| HurtBox | Deal damage to HitBoxComponents | `scripts/hurt_box_component.gd` |
| Interaction | Decoupled handler using injected `Callable` | `scripts/interaction_component.gd` |
| Follower | Tracking logic via `NodePath` injection | `scripts/follower_component.gd` |
| State (VSM) | Component-based FSM using child nodes as states | `scripts/state_component_vsm.gd` |
| Status Effect | Temporary modifiers stacked as child scenes | `scripts/status_effect_component.gd` |
| Visual Sync | Separate logical state from visual representation | `scripts/visual_sync_component.gd` |

**When to load each reference file:**
- Load `scripts/health_component.gd` when implementing damage or death logic on any entity.
- Load `scripts/hit_box_component.gd` and `scripts/hurt_box_component.gd` together when implementing combat collision.
- Load `scripts/velocity_component.gd` when implementing movement for Players or Enemies.
- Load `scripts/interaction_component.gd` when implementing context-aware player interactions (doors, items, NPCs).
- Load `scripts/follower_component.gd` when implementing pets, minions, or camera tracking.
- Load `scripts/state_component_vsm.gd` when an entity needs a finite state machine (idle, chase, attack).
- Load `scripts/status_effect_component.gd` when implementing buffs/debuffs or status ailments.
- Load `scripts/visual_sync_component.gd` when separating velocity/direction from sprite flipping.
- Load `scripts/composition_root_init.gd` when wiring and connecting components in a parent Orchestrator node.

### 2. Write the Component (Selfish Node)

Each component defines `class_name`, uses `@export` for wiring, and validates dependencies early.

```gdscript
class_name MyComponent extends Node
# Use Node for logic, Node3D/2D if it needs position

@export var stats: Resource
signal happened_something(value)

func _ready() -> void:
    _validate_dependencies()

func _validate_dependencies() -> void:
    # Fail early during development if setup is wrong.
    # NOTE: assert() is stripped in release builds.
    assert(stats != null, "Stats Resource missing on %s" % name)

func do_logic(delta: float) -> void:
    pass
```

### 3. Write the Orchestrator (Root Script)

The Orchestrator does **no logic**. It wires components via `@export` or `%UniqueNames`, connects signals, and passes data in `_physics_process`.

```gdscript
class_name Player extends CharacterBody3D

@export var health_component: HealthComponent
@export var movement_component: MovementComponent
@export var input_component: InputComponent

# Or use Scene Unique Names (%) for auto-assignment:
@onready var input: InputComponent = %InputComponent
@onready var move: MovementComponent = %MovementComponent
@onready var health: HealthComponent = %HealthComponent

func _ready():
    health.died.connect(_on_death)

func _physics_process(delta):
    input.update()
    move.tick(delta, input.move_dir, input.jump_pressed)

func _on_death():
    queue_free()
```

### 4. Standard Component Templates

**Input Component (The Senses)** — reads hardware state, stores it, does NOT act:
```gdscript
class_name InputComponent extends Node

var move_dir: Vector2
var jump_pressed: bool

func update() -> void:
    move_dir = Input.get_vector("left", "right", "up", "down")
    jump_pressed = Input.is_action_just_pressed("jump")
```

**Movement Component (The Legs)** — manipulates physics body, requires body reference:
```gdscript
class_name MovementComponent extends Node

@export var body: CharacterBody3D
@export var speed: float = 8.0
@export var jump_velocity: float = 12.0

func tick(delta: float, direction: Vector2, wants_jump: bool) -> void:
    if not body: return
    if not body.is_on_floor():
        body.velocity.y -= 9.8 * delta
    if direction:
        body.velocity.x = direction.x * speed
        body.velocity.z = direction.y * speed
    else:
        body.velocity.x = move_toward(body.velocity.x, 0, speed)
        body.velocity.z = move_toward(body.velocity.z, 0, speed)
    if wants_jump and body.is_on_floor():
        body.velocity.y = jump_velocity
    body.move_and_slide()
```

**Health Component (The Life)** — context-agnostic, works on Player, Enemy, or Crate:
```gdscript
class_name HealthComponent extends Node

signal died
signal health_changed(current, max)

@export var max_health: float = 100.0
var current_health: float

func _ready():
    current_health = max_health

func damage(amount: float):
    current_health = clamp(current_health - amount, 0, max_health)
    health_changed.emit(current_health, max_health)
    if current_health == 0:
        died.emit()
```

### 5. Expert Pattern: State-Component FSM

Encapsulate complex behaviors into child nodes acting as states. The parent `StateMachine` delegates lifecycle calls to the active child.

```gdscript
class_name StateMachine extends Node
@export var initial_state: Node
@onready var _state: Node = initial_state

func _ready() -> void:
    if _state.has_method("enter"): _state.enter()

func _physics_process(delta: float) -> void:
    if _state.has_method("physics_process"):
        _state.physics_process(delta)

func transition_to(target_state_path: NodePath) -> void:
    if _state.has_method("exit"): _state.exit()
    _state = get_node(target_state_path)
    if _state.has_method("enter"): _state.enter()
```

### 6. Expert Pattern: Component-Registry (O(1) Lookup)

Avoid slow tree traversal for sibling communication. Catalog children in a Dictionary.

```gdscript
var _components: Dictionary = {}

func _ready() -> void:
    for child in get_children():
        _components[child.name] = child
        for group in child.get_groups():
            _components[group] = child

func get_comp(key: StringName) -> Node:
    return _components.get(key)
```

### 7. Expert Pattern: Dependency-Validation

Fail fast during development if required components are missing.

```gdscript
func _ready() -> void:
    assert(get_node_or_null("HealthComponent") != null, "Missing HealthComponent!")
    assert(get_node_or_null("InputComponent") != null, "Missing InputComponent!")
```

## Pitfalls

### NEVER Do in Composition

1. **NEVER use deep inheritance chains** (e.g., `Player > Entity > LivingThing > Node`) — Creates brittle "God Classes" that are hard to refactor.
2. **NEVER use `get_node()` or `$` for components** — Breaks if the scene tree is rearranged. Always use `@export` or `%UniqueNames`.
3. **NEVER let a component reference its parent script directly** — Makes the component impossible to reuse. Use signals or dependency injection.
4. **NEVER mix Input, Physics, and Game Logic in one script** — Violates Single Responsibility. Split into specialized components.
5. **NEVER create components that require a specific SceneTree structure** — A component should be "selfish" and only care about its own properties and direct children.
6. **NEVER use inheritance to "add a feature"** — If you want an enemy to shoot, add a `ShootingComponent`, don't make it inherit from `ShooterEnemy`.
7. **NEVER hardcode component dependencies** — If `CombatComponent` needs `HealthComponent`, look it up in `_ready()` or inject it via the parent.
8. **NEVER treat Godot nodes as pure data** — Nodes provide lifecycle (`_process`) and signals. If you only need data, use a `Resource`.
9. **NEVER ignore the Node lifecycle in components** — Use `_enter_tree()` and `_exit_tree()` for setup/cleanup that must happen regardless of the parent's state.
10. **NEVER hide component points of access** — Expose `NodePath` or `Callable` properties so the parent can wire the component in the Inspector.

### Additional Warnings

- **`assert()` is stripped in release builds** — Do not rely on it for runtime validation in shipped games. Use explicit `push_error()` with early returns for production-critical checks.
- **NEVER assume Godot 4.6 defaults** — Stretch mode, audio `area_mask`, and `RichTextLabel` percent flags changed in 4.7. Always check migration notes.
- **Performance**: Nodes are lightweight. Do not fear adding 10-20 nodes per entity. The organizational benefit of Composition vastly outweighs the negligible memory cost of `Node` instances.

## Verification

1. **Check `class_name` is declared** on every component so it can be used as a type:
   ```powershell
   Select-String -Path "scripts\*.gd" -Pattern "^class_name" | Measure-Object
   ```
   Expected: count matches the number of component scripts.

2. **Verify no `get_node()` or `$` references for component access**:
   ```powershell
   Select-String -Path "scripts\*.gd" -Pattern 'get_node\(|\$[A-Za-z]' | Where-Object { $_.Line -notmatch 'transition_to|get_node_or_null' }
   ```
   Expected: no matches (or only matches inside StateMachine `transition_to`).

3. **Verify no parent script references in components** (components must not import or type-check against parent scripts):
   ```powershell
   Select-String -Path "scripts\*_component.gd" -Pattern 'Player|Enemy|NPC'
   ```
   Expected: no matches in component files (only Orchestrator scripts may reference these).

4. **Verify `@export` or `%UniqueNames` used for component wiring**:
   ```powershell
   Select-String -Path "scripts\*.gd" -Pattern '@export|%[A-Z]'
   ```
   Expected: matches in Orchestrator scripts for each component dependency.

5. **Verify signals are used for upward communication**:
   ```powershell
   Select-String -Path "scripts\*_component.gd" -Pattern '^signal '
   ```
   Expected: matches in HealthComponent (`died`, `health_changed`) and other components that notify parents.

## Related Skills

- Master Skill: [godot-master](../godot-master/SKILL.md)
