---
name: bevy-navigation
description: "Bevy ECS skill for navigation. Keywords: Bevy, navigation, pathfinding, ECS."
---

# Bevy navigation

## When to use

Load this when agents need a path over walkable space before adding a crate. Movement of the actor after a path exists belongs on bevy-character-movement. Policy for chase, patrol, and retarget belongs on bevy-ai-navigation.

## ECS shape

- **Components** may store a goal `Transform` target and a path as your own data (a list of positions you define). The ECS page allows plain `Component` structs. It does not define a nav agent.
- **Resources** would own a map. None was opened.
- **Systems** that follow a path you already computed should move on `Fixed` / `FixedMain` (`bevy::time`) and use `.chain()` when the next waypoint must be visible before motion. Check the docs for a path-computation API before writing one.
- **Schedule:** do not invent a navigation schedule name.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Navigation agent | Check the docs for an agent component before writing one. |
| Baked region | Unverified. Do not copy Godot bake calls |
| Avoidance | Unverified |
| Next waypoint | Your component data, then bevy-character-movement |

## Scope

- Check docs.rs `bevy` `latest` (0.20.0 on bevy-master) for a navigation module before naming mesh, link, layer, or cost types.
- `add_plugins` allows a third-party crate later. No navigation plugin path is named here. Check the assets catalog before choosing one.
- Runtime rebake, stuck recovery, and crowd radius are unverified.

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
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No Godot navigation agent, region, or server types. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No named third-party navigation crate as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented bake, avoidance, or path-query APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

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
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - ECS ownership.
- [bevy-character-movement](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-character-movement/SKILL.md) - How an actor moves once a waypoint exists.

#### Complements
- [bevy-ai-navigation](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ai-navigation/SKILL.md) - Chase, patrol, and retarget policy. Not the mesh.
- [godot-navigation-pathfinding](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-navigation-pathfinding/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- Genre skills route chase, patrol, and similar policies.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
