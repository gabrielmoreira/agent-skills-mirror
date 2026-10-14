---
name: bevy-physics-3d
description: "Bevy ECS skill for 3D physics. Keywords: Bevy, physics, ECS, 3D."
---

# Bevy 3D physics

## When to use

Load this when a Bevy app needs simulated 3D bodies (props, impulses, constraints) before choosing a solver. Pair with bevy-character-movement for player motion that should not be a rigid body.

## ECS shape

- **Components** would own body kind, velocity, and collider data once a solver crate is chosen. The ECS page only shows plain `Component` structs. It does not define a rigid body.
- **Resources** would own gravity and solver settings. Check the solver docs before naming those fields.
- **Systems** would step the solver on a fixed schedule. `bevy::time` 0.20.0 documents `Fixed` and `run_fixed_main_schedule` (`FixedMain`). That is a clock, not a physics engine.
- **Schedule:** fixed timestep for the step; `.chain()` when a system must see the step result before it runs (ECS page).

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Simulated prop | Entity plus solver-defined components, after a crate is verified |
| Player locomotion | Not a rigid body. Use bevy-character-movement |
| Joints, ragdolls, bones driven by physics | Choose a physics solver before adding joints, ragdolls, or physics-driven bones. |
| Layers and masks | Unverified. Do not copy Godot bit names |

## Scope

- The `bevy` 0.20.0 crate feature list on docs.rs has no physics-engine feature. Jolt, a Godot physical-bone type, and Godot joint types are not Bevy names. Do not pretend those APIs exist.
- Third-party plugins are allowed by the plugins page (add a crate, then `add_plugins`). Check a 3D physics crate's own docs before naming its plugin path.
- Raycasts, CCD, and collision events are unverified.

## Expert Knowledge Delta

Target: **Bevy 0.20+**.

Core ECS types: `Component`, `Resource`, `Query`, `Commands`, `Startup`, `Update`, `Fixed` / `FixedMain` (`bevy::time`), `.chain()`, `Plugin`, `DefaultPlugins`, `MinimalPlugins`. Messages and observers are an ownership slot. See `bevy-events-messaging` for their APIs. Systems run in parallel unless `.chain()` orders the ones that conflict.

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
| An API outside the documented set | Check the official docs first | A made-up crate or API |

Load [references/ecs-ownership.md](references/ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not name Jolt, a Godot physical-bone type, or Godot joint types as Bevy APIs. WHY: the `bevy` feature list has no physics-engine feature.
- Do not pin Avian, Rapier, or any other solver crate. Check a solver crate's own docs before naming its plugin path.
- Do not treat `Fixed` / `FixedMain` as a physics engine. WHY: `bevy::time` documents a clock, not a solver.
- Do not mutably query the same body component from two unordered systems. WHY: systems run in parallel unless `.chain()` orders them.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/) - Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/)  -  Unversioned API index. The 0.20.0 feature list has no physics-engine feature.
- [Assets](https://bevy.org/assets/)  -  Official asset catalog. No physics plugin is named from it here.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch.
- [Quick Start: plugins](https://bevy.org/learn/quick-start/getting-started/plugins/)  -  `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and third-party `add_plugins`.
- [bevy::time](https://docs.rs/bevy/latest/bevy/time/index.html)  -  `Fixed` and `run_fixed_main_schedule` (`FixedMain`) as a clock, not a solver.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  ECS ownership and the fixed-timestep schedule names.

#### Complements
- [bevy-character-movement](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-character-movement/SKILL.md)  -  Player locomotion that should not be a rigid body.
- [godot-physics-3d](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-physics-3d/SKILL.md)  -  Equivalent Godot skill. Jolt, physical bones, and Godot joint types are not Bevy names.

#### Downstream / consumers
- Combat, racing, and shooter skills cover hits, vehicles, and shots.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Bevy router.
