---
name: bevy-animation
description: "Bevy ECS skill for animation playback. Keywords: Bevy, AnimationPlayer, AnimationClip, AnimationPlugin, animate_targets."
---

# Bevy animation playback

## When to use

Load this when an entity should play an AnimationClip. Blend graphs belong on bevy-animation-graph. 2D sprite specifics belong on bevy-2d-animation.

## ECS shape

- **Components:** `AnimationPlayer` controls playback. `AnimatedBy` links a target entity to the player entity. `AnimationTargetId` selects which curves apply.
- **Assets:** `AnimationClip` holds `VariableCurve` entries.
- **Systems:** `advance_animations` advances time. `animate_targets` writes the curves. `AnimationPlugin` adds animation support.
- **Events:** `AnimationEvent` can be triggered from a clip. Check the animation docs for observer wiring beyond the trait name.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Timeline player | AnimationPlayer on an entity, not a node |
| Clip asset | AnimationClip |
| Which bone or field | AnimationTargetId plus AnimatedBy |
| Repeat | RepeatAnimation |

## Scope

- Check the `AnimationPlayer` docs for method names such as play, pause, and seek before writing them.
- glTF curve loading is a separate module (`gltf_curves`) and the `gltf_animation` feature. Check those docs for loader steps before writing them.
- Check the animation docs for root-motion extraction before writing it.

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

- No Godot AnimationPlayer node or track types. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

- No Godot types in Bevy code. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/) - Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/) - API reference and Cargo feature list.
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.
- [bevy::animation](https://docs.rs/bevy/latest/bevy/animation/index.html) - Player, clip, plugin, advance and animate systems.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.

#### Complements
- [bevy-animation-graph](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-animation-graph/SKILL.md) - Blend instead of a single clip.
- [bevy-2d-animation](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-2d-animation/SKILL.md) - Sprite targets.
- [bevy-asset-scenes](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-asset-scenes/SKILL.md) - Load clip assets.
- [godot-animation-player](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-animation-player/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- [bevy-animation-graph](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-animation-graph/SKILL.md) - Consumes clips.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
