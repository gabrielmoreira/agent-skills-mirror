---
name: bevy-physics-3d
description: "Docs-first stub for Bevy 3D physics. Godot counterpart: godot-physics-3d. Not a full port. Keywords: Bevy, physics, ECS, 3D."
---

# Bevy 3D physics (docs-first stub)

Not a full port. No Rust crate in this phase.

## When to use

Load this when a Bevy app needs simulated 3D bodies (props, impulses, constraints) and you need the gap list before choosing a solver. Pair with bevy-character-movement for player motion that should not be a rigid body.

## ECS shape

- **Components** would own body kind, velocity, and collider data once a solver crate is chosen. The ECS page only shows plain `Component` structs. It does not define a rigid body.
- **Resources** would own gravity and solver settings. Not specified in the pages opened here.
- **Systems** would step the solver on a fixed schedule. `bevy::time` 0.20.0 documents `Fixed` and `run_fixed_main_schedule` (`FixedMain`). That is a clock, not a physics engine.
- **Schedule:** fixed timestep for the step; `.chain()` when a system must see the step result before it runs (ECS page).

## Godot idea to Bevy idiom

| Idea | Bevy idiom (idea only) |
| --- | --- |
| Simulated prop | Entity plus solver-defined components, after a crate is verified |
| Player locomotion | Not a rigid body. Use bevy-character-movement |
| Joints, ragdolls, bones driven by physics | Unverified. Leave out until a solver page is opened |
| Layers and masks | Unverified. Do not copy Godot bit names |

## Gaps

- The `bevy` 0.20.0 crate feature list opened on docs.rs has no physics-engine feature. Jolt, a Godot physical-bone type, and Godot joint types are not Bevy names. Do not pretend those APIs exist.
- Third-party plugins are allowed by the plugins page (add a crate, then `add_plugins`). This pass did not open a specific 3D physics crate, so no plugin path is recorded.
- Raycasts, CCD, and collision events are unverified.


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
- Do not name Jolt, a Godot physical-bone type, or Godot joint types as Bevy APIs. WHY: the opened `bevy` feature list has no physics-engine feature.
- Do not pin Avian, Rapier, or any other solver crate. WHY: this pass did not open a specific 3D physics crate.
- Do not treat `Fixed` / `FixedMain` as a physics engine. WHY: `bevy::time` documents a clock, not a solver.
- Do not mutably query the same body component from two unordered systems. WHY: systems run in parallel unless `.chain()` orders them.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/) - Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/)  -  Unversioned API index. The opened 0.20.0 feature list had no physics-engine feature.
- [Assets](https://bevy.org/assets/)  -  Official asset catalog. No physics plugin was selected from it on this pass.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch.
- [Quick Start: plugins](https://bevy.org/learn/quick-start/getting-started/plugins/)  -  `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and third-party `add_plugins`.
- [bevy::time](https://docs.rs/bevy/latest/bevy/time/index.html)  -  `Fixed` and `run_fixed_main_schedule` (`FixedMain`) as a clock, not a solver.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-master/SKILL.md)  -  ECS ownership and the fixed-timestep schedule names this stub is allowed to use.

#### Complements
- [bevy-character-movement](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-character-movement/SKILL.md)  -  Player locomotion that should not be a rigid body.
- [godot-physics-3d](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-physics-3d/SKILL.md)  -  Godot counterpart. Source idea only. Jolt, physical bones, and Godot joint types are not Bevy names.

#### Downstream / consumers
- None yet. Combat, racing, and shooter skills are not ported.

#### Master
- [bevy-master](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-master/SKILL.md)  -  Bevy router.
