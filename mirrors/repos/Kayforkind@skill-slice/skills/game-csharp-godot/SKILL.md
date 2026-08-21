---
name: game-csharp-godot
version: 1.1.1
description: "Authors Godot 4.3+ gameplay in C# with GodotSharp: partial classes, [Export] properties, [Signal] EventHandler delegates, ToSignal awaits, Variant marshalling, and GDScript Call/Get/Set at language boundaries. Use when the project needs .NET libraries, compiled hot loops, or C# and GDScript interop. Not for GDScript style guides, @tool editor plugins, or GDExtension C++. Do not use where the export target has no .NET runtime."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# C# in Godot 4.3+

This skill covers C#-specific conventions, API differences from GDScript, project setup, and interop patterns for Godot 4.3+ with the GodotSharp NuGet package. All examples are C# only.

> **Related skills:** **csharp-signals** for C# signal patterns, **godot-project-setup** for C# project scaffolding, **godot-testing** for C# testing with gdUnit4, **gdextension** for native C++ when C# is not enough, **multithreading** for C# concurrency.

---

## When to Use

- You are developing a Godot 4.3+ project and want to write gameplay code in C# instead of GDScript.
- You need strong typing, IDE tooling, or want to integrate existing .NET libraries.
- You require performance-critical systems (physics, AI, procedural generation) that benefit from compiled C# code.
- You are hitting GDScript interop boundaries and need marshalling guidance.

## Do Not Use

- For quick editor plugins or `@tool` scripts where hot-reloading and minimal compile time matter more than performance.
- When the target platform does not support the .NET runtime required by GodotSharp (e.g., certain restricted web/mobile environments without .NET support).
- If the team is unfamiliar with C# and the project timeline does not allow a learning curve.
- **Warning:** Avoid using `async void` for logic that requires error handling; use `async Task` to prevent silent crashes.

## Prerequisites

- Godot 4.3+ with .NET support enabled (download the .NET version of the Godot editor).
- .NET 8.0 SDK or newer installed on the host machine.
- An IDE with Godot C# support: JetBrains Rider (2023.3+), VS Code (C# Dev Kit + Godot Tools), or Visual Studio (Godot extension, Windows only).
- Windows host is primary (PowerShell). All path examples assume Windows conventions.

## Procedure

### 1. Create the C# Project

1. Open Godot 4.3+ and create or open a project.
2. Create a new C# script via **Script > New Script > C#**. Godot auto-generates the `.csproj` and `.sln`.
3. Do **not** edit the generated `.csproj` file structure manually — let the editor manage it. Only edit to add NuGet packages.
4. Open the generated `.sln` (not just the folder) in your IDE for full solution resolution.

```
MyProject/
├── MyProject.csproj          # Auto-generated, edit only for NuGet packages
├── MyProject.sln             # Auto-generated solution file
├── project.godot
└── scripts/
    └── Player.cs
```

### 2. Configure the .csproj for NuGet and .NET 8

1. Open `MyProject.csproj`.
2. Ensure `TargetFramework` is `net8.0` or newer.
3. Add any third-party NuGet packages inside `<ItemGroup>`.

```xml
<Project Sdk="Godot.NET.Sdk/4.3.0">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <AllowUnsafeBlocks>true</AllowUnsafeBlocks>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
  </ItemGroup>
</Project>
```

4. Run `dotnet restore` or let the IDE restore automatically after editing.

### 3. Write a C# Script — The `partial class` Requirement

Every class that extends a Godot type **must** be declared `partial`. This is not optional. Godot uses C# source generators to emit signal registration, property binding, and RPC code alongside your class. Source generators require `partial` to inject into the same class declaration.

```csharp
// CORRECT
public partial class Player : CharacterBody2D { }

// WRONG — will cause source generator errors
public class Player : CharacterBody2D { }
```

**Error when forgotten:**

```
Error CS0260: Missing partial modifier on declaration of type 'Player';
another partial declaration of this type exists.
```

Or the class compiles but signals and `[Export]` properties silently fail to register. This applies to every class in the inheritance chain that extends a Godot type, including intermediate base classes.

