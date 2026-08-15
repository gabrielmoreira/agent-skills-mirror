---
name: godot-scene-organization
version: 1.1.1
description: "Organizes Godot 4.4+ scene trees around one-concept scenes, composition versus inherited variants, split-versus-keep heuristics, and signals-up / calls-down / EventBus-sideways communication. Use when choosing hierarchy, extracting a sub-scene, or wiring HUD and level instances. Not a component-class implementation chair (godot-component-system) and not for throwaway prototype scenes."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Overview

Scenes are building blocks. Each scene should encapsulate exactly one concept — a player, an enemy, a health bar, a weapon — for one practical reason: a scene that owns a single concept can be understood on its own, dropped into another scene without modification, and replaced without breaking its neighbors. The moment a scene owns two concepts, all three of those properties weaken at once.

> One scene = one responsibility. If you cannot name a scene in two words or fewer, it is probably doing too much — and the parts you would name separately are the sub-scenes waiting to be extracted.

## When to Use

- You are laying out a Godot **4.4 LTS** (or newer) scene tree and need to choose between composition and inheritance. The choice locks in how reusable and how coupled the entity will be, so it is worth making deliberately up front rather than discovering the cost later.
- You are deciding whether a growing scene should be split into sub-scenes. Splitting pays off in reuse, isolated testing, and fewer merge conflicts; it costs wiring. The decision depends on which side is heavier for *this* scene.
- You are organizing a node hierarchy and want the communication paths — signals up, calls down, EventBus sideways — to be obvious to the next person who opens the scene.

### Do Not Use

- **On throwaway prototypes.** When you are validating an idea you will delete next week, the wiring overhead of many small scenes buys you nothing. Keep it in one scene until the idea survives.
- **When the nodes are genuinely one unit.** If two nodes only ever exist together and a split would force you to re-create a direct reference through three relayed signals, the split adds indirection without adding independence. Keep them together until a second use site appears.
- **When variants share identical structure.** If two scenes differ only by a handful of exported values and have the same node layout, reach for inheritance rather than hand-composing each one — composition here is just copy-paste with extra steps.

### Hard Rules

- **Keep authoritative state out of autoloads.** An autoloaded singleton (like an EventBus) is global, mutable, and reachable from every script with zero encapsulation. That is fine for fire-and-forget events, but anything that decides *authority* — score that affects rewards, server-validated state in a networked game, anti-cheat checks — should live behind a class that owns and validates it, not in a public `var` any script can overwrite. The danger is less malice than accidental, untraceable mutation from across the codebase.
- **Use typed node access, and know the language difference.** Prefer a typed reference (`@onready var health: HealthComponent = $HealthComponent`) over an untyped lookup, so a missing or wrong-typed node fails immediately and obviously. Note the GDScript/C# split: C# has the generic `GetNode<T>()` / `GetNodeOrNull<T>()` that return a typed result (or `null`) directly; GDScript has **no** `get_node_or_null<T>()` generic — you write `get_node_or_null("Path") as Type` and check for `null`. `get_node_or_null()` is not deprecated; it is the correct tool when a node may legitimately be absent.

## Prerequisites

- Godot 4.4 LTS or newer installed on Windows (PowerShell is the primary shell).
- A project with at least one scene to organize. If starting from scratch, create the project first:
  ```powershell
  # From the project root (where project.godot lives)
  godot --headless --editor  # Opens the editor to create initial scenes
  ```
- For C# projects, the .NET SDK (8.0+) and the Godot .NET NuGet packages must be restored:
  ```powershell
  dotnet restore
  ```

## Procedure

### 1. Choose Composition vs Inheritance

Composition is the default because it lets unrelated entity types share *behavior* without sharing a *class hierarchy*. A crate, a boss, and a player have nothing in common as types, yet all three can take damage — so damage belongs in a component they each include, not in a base class they would each have to inherit from.

| Scenario | Pattern | Why |
|---|---|---|
| You would duplicate an entire scene and change only a few exported values | **Inheritance** | The variants are one shape; a base scene keeps that shape defined in a single place. |
| You want to mix and match a subset of nodes across unrelated entity types | **Composition** | The behavior is shared but the types are not, so a shared class hierarchy would be a poor fit. |

