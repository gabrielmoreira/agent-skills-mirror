---
name: godot-component-system
version: 1.1.1
description: "Assembles Godot 4.3+ entities from single-purpose nodes (Health, Hitbox, Hurtbox, Interactable, StateMachine) with signals outward, typed @export inward, weakrefs, and type-based sibling lookup. Use when orthogonal capabilities must mix without a tall inheritance chain. Never a scene-split/layout chair (godot-scene-organization); this folder does not ship extra markdown companions."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Overview

Build behavior through composition: attach small, single-purpose components — a `HealthComponent`, a `HitboxComponent`, a `HurtboxComponent` — to any entity instead of deriving that entity from a tall base class. All examples target Godot 4.3+ and use no deprecated APIs.

**Why composition rather than inheritance.** Inheritance forces every entity onto a single linear hierarchy, but real games need *orthogonal* capabilities that do not nest cleanly. A crate is destructible but never animated; a boss is animated, destructible, and stateful; a spike trap deals damage but has no health of its own. Trying to express those combinations as one chain (`Entity → DamageableEntity → AnimatedDamageableEntity → …`) produces a brittle tree: adding a capability to one branch ripples into unrelated siblings, and any entity that needs two capabilities from different branches simply cannot be expressed. Composition lets each entity opt into exactly the components it needs, lets two unrelated entities share a capability without sharing an ancestor, and lets you test each component in isolation.

## When to Use

- You are assembling entity behavior from small, single-purpose components rather than a deep inheritance hierarchy.
- You need orthogonal capabilities (health, hitbox, hurtbox, interaction, state machine) that different entity types share in varying combinations.
- You want each component to be independently testable in a minimal scene with no dependency on a specific parent type.
- You are targeting Godot 4.3+ and want to avoid deprecated APIs.

## When NOT to Use

Reach for plain inheritance only for genuine "is-a" specialization along a *single* axis (for example, a custom `Resource` subtype that adds one typed field). Do **not** use it to assemble behavior. Concretely, avoid:

- **Deep behavior chains.** Each layer can silently change what a method does for everything below it, so a fix at the top can break a leaf three levels down. The hierarchy becomes the thing you debug instead of the gameplay.
- **A shared base class that bundles unrelated behavior** just so two entities can reuse one method. That couples those entities permanently; the next time one needs to diverge, you are forced to either copy the base or thread a flag through it. Extract the shared behavior into a component instead.
- **A "god" component that keeps accreting responsibilities.** The moment its name needs an "And" (`HealthAndShieldAndRegenComponent`), it can no longer be reused by an entity that wants only one of those parts. Split it.

## Prerequisites

