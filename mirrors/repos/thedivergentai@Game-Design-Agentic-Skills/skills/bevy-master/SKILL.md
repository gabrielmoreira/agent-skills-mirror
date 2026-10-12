---
name: bevy-master
description: "Bevy ECS hub for this library. Routes the docs-first Bevy domain skills. Use when starting a Bevy game, choosing ECS boundaries, or picking a Bevy skill. The parity matrix is the routing table. Keywords: Bevy, ECS, bevy-master, A-gate."
---

# Bevy Master: ECS hub

Docs-first hub for the Bevy library (A-gate depth, not a Phase-1 flood lock). Peer of the Godot hub, not a parent of it. The living matrix is the routing table. This file does not claim a full port of the Godot library. Networking stays blocked until 2026-11-11. XR stays revisit until 2026-11-11.

## Library target

Bevy stable pinned in this file's Reference on the implement date: **0.20.0** (crates.io, 2026-10-08; docs.rs `bevy` 0.20.0). Version hops do not live in this hub.

## Who owns what (ECS)

For every piece of state, name:

- which **component** or **resource** owns it
- which **system** may mutate it
- which message or observer should observe it

Schedules replace a scene tree. Do not add an autoload, a signal bus, or a Node layer cake.

The Quick Start ECS page (opened 2026-10-11) defines entities, components (`Component`), systems as functions, `Query`, `Commands`, `Startup`, and `Update`, plus `.chain()` for order. Messages, observers, resources, and app states are opened in the Batch B skills. See those files before calling a type.

## Decision matrix

| Scenario | Route |
| --- | --- |
| New Bevy app, ECS boundaries, which skill to load | This hub, then the matrix |
| New crate, Cargo features, feature folders | [bevy-project-foundations](references/project-foundations.md) |
| Entity composition, components, systems | [bevy-ecs-composition](references/ecs-composition.md) |
| Messages, events, observers | [bevy-events-messaging](references/events-messaging.md) |
| Components and resources as data | [bevy-data-resources](references/data-resources.md) |
| App states or a per-entity mode flag | [bevy-state-machines](references/state-machines.md) |
| App-wide resources and schedules | [bevy-app-resources](references/app-resources.md) |
| Character movement | [bevy-character-movement](references/character-movement.md) |
| 3D physics | [bevy-physics-3d](references/physics-3d.md) |
| 2D physics | [bevy-physics-2d](references/physics-2d.md) (gap: no solver crate) |
| Ray, overlap, or physics pick | [bevy-spatial-queries](references/spatial-queries.md) (gap: same solver) |
| Navigation mesh or path data | [bevy-navigation](references/ai-navigation.md) (gap: no nav module) |
| Chase, patrol, retarget | [bevy-ai-navigation](references/ai-navigation.md) |
| Seeded level or loot layout | [bevy-procedural-generation](references/procedural-generation.md) |
| Keyboard, mouse, gamepad | [bevy-input-handling](references/input-handling.md) |
| 2D or 3D camera entity | [bevy-camera-systems](references/camera-systems.md) |
| Play or control a clip | [bevy-audio-systems](references/audio-systems.md) |
| Load assets or spawn a scene | [bevy-asset-scenes](references/asset-scenes.md) |
| Player save slot | [bevy-save-load](references/save-load.md) (gap: no save format opened) |
| Logs and frame diagnostics | [bevy-debugging-profiling](references/debugging-profiling.md) |
| Parallelism, fixed step, handle lifetime | [bevy-performance](references/performance.md) |
| `cargo test` | [bevy-testing-patterns](references/testing-patterns.md) |
| Clips, blend graphs, sprites, lights, materials, UI, or a genre loop | Module directory below. Gaps stay in each skill |
| Godot language, version hops, CLI, or project audit | Stay on the Godot skill (`n_a_godot_only` in the matrix) |
| Networking or a dedicated server | Blocked until 2026-11-11. No Bevy skill |
| Console certification | `n_a_godot_only`. No Bevy skill |
| XR / VR | `revisit` until 2026-11-11. No XR module was opened |

## When not to spawn an entity

Data that is not simulated can be a plain Rust struct or a resource. The Quick Start treats resources as app-wide data (resources page linked from the same guide; this pass opened plugins and ECS, not the resources page body). Do not copy a Godot Object / RefCounted / Resource / Node table into Bevy.

## Workflows

**(a) App scaffold.** `App::new()`, plugins, schedules, and states. The plugins page documents `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`. The `bevy` 0.20.0 crate docs list a `bevy_state` feature ("built in global state machines"). This pass did not open the state API. Do not invent a plugin list beyond `DefaultPlugins` / `MinimalPlugins`.

**(b) Entity.** Components plus systems. Movement belongs on a fixed timestep. `bevy::time` 0.20.0 documents `Fixed` ("fixed timestep game clock") and `run_fixed_main_schedule` (`FixedMain`). Do not invent a schedule label beyond those names.

**(c) Data.** Components and resources. Not `.tres` files.

