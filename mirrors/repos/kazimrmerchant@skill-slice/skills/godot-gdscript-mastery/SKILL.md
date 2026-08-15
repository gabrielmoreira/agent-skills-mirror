---
name: godot-gdscript-mastery
description: "Codifies GDScript 2.0 craft: static typing and green-gutter opcodes, typed signals, %UniqueNames, @onready versus _init, Callable.bind, and yield-to-await ports. Use for GDScript reviews, style-guide lock-in, or Godot 3.x script migrations. Not /game-csharp-godot (GodotSharp C#) and not the removed godot-gdscript-patterns twin. Never string-connect signals or pair @onready with @export."
version: 1.0.1
---

## When to Use
- Writing or refactoring GDScript for Godot 4.x in a TBS game context.
- Establishing project coding standards and performing code reviews.
- Porting legacy Godot 3.x scripts to GDScript 2.0.
- Trigger keywords: static_typing, signal_architecture, unique_nodes, @onready, class_name, signal_up_call_down, gdscript_style_guide.

## Prerequisites
- Godot 4.x (specifically 4.7+ features noted where applicable).
- Windows host primary (PowerShell).

## Procedure

### 1. Strong Typing & Performance
Always use static typing. In Godot 4.x, this enables **optimized opcodes** by bypassing runtime `Variant` type-checking.
- **Opcode Optimization**: When types are known at compile-time, the engine uses faster, typed execution paths.
    - **Why it's faster**: Dynamic variables are internally tracked as 24-byte `Variant` structures. Every operation on a dynamic variable requires the engine to evaluate the underlying type at runtime, incurring significant overhead.
    - **Safe Lines**: Confirm optimizations in the script editor; green line numbers in the gutter indicate guaranteed type safety and optimized execution.
- **Typed Global Methods**: Use typed math functions for a performance boost (e.g., use `absf()`, `ceili()`, `clampf()` instead of the generic `abs()`, `ceil()`, `clamp()`).
- **Rule**: Prefer explicit inference `:=` when the type is obvious: `var pos := Vector2(10, 10)`.
- **Rule**: Always specify return types for functions: `func _ready() -> void:`.

### 2. Signal Architecture
- **Connect in `_ready()`**: Preferably connect signals in code to maintain visibility, rather than just in the editor.
- **Typed Signals**: Define signals with types: `signal item_collected(item: ItemResource)`.
- **Pattern**: "Signal Up, Call Down". Children should never call methods on parents; they should emit signals instead.

### 3. Node Access & Lifecycle Safety
- **@onready vs _init()**: 
    - Use `_init()` ONLY for constructor logic (data initialization, memory allocation).
    - Use `@onready` for node dependencies. Child nodes are NOT available in `_init()`.
    - **DANGER**: Avoid `_init(args)` for nodes that will be part of a Scene. It breaks `PackedScene.instantiate()`. Use `@export` for parameter injection.
- **Unique Names**: Use `%UniqueNames` for nodes that are critical to the script's logic.
- **Onready Overrides**: Prefer `@onready var sprite = %Sprite2D` over calling `get_node()` in every function.

### 4. Callable & Signal (First-Class Citizens)
In Godot 4, `Callable` and `Signal` are built-in types. They can be stored in variables and passed as arguments.
- **No Strings**: Always connect via references: `button.pressed.connect(_on_pressed)`.
- **Anonymous Lambdas**: Use for quick inline logic: `timer.timeout.connect(func(): print("Time up!"))`.
- **Binding Context**: Use `Callable.bind()` to pass extra arguments to a signal callback: `hit.connect(_on_hit.bind("Sword"))`.

### 5. Code Structure
Follow the standard Godot script layout:
1. `extends`
2. `class_name`
3. `signals` / `enums` / `constants`
4. `@export` / `@onready` / `properties`
5. `_init()` / `_ready()` / `_process()`
6. Public methods
7. Private methods (prefixed with `_`)

### 6. Refactoring Checklist: Godot 3.x to 4.x
Essential syntax shifts when porting legacy scripts to GDScript 2.0.
- **Annotations**: Replace `export`, `onready`, `tool` with `@export`, `@onready`, and `@tool`.
    - *Example*: `@export_enum("A", "B") var type: int` replaces legacy string hints.
- **Coroutines**: Replace `yield()` with the `await` keyword.
    - *Example*: `await get_tree().create_timer(1.0).timeout`
    - *Common Pattern*: `await get_tree().process_frame` replaces `yield(get_tree(), "idle_frame")`.
- **Properties**: Replace `setget` with inline property syntax.
    - *Syntax*: `var x: int: set(v): x = v; get: return x`