- **Godot 4.3 or later.** All APIs used (`@export_range`, `@export_flags_2d_physics`, `StringName`, `weakref()`, typed signals) require 4.3+.
- **No external addons.** Every component is pure GDScript (or C# with nullable reference types enabled). No third-party plugin or asset is required.
- **Project structure.** Create a `components/` directory under your project root (e.g. `res://components/`) and save each component as its own `.tscn` + `.gd` pair so they can be instanced into any entity scene.
- **Design and security rules.** Follow Step 1 before writing a new component from scratch. Follow Step 2 when scene files are user-editable (mod support) or when game state is authoritative for networked / anti-cheat reasons. Those rules are inlined in this file; this folder does not ship extra markdown companions.

## Procedure

### Step 1 — Follow the Component Design Rules

These five rules govern every component you write:

1. **One responsibility per component.** A component you can describe in one sentence *without* the word "and" is a component you can reuse on an entity that needs only that one thing, test in isolation, and reason about without loading the whole game. The "and" in `HealthAndShieldComponent` is the seam where it should split.
2. **Communicate outward with signals; depend inward with typed `@export` references.** A signal *broadcasts an event* to listeners the component has never heard of — UI, audio, score — which is what keeps the component decoupled from the rest of the game. A typed `@export` reference, by contrast, is for a *declared dependency* you wire in the Inspector (a `HurtboxComponent` legitimately needs to know its `HealthComponent`). The pattern to avoid is the third one: `get_parent().get_node("HealthComponent")`, which hardcodes a sibling's name and tree position and breaks silently the moment someone renames or reparents a node.
3. **Prefer derived, stateless logic; keep any necessary state private.** Every piece of mutable state is something that can desync, get saved in a bad combination, or be mutated from two places at once. Derive what you can from inputs and `@export` configuration; when you genuinely must store state, keep it private (`_current_health`) behind explicit getters so the invariants live in exactly one place.
4. **Put configuration in `@export`, not in constants.** Damage, cooldown duration, and layer masks belong in the Inspector so designers can tune them without touching code and so the *same* component scene can be reused with different values on different entities.
5. **Clean up connections to longer-lived objects in `_exit_tree()`.** Connections to a node's own children are freed automatically when the node is freed, but a connection to an autoload, a parent, or a shared event bus *outlives* the component and leaves a dangling callable that can fire on freed state. Disconnecting in `_exit_tree()` is the habit that makes those long-lived connections safe; doing it for self-owned connections too keeps the ownership of every connection explicit and survives later refactors.

### Step 2 — Apply Security Considerations

These guards matter most when scene files are user-editable (mod support) or when game state is authoritative for networked / anti-cheat reasons. Even in a purely single-player build they prevent hard crashes from malformed or stale data, so treat them as baseline robustness rather than optional hardening.

- **Validate signal payloads that cross scene boundaries.** A signal can deliver a node reference that has already been freed, or an object of an unexpected type. Check `is_instance_valid()` and the type before you touch it, so a dangling reference fails as a no-op instead of a crash.
- **Keep gameplay-rule timers private.** Cooldowns and invincibility frames *are* rules. Expose them only through methods (`receive_hit()`), never as public fields, so external code — or a mod editing the scene — cannot reset a timer to fire faster than intended and bypass the rule the component exists to enforce.
- **Range-validate every exported number with `@export_range`.** Bounding a value at the source stops a hand-edited `.tscn` (or a careless designer) from configuring negative damage that secretly heals, or an absurd value that overflows arithmetic and breaks balance.
- **Hold cross-entity references weakly.** When a component remembers a node it does *not* own — the last attacker, the current target — store a `weakref()`. A strong reference would keep a freed enemy alive in memory just because a corpse remembered who killed it, leaking nodes over a long session. The `HurtboxComponent` below demonstrates this.

### Step 3 — Implement Common Components

The table below summarizes the five canonical components. Each is detailed with full source in the sections that follow.

| Component | Purpose | Key Signals | Guards & validation |
|---|---|---|---|
| `HealthComponent` | Tracks current and max HP, applies damage and healing | `health_changed(current, maximum)`, `died` | Rejects non-positive damage/heal; clamps HP to `[0, max]`; emits `died` exactly once |
| `HitboxComponent` | Detects overlapping hurtboxes and deals damage | `hit(target_hurtbox)` | Type-checks the overlapping area; enforces a private cooldown; passes itself as the damage source |
| `HurtboxComponent` | Receives hits, routes damage to `HealthComponent` | `hurt(damage_amount)` | Rejects non-positive damage; enforces private i-frames; stores the attacker as a `weakref` |
| `InteractableComponent` | Marks an entity as interactable and fires on player overlap | `interacted(interactor)` | Validates the interactor; enforces one-shot vs. repeatable use |
| `StateMachineComponent` | Delegates `_process`/`_physics_process` to child state nodes | `state_changed(from, to)` | Rejects transitions to unknown states; only indexes children that implement the state contract |

#### HealthComponent

Attach to any entity with a hit-point pool. It owns the damage/heal *rules*; other nodes react to its signals rather than mutating its fields.

```gdscript
class_name HealthComponent
extends Node

## Emitted whenever current HP changes, so UI and audio can react without
## reading this component's private state every frame.
signal health_changed(current_health: int, maximum_health: int)

## Emitted exactly once when HP reaches zero. Listeners handle the consequences
## (despawn, ragdoll, game over) — this component does not decide them.
signal died

## Maximum hit points. Range-bounded so the Inspector cannot configure a
## non-positive pool that would make the entity dead on spawn.
@export_range(1, 100000) var max_health: int = 100

## Starting hit points. Clamped to max_health in _ready() so a designer cannot
## start an entity above its own cap.
@export_range(0, 100000) var starting_health: int = 100

var _current_health: int = 0
var _is_dead: bool = false

func _ready() -> void:
    _current_health = clampi(starting_health, 0, max_health)
    health_changed.emit(_current_health, max_health)

## Apply damage. Non-positive amounts are rejected so a malformed hit cannot
## secretly heal the target, and a dead entity ignores further damage.
func take_damage(amount: int) -> void:
    if _is_dead:
        return
    if amount <= 0:
        push_warning("HealthComponent.take_damage ignored non-positive amount: %d" % amount)
        return
    _set_health(_current_health - amount)

## Restore hit points. Non-positive amounts are rejected so a malformed heal
## cannot be used to deal damage.
func heal(amount: int) -> void:
    if _is_dead:
        return
    if amount <= 0:
        push_warning("HealthComponent.heal ignored non-positive amount: %d" % amount)
        return
    _set_health(_current_health + amount)

func get_current_health() -> int:
    return _current_health

func get_max_health() -> int:
    return max_health

func is_dead() -> bool:
    return _is_dead

## Single chokepoint for every HP change, so clamping and the death edge are
## enforced in one place no matter who calls take_damage()/heal().
func _set_health(new_value: int) -> void:
    var clamped_value: int = clampi(new_value, 0, max_health)
    if clamped_value == _current_health:
        return
    _current_health = clamped_value
    health_changed.emit(_current_health, max_health)
    if _current_health == 0 and not _is_dead:
        _is_dead = true
        died.emit()
```

#### HitboxComponent

Attach to any entity that deals contact damage. Configure `damage` and `cooldown_duration` in the Inspector.

```gdscript
class_name HitboxComponent
extends Area2D

## Emitted after a successful hit, so other systems (VFX, audio, score) can react
## without this component needing to know they exist.
signal hit(target_hurtbox: HurtboxComponent)

## Damage dealt to the target hurtbox on contact. Range-bounded so the Inspector
## cannot configure negative damage (which would heal) or an absurd one-shot value.
@export_range(0, 1000) var damage: int = 10

## Minimum seconds between successive hits (0 = no cooldown). Prevents a single,
## sustained overlap from registering many hits per second while the areas touch.
@export_range(0.0, 10.0) var cooldown_duration: float = 0.5

## Physics layers this hitbox will inspect for hurtboxes. Exposed so designers can
## scope friendly fire in the Inspector instead of hardcoding a mask.
@export_flags_2d_physics var target_mask: int = 1

var _on_cooldown: bool = false
var _cooldown_timer: Timer

func _ready() -> void:
    collision_mask = target_mask
    _cooldown_timer = Timer.new()
    _cooldown_timer.one_shot = true
    _cooldown_timer.timeout.connect(_on_cooldown_timeout)
    add_child(_cooldown_timer)
    area_entered.connect(_on_area_entered)

func _exit_tree() -> void:
    # These targets (this node's own signal and a child timer) are freed
    # automatically, but disconnecting explicitly keeps the connection ownership
    # documented and stays correct if this hitbox is later rewired to emit into a
    # longer-lived listener such as an event bus.
    if area_entered.is_connected(_on_area_entered):
        area_entered.disconnect(_on_area_entered)
    if is_instance_valid(_cooldown_timer) and _cooldown_timer.timeout.is_connected(_on_cooldown_timeout):
        _cooldown_timer.timeout.disconnect(_on_cooldown_timeout)

func _on_area_entered(area: Area2D) -> void:
    if _on_cooldown:
        return
    # Reject anything that is not a hurtbox before touching it: an Area2D from an
    # unrelated system (a pickup, a region trigger) must never be treated as a
    # damage target. `as` yields null on a type mismatch, so this both type-checks
    # and casts in one step.
    var hurtbox: HurtboxComponent = area as HurtboxComponent
    if hurtbox == null or not is_instance_valid(hurtbox):
        return

    hit.emit(hurtbox)
    # Pass `self` as the damage source so the hurtbox can credit/knockback away
    # from this attacker without a global lookup.
    hurtbox.receive_hit(damage, self)

    if cooldown_duration > 0.0:
        _on_cooldown = true
        _cooldown_timer.start(cooldown_duration)

func _on_cooldown_timeout() -> void:
    _on_cooldown = false
```

#### HurtboxComponent

Attach to any entity that can take damage. Wire it to a sibling `HealthComponent` via `@export` in the Inspector.

```gdscript
class_name HurtboxComponent
extends Area2D

## Emitted before damage is forwarded, so feedback systems (hit-flash, knockback,
## hit-stop) can react even on entities that have no HealthComponent at all.
signal hurt(damage_amount: int)

## The HealthComponent on the same entity. Optional on purpose: a destructible
## prop may want hurt feedback without a health pool, so null is a valid state.
@export var health_component: HealthComponent

## Invincibility-frame duration in seconds (0 = none). Stops rapid multi-hits from
## chaining into an unavoidable death during what should be a single damage event.
@export_range(0.0, 10.0) var invincibility_duration: float = 0.0

var _invincible: bool = false
var _iframes_timer: Timer

# Stored weakly: we want to remember who last hit us (for kill credit or knockback
# direction) without keeping that attacker alive in memory after it is freed.
var _last_attacker_ref: WeakRef = null

func _ready() -> void:
    _iframes_timer = Timer.new()
    _iframes_timer.one_shot = true
    _iframes_timer.timeout.connect(_on_iframes_timeout)
    add_child(_iframes_timer)

func _exit_tree() -> void:
    if is_instance_valid(_iframes_timer) and _iframes_timer.timeout.is_connected(_on_iframes_timeout):
        _iframes_timer.timeout.disconnect(_on_iframes_timeout)

## Public entry point called by a HitboxComponent. Guards against non-positive
## damage and active i-frames so a caller cannot bypass the rules this component
## exists to enforce. `source` is optional so non-combat callers still work.
func receive_hit(damage: int, source: Node = null) -> void:
    if _invincible:
        return
    if damage <= 0:
        push_warning("HurtboxComponent.receive_hit ignored non-positive damage: %d" % damage)
        return

    if source != null and is_instance_valid(source):
        _last_attacker_ref = weakref(source)

    hurt.emit(damage)

    if health_component != null and is_instance_valid(health_component):
        health_component.take_damage(damage)

    if invincibility_duration > 0.0:
        _invincible = true
        _iframes_timer.start(invincibility_duration)

func is_invincible() -> bool:
    return _invincible

## Returns the last attacker, or null if there was none or it has since been freed.
func get_last_attacker() -> Node:
    if _last_attacker_ref == null:
        return null
    var attacker: Object = _last_attacker_ref.get_ref()
    if attacker is Node:
        return attacker as Node
    return null

func _on_iframes_timeout() -> void:
    _invincible = false
```

#### InteractableComponent

Attach to anything the player can use — a door, a lever, a pickup. An interaction controller calls `interact()` when the player presses the use key while overlapping; the component decides whether that interaction is valid.

```gdscript
class_name InteractableComponent
extends Area2D

## Emitted when a valid interactor activates this entity. The interactor is passed
## so listeners can branch on who interacted (player vs. NPC) without a global lookup.
signal interacted(interactor: Node)

## Human-readable prompt shown by UI ("Open", "Talk", "Pick up"). Exported so the
## same component scene is reused for many interactions purely via the Inspector.
@export var prompt_text: String = "Interact"

## Only bodies on these layers may interact. Defaults to the player layer so a
## stray physics body cannot trigger a story event.
@export_flags_2d_physics var interactor_mask: int = 1

## Whether this can be used more than once. One-shot doors, levers, and pickups set
## this false to prevent duplicate rewards.
@export var repeatable: bool = true

var _used: bool = false

func _ready() -> void:
    collision_mask = interactor_mask

## Called by an interaction controller. Validates the interactor and the one-shot
## state before firing, and reports whether the interaction was accepted so the
## caller can play a "denied" sound on false.
func interact(interactor: Node) -> bool:
    if interactor == null or not is_instance_valid(interactor):
        push_warning("InteractableComponent.interact called with an invalid interactor.")
        return false
    if _used and not repeatable:
        return false
    _used = true
    interacted.emit(interactor)
    return true

func get_prompt_text() -> String:
    return prompt_text

## Lets a one-shot interactable be reset by external systems (e.g. a checkpoint
## reload) without rebuilding the node.
func reset() -> void:
    _used = false
```

#### StateMachineComponent

Attach as the parent of a set of *state* nodes. Each state node implements `enter()` / `exit()` and optionally `update(delta)` / `physics_update(delta)`. The machine forwards the engine callbacks to whichever state is active and validates every transition.

```gdscript
class_name StateMachineComponent
extends Node

## Emitted on every accepted transition, so debug overlays and UI subscribe
## instead of polling the current state each frame.
signal state_changed(from_state: StringName, to_state: StringName)

## The state node entered when the machine starts. Exported so a designer chooses
## the initial state per entity without editing code.
@export var initial_state: Node

var _current_state: Node = null
var _states: Dictionary = {}

func _ready() -> void:
    # Index direct children that satisfy the state contract exactly once, so
    # transitions become O(1) name lookups instead of get_node() string paths
    # scattered through gameplay code. Children that do not implement the contract
    # (sprites, timers) are ignored rather than misfiring as states.
    for child in get_children():
        if child.has_method("enter") and child.has_method("exit"):
            _states[child.name] = child
    if initial_state != null and is_instance_valid(initial_state):
        _transition_to(initial_state.name)

func _process(delta: float) -> void:
    if _current_state != null and _current_state.has_method("update"):
        _current_state.update(delta)

func _physics_process(delta: float) -> void:
    if _current_state != null and _current_state.has_method("physics_update"):
        _current_state.physics_update(delta)

## Request a transition by state name. Rejecting unknown names makes a typo fail
## loudly in the console instead of silently leaving the entity in a dead state.
func transition_to(target_name: StringName) -> bool:
    if not _states.has(target_name):
        push_warning("StateMachineComponent has no state named '%s'." % target_name)
        return false
    return _transition_to(target_name)

func get_current_state_name() -> StringName:
    return _current_state.name if _current_state != null else &""

func _transition_to(target_name: StringName) -> bool:
    var next_state: Node = _states.get(target_name)
    if next_state == null or not is_instance_valid(next_state):
        return false
    var previous_name: StringName = _current_state.name if _current_state != null else &""
    if _current_state != null and _current_state.has_method("exit"):
        _current_state.exit()
    _current_state = next_state
    if _current_state.has_method("enter"):
        _current_state.enter()
    state_changed.emit(previous_name, target_name)
    return true
```

### Step 4 — Implement ComponentUtils for Lookups

A static utility that finds a sibling component by type without hardcoding node names or paths. This replaces every `get_parent().get_node("Sibling")` call.

#### GDScript (`component_utils.gd`)

```gdscript
class_name ComponentUtils
extends RefCounted

## Returns the first child of `owner` that is an instance of `component_type`,
## or null. Validates the owner so a bad call surfaces as a warning instead of
## a silent crash deep in gameplay code.
static func get_component(owner: Node, component_type: Script) -> Node:
    if owner == null or not is_instance_valid(owner):
        push_warning("ComponentUtils.get_component called with an invalid owner.")
        return null

    for child in owner.get_children():
        if child is component_type:
            return child
    return null

# True when `owner` has at least one child of `component_type`. Useful for
# feature-detecting a capability before relying on it.
static func has_component(owner: Node, component_type: Script) -> bool:
    return get_component(owner, component_type) != null
```

Usage from an entity script:

```gdscript
func _ready() -> void:
    var health: HealthComponent = ComponentUtils.get_component(self, HealthComponent) as HealthComponent
    if health != null and is_instance_valid(health):
        health.take_damage(5)
```

#### C# (`ComponentUtils.cs`)

The C# components mirror the GDScript API one-to-one (`TakeDamage` ↔ `take_damage`), so a project can use either language. These snippets assume the project has nullable reference types enabled (`<Nullable>enable</Nullable>`).

```csharp
#nullable enable
using Godot;

public static class ComponentUtils
{
    // Returns the first child of `owner` assignable to T, or null. Validates the
    // owner so a bad call surfaces as a warning instead of a NullReferenceException.
    public static T? GetComponent<T>(Node owner) where T : Node
    {
        if (owner == null || !GodotObject.IsInstanceValid(owner))
        {
            GD.PushWarning("ComponentUtils.GetComponent called with an invalid owner.");
            return null;
        }

        foreach (Node child in owner.GetChildren())
        {
            if (child is T typedChild)
            {
                return typedChild;
            }
        }

        return null;
    }

    public static bool HasComponent<T>(Node owner) where T : Node
    {
        return GetComponent<T>(owner) != null;
    }
}
```

#### C# HealthComponent

```csharp
#nullable enable
using Godot;

public partial class HealthComponent : Node
{
    [Signal]
    public delegate void HealthChangedEventHandler(int currentHealth, int maximumHealth);

    [Signal]
    public delegate void DiedEventHandler();

    [Export(PropertyHint.Range, "1,100000,1")]
    public int MaxHealth { get; set; } = 100;

    [Export(PropertyHint.Range, "0,100000,1")]
    public int StartingHealth { get; set; } = 100;

    private int _currentHealth;
    private bool _isDead;

    public override void _Ready()
    {
        _currentHealth = Mathf.Clamp(StartingHealth, 0, MaxHealth);
        EmitSignal(SignalName.HealthChanged, _currentHealth, MaxHealth);
    }

    public void TakeDamage(int amount)
    {
        if (_isDead)
        {
            return;
        }
        if (amount <= 0)
        {
            GD.PushWarning($"HealthComponent.TakeDamage ignored non-positive amount: {amount}");
            return;
        }
        SetHealth(_currentHealth - amount);
    }

    public void Heal(int amount)
    {
        if (_isDead)
        {
            return;
        }
        if (amount <= 0)
        {
            GD.PushWarning($"HealthComponent.Heal ignored non-positive amount: {amount}");
            return;
        }
        SetHealth(_currentHealth + amount);
    }

    public int CurrentHealth => _currentHealth;
    public bool IsDead => _isDead;

    private void SetHealth(int newValue)
    {
        int clamped = Mathf.Clamp(newValue, 0, MaxHealth);
        if (clamped == _currentHealth)
        {
            return;
        }
        _currentHealth = clamped;
        EmitSignal(SignalName.HealthChanged, _currentHealth, MaxHealth);
        if (_currentHealth == 0 && !_isDead)
        {
            _isDead = true;
            EmitSignal(SignalName.Died);
        }
    }
}
```

#### C# Usage

```csharp
#nullable enable
using Godot;

public override void _Ready()
{
    HealthComponent? health = ComponentUtils.GetComponent<HealthComponent>(this);
    if (health != null && GodotObject.IsInstanceValid(health))
    {
        health.TakeDamage(5);
    }
}
```

### Step 5 — Assemble Entity Scenes

Lay out each scene so the components are children of the entity root:

```
Player (CharacterBody2D)
├── HealthComponent
├── HurtboxComponent (Area2D)   ← health_component exported to the sibling HealthComponent
│   └── CollisionShape2D
└── Sprite2D

Enemy (CharacterBody2D)
├── HealthComponent
├── HitboxComponent (Area2D)    ← deals contact damage on overlap
│   └── CollisionShape2D
└── Sprite2D
```

The player script owns *presentation and consequences*; it reacts to component signals instead of reaching into component internals:

```gdscript
# player.gd
extends CharacterBody2D

@onready var _health: HealthComponent = ComponentUtils.get_component(self, HealthComponent) as HealthComponent
@onready var _hurtbox: HurtboxComponent = ComponentUtils.get_component(self, HurtboxComponent) as HurtboxComponent

func _ready() -> void:
    if _health != null:
        _health.health_changed.connect(_on_health_changed)
        _health.died.connect(_on_died)
    if _hurtbox != null:
        _hurtbox.hurt.connect(_on_hurt)

func _on_health_changed(current_health: int, maximum_health: int) -> void:
    # The HealthComponent owns the rules; the player only forwards to the HUD.
    print("Player HP: %d / %d" % [current_health, maximum_health])

func _on_hurt(damage_amount: int) -> void:
    # Feedback that should fire even before HP is applied (flash, hit-stop).
    print("Player took %d damage" % damage_amount)

func _on_died() -> void:
    set_physics_process(false)
    queue_free()
```

The enemy script is symmetric: it carries a `HitboxComponent` for contact damage and its own `HealthComponent`, and it reacts to their signals:

```gdscript
# enemy.gd
extends CharacterBody2D

@onready var _health: HealthComponent = ComponentUtils.get_component(self, HealthComponent) as HealthComponent
@onready var _hitbox: HitboxComponent = ComponentUtils.get_component(self, HitboxComponent) as HitboxComponent

func _ready() -> void:
    if _hitbox != null:
        _hitbox.hit.connect(_on_hit_landed)
    if _health != null:
        _health.died.connect(_on_died)

func _on_hit_landed(target_hurtbox: HurtboxComponent) -> void:
    if is_instance_valid(target_hurtbox):
        print("Enemy struck %s" % target_hurtbox.get_parent().name)

func _on_died() -> void:
    queue_free()
```

**Resulting hit flow.** When the enemy's `HitboxComponent` overlaps the player's `HurtboxComponent`: the hitbox type-checks the area, emits `hit`, and calls `receive_hit(damage, self)`; the hurtbox rejects non-positive damage, records the attacker weakly, emits `hurt`, forwards the damage to the exported `HealthComponent`, and starts its i-frames; the health component clamps the new value and, if it reaches zero, emits `died` once; the player script handles `died` by freeing itself. No script reached across the tree by node path, and every component could be unit-tested by dropping it alone into a minimal scene.

## Examples

### Minimal Test Scene for HealthComponent

1. Create a new scene with a `Node` root named `TestEntity`.
2. Instance `HealthComponent` as a child.
3. Attach a script to the root:

```gdscript
extends Node

@onready var _health: HealthComponent = $HealthComponent

func _ready() -> void:
    _health.health_changed.connect(func(c, m): print("HP: %d/%d" % [c, m]))
    _health.died.connect(func(): print("Entity died"))
    _health.take_damage(30)
    _health.take_damage(80)
    _health.heal(-5)  # Should print a warning and be ignored
```

4. Run the scene. Expected console output:

```
HP: 100/100
HP: 70/100
HP: 0/100
Entity died
WARNING: HealthComponent.heal ignored non-positive amount: -5
```

## Pitfalls

- **Never use `get_parent().get_node("SiblingName")` to find a component.** This hardcodes the sibling's name and tree position. If someone renames or reparents the node, the lookup silently returns null and the component breaks at runtime with no compile-time error. Always use `ComponentUtils.get_component(owner, ComponentType)` or a typed `@export` reference wired in the Inspector.

- **Never expose cooldown or i-frame timers as public fields.** Cooldowns and invincibility frames *are* gameplay rules. If external code (or a mod editing the scene) can reset `_on_cooldown = false` or `_invincible = false` directly, it can bypass the rule the component exists to enforce. Keep them private and expose only the intended entry methods (`receive_hit()`, `take_damage()`).

- **Never store a strong reference to a node you do not own.** If a `HurtboxComponent` stores `var _last_attacker: Node` (strong reference) and the attacker is freed, the attacker stays alive in memory because the hurtbox is still holding it. Over a long session this leaks nodes. Always use `weakref()` for cross-entity references you do not own.

- **Never skip `is_instance_valid()` on signal payloads.** A signal can deliver a node reference that has already been freed (e.g. the attacker was `queue_free()`d in the same frame). Touching a freed instance crashes. Always check `is_instance_valid()` before accessing any node received via signal or parameter.

- **Never put configuration in constants instead of `@export`.** If `damage` is `const DAMAGE = 10`, every entity that instances the component deals exactly 10 damage. Designers cannot tune it, and you cannot reuse the same component scene with different values. Always use `@export_range` so values are Inspector-configurable and range-bounded.

- **Never forget to disconnect from longer-lived objects in `_exit_tree()`.** Connections to autoloads, parents, or a shared event bus outlive the component. If the component is freed but the connection remains, the callable fires on freed state and crashes. Always disconnect in `_exit_tree()`.

- **Never let a `StateMachineComponent` accept unknown state names silently.** If `transition_to("IdleTypo")` silently does nothing, the entity is stuck in a dead state with no feedback. The implementation above uses `push_warning()` to make typos loud.

- **Never bundle multiple responsibilities into one component.** The moment the name needs an "And" (`HealthAndShieldAndRegenComponent`), it cannot be reused by an entity that wants only one of those parts. Split it into separate components that communicate via signals.

## Verification

A component system is healthy when each component could be lifted into another project unchanged. Check that:

- [ ] Each component is saved as its own `.tscn` scene and reused by instancing
- [ ] Components emit signals for events and use typed `@export` references for declared dependencies — no `get_parent().get_node("Sibling")` string lookups anywhere
- [ ] All tuneable numbers use `@export_range` (or `@export_flags_*`) so out-of-bounds values cannot be configured
- [ ] Signal connections to longer-lived objects are disconnected in `_exit_tree()`
- [ ] Public methods validate their inputs (non-positive damage/heal rejected, invalid references treated as no-ops)
- [ ] Cross-entity references the component does not own are stored as `weakref()`
- [ ] Each component can be exercised by attaching it to a minimal test scene in isolation, with no dependency on a specific parent type

### Quick Verification Commands (PowerShell)

```powershell
# Verify no hardcoded sibling lookups remain in component scripts
Select-String -Path .\components\*.gd -Pattern 'get_parent\(\)\.get_node' -SimpleMatch
# Expected: no matches. If any match appears, refactor to use ComponentUtils or @export.

# Verify all exported numbers use range bounds
Select-String -Path .\components\*.gd -Pattern '@export var' | Where-Object { $_.Line -match 'var (damage|health|cooldown|duration|speed)' -and $_.Line -notmatch '@export_range' }
# Expected: no matches. Every numeric export should use @export_range.

# Verify _exit_tree is defined in every component that connects signals
Get-ChildItem .\components\*.gd | ForEach-Object { $has = Select-String -Path $_.FullName -Pattern '_exit_tree'; if (-not $has) { Write-Host "Missing _exit_tree: $($_.Name)" } }
# Expected: no "Missing _exit_tree" lines for components that connect to longer-lived objects.

# Verify weakref usage for cross-entity references
Select-String -Path .\components\*.gd -Pattern 'weakref'
# Expected: at least one match in hurtbox_component.gd
```

## Related Skills

- **scene-organization** for scene tree composition
- **event-bus** for decoupled component communication
- **resource-pattern** for data-driven component configuration
- **physics-system** for Area2D/3D overlap detection and collision shapes
- **memory-management** for component lifecycle handling
