---
name: bevy-debugging-profiling
description: "Docs-first stub for Bevy logs and diagnostics. Godot counterpart: godot-debugging-profiling. Not a full port. Keywords: Bevy, LogPlugin, DiagnosticsPlugin, FrameTimeDiagnosticsPlugin."
---

# Bevy debugging and profiling (docs-first stub)

Not a full port. Diagnostics are plugins and a store resource. They are not a Godot profiler panel.

## When to use

Load this when a running app should print logs or record frame time, entity count, or process CPU and memory. `bevy::log::LogPlugin` and `bevy::diagnostic` on docs.rs `latest` (0.20.0) are the sources.

## ECS shape

- **Logs:** `LogPlugin` is part of `DefaultPlugins`. Override it with `DefaultPlugins.set(LogPlugin { level, filter, .. })`. The page's example uses `Level::DEBUG` and a filter string such as `wgpu=error,bevy_render=info,bevy_ecs=trace`. The same filter works as `RUST_LOG`. To bring your own collector, disable this plugin on `DefaultPlugins`.
- **Diagnostics core:** `DiagnosticsPlugin` adds the core resources. `DiagnosticsStore` holds the collection. `Diagnostic` is a timeline of `DiagnosticMeasurement` values addressed by `DiagnosticPath`. `RegisterDiagnostic` adds `register_diagnostic` on `App`.
- **Built-in plugins:** `FrameTimeDiagnosticsPlugin` adds frame time, fps, and frame count. `EntityCountDiagnosticsPlugin` adds an entity count. `SystemInformationDiagnosticsPlugin` adds `cpu_usage` and `mem_usage` percent. `LogDiagnosticsPlugin` prints diagnostics to the console. `FrameCount` / `FrameCountPlugin` count frames since start.
- **Order:** the log-diagnostics example adds these plugins after `DefaultPlugins` because they use the time plugin for timestamps.
- **Schedule:** you do not write the measurement systems yourself unless you register your own `Diagnostic`. Reading `DiagnosticsStore` from a system was not opened as a recipe.

## Godot idea to Bevy idiom

| Idea | Bevy idiom (idea only) |
| --- | --- |
| Print debug lines | `LogPlugin` filter or `RUST_LOG` |
| FPS readout | `FrameTimeDiagnosticsPlugin` |
| How many entities | `EntityCountDiagnosticsPlugin` |
| Process CPU and memory | `SystemInformationDiagnosticsPlugin` |
| Dump those numbers | `LogDiagnosticsPlugin` |

## Gaps

- Per-system flame graphs and Tracy wiring (`enable_tracy` appears as a field fragment on the log plugin page) were not opened as a setup guide.
- A custom `Diagnostic` registration example was not opened. Names stop at `Diagnostic`, `DiagnosticPath`, and `register_diagnostic`.
- Render-app diagnostic forwarding was not opened on docs.rs (an examples page mentions it; this skill does not copy that plugin path).


## Expert Knowledge Delta

Library target in prose: **Bevy 0.20.0**. Lattice URLs stay unversioned.

Opened canon only: `Component`, `Resource`, `Query`, `Commands`, `Startup`, `Update`, `Fixed` / `FixedMain` (`bevy::time`), `.chain()`, `Plugin`, `DefaultPlugins`, `MinimalPlugins`. Messages and observers are an ownership slot. This file does not invent their struct APIs. Systems run in parallel unless `.chain()` orders the ones that conflict.

### Who owns state

| Piece | Owner | Who may mutate | Schedule |
| --- | --- | --- | --- |
| Data on one entity | `Component` | One system via `Query` | `Update` or `FixedMain` |
| One value for the whole app | `Resource` | One system | `Startup` to insert, then the schedule that reads it |
| Spawn | `Commands` | The spawning system | `Startup` for the initial world; later schedules for runtime spawn |
| Order that must not race | `.chain()` | The chained systems only | Same schedule |
| Plugin boundary | `Plugin` | `build` registers systems and resources | Before the app runs |

Borrow rule: two systems that both mutably query the same component must be ordered (`.chain()`) or split so only one writes. Unrelated systems stay parallel. That is the ECS page rule, not a guess at a system-set API.

### Decision

| If you need | Do this | Do not |
| --- | --- | --- |
| Per-entity data | `Component` + `Query` | A Godot node script |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API this skill did not open | A Gaps row | A fabricated crate (solver, navmesh module, net, XR) |

Load `references/a-gate-notes.md` for the same table plus the gap rule.

## NEVER

- Do not put `/0.20.0/` in lattice URLs. WHY: permalinks stay on `latest`. The 0.20.0 pin belongs in prose once.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: those rows are gaps, blocked, or revisit.

- No Godot debugger, monitor, or profiler types. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No Tracy or external profiler setup this file did not open. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No third-party profiling crates. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No Creation Station content. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No umbrella skill over Godot and Bevy. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- Do not mark this row `ported`. It is `docs_mapped`. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/)  -  Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/)  -  Unversioned API index.
- [LogPlugin](https://docs.rs/bevy/latest/bevy/log/struct.LogPlugin.html)  -  Filter, level, `RUST_LOG`.
- [bevy::diagnostic](https://docs.rs/bevy/latest/bevy/diagnostic/index.html)  -  Store, frame time, entity count, system info, log plugin.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch.

### Related Skills

#### Prerequisites
- [bevy-master](../SKILL.md)  -  Who owns which piece of state.
- [bevy-project-foundations](project-foundations.md)  -  `DefaultPlugins` and `App`.

#### Complements
- [bevy-performance](performance.md)  -  What the frame-time numbers are for.
- [godot-debugging-profiling](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-debugging-profiling/SKILL.md)  -  Godot counterpart. Source idea only.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](../SKILL.md)  -  Bevy router.