**Good inheritance candidates:**
- `Enemy` → `Orc`, `Goblin` — identical bones (Sprite2D, CollisionShape2D, HealthComponent, AI), differing only in stats and art.
- `Weapon` → `Sword`, `Bow` — same slot-attachment logic, differing animations and damage type.
- `Pickup` → `HealthPickup`, `AmmoPickup` — same Area2D + CollisionShape2D + animation, differing effect on collection.

**Trade-off:** every inherited scene is bound to the base's exact tree, so a structural change to the base ripples to all of them. That is a feature when the variants really are the same shape (the change *should* reach all of them) and a liability the moment one variant needs a different layout.

### 2. Build Composed Scenes from Reusable Parts

#### Player Scene — Composed from Reusable Parts

```
Player (CharacterBody2D)
├── Sprite2D
├── CollisionShape2D
├── HealthComponent
├── HitboxComponent
├── StateMachine
└── AnimationPlayer
```

`HealthComponent`, `HitboxComponent`, and `StateMachine` are separate `.tscn` files instantiated as child scenes. Any entity that needs health — enemy, destructible crate, boss — includes `HealthComponent` and gets the exact same, already-tested behavior. Fix a bug in the component once and every entity inherits the fix, with no base class in sight.

#### HealthComponent — Full Example (GDScript, Godot 4.4)

The component below validates its inputs, refuses nonsensical operations (negative damage, healing the dead), and surfaces setup mistakes in the editor instead of at runtime. The `@tool` annotation exists for exactly one reason — to run `_get_configuration_warnings()` so a misconfigured `max_health` is flagged in the editor — and every line of gameplay logic is explicitly skipped when the script runs there.

```gdscript
# health_component.gd
@tool
class_name HealthComponent
extends Node

## Emitted whenever health changes. Both values are passed so a listener can
## react to the delta (flash red on a drop, green on a gain) without having to
## cache the previous value itself.
signal health_changed(old_value: int, new_value: int)

## Emitted exactly once, the moment health first reaches zero. Treat it as a
## one-shot "this entity is now dead": heal() deliberately will not revive, so
## the signal cannot fire a second time without an explicit reset.
signal died

@export_range(1, 100000) var max_health: int = 100:
    set(value):
        # Clamp on assignment so the component can never be configured into an
        # already-dead state (max_health <= 0).
        max_health = maxi(1, value)
        if Engine.is_editor_hint():
            update_configuration_warnings()

## Hit points restored per second. Left at 0 the node never starts _process, so
## an entity whose health never regenerates costs nothing per frame.
@export_range(0.0, 1000.0) var auto_heal_rate: float = 0.0

var _current_health: int
var _heal_accumulator: float = 0.0

func _ready() -> void:
    # A @tool script also runs in the editor; its only job there is to emit
    # configuration warnings, so bail before touching any gameplay state.
    if Engine.is_editor_hint():
        return
    _current_health = max_health
    set_process(auto_heal_rate > 0.0)

func _process(delta: float) -> void:
    if _current_health <= 0 or _current_health >= max_health:
        return
    # Accumulate fractional healing across frames. Without this, a rate like
    # 10 hp/s at 60 fps computes int(10 * 0.016) == 0 every frame and never
    # heals at all — a silent, easy-to-miss bug.
    _heal_accumulator += auto_heal_rate * delta
    var whole_points := int(_heal_accumulator)
    if whole_points > 0:
        _heal_accumulator -= float(whole_points)
        heal(whole_points)

func take_damage(amount: int) -> void:
    # Negative "damage" would silently heal the entity. Reject it loudly in debug
    # builds so the miscall is found, then no-op safely in a release build.
    assert(amount >= 0, "take_damage() expects a non-negative amount; use heal() to restore health")
    if amount <= 0 or _current_health <= 0:
        return
    var old_health := _current_health
    _current_health = maxi(0, _current_health - amount)
    health_changed.emit(old_health, _current_health)
    if _current_health == 0:
        died.emit()

func heal(amount: int) -> void:
    assert(amount >= 0, "heal() expects a non-negative amount; use take_damage() to remove health")
    # Refuse to heal a dead entity. Resurrection should be a deliberate, explicit
    # act (reset health, re-enable nodes), never a side effect of a stray heal
    # tick arriving the frame after death.
    if amount <= 0 or _current_health <= 0:
        return
    var old_health := _current_health
    _current_health = mini(max_health, _current_health + amount)
    if _current_health != old_health:
        health_changed.emit(old_health, _current_health)

func is_alive() -> bool:
    return _current_health > 0

func get_health() -> int:
    return _current_health

func get_health_fraction() -> float:
    # A freshly spawned HUD needs the current ratio to size its health bar; the
    # maxi(1, max_health) guard keeps this divide safe even if a future refactor
    # loosens the clamp on max_health.
    return float(_current_health) / float(maxi(1, max_health))

func _get_configuration_warnings() -> PackedStringArray:
    var warnings: PackedStringArray = []
    if max_health <= 0:
        warnings.append("max_health must be greater than 0, otherwise the entity spawns dead.")
    return warnings
```