- **Signals**: Migrate from string-based connections to first-class Callable references.
    - *Connection*: `btn.pressed.connect(_on_pressed)` (deprecated: `btn.connect("pressed", ...)`).
    - *Emission*: `my_signal.emit(args)` (deprecated: `emit_signal("my_signal", ...)`).
- **Node Renames**: Be aware of renamed nodes (e.g., `KinematicBody3D` -> `CharacterBody3D`, `Position2D` -> `Marker2D`).
- **Lifecycle Calls**: Explicitly call `super()` in overridden `_ready()`, `_process()`, or `_init()` if parent logic is required.

### 7. Static Utility Libraries
Use `static` members to build lightweight helper libraries that bypass the SceneTree.
- **Static Functions**: Call via class name without instantiating: `MathUtils.calculate(val)`.
    - **Restriction**: No access to `self`, `instance` variables, or non-static methods.
- **Static Variables**: Shared globally across the project.
    - **Restriction**: Cannot use `@export` or `@onready` on static variables.
- **@static_unload**: Place at the top of the script to instruct the engine to unload the script when no references remain.
    - **CRITICAL**: Due to a current engine bug, scripts with static variables may not be automatically freed. Manually nullify large static data structures (like Dictionaries or Arrays of Resources) when no longer needed to prevent memory leaks.

### 8. The "Safe" Dictionary Lookup
Avoid `dict["key"]` if you aren't 100% sure it exists. Use `dict.get("key", default)`.

### 9. Scene Unique Nodes
When building complex UI, always toggle "Access as Scene Unique Name" on critical nodes (Labels, Buttons) and access them via `%Name`.

### 10. Godot 4.7: GDScript Specifics
- Typed override methods **inherit return type** — overrides require explicit `return` (add `return null` if needed).
- Setting packed array elements no longer invokes the whole-array property setter.

## Available Scripts (Load these when dealing with specific patterns)
- `scripts/typed_collections_mastery.gd`: Load when optimizing Arrays and Dictionaries.
- `scripts/functional_lambda_logic.gd`: Load when using `reduce()`, `all()`, and `any()`.
- `scripts/safe_type_casting.gd`: Load when using the `as` operator for object identification.
- `scripts/typed_signal_definitions.gd`: Load when enforcing type safety on signal arguments.
- `scripts/callable_binding_context.gd`: Load when injecting context into signal callbacks using `Callable.bind()`.
- `scripts/unbind_signal_args.gd`: Load when discarding unneeded signal arguments using `Callable.unbind()`.
- `scripts/await_sequence_manager.gd`: Load when managing async flows and timers using `await`.
- `scripts/array_preallocation_perf.gd`: Load when pre-sizing large arrays with `resize()`.
- `scripts/static_var_singleton_alt.gd`: Load when using `static var` for global state as an Autoload alternative.
- `scripts/dictionary_safe_iteration.gd`: Load when erasing dictionary keys while iterating.

## Pitfalls
- **NEVER use `@onready` and `@export` on the same variable** — Initialization order will cause `@onready` to overwrite the Inspector value.
- **NEVER modify a Dictionary's size while iterating it** — Use `dict.keys().duplicate()` or iterate a clone to safely erase elements.
- **NEVER use string-based `connect("signal", ...)`** — Always use the Signal object syntax (`button.pressed.connect(...)`) for compile-time safety.
- **NEVER attempt to override non-virtual native engine methods** — Overriding `queue_free()` or `get_class()` is unsupported and will be ignored by engine callbacks.
- **NEVER use dynamic `get_node()` or `$` inside `_process()`** — Fetching paths every frame stalls the CPU. Cache and use `@onready`.
- **NEVER use `Parent.method()` calls** — Violates "Signal Up, Call Down". Use signals to communicate with parents.
- **NEVER use `is` followed by a hard cast** — If the type check passes but the object changes, it crashes. Use `as` and check for null.
- **NEVER use `print()` for production debugging** — Use `push_error()`, `push_warning()`, or breakpoints to ensure errors are visible in the console/logs.
- **NEVER pre-load huge resources in `_ready()`** — This causes frame stutters. Use `ResourceLoader.load_threaded_request()` for async loading.
- **NEVER use global variables in Autoloads when `static var` is sufficient** — Static variables offer better encapsulation and less project pollution.

## Verification
- Check for green line numbers in the Godot script editor gutter to confirm type safety and optimized execution.
- Ensure no `print()` statements exist in production code (search for `print(`).
- Verify no string-based signal connections exist (search for `.connect("`).
- Confirm no `get_node()` or `$` calls inside `_process()` or `_physics_process()`.

## Related skills
- Master Skill: [godot-master](../godot-master/SKILL.md)

## Reference
- Official Docs: `tutorials/scripting/gdscript/gdscript_styleguide.rst`
- Official Docs: `tutorials/best_practices/logic_preferences.rst`