**(d) Performance.** The ECS page states systems run in parallel by default when they can, and `.chain()` forces order. Frame-time diagnostics and handle lifetimes are on `bevy-performance`. No numeric budget is copied here; the opened pages do not give one.


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

- No umbrella skill over Godot and Bevy. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No Godot or gdext type imports in Bevy code. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No GDScript line-translate. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No APIs that this file did not open. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No Coil or Ouroboros UI. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No Creation Station content. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No deleting Godot skills. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- Do not mark any row `ported`. These stubs are `docs_mapped`. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.

## Module directory

Domain skills (docs-first):

- [bevy-project-foundations](references/project-foundations.md)
- [bevy-ecs-composition](references/ecs-composition.md)
- [bevy-events-messaging](references/events-messaging.md)
- [bevy-data-resources](references/data-resources.md)
- [bevy-state-machines](references/state-machines.md)
- [bevy-app-resources](references/app-resources.md)
- [bevy-character-movement](references/character-movement.md)
- [bevy-physics-3d](references/physics-3d.md)
- [bevy-physics-2d](references/physics-2d.md)
- [bevy-spatial-queries](references/spatial-queries.md)
- [bevy-navigation](references/ai-navigation.md)
- [bevy-ai-navigation](references/ai-navigation.md)
- [bevy-procedural-generation](references/procedural-generation.md)
- [bevy-input-handling](references/input-handling.md)
- [bevy-camera-systems](references/camera-systems.md)
- [bevy-audio-systems](references/audio-systems.md)
- [bevy-asset-scenes](references/asset-scenes.md)
- [bevy-save-load](references/save-load.md)
- [bevy-debugging-profiling](references/debugging-profiling.md)
- [bevy-performance](references/performance.md)
- [bevy-testing-patterns](references/testing-patterns.md)

Rendering and animation:

- [bevy-2d-animation](references/2d-animation.md)
- [bevy-animation](references/2d-animation.md)
- [bevy-animation-graph](references/animation-graph.md)
- [bevy-particles](references/particles.md)
- [bevy-shaders](references/shaders.md)
- [bevy-tilemap](references/tilemap.md)
- [bevy-tweening](references/tweening.md)
- [bevy-3d-lighting](references/3d-lighting.md)
- [bevy-3d-materials](references/3d-materials.md)
- [bevy-3d-world-building](references/3d-world-building.md)

Gameplay:

- [bevy-ability-system](references/ability-system.md)
- [bevy-combat-system](references/combat-system.md)
- [bevy-dialogue-system](references/dialogue-system.md)
- [bevy-economy-system](references/economy-system.md)
- [bevy-game-loop-collection](references/game-loop-collection.md)
- [bevy-game-loop-harvest](references/game-loop-harvest.md)
- [bevy-game-loop-time-trial](references/game-loop-time-trial.md)
- [bevy-game-loop-waves](references/game-loop-waves.md)
- [bevy-inventory-system](references/inventory-system.md)
- [bevy-mechanic-revival](references/mechanic-revival.md)
- [bevy-mechanic-secrets](references/mechanic-secrets.md)
- [bevy-quest-system](references/quest-system.md)
- [bevy-rpg-stats](references/rpg-stats.md)
- [bevy-turn-system](references/turn-system.md)

UI, platforms, adapts, templates:

- [bevy-ui-layout](references/ui-layout.md)
- [bevy-ui-text](references/ui-text.md)
- [bevy-ui-theming](references/ui-theming.md)
- [bevy-platform-desktop](references/platform-desktop.md)
- [bevy-platform-web](references/platform-web.md)
- [bevy-platform-mobile](references/platform-mobile.md)
- [bevy-adapt-2d-to-3d](references/adapt-2d-to-3d.md)
- [bevy-adapt-3d-to-2d](references/adapt-3d-to-2d.md)
- [bevy-adapt-desktop-to-mobile](references/adapt-desktop-to-mobile.md)
- [bevy-adapt-mobile-to-desktop](references/adapt-mobile-to-desktop.md)
- [bevy-project-templates](references/project-templates.md)

Genre routers:

- [bevy-genre-action-rpg](references/genre-action-rpg.md)
- [bevy-genre-fighting](references/genre-fighting.md)
- [bevy-genre-platformer](references/genre-platformer.md)
- [bevy-genre-shooter](references/genre-shooter.md)
- [bevy-genre-shooter-fps](references/genre-shooter-fps.md)
- [bevy-genre-rts](references/genre-rts.md)
- [bevy-genre-tower-defense](references/genre-tower-defense.md)
- [bevy-genre-metroidvania](references/genre-metroidvania.md)
- [bevy-genre-open-world](references/genre-open-world.md)
- [bevy-genre-roguelike](references/genre-roguelike.md)
- [bevy-genre-survival](references/genre-survival.md)
- [bevy-genre-card-game](references/genre-card-game.md)
- [bevy-genre-educational](references/genre-educational.md)
- [bevy-genre-horror](references/genre-horror.md)
- [bevy-genre-puzzle](references/genre-puzzle.md)
- [bevy-genre-visual-novel](references/genre-visual-novel.md)
- [bevy-genre-romance](references/genre-romance.md)
- [bevy-genre-idle-clicker](references/genre-idle-clicker.md)
- [bevy-genre-party](references/genre-party.md)
- [bevy-genre-racing](references/genre-racing.md)
- [bevy-genre-rhythm](references/genre-rhythm.md)
- [bevy-genre-sandbox](references/genre-sandbox.md)
- [bevy-genre-simulation](references/genre-simulation.md)
- [bevy-genre-sports](references/genre-sports.md)
- [bevy-genre-stealth](references/genre-stealth.md)