#### HealthComponent — Full Example (C#, Godot 4.4)

```csharp
// HealthComponent.cs
using System;
using Godot;

[GlobalClass]
[Tool]
public partial class HealthComponent : Node
{
    /// <summary>Emitted on every health change, carrying both values so listeners can react to the delta.</summary>
    [Signal]
    public delegate void HealthChangedEventHandler(int oldValue, int newValue);

    /// <summary>Emitted once, the moment health first reaches zero.</summary>
    [Signal]
    public delegate void DiedEventHandler();

    private int _maxHealth = 100;

    [Export(PropertyHint.Range, "1,100000")]
    public int MaxHealth
    {
        get => _maxHealth;
        set
        {
            // Clamp so the component can never be configured into a dead state.
            _maxHealth = Mathf.Max(1, value);
            if (Engine.IsEditorHint())
                UpdateConfigurationWarnings();
        }
    }

    /// <summary>Hit points restored per second; 0 disables per-frame processing entirely.</summary>
    [Export(PropertyHint.Range, "0,1000")]
    public float AutoHealRate { get; set; } = 0f;

    public int CurrentHealth { get; private set; }

    private float _healAccumulator;

    public override void _Ready()
    {
        // The editor instance exists only to surface warnings — run no gameplay logic there.
        if (Engine.IsEditorHint())
            return;
        CurrentHealth = MaxHealth;
        SetProcess(AutoHealRate > 0f);
    }

    public override void _Process(double delta)
    {
        if (CurrentHealth <= 0 || CurrentHealth >= MaxHealth)
            return;
        // Accumulate fractional healing so small rates are not lost to int truncation each frame.
        _healAccumulator += AutoHealRate * (float)delta;
        int wholePoints = (int)_healAccumulator;
        if (wholePoints > 0)
        {
            _healAccumulator -= wholePoints;
            Heal(wholePoints);
        }
    }

    public void TakeDamage(int amount)
    {
        // Negative damage would heal — treat it as a programming error, not a quiet no-op.
        if (amount < 0)
            throw new ArgumentOutOfRangeException(nameof(amount), "Damage must be non-negative; use Heal() to restore health.");
        if (amount == 0 || CurrentHealth <= 0)
            return;
        int oldHealth = CurrentHealth;
        CurrentHealth = Mathf.Max(0, CurrentHealth - amount);
        EmitSignal(SignalName.HealthChanged, oldHealth, CurrentHealth);
        if (CurrentHealth == 0)
            EmitSignal(SignalName.Died);
    }

    public void Heal(int amount)
    {
        if (amount < 0)
            throw new ArgumentOutOfRangeException(nameof(amount), "Heal amount must be non-negative; use TakeDamage() to remove health.");
        // Never revive a dead entity through healing — resurrection must be explicit.
        if (amount == 0 || CurrentHealth <= 0)
            return;
        int oldHealth = CurrentHealth;
        CurrentHealth = Mathf.Min(MaxHealth, CurrentHealth + amount);
        if (CurrentHealth != oldHealth)
            EmitSignal(SignalName.HealthChanged, oldHealth, CurrentHealth);
    }

    public bool IsAlive() => CurrentHealth > 0;

    public float GetHealthFraction() => (float)CurrentHealth / Mathf.Max(1, MaxHealth);

    public override string[] _GetConfigurationWarnings()
    {
        if (MaxHealth <= 0)
            return new[] { "MaxHealth must be greater than 0, otherwise the entity spawns dead." };
        return Array.Empty<string>();
    }
}
```

### 3. Apply Scene Splitting Rules

These are heuristics, not laws — each one is really a question about whether independence is worth its wiring cost.

#### Split a scene when:

- **Reuse** — the sub-scene is needed in more than one parent. A second use site is the clearest possible signal that the part is its own concept.
- **Complexity** — the scene has grown past roughly 15 nodes or has started mixing concerns (movement *and* inventory *and* dialogue). The number is a proxy; the real trigger is "I can no longer hold this scene in my head."
- **Independence** — the part can be tested, previewed, or edited without opening its parent. If that is already true, a split just makes the boundary explicit.
- **Team** — separate `.tscn` files let two people edit related features without colliding in the same scene file, where Godot's text merges are painful.

#### Keep nodes together when:

- They are **tightly coupled** — a split would force you to relay through signals what a single direct reference already handles cleanly. You would be paying in indirection for independence you do not need.
- The grouping is **small and single-use** — a two-node helper living in exactly one scene does not earn its own file; the file is overhead with no reuse to amortize it.
- The split would be **all cost, no benefit** — if a parent must wire three signals just to tell a child "you were hit," the boundary is in the wrong place. Move it to where the coupling is naturally thin.

### 4. Wire Node Communication

The three patterns below map directly onto the tree's shape, and that is the point: when communication follows the hierarchy, you can predict who talks to whom just by looking at the tree.

```
        [Parent]
        /      \
  [Child A]  [Child B]
       \
     [Child C]
```

#### Pattern 1: Signals Travel Up (child → parent)

A child emits a signal and stays ignorant of who listens. This is what keeps the child reusable: `HealthComponent` can announce `died` without knowing whether a player, an enemy, or a crate is on the other end.

**GDScript:**
```gdscript
# player.gd — the parent listens; the child HealthComponent stays context-free.
extends CharacterBody2D

@onready var _health: HealthComponent = $HealthComponent

func _ready() -> void:
    # A direct @onready reference is stable across tree edits. A chain such as
    # get_parent().get_parent() silently breaks the instant a node is reparented.
    _health.died.connect(_on_health_died)

func _on_health_died() -> void:
    # The player owns what "died" means — stop control, play a death animation —
    # while HealthComponent stays reusable by any other entity, unchanged.
    set_physics_process(false)
    ($AnimationPlayer as AnimationPlayer).play("death")
```

**C#:**
```csharp
// Pattern 1: Signals travel up (child → parent).
public partial class Player : CharacterBody2D
{
    private HealthComponent _health = null!;

    public override void _Ready()
    {
        // GetNode<T> throws if the child is missing or the wrong type, turning a
        // scene-setup mistake into an obvious failure at startup rather than later.
        _health = GetNode<HealthComponent>("HealthComponent");
        _health.Died += OnHealthDied;
    }

    private void OnHealthDied()
    {
        // The parent decides what death means; the child stays reusable.
        SetPhysicsProcess(false);
        GetNode<AnimationPlayer>("AnimationPlayer").Play("death");
    }
}
```

#### Pattern 2: Method Calls Travel Down (parent → child)

A parent owns its children, so it may reach in and command them by their stable paths. The defensive null check turns a missing child — a scene-setup mistake — into a clear error instead of a null-reference crash several frames later.

**GDScript:**
```gdscript
# Lives on any entity that owns a HealthComponent child.
func apply_hit(damage: int) -> void:
    var health := get_node_or_null("HealthComponent") as HealthComponent
    if health == null:
        push_error("apply_hit: this entity has no HealthComponent child.")
        return
    health.take_damage(damage)
    ($AnimationPlayer as AnimationPlayer).play("hurt")
```

**C#:**
```csharp
// Pattern 2: Method calls travel down (parent → child).
public partial class Level : Node2D
{
    public void ApplyHitToPlayer(int damage)
    {
        // GetNodeOrNull<T> returns null instead of throwing, so the caller chooses
        // how to handle an absent child — here, log the setup error and bail.
        var health = GetNodeOrNull<HealthComponent>("Player/HealthComponent");
        if (health is null)
        {
            GD.PushError("ApplyHitToPlayer: Player/HealthComponent was not found.");
            return;
        }
        health.TakeDamage(damage);
        GetNode<AnimationPlayer>("Player/AnimationPlayer").Play("hurt");
    }
}
```

#### Pattern 3: EventBus Travels Sideways (peer → peer)

When two scenes have no parent/child relationship — an enemy deep in the level and a HUD on a CanvasLayer — routing a signal up and back down through their common ancestor would couple every node in between. An autoloaded EventBus lets them communicate without any of them holding a reference to the others.

**GDScript:**
```gdscript
# event_bus.gd — registered under Project Settings ▸ Autoload as "EventBus".
extends Node

## Fired when any enemy dies, anywhere. Producers (enemies) and consumers (HUD,
## score, audio) never reference each other — only this shared signal.
signal enemy_killed(enemy: Enemy)
```