### 4. Follow Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Methods | PascalCase | `public void TakeDamage(int amount)` |
| Properties | PascalCase | `public float MaxHealth { get; set; }` |
| Signals (delegate) | PascalCase + `EventHandler` suffix | `HealthChangedEventHandler` |
| `[Export]` properties | PascalCase | `[Export] public float Speed { get; set; }` |
| Private fields | `_camelCase` with underscore prefix | `private float _currentSpeed;` |
| Local variables | camelCase | `var newPosition = ...` |
| Parameters | camelCase | `void SetHealth(int newHealth)` |
| Godot API names | Match Godot's PascalCase exactly | `GlobalPosition` not `global_position` |
| Enums | PascalCase type, PascalCase members | `enum State { Idle, Running, Dead }` |
| Constants | PascalCase or SCREAMING_SNAKE per team style | `const float MaxSpeed = 200f;` |

Always match GodotSharp property and method names exactly — they are PascalCase translations of the GDScript snake_case names (e.g. `is_on_floor()` → `IsOnFloor()`).

### 5. Declare and Emit Signals

Signals require a delegate declaration with the `[Signal]` attribute. The delegate name **must** end with `EventHandler`.

```csharp
using Godot;

public partial class Player : CharacterBody2D
{
    [Signal] public delegate void HealthChangedEventHandler(int newHealth);
    [Signal] public delegate void DiedEventHandler();

    private int _health = 100;

    public void TakeDamage(int amount)
    {
        _health -= amount;
        EmitSignal(SignalName.HealthChanged, _health);  // Use SignalName.X, not a string
        if (_health <= 0)
            EmitSignal(SignalName.Died);
    }
}
```

**Connecting and disconnecting:**

```csharp
// Connect with +=
player.HealthChanged += OnHealthChanged;
player.Died += OnPlayerDied;

// Disconnect with -=
player.HealthChanged -= OnHealthChanged;
player.Died -= OnPlayerDied;

private void OnHealthChanged(int newHealth)
{
    GD.Print($"Health changed to {newHealth}");
}

private void OnPlayerDied()
{
    GD.Print("Player has died, triggering game over sequence.");
}
```

> For full signal patterns including one-shot connections, static typed signals, and cross-language signal wiring, load the **csharp-signals** skill.

### 6. Use Async / Await

GDScript's `await` maps to C#'s `await ToSignal(...)`. Godot signals return a `SignalAwaiter` compatible with C# `await`.

```csharp
public async void StartCutscene()
{
    await ToSignal(GetTree().CreateTimer(2.0), Timer.SignalName.Timeout);

    var anim = GetNode<AnimationPlayer>("AnimationPlayer");
    anim.Play("intro");
    await ToSignal(anim, AnimationPlayer.SignalName.AnimationFinished);

    GD.Print("Cutscene complete");
}
```

For CPU-bound work, use `Task.Run` — but **never** touch Godot objects from a non-main thread:

```csharp
public async Task LoadHeavyData()
{
    // Off main thread: pure C# computation only
    var result = await Task.Run(() => ComputeSomethingExpensive());

    // Back on main thread: safe to use Godot API
    ApplyResult(result);
}

private int ComputeSomethingExpensive()
{
    // No Godot API calls here
    return Enumerable.Range(0, 1_000_000).Sum();
}
```

**GDScript `await` equivalents:**

| GDScript | C# |
|---|---|
| `await get_tree().create_timer(1.0).timeout` | `await ToSignal(GetTree().CreateTimer(1.0), Timer.SignalName.Timeout)` |
| `await animation_player.animation_finished` | `await ToSignal(animPlayer, AnimationPlayer.SignalName.AnimationFinished)` |
| `await signal_name` | `await ToSignal(this, SignalName.YourSignal)` |

### 7. GDScript Interop

**Calling GDScript from C#:**

```csharp
GodotObject enemy = GetNode("Enemy");

// Call a GDScript method
enemy.Call("take_damage", 25);

// Get a GDScript property
float health = enemy.Get("health").AsSingle();

// Set a GDScript property
enemy.Set("is_stunned", true);
```

**Calling C# from GDScript** — if a C# class is registered as `[GlobalClass]`, GDScript can instantiate and use it directly:

