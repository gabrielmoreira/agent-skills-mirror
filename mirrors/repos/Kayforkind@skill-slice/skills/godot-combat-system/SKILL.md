---
name: godot-combat-system
description: "Wires Godot combat with Area2D Hitbox/Hurtbox, DamageData, HealthComponent, combo windows, ability cooldowns, i-frames, and damage popups. Use when the user wants action, RPG, or fighting hit detection and damage flow. Trigger: invincibility_frames, combat_state, knockback. Not for entity orchestrator/Has-A architecture (godot-composition) or scene layout. Never write target.health -= n or leave hitboxes enabled between attacks."
version: 1.0.1
---

## Overview
Expert guidance for building flexible, component-based combat systems in Godot 4.7+. This skill provides production-ready GDScript patterns for damage calculation, hit detection, health management, and combat state machines.

## When to Use
- Building combat systems in Godot 4.7+ (action games, RPGs, fighting games).
- Implementing hitbox/hurtbox architecture, damage calculation, or health components.
- Creating combat state machines, combo systems, or ability cooldowns.
- Trigger keywords: Hitbox, Hurtbox, DamageData, HealthComponent, combat_state, combo_system, ability_cooldown, invincibility_frames, damage_popup.

## Prerequisites
- Godot 4.7+ (stable, 2026-06-18). Consult the [Godot 4.7 migration guide](https://docs.godotengine.org/en/4.7/tutorials/migrating/upgrading_to_godot_4.7.html) when upgrading from 4.6.
- Windows host is primary (PowerShell). Ensure Godot CLI is accessible or use the Godot editor directly.

## Procedure

### 1. Load Reference Scripts
Before implementing any combat pattern, read the appropriate reference script:
- Load `scripts/combat_system_patterns.gd` when implementing safe duck-typing, hitstun tweens, nodeless AoE shape casting, or frame-perfect sync.
- Load `scripts/hitbox_hurtbox.gd` when implementing component-based hitboxes with hit-stop and knockback logic.

### 2. Implement DamageData
Create a lightweight `RefCounted` class to pass damage context.
```gdscript
# damage_data.gd
class_name DamageData
extends RefCounted

var amount: float
var source: Node
var damage_type: String = "physical"
var knockback: Vector2 = Vector2.ZERO
var is_critical: bool = false

func _init(dmg: float, src: Node = null) -> void:
    amount = dmg
    source = src
```

### 3. Implement Hitbox/Hurtbox
Use `Area2D` for collision detection. The Hitbox generates `DamageData`, and the Hurtbox receives it.
```gdscript
# hurtbox.gd
extends Area2D
class_name Hurtbox

signal damage_received(data: DamageData)

@export var health_component: Node

func _ready() -> void:
    area_entered.connect(_on_area_entered)

func _on_area_entered(area: Area2D) -> void:
    if area is Hitbox:
        var damage := area.get_damage()
        damage_received.emit(damage)
        
        if health_component:
            health_component.take_damage(damage)
```
```gdscript
# hitbox.gd
extends Area2D
class_name Hitbox

@export var damage: float = 10.0
@export var damage_type: String = "physical"
@export var knockback_force: float = 100.0
@export var owner_node: Node

func get_damage() -> DamageData:
    var data := DamageData.new(damage, owner_node)
    data.damage_type = damage_type
    
    if owner_node:
        var direction := (global_position - owner_node.global_position).normalized()
        data.knockback = direction * knockback_force
    
    return data
```

### 4. Implement HealthComponent
Manage health, invincibility, and signals.
```gdscript
# health_component.gd
extends Node
class_name HealthComponent

signal health_changed(old_health: float, new_health: float)
signal died
signal healed(amount: float)

@export var max_health: float = 100.0
@export var current_health: float = 100.0
@export var invincible: bool = false

func take_damage(data: DamageData) -> void:
    if invincible:
        return
    
    var old_health := current_health
    current_health -= data.amount
    current_health = clampf(current_health, 0, max_health)
    
    health_changed.emit(old_health, current_health)
    
    if current_health <= 0:
        died.emit()

func heal(amount: float) -> void:
    var old_health := current_health
    current_health += amount
    current_health = minf(current_health, max_health)
    
    healed.emit(amount)
    health_changed.emit(old_health, current_health)

func is_dead() -> bool:
    return current_health <= 0
```

### 5. Implement Combat State Machine
Use `StringName` for state names in high-frequency loops.
```gdscript
# combat_state.gd
extends Node
class_name CombatState

enum State { IDLE, ATTACKING, BLOCKING, DODGING, STUNNED }

var current_state: State = State.IDLE
var can_act: bool = true

func enter_attack_state() -> bool:
    if not can_act:
        return false
    
    current_state = State.ATTACKING
    can_act = false
    return true

func enter_block_state() -> void:
    current_state = State.BLOCKING

func enter_dodge_state() -> bool:
    if not can_act:
        return false
    
    current_state = State.DODGING
    can_act = false
    return true

func exit_state() -> void:
    current_state = State.IDLE
    can_act = true
```

### 6. Implement Combo System
Buffer inputs and check for sequences.
```gdscript
# combo_system.gd
extends Node
class_name ComboSystem

signal combo_executed(combo_name: String)

@export var combo_window: float = 0.5
var combo_buffer: Array[String] = []
var last_input_time: float = 0.0

func register_input(action: String) -> void:
    var current_time := Time.get_ticks_msec() / 1000.0
    
    if current_time - last_input_time > combo_window:
        combo_buffer.clear()
    
    combo_buffer.append(action)
    last_input_time = current_time
    
    check_combos()

func check_combos() -> void:
    if combo_buffer.size() >= 3:
        var last_three := combo_buffer.slice(-3)
        if last_three == ["light", "light", "heavy"]:
            execute_combo("special_attack")
            combo_buffer.clear()

func execute_combo(combo_name: String) -> void:
    combo_executed.emit(combo_name)
```

### 7. Implement Ability System
Use `Resource` for lightweight stat containers.
```gdscript
# ability.gd
class_name Ability
extends Resource

@export var ability_name: String
@export var cooldown: float = 1.0
@export var damage: float = 25.0
@export var range: float = 100.0
@export var animation: String

var is_on_cooldown: bool = false

func can_use() -> bool:
    return not is_on_cooldown

func use(caster: Node) -> void:
    if not can_use():
        return
    
    is_on_cooldown = true
    _execute(caster)
    
    await caster.get_tree().create_timer(cooldown).timeout
    is_on_cooldown = false

func _execute(caster: Node) -> void:
    pass
```

### 8. Implement Damage Popups
Use tweens for visual feedback.
```gdscript
# damage_popup.gd
extends Label

func show_damage(amount: float, is_crit: bool = false) -> void:
    text = str(int(amount))
    
    if is_crit:
        modulate = Color.RED
        scale = Vector2(1.5, 1.5)
    
    var tween := create_tween()
    tween.set_parallel(true)
    tween.tween_property(self, "position:y", position.y - 50, 1.0)
    tween.tween_property(self, "modulate:a", 0.0, 1.0)
    tween.finished.connect(queue_free)
```

## Pitfalls

- **NEVER use direct damage references (`target.health -= 10`)** — This bypasses armor, resistances, and invincibility logic. Always use a `DamageData` + `HealthComponent` pattern.
- **NEVER forget invincibility frames (i-frames)** — Without them, multi-hit attacks deal damage every single frame. Always apply a brief invincibility period (0.1–0.5s) after taking a hit.
- **NEVER keep hitboxes active permanently** — This causes unintended "ghost" damage. Enable and disable hitboxes precisely using `AnimationPlayer` tracks or code-timed triggers.
- **NEVER use groups for physics-based hit filtering** — Collision layers are evaluated in C++ and are significantly faster. Groups don't restrict physics intersections adequately for high-performance combat.
- **NEVER emit damage signals without a DamageData object** — A raw number loses critical context like damage type, source, and knockback direction.
- **NEVER use try/catch blocks with validate targets** — GDScript does not support exceptions. Use `has_method(&"take_damage")` or the `is` operator for safe type checking.
- **NEVER hardcode hitstun pauses using OS.delay_msec()** — This blocks the entire OS thread and freezes the game. Use `create_tween()` or `Engine.time_scale` for visual hit-stop effects.
- **NEVER apply massive impulses to a RigidBody inside _process()** — Physics-altering impulses must happen in `_physics_process()` or `_integrate_forces()` to remain deterministic and stable.
- **NEVER couple UI lifebars directly inside the Player script** — Use a `health_changed` signal. This keeps your combat logic clean and independent of UI implementation details.
- **NEVER leave CollisionShapes active on dead entities** — Corpses will block players and towers. Disable them immediately using `set_deferred("disabled", true)`.
- **NEVER scale CollisionShapes non-uniformly** — Non-uniform scaling breaks the physics engine's collision math. Always scale the internal resource (e.g., `CircleShape2D.radius`) instead.
- **NEVER use instanced Nodes for base stat data** — Nodes carry unnecessary overhead. Use Godot's `Resource` class for lightweight, efficient, and inspectable stat containers.
- **NEVER use raw strings for elemental damage types** — Strings are slow and error-prone. Use `enum` flags (optionally with `@export_flags`) to manage multi-type damage efficiently.
- **NEVER use standard strings for state names in high-frequency loops** — Use `StringName` (&"attacking", &"stunned") to drastically improve dictionary lookups and hash comparison speeds.
- **NEVER forget to duplicate() a shared Resource stats block** — If you don't call `duplicate()` when instancing a mob, all enemies of that type will share the same health pool.
- **NEVER assume 4.6 defaults** (stretch mode, audio area_mask, RichTextLabel percent flags) without checking 4.7 migration notes.

## Verification

1. **Check Script Compilation**: Open the Godot editor and ensure no parse errors exist in `damage_data.gd`, `hurtbox.gd`, `hitbox.gd`, `health_component.gd`, `combat_state.gd`, `combo_system.gd`, `ability.gd`, and `damage_popup.gd`.
2. **Test Hitbox/Hurtbox Interaction**: 
   - Create a test scene with a `Hitbox` and `Hurtbox` node.
   - Overlap them and verify that the `damage_received` signal fires and `HealthComponent.take_damage` is called.
3. **Verify Invincibility Frames**:
   - Set `invincible = true` on the `HealthComponent`.
   - Overlap the hitbox and confirm no damage is applied.
4. **Verify Combo System**:
   - Call `register_input("light")` twice, then `register_input("heavy")`.
   - Confirm the `combo_executed` signal emits with `"special_attack"`.
5. **Verify Resource Duplication**:
   - Instance two enemies sharing the same `Ability` resource.
   - Use the ability on one enemy and confirm the other enemy's ability is not on cooldown.

## Related skills
- Master Skill: [godot-master](../godot-master/SKILL.md)