```gdscript
# enemy.gd — the producer announces on the bus and forgets about it.
class_name Enemy
extends CharacterBody2D

@onready var _health: HealthComponent = $HealthComponent

func _ready() -> void:
    _health.died.connect(_die)

func _die() -> void:
    # Any number of unrelated systems can react to this without _die() gaining a
    # single new dependency.
    EventBus.enemy_killed.emit(self)
    queue_free()
```

```gdscript
# hud.gd — the consumer subscribes on the bus, ignorant of where enemies live.
extends CanvasLayer

@onready var _kill_label: Label = $MarginContainer/TopBar/KillLabel
var _kill_count: int = 0

func _ready() -> void:
    EventBus.enemy_killed.connect(_on_enemy_killed)

func _on_enemy_killed(enemy: Enemy) -> void:
    # The dead enemy is handed over for context (point value, position for a
    # floating "+10") but the HUD never had to find it in the tree.
    _kill_count += 1
    _kill_label.text = "Kills: %d" % _kill_count
```

**C#:**
```csharp
// Pattern 3: EventBus travels sideways (peer → peer).
// Registered under Project Settings ▸ Autoload, reachable at "/root/EventBus".
public partial class EventBus : Node
{
    [Signal]
    public delegate void EnemyKilledEventHandler(Enemy enemy);
}

// The producer emits on the bus and never references the HUD.
public partial class Enemy : CharacterBody2D
{
    public void Die()
    {
        var bus = GetNode<EventBus>("/root/EventBus");
        bus.EmitSignal(EventBus.SignalName.EnemyKilled, this);
        QueueFree();
    }
}

// The consumer subscribes on the bus and never references any Enemy.
public partial class Hud : CanvasLayer
{
    private Label _killLabel = null!;
    private int _killCount;

    public override void _Ready()
    {
        _killLabel = GetNode<Label>("MarginContainer/TopBar/KillLabel");
        var bus = GetNode<EventBus>("/root/EventBus");
        bus.EnemyKilled += OnEnemyKilled;
    }

    private void OnEnemyKilled(Enemy enemy)
    {
        // The dead enemy arrives for context (score value, position) but the HUD
        // never had to know where it lived in the scene tree.
        _killCount++;
        _killLabel.Text = $"Kills: {_killCount}";
    }
}
```

### 5. Organize Node Hierarchy with Container Nodes

Grouping nodes under plain `Node`/`Node2D` containers (`Visuals`, `Collision`, `Components`, `AI`) is not decoration — it gives each subsystem a stable parent path, lets you show/hide or process a whole group at once, and tells the next reader where to look.

#### Entity-Component Pattern

```
Enemy (CharacterBody2D)
├── Visuals
│   ├── Sprite2D
│   └── AnimationPlayer
├── Collision
│   └── CollisionShape2D
├── Components
│   ├── HealthComponent
│   └── HitboxComponent
└── AI
    ├── NavigationAgent2D
    └── StateMachine
```

Each branch is a subsystem you can reason about in isolation; swapping the `AI` branch for a player-controlled input node turns the same body into a playable character.

#### UI Scene Pattern

```
HUD (CanvasLayer)
├── MarginContainer
│   ├── TopBar
│   │   ├── HealthBar
│   │   └── ResourceBar
│   └── BottomBar
│       ├── Hotbar
│       └── MiniMap
└── PauseMenu
```

The `CanvasLayer` root keeps the HUD pinned regardless of camera movement, and the container nesting lets Godot's layout system handle resolution and aspect-ratio changes for you.

#### Level Scene Pattern

```
Level01 (Node2D)
├── TileMapLayer
├── Entities
│   ├── Player (instance)
│   └── Enemies (Node2D)
│       ├── Orc (instance)
│       └── Goblin (instance)
├── Pickups (Node2D)
├── Navigation
│   └── NavigationRegion2D
└── Camera2D
```

Instances (Player, Orc, Goblin) come from their own `.tscn` files, so the level stays a thin layout of *where* things go while *what* they are is defined and tested elsewhere. The `Entities` and `Pickups` containers give spawn/despawn code a single, stable place to add and remove children.

## Examples

