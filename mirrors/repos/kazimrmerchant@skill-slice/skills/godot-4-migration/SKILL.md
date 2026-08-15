---
name: godot-4-migration
description: "Rewrites Godot 3.x GDScript onto 4.x: @export/@onready/@tool, create_tween(), callable signal connect/emit, await instead of yield, inline set/get, typed arrays, and super(). Use when a 3.x project must compile under Godot 4 or Tween/export/yield parse errors appear after the bump. Do not use to scaffold a brand-new Godot 4 game, and not a combat/UI systems playbook."
version: 1.0.1
risk: safe
source: community
date_added: "2026-02-27"
---

# Godot 4 Migration Guide

## Overview

A critical guide for developers transitioning from Godot 3.x to Godot 4. Covers the major syntax changes in GDScript 2.0, the new `Tween` system, `export` annotation updates, signal connections, typed arrays, and coroutine `await` replacements.

## When to Use

- Use when porting a Godot 3.x project to Godot 4.
- Use when encountering GDScript syntax errors after upgrading the engine version.
- Use when replacing deprecated `Tween` nodes with `create_tween()`.
- Use when updating `export` variables to `@export` annotations.
- Use when converting `yield`/`setget`/string-based signal connections to Godot 4 equivalents.

## Prerequisites

- Godot 4.x installed and opening the project without crashing (project.godot upgraded).
- A backup or version-controlled copy of the original Godot 3.x project.
- Familiarity with GDScript syntax.

## Procedure

### 1. Update Annotations (`@` prefix)

Godot 4 uses `@` for keywords that modify behavior. Replace all old annotation syntax:

| Godot 3.x | Godot 4 |
|---|---|
| `export var x` | `@export var x` |
| `onready var y` | `@onready var y` |
| `tool` (top of file) | `@tool` |
| `export_range(...)` | `@export_range(...)` |
| `export_file(...)` | `@export_file(...)` |

### 2. Convert Setters and Getters to Inline Syntax

Properties now define setters/getters inline instead of using `setget`.

**Godot 3.x:**
```gdscript
var health setget set_health, get_health

func set_health(value):
    health = value
```

**Godot 4:**
```gdscript
var health: int:
    set(value):
        health = value
        health_changed.emit(health)
    get:
        return health
```

### 3. Replace Tween Node with `create_tween()`

The `Tween` node is deprecated. Use `create_tween()` which returns a `Tween` object.

**Godot 3.x:**
```gdscript
$Tween.interpolate_property($Sprite, "position", Vector2.ZERO, Vector2(100, 100), 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN_OUT)
$Tween.start()
```

**Godot 4:**
```gdscript
var tween = create_tween()
tween.tween_property($Sprite, "position", Vector2(100, 100), 1.0)
tween.parallel().tween_property($Sprite, "modulate:a", 0.0, 1.0)
```

Key differences:
- `create_tween()` is called on any `Node`; no `Tween` node needed in the scene tree.
- `tween_property(target, property, final_value, duration)` — note the simplified signature.
- Use `.parallel()` to run tweens concurrently instead of sequentially.
- Use `.set_trans()` and `.set_ease()` for transition/ease types.

### 4. Update Signal Connections to Callable Syntax

String-based connections are discouraged. Use callables directly.

**Godot 3.x:**
```gdscript
connect("pressed", self, "_on_pressed")
emit_signal("health_changed", health)
```

**Godot 4:**
```gdscript
pressed.connect(_on_pressed)
health_changed.emit(health)
```

For dynamic connections by name:
```gdscript
button.connect("pressed", Callable(self, "_on_pressed"))
```

### 5. Replace `yield` with `await`

`yield` is replaced by `await` for coroutines.

**Godot 3.x:**
```gdscript
yield(get_tree().create_timer(1.0), "timeout")
yield($AnimationPlayer, "animation_finished")
```

**Godot 4:**
```gdscript
await get_tree().create_timer(1.0).timeout
await $AnimationPlayer.animation_finished
```

### 6. Add Typed Arrays and Variable Types

GDScript 2.0 supports typed arrays and variable typing for performance and type safety.

```gdscript
# Godot 3
var enemies = []

# Godot 4
var enemies: Array[Enemy] = []

func _ready():
    for child in get_children():
        if child is Enemy:
            enemies.append(child)
```