No file: console (`n_a_godot_only`), XR (`revisit` 2026-11-11), export packaging (`n_a_godot_only`), networking and net-heavy genres (`blocked` until 2026-11-11). The matrix is the full list.

## Reference

Living matrix: [parity-matrix.md](references/parity-matrix.md) (full inventory).

docs.rs links use the unversioned `latest` permalink (same role as Godot `/en/stable/`). The library pin above stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/)  -  Unversioned hop index. Version numbers stay in prose; this link does not pin a release.
- [bevy crate](https://docs.rs/bevy/latest/bevy/)  -  Unversioned API index. Feature samples on the pinned page may still show older version strings.
- [Assets](https://bevy.org/assets/)  -  Official asset catalog.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch, not a release tag.
- [Quick Start](https://bevy.org/learn/quick-start/)  -  Guide index. The legacy `/learn/book/` path returned 404 on 2026-10-11.
- [Getting started](https://bevy.org/learn/quick-start/getting-started/)  -  App setup before ECS and plugins.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/)  -  Entities, components, systems, `Query`, `Commands`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/)  -  `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.
- [bevy::time](https://docs.rs/bevy/latest/bevy/time/index.html)  -  `Fixed` and `run_fixed_main_schedule` (`FixedMain`).
- [crates.io bevy](https://crates.io/crates/bevy)  -  Release pin source (0.20.0, 2026-10-08).

### Related Skills

#### Prerequisites
- None. This hub is the Bevy entry point.

#### Complements
- [godot-master](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-master/SKILL.md)  -  Peer hub for Godot. Language, version hops, CLI, and project audit stay there (`n_a_godot_only` in the matrix).

#### Downstream / consumers
- [bevy-project-foundations](references/project-foundations.md)  -  Crate, Cargo features, and layout habits.
- [bevy-ecs-composition](references/ecs-composition.md)  -  Components, spawn tuples, queries, and `.chain()`.
- [bevy-events-messaging](references/events-messaging.md)  -  `Message` readers and `Event` observers.
- [bevy-data-resources](references/data-resources.md)  -  `Component` versus `Resource`.
- [bevy-state-machines](references/state-machines.md)  -  `bevy::state` and per-entity mode flags.
- [bevy-app-resources](references/app-resources.md)  -  App-wide resources and `Startup` / `Update`.
- [bevy-character-movement](references/character-movement.md)  -  Player and actor motion on the fixed timestep.
- [bevy-physics-3d](references/physics-3d.md)  -  Simulated 3D bodies once a solver crate is verified.
- [bevy-physics-2d](references/physics-2d.md)  -  Simulated 2D bodies. Same solver gap.
- [bevy-spatial-queries](references/spatial-queries.md)  -  Casts and overlaps. Solver still unpicked.
- [bevy-navigation](references/ai-navigation.md)  -  Path data gap. No nav module opened.
- [bevy-ai-navigation](references/ai-navigation.md)  -  Chase and patrol policy.
- [bevy-procedural-generation](references/procedural-generation.md)  -  Seed resource and spawn. No noise API.
- [bevy-input-handling](references/input-handling.md)  -  `ButtonInput`, mouse, and gamepad.
- [bevy-camera-systems](references/camera-systems.md)  -  `Camera2d` and `Camera3d`.
- [bevy-audio-systems](references/audio-systems.md)  -  `AudioPlayer` and `AudioSink`.
- [bevy-asset-scenes](references/asset-scenes.md)  -  `AssetServer` and `spawn_scene`.
- [bevy-save-load](references/save-load.md)  -  Save-slot gap. Scene spawn is not a save.
- [bevy-debugging-profiling](references/debugging-profiling.md)  -  `LogPlugin` and diagnostics plugins.
- [bevy-performance](references/performance.md)  -  Parallel systems, fixed step, handle lifetimes.
- [bevy-testing-patterns](references/testing-patterns.md)  -  `cargo test`. Not GdUnit.

#### Master
- This file. Do not route Bevy work through a parent that also owns Godot.

Cipher rule titles only: Godot is source of truth; blockers on blocked and `n_a_godot_only` rows; runtime gameplay is Rust; do not pull Godot types into Bevy crates.

## Gaps

- Resources, states, messages, and observers: opened for the Batch B skills. Call only the types those skills cite. `App` state-installation method names are still unopened.
- The getting-started snippet still shows `bevy = "0.19"` while crates.io latest is 0.20.0. Pin **0.20.0** from crates.io and docs.rs, not from that stale snippet.
- docs.rs feature examples on the 0.20.0 page still show `version = "0.18"` in one sample. That sample is not the pin.
