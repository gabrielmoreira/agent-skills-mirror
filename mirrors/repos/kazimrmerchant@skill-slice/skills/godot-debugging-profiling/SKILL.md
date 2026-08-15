---
name: godot-debugging-profiling
description: "Profiles and debugs Godot 4.7 with the Debugger, breakpoint, push_error, Performance.get_monitor, orphan nodes, remote_debug, and release-export timing. Use when the user wants Godot-specific leak hunts, draw-call spikes, or editor profiler frame time. Trigger: print_debug, assert, OBJECT_ORPHAN_NODE_COUNT, Time.get_ticks_usec. Not for engine-agnostic git bisect or regression hunting (bug-hunter). Never profile in a debug build or with V-Sync on, and never leave unlabeled print() in release."
version: 1.0.1
---

## When to Use
Use this skill for bug fixing, performance tuning, or development diagnostics in Godot 4.7+. Trigger keywords: breakpoint, print_debug, push_error, assert, profiler, remote_debug, memory_leak, orphan_nodes, Performance.get_monitor.

## Prerequisites
- **Godot 4.7+ Baseline**: Expert patterns target Godot 4.7+ (stable, 2026-06-18). Consult the [Godot 4.7 migration guide](https://docs.godotengine.org/en/4.7/tutorials/migrating/upgrading_to_godot_4.7.html) when upgrading.
- **Windows Host (Primary)**: Commands assume PowerShell. Adjust paths for other OS if necessary.
- **NEVER assume 4.6 defaults** (stretch mode, audio area_mask, RichTextLabel percent flags) without checking 4.7 migration notes.

## Procedure

### 1. Print Debugging & Error Handling
Use descriptive context for prints. Wrap debug prints in `if OS.is_debug_build()` or use a custom `DEBUG` const.

```gdscript
# Basic print with context
print("Player at %s with health %d" % [position, health])

# Warning (non-fatal)
push_warning("This might be a problem")

# Error (non-fatal)
push_error("Something went wrong!")

# Assert (fatal in debug)
assert(health > 0, "Health cannot be negative!")
```

**Error Handling Example (File Access):**
```gdscript
func load_save() -> Dictionary:
    if not FileAccess.file_exists(SAVE_PATH):
        push_warning("No save file found")
        return {}
    
    var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
    if file == null:
        push_error("Failed to open save: %s" % FileAccess.get_open_error())
        return {}
    
    var json := JSON.new()
    var error := json.parse(file.get_as_text())
    if error != OK:
        push_error("JSON parse error: %s" % json.get_error_message())
        return {}
    
    return json.data
```

### 2. Breakpoints & Debugger Panel
- **Set Breakpoint**: Click line number gutter in script editor, or use `breakpoint` keyword.
- **Conditional Breakpoint**:
```gdscript
if player.health <= 0:
    breakpoint
```
- **Debugger Panel**: Access via **Debug → Debugger** (Ctrl+Shift+D).
  - **Stack Trace**: Call stack when paused.
  - **Variables**: Inspect local/member variables.
  - **Breakpoints**: Manage all breakpoints.
  - **Errors**: Runtime errors and warnings.

### 3. Remote Debug & Visual Debugging
1. Run project (F5).
2. Debug → Remote Debug → Select running instance.
3. Inspect live game state and scene tree hierarchy.

**Visualize Raycasts (2D):**
```gdscript
func _draw() -> void:
    if Engine.is_editor_hint():
        draw_line(Vector2.ZERO, ray_direction * ray_length, Color.RED, 2.0)
```

**Debug Draw in 3D:**
```gdscript
func debug_draw_sphere(pos: Vector3, radius: float) -> void:
    var mesh := SphereMesh.new()
    mesh.radius = radius
    var instance := MeshInstance3D.new()
    instance.mesh = mesh
    instance.global_position = pos
    add_child(instance)
```

### 4. Profiler & Performance Monitoring
Access via **Debug → Profiler** (F3).
- **Time Profiler**: Shows function execution times. Target: < 16.67ms per frame (60 FPS).
- **Monitor**: FPS, physics, memory, object count, draw calls.

**Check FPS in `_process`:**
```gdscript
func _process(delta: float) -> void:
    print(Engine.get_frames_per_second())
```

**Check Orphaned Nodes:**
```gdscript
func check_orphans() -> void:
    print("Orphan nodes: ", Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT))
```

### 5. Expert Debugging Patterns

#### Automated-QA-Suite (Headless CI/CD)
- **Headless Execution**: Use `godot --headless -s test_runner.gd` to run tests without a display server.
- **Verification**: Evaluate state and call `get_tree().quit(0)` for success or `quit(1)` for failure.
- **CLI Flags**: Use `--gpu-validation` and `--gpu-abort` to catch driver-level errors in CI.

```gdscript
func _run() -> void:
    var success := _run_all_tests()
    if success:
        print("[TEST_RESULT] PASS")
        get_tree().quit(0)
    else:
        printerr("[TEST_RESULT] FAIL")
        get_tree().quit(1)
```

#### Visual-Profiler-Extensions (GPU Costs)
- **Metric Querying**: Use `RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME)`.
- **GPU Profiling**: Enable `debug/settings/stdout/print_gpu_profile` in Project Settings.
- **VRAM Tracking**: Use `Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)`.

#### Thread-Safety-Analyzer (Race Conditions)
- **Safety Checks**: Use `Thread.set_thread_safety_checks_enabled(true)`.
- **Deferred Access**: ALWAYS use `call_deferred()` or `set_deferred()` when a worker thread modifies the SceneTree.
- **Server Safety**: Servers (Rendering/Physics) are thread-safe ONLY if enabled in Project Settings under `threading/worker_pool/allow_group_tasks`.

#### Memory-Leak-Tracker (Transient Scenes)
- **Orphan Detection**: Periodically check `Node.get_orphan_node_ids()`.
- **ObjectDB Snapshots**: Use the Godot 4.7 ObjectDB Profiler to take "Before" and "After" snapshots to reveal `RefCounted` circular reference leaks.

### 6. Available Scripts (Load on Demand)
> **MANDATORY**: Read the appropriate script before implementing the corresponding pattern.

- **[high_precision_benchmarker.gd](scripts/high_precision_benchmarker.gd)**: Load when implementing micrometer-precision execution timing using `Time.get_ticks_usec()`.
- **[orphan_node_detector.gd](scripts/orphan_node_detector.gd)**: Load when automating detection of "Orphan Nodes" using internal Performance monitors.
- **[advanced_backtrace_recorder.gd](scripts/advanced_backtrace_recorder.gd)**: Load when capturing detailed script backtraces programmatically.
- **[engine_error_interceptor.gd](scripts/engine_error_interceptor.gd)**: Load when intercepting C++ engine errors for custom logs/analytics.
- **[custom_editor_monitor.gd](scripts/custom_editor_monitor.gd)**: Load when exposing game-specific metrics to the Godot Editor Debugger > Monitors tab.
- **[debugger_tab_plugin.gd](scripts/debugger_tab_plugin.gd)**: Load when injecting custom visual tabs into the Godot bottom panel.
- **[thread_safe_logger.gd](scripts/thread_safe_logger.gd)**: Load when implementing thread-safe logging from worker threads.
- **[custom_debug_draw.gd](scripts/custom_debug_draw.gd)**: Load when visualizing non-visual data like pathfinding nodes or AI influence maps.
- **[break_on_condition.gd](scripts/break_on_condition.gd)**: Load when creating hardcoded breakpoint triggers for invalid logic states.
- **[remote_debug_console.gd](scripts/remote_debug_console.gd)**: Load when building an in-game command console for mobile/console builds.

> **Do NOT Load** `debug_overlay.gd` in release builds - wrap usage in `if OS.is_debug_build()`.

## Pitfalls
- **NEVER use `print()` without descriptive context** — `print(value)` is useless. Use `print("Player health:", health)` with labels.
- **NEVER leave debug prints in release builds** — Wrap in `if OS.is_debug_build()` or use custom DEBUG const. Prints slow down release.
- **NEVER ignore `push_warning()` messages** — Warnings indicate potential bugs (null refs, deprecated APIs). Fix them before they become errors.
- **NEVER use `assert()` for runtime validation in release** — Asserts are disabled in release builds. Use `if not condition: push_error()` for runtime checks.
- **NEVER profile in debug mode** — Debug builds are 5-10x slower. Always profile with release exports or `--release` flag.
- **NEVER assume `Engine.capture_script_backtraces(true)` is cheap** — Capturing locals allocates significant memory and can prevent objects from being deallocated, causing artificial leaks [19].
- **NEVER call `push_error()` or `print()` inside a custom `Logger._log_message` override** — This causes infinite recursion and crashes as the logger intercepts its own output [20].
- **NEVER leave the Visual Profiler running during gameplay tests** — Continuous polling degrades framerates significantly, invalidating actual performance metrics [21].
- **NEVER rely on `OS.get_ticks_msec()` for microbenchmarking** — Milliseconds lack precision for logic timing; ALWAYS use `Time.get_ticks_usec()` for microsecond precision [22].
- **NEVER assume `OBJECT_ORPHAN_NODE_COUNT` works in production** — This monitor is strictly debug-only; it safely returns 0 in release builds, potentially hiding leaks [23].
- **NEVER benchmark with V-Sync enabled** — V-Sync throttles metrics to the monitor refresh rate, masking the true CPU/GPU processing overhead [24].
- **NEVER leave `print_stack()` or `print_debug()` in release builds** — These are often stripped or useless outside the debugger. Use structured logging for production [25].
- **NEVER strip debugging symbols if using external C++ profilers** — Stripping destroys call stack readability for external tools like Perfetto or VerySleepy [26].
- **NEVER forget to unregister an `EditorDebuggerPlugin` in `_exit_tree()`** — Failing to clean up leaves "ghost" connections in the engine's debugging loop [27].
- **NEVER trust the Visual Profiler on macOS when using the Compatibility renderer** — Platform-specific driver limitations severely restrict OpenGL profiling accuracy on macOS [28].

## Verification
1. **Check for Debug Prints in Release**: Search the codebase for `print(` and ensure all instances are wrapped in `if OS.is_debug_build():` or a `DEBUG` const check.
2. **Verify Headless CI/CD Exit Codes**: Run `godot --headless -s test_runner.gd` in PowerShell. Verify the process exits with code `0` for success and `1` for failure.
3. **Monitor Orphan Nodes**: In a debug build, run the game and periodically call `Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT)`. Ensure the count does not grow indefinitely after closing transient scenes.
4. **Profile in Release**: Run the game with `godot --release` (or export a release build). Open the Profiler and verify frame times are < 16.67ms for 60 FPS targets.

## Related skills
- Master Skill: [godot-master](../godot-master/SKILL.md)
