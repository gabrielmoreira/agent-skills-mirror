---
name: bevy-navigation
description: "Docs-first stub for Bevy navigation. Godot counterpart: godot-navigation-pathfinding. Not a full port. Keywords: Bevy, navigation, pathfinding, ECS, gaps."
---

# Bevy navigation (docs-first stub)

Not a full port. Bevy's opened pages do not ship a navigation mesh, agent, or avoidance solver. No third-party nav crate was chosen.

## When to use

Load this when agents need a path over walkable space and you need the gap list before adding a crate. Movement of the actor after a path exists belongs on bevy-character-movement. Policy for chase, patrol, and retarget belongs on bevy-ai-navigation.

## ECS shape

- **Components** may store a goal `Transform` target and a path as your own data (a list of positions you define). The ECS page allows plain `Component` structs. It does not define a nav agent.
- **Resources** would own a map. None was opened.
- **Systems** that follow a path you already computed should move on `Fixed` / `FixedMain` (`bevy::time`) and use `.chain()` when the next waypoint must be visible before motion. Computing the path itself has no opened API.
- **Schedule:** do not invent a navigation schedule name.

## Godot idea to Bevy idiom

| Idea | Bevy idiom (idea only) |
| --- | --- |
| Navigation agent | Unverified. No agent component was opened |
| Baked region | Unverified. Do not copy Godot bake calls |
| Avoidance | Unverified |
| Next waypoint | Your component data, then bevy-character-movement |

## Gaps

- docs.rs `bevy` `latest` (pin 0.20.0 on bevy-master) was not opened onto a navigation module. Do not invent mesh, link, layer, or cost types.
- The assets catalog was not used to select a navigation plugin. `add_plugins` allows a third-party crate later; this pass records no path.
- Runtime rebake, stuck recovery, and crowd radius are unverified.


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

- No Godot navigation agent, region, or server types. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No named third-party navigation crate as the chosen solver. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No invented bake, avoidance, or path-query APIs. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No Creation Station content. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No umbrella skill over Godot and Bevy. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- Do not mark this row `ported`. It is `docs_mapped`. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/) - Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/) - Unversioned API index. No navigation module was opened.
- [Assets](https://bevy.org/assets/) - Official asset catalog. No navigation plugin was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, `Query`, `Commands`, and `.chain()`.
- [bevy::time](https://docs.rs/bevy/latest/bevy/time/index.html) - `Fixed` and `FixedMain` for motion after a path exists.
- [Quick Start: plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `add_plugins` without a chosen nav crate.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-master/SKILL.md) - ECS ownership.
- [bevy-character-movement](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-character-movement/SKILL.md) - How an actor moves once a waypoint exists.

#### Complements
- [bevy-ai-navigation](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-ai-navigation/SKILL.md) - Chase, patrol, and retarget policy. Not the mesh.
- [godot-navigation-pathfinding](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-navigation-pathfinding/SKILL.md) - Godot counterpart. Source idea only.

#### Downstream / consumers
- None yet. Genre routers are not ported.

#### Master
- [bevy-master](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