```csharp
[GlobalClass]
public partial class WeaponData : Resource
{
    [Export] public float Damage { get; set; } = 10f;
    [Export] public float Cooldown { get; set; } = 0.5f;
}
```

```gdscript
# GDScript — works because WeaponData is a [GlobalClass]
var data := WeaponData.new()
data.damage = 50.0
```

Non-`[GlobalClass]` C# types are not visible to GDScript by name but can still be passed as `Variant`/`Object` references.

### 8. C# vs GDScript Syntax Quick Reference

| GDScript | C# Equivalent | Notes |
|---|---|---|
| `var x = 5` | `var x = 5;` or typed `int x = 5;` | C# `var` infers type at compile time |
| `func MyMethod() -> void:` | `public void MyMethod() { }` | Methods are PascalCase in C# |
| `signal health_changed(amount: int)` | `[Signal] public delegate void HealthChangedEventHandler(int amount);` | Must use `EventHandler` suffix |
| `@export var speed: float = 100.0` | `[Export] public float Speed { get; set; } = 100f;` | PascalCase, property syntax |
| `@onready var label = $Label` | `private Label _label;` + `_label = GetNode<Label>("Label");` in `_Ready()` | No `@onready` equivalent |
| `match value:` | `switch (value) { case X: break; }` | C# switch supports pattern matching |
| `class_name MyClass` | `[GlobalClass] public partial class MyClass : GodotObject { }` | Requires `[GlobalClass]` attribute |
| `extends Node` | `public partial class MyScript : Node { }` | Inheritance via `:` |
| `preload("res://scene.tscn")` | `GD.Load<PackedScene>("res://scene.tscn")` | Loaded at runtime, not compile time |
| `push_error("msg")` | `GD.PushError("msg");` | Prints to Godot error log |
| `print("msg")` | `GD.Print("msg");` | Also: `GD.PrintS()`, `GD.PrintT()` |
| `node is CharacterBody2D` | `node is CharacterBody2D` | Same keyword, same semantics |
| `node as CharacterBody2D` | `node as CharacterBody2D` | Returns `null` on failure in both |
| `await signal_name` | `await ToSignal(source, SignalName.X);` | Must use `ToSignal()` wrapper |
| `Array` | `Godot.Collections.Array` | Not `System.Collections.Generic.List<T>` |
| `Dictionary` | `Godot.Collections.Dictionary` | Not `System.Collections.Generic.Dictionary<K,V>` |

## Examples

### Variant Marshalling Gotchas

| Scenario | Issue | Fix |
|---|---|---|
| Passing `null` across boundary | GDScript `null` becomes `default(Variant)`, not C# `null` | Check `variant.VariantType == Variant.Type.Nil` |
| Returning `int[]` from C# | GDScript receives a `PackedInt32Array`, not an `Array` | Return `Godot.Collections.Array<int>` for consistent typing |
| Passing `System.Collections.Generic.List<T>` | Not marshallable — Godot doesn't know this type | Convert to `Godot.Collections.Array<T>` first |
| Godot `Color` struct | Passed by value through Variant correctly | No issue |

### Performance: C# vs GDScript

| Workload | Winner | Reason |
|---|---|---|
| Math-heavy loops (pathfinding, simulation) | C# (significantly faster) | Compiled JIT vs interpreted GDScript |
| Large array/collection processing | C# | Value type arrays avoid boxing |
| Godot API calls (move_and_slide, etc.) | Roughly equal | Both route through the same C++ engine |
| Scene tree operations | Roughly equal | Bottleneck is C++ overhead, not language |
| Rapid prototyping | GDScript | Less boilerplate, hot-reload without recompile |
| Editor tooling (plugins, @tool) | GDScript | C# tool scripts require a full build cycle |

**Guidance:**
- Use C# for systems with tight loops: physics solvers, procedural generation, AI decision trees, data processing.
- Use GDScript for editor plugins, `@tool` scripts, and rapid iteration on gameplay logic.
- Mixing languages in the same project is supported — interop cost is minimal for occasional cross-language calls.
- Avoid `Godot.Collections.Array` for hot paths; prefer typed arrays (`Array<T>`) or native C# arrays (`T[]`) converted at boundaries.
- `StringName` lookups are O(1) but `StringName` construction is not — cache them if created frequently.