Type all variables where possible (`var x: int`, `var name: String`) for performance gains.

### 7. Replace Implicit Parent Calls with `super()`

**Godot 3.x:**
```gdscript
func _ready():
    ._ready()
```

**Godot 4:**
```gdscript
func _ready():
    super._ready()
    # or for regular methods:
    super()
```

### 8. Update `@export` Variants for Inspector UI

Use specialized export annotations for better inspector controls:

```gdscript
@export_range(0, 100, 1) var health: int = 100
@export_file("*.json") var data_file: String
@export_enum("Warrior", "Mage", "Rogue") var class_type: int = 0
@export_group("Combat")
@export var damage: int = 10
```

## Examples

### Full Migration Example: A Simple Button Handler

**Godot 3.x:**
```gdscript
extends Control

export var button_text: String = "Click Me"
onready var label = $Label

func _ready():
    connect("pressed", self, "_on_pressed")

func _on_pressed():
    yield(get_tree().create_timer(0.5), "timeout")
    label.text = "Done!"
```

**Godot 4:**
```gdscript
extends Control

@export var button_text: String = "Click Me"
@onready var label: Label = $Label

func _ready():
    pressed.connect(_on_pressed)

func _on_pressed():
    await get_tree().create_timer(0.5).timeout
    label.text = "Done!"
```

## Pitfalls

- **"Identifier 'Tween' is not a valid type."** — `Tween` is now an object returned by `create_tween()`. You rarely type it explicitly; just use `var tween = create_tween()`. If you must type it, use `var tween: Tween = create_tween()`.

- **Signal connection errors after migration.** — String-based `connect("signal", target, "method")` still works but is discouraged. Ensure the callable signature matches; Godot 4 is stricter about argument counts.

- **`setget` silently broken.** — The `setget` keyword is removed entirely in Godot 4. The editor will show a parse error. Must convert to inline `set`/`get` blocks.

- **`yield` causes parse errors.** — `yield` is fully removed in GDScript 2.0. Every instance must be replaced with `await`.

- **`.method_name()` parent calls fail.** — The dot-prefix syntax for calling parent methods is removed. Use `super.method_name()` or `super()` for the same-named method.

- **`@onready` timing.** — `@onready` variables are initialized just before `_ready()` is called, same as Godot 3's `onready`. But if you access them in `_init()` or `_enter_tree()`, they will be null.

- **Typed array casting.** — `Array[Node]` requires all elements to be `Node` or subclasses. Mixing types causes runtime errors. Use `Array[Variant]` if you need mixed types.

- **`emit_signal` still works but is deprecated style.** — Prefer `signal_name.emit(args)` over `emit_signal("signal_name", args)` for clarity and refactoring safety.

- **Resource `.tres`/`.tscn` files.** — Scene and resource files may need re-saving in Godot 4. Open them in the editor and save to update the format. Some property names changed (e.g., `margin` → `offset` in `Control`).

- **Do not treat this guide as a substitute for environment-specific validation, testing, or expert review.** Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.

## Verification

After migration, verify the project loads and runs correctly:

1. **Open the project in Godot 4** — check the editor console for parse errors:
   ```
   No GDScript parse errors in the Output panel.
   ```

2. **Run the project** (F5 or CLI):
   ```powershell
   & "C:\Program Files\Godot\Godot4.exe" --path . --check-only
   ```
   Expected: exits with code 0, no script errors reported.

3. **Verify no deprecated patterns remain** — search the codebase:
   ```powershell
   Get-ChildItem -Recurse -Filter *.gd | Select-String -Pattern "setget|yield\(|connect\(`"|emit_signal\(" | ForEach-Object { "$($_.Path):$($_.LineNumber): $($_.Line)" }
   ```
   Expected: no matches (or only intentional dynamic connections).

4. **Verify Tween usage** — confirm no `Tween` node references in scenes:
   ```powershell
   Get-ChildItem -Recurse -Filter *.tscn | Select-String -Pattern "type=`"Tween`""
   ```
   Expected: no matches.

5. **Run the main scene and test interactions** — confirm signals fire, tweens animate, and no runtime errors appear in the console.

## Related Skills

- `godot-gdscript-best-practices` — GDScript 2.0 coding standards and patterns.
- `godot-scene-architecture` — Node and scene tree organization for Godot 4.