- **HealthComponent as shared behavior** — the same `.tscn` dropped into a player, an enemy, and a destructible crate, each getting identical, already-tested damage handling (see the GDScript and C# components above).
- **Enemy → HUD via EventBus** — an enemy deep in the level updates a kill counter on a CanvasLayer HUD without either scene referencing the other (GDScript and C# above).
- **Scene-splitting checklist on a level** — applying the "split when / keep together when" questions to a 40-node level scene: extract the player and each enemy into instances, then leave the level as a thin layout.

## Pitfalls

1. **Fragile tree walks.** Using `get_parent().get_parent()` or `GetParent().GetParent()` silently breaks the instant a node is reparented. Replace with a typed `@onready` / `GetNode<T>()` reference or a signal.
2. **Polling instead of signaling.** A parent reading child state every frame in `_process` quietly reintroduces the coupling that signals exist to remove. Use child→parent signals instead.
3. **Inheritance where layout differs.** If an inherited scene adds or removes nodes (rather than only changing exported values), it should be composition instead. The base's structural changes ripple to all children — a feature when they are the same shape, a liability when they are not.
4. **Unguarded mutable state in autoloads.** A public `var` on an autoloaded singleton can be overwritten by any script in the codebase, with no trace. Put authoritative state behind getters/setters or signals so global changes are intentional and traceable.
5. **Fractional healing lost to int truncation.** A rate like 10 hp/s at 60 fps computes `int(10 * 0.016) == 0` every frame and never heals at all. Accumulate fractional healing across frames before converting to int.
6. **Healing the dead.** A stray heal tick arriving the frame after death can silently revive an entity. Refuse to heal when `_current_health <= 0`; resurrection must be a deliberate, explicit act.
7. **Negative damage healing silently.** Negative "damage" passed to `take_damage()` would silently heal the entity. Reject it loudly with an `assert` (GDScript) or `throw` (C#) in debug builds.
8. **`@tool` scripts running gameplay logic in the editor.** A `@tool` script also runs in the editor. Bail early with `if Engine.is_editor_hint(): return` before touching any gameplay state — the only job there is to emit configuration warnings.
9. **Splitting too early on a prototype.** The wiring overhead of many small scenes buys nothing on a throwaway prototype. Keep it in one scene until the idea survives.
10. **Splitting tightly coupled nodes.** If a split forces you to relay through three signals what a single direct reference already handles, the boundary is in the wrong place. Keep them together until a second use site appears.

## Verification

1. **Every sub-scene opens standalone.** Open each extracted `.tscn` directly from the FileSystem dock, run it with **F6**, and confirm **Debugger ▸ Errors** stays clean. A scene that only works when embedded in its parent has a hidden dependency that defeats the reason you split it. If the project uses a test framework (e.g. GUT), back this with a test that instantiates the sub-scene alone and asserts it reaches `_ready` without error.
   ```powershell
   # Headless check: instantiate a scene and confirm no errors
   godot --headless --path . --script res://test_scene_standalone.gd
   ```

2. **No fragile tree walks.** Use **Search ▸ Find in Files** for `get_parent().get_parent()` and `GetParent().GetParent()`. Each hit is a path that breaks on reparenting — replace it with a typed `@onready` / `GetNode<T>()` reference or a signal.
   ```powershell
   # PowerShell: find fragile tree walks in GDScript and C#
   Select-String -Path "*.gd","*.cs" -Pattern "get_parent\(\)\.get_parent\(\)|GetParent\(\)\.GetParent\(\)" -Recurse
   ```

3. **Child→parent uses signals, not polling.** Confirm parents react to child signals rather than reading child state every frame in `_process`; polling quietly reintroduces the coupling that signals exist to remove.

4. **Inheritance only where layout is identical.** For each inherited scene, compare its node tree to its base. If it adds or removes nodes (rather than only changing exported values), it should be composition instead.

5. **Autoloads expose no unguarded mutable state.** Review each singleton for public `var`s any script can overwrite. Put authoritative state behind getters/setters or signals so global changes are intentional and traceable, not accidental.
   ```powershell
   # PowerShell: find public vars in autoload scripts
   Select-String -Path "autoloads/*.gd" -Pattern "^var |^@export var " | Select-Object Filename, LineNumber, Line
   ```

## Related Skills

- **component-system** — deeper patterns for building and combining reusable components.
- **event-bus** — designing decoupled peer-to-peer communication and avoiding signal spaghetti.
- **godot-brainstorming** — high-level scene tree planning before you start wiring nodes.
- **2d-essentials** — TileMapLayer, CanvasLayer, and 2D-specific organization.