## Pitfalls

| Gotcha | Problem | Fix |
|---|---|---|
| `Variant` to C# type conversion | `(float)someVariant` throws if the underlying type is `int` | Use `.AsSingle()`, `.AsInt32()`, etc. instead of casts |
| `null` vs `default(Variant)` | Godot signals passing no value give `default(Variant)`, not C# `null` | Check `.VariantType == Variant.Type.Nil` |
| `Godot.Collections` vs `System.Collections` | Godot API methods return `Godot.Collections.Array`; passing `List<T>` causes runtime error | Always use `Godot.Collections.Array`/`Dictionary` at Godot API boundaries |
| Disposing native objects | Calling methods on a freed Godot object throws `ObjectDisposedException` | Check `IsInstanceValid(obj)` before use |
| `StringName` construction in hot loops | `new StringName("my_signal")` allocates each call | Cache as `private static readonly StringName _signalName = "my_signal";` |
| Export array types | `[Export] public Array Items;` exports untyped array | Use `[Export] public Godot.Collections.Array<MyResource> Items { get; set; }` |
| Node path strings | `GetNode("../UI/Label")` fails silently if the path changes | Use `GetNode<Label>("%Label")` with unique names or typed `[Export]` node references |
| `partial class` forgotten | Source generators silently fail; `[Export]` and `[Signal]` don't register | Every class extending a Godot type must be `partial` |
| `async void` vs `async Task` | `async void` swallows exceptions | Use `async Task` except for top-level event handlers that Godot calls |

## Verification

1. **Build check:** Run `dotnet build` in the project root. Verify it completes without warnings regarding target framework compatibility.

   ```powershell
   dotnet build
   ```

2. **Source generator check:** Open the `.sln` in your IDE and build. Verify no source-generator errors appear (no CS0260 missing partial modifier errors).

3. **Runtime registration check:** Execute a sample scene that uses a partial class, exported properties, and a custom signal. Confirm:
   - `[Export]` properties appear in the Godot inspector.
   - Custom signals appear in the node's Signals tab.
   - `EmitSignal(SignalName.X)` triggers connected handlers.

4. **Interop check:** If using GDScript interop, verify `Call`, `Get`, and `Set` marshal values correctly by printing received values on both sides.

5. **Thread safety check:** If using `Task.Run`, confirm no Godot API calls occur inside the callback — all engine calls must happen on the main thread.

6. **Final checklist:**

- [ ] Every class extending a Godot type is declared `partial`
- [ ] Method names match GodotSharp PascalCase (e.g. `_Ready`, `_PhysicsProcess`, `IsOnFloor()`)
- [ ] `[Export]` properties are PascalCase and use property syntax (`{ get; set; }`)
- [ ] Signal delegates end with `EventHandler` and use `EmitSignal(SignalName.X)`
- [ ] Signals connected with `+=` and disconnected with `-=` when no longer needed
- [ ] `await ToSignal(...)` used for Godot signals — not raw `Task.Delay` for game timing
- [ ] `Godot.Collections.Array`/`Dictionary` used at Godot API boundaries, not `System.Collections` types
- [ ] `IsInstanceValid(obj)` checked before using any potentially freed Godot object
- [ ] `StringName` instances cached if constructed in loops or frequently called methods
- [ ] No Godot API calls inside `Task.Run(...)` callbacks — all engine calls happen on the main thread
- [ ] `.csproj` opened via the `.sln` file in the IDE for full solution resolution
- [ ] C# used for computation-heavy systems; GDScript retained for editor tooling and `@tool` scripts

## Related Skills

- **csharp-signals** – detailed patterns for typed signals and cross-language wiring. Load when you need one-shot connections, static typed signals, or complex signal routing.
- **godot-project-setup** – initial project configuration, export presets, and platform targets. Load when scaffolding a new Godot C# project.
- **godot-testing** – unit and integration testing of C# scripts with gdUnit4. Load when writing tests for C# gameplay code.
- **gdextension** – when native C++ extensions are required beyond C# capabilities. Load when C# performance is insufficient.
- **multithreading** – advanced threading models and synchronization in Godot C#. Load when implementing concurrent systems.
