---
name: bevy-character-movement
description: "Docs-first stub for Bevy character movement. Godot counterpart: godot-characterbody-2d. Not a full port. Keywords: Bevy, movement, ECS, fixed timestep."
---

# Bevy character movement (docs-first stub)

Not a full port. No Rust crate in this phase.

## When to use

Load this when a Bevy app needs a player or actor that moves in discrete steps (walk, jump feel, ground check) and you need the ECS shape before any solver code exists. Coyote time and a jump buffer are design notes. They are not a node port.

## ECS shape

- **Components** own pose and intent: position, velocity, and a jump-buffer or coyote timer as data. The Quick Start ECS page shows components as Rust structs that derive `Component`.
- **Resources** own clocks and tuning shared by every mover. `bevy::time` 0.20.0 documents `Time`, `Fixed` (fixed timestep clock), and `Virtual`.
- **Systems** read intent and write velocity or position. Register them on the fixed schedule, not on a per-node physics callback.
- **Schedule:** `run_fixed_main_schedule` runs `FixedMain` from virtual time (`bevy::time` 0.20.0). Order dependent systems with `.chain()` (ECS page). Do not paste a Godot physics-process function.

## Godot idea to Bevy idiom

| Idea | Bevy idiom (idea only) |
| --- | --- |
| Body that you move yourself | Entity with movement components and a system |
| Step that should stay stable when frame time changes | System on the fixed timestep (`Fixed` / `FixedMain`) |
| Coyote time, jump buffer | Timer data on the entity or a small resource, consumed by the movement system |
| Collision response | Not in this stub. See bevy-physics-3d gaps |

## Gaps

- No verified character-controller type in the `bevy` 0.20.0 crate docs opened for this pass. The feature list has no physics solver.
- Do not call `move_and_slide`, `_physics_process`, or `CharacterBody2D`.
- Ground detection, shape casts, and collision layers are unverified. Do not invent query APIs.


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
- Do not step locomotion on raw `Update` when the step must stay stable. WHY: `bevy::time` documents `Fixed` and `run_fixed_main_schedule` (`FixedMain`) for a fixed clock.
- Do not call `move_and_slide`, `_physics_process`, or `CharacterBody2D`. WHY: those are Godot types. This skill only owns ECS movement data.
- Do not invent a character-controller or shape-cast API. WHY: no verified controller type was opened in the `bevy` crate docs for this pass.
- Do not mutably query the same movement component from two unordered systems. WHY: systems run in parallel unless `.chain()` orders them.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/)  -  Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/)  -  Unversioned API index.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch.
- [Quick Start: ECS](https://bevy.org/learn/quick-start/getting-started/ecs/)  -  Entities, `Component`, systems, `Query`, `Commands`, and `.chain()`.
- [bevy::time](https://docs.rs/bevy/latest/bevy/time/index.html)  -  `Time`, `Fixed`, and `run_fixed_main_schedule` (`FixedMain`).

### Related Skills

#### Prerequisites
- [bevy-master](../SKILL.md)  -  ECS ownership, schedules, and which Bevy skill to load.

#### Complements
- [bevy-physics-3d](physics-3d.md)  -  Collision and solver gaps. Player motion stays in this stub.
- [godot-characterbody-2d](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-characterbody-2d/SKILL.md)  -  Godot counterpart. Source idea only. Do not import Godot types.

#### Downstream / consumers
- None yet. Genre skills are not ported.

#### Master
- [bevy-master](../SKILL.md)  -  Bevy router.
