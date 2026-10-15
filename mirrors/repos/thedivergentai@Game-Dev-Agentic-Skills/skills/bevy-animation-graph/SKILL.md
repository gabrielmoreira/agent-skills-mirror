---
name: bevy-animation-graph
description: "Bevy ECS skill for animation blending. Keywords: Bevy, AnimationGraph, blend, AnimationGraphHandle, AnimationNodeType."
---

# Bevy animation graph

## When to use

Load this when clips must blend, add, or mask. Single-clip playback stays on bevy-animation.

## ECS shape

- **Assets:** `AnimationGraph` describes how clips blend. `add_clip` parents a clip node. `add_blend` parents a blend node. `add_clip_with_mask` stores a `u64` mask (bone groups you assign; `0` means no mask).
- **Components:** `AnimationGraphHandle` is a handle to the graph used by the `AnimationPlayer` on the same entity. `AnimationTransitions` crossfades between nodes.
- **Weights:** `ActiveAnimation::set_weight` on the player, after `play`, drives a node that is already in the graph.
- **Systems:** evaluation still runs through the animation player systems. Do not add a second player.

```rust
#[derive(Resource)]
struct LocomotionNodes {
    graph: Handle<AnimationGraph>,
    walk: AnimationNodeIndex,
    run: AnimationNodeIndex,
}

fn build_locomotion_graph(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    mut graphs: ResMut<Assets<AnimationGraph>>,
) {
    let mut graph = AnimationGraph::new();
    let blend = graph.add_blend(0.5, graph.root);
    let walk = graph.add_clip(
        asset_server.load(GltfAssetLabel::Animation(0).from_asset("models/fox.glb")),
        1.0,
        blend,
    );
    let run = graph.add_clip_with_mask(
        asset_server.load(GltfAssetLabel::Animation(1).from_asset("models/fox.glb")),
        0b0011,
        1.0,
        blend,
    );
    let handle = graphs.add(graph);
    commands.insert_resource(LocomotionNodes {
        graph: handle,
        walk,
        run,
    });
}
```

```rust
#[derive(Resource)]
struct LocomotionNodes {
    graph: Handle<AnimationGraph>,
    walk: AnimationNodeIndex,
    run: AnimationNodeIndex,
}

fn attach_player(
    mut commands: Commands,
    nodes: Res<LocomotionNodes>,
    mut players: Query<(Entity, &mut AnimationPlayer), Without<AnimationGraphHandle>>,
) {
    for (entity, mut player) in &mut players {
        commands.entity(entity).insert((
            AnimationGraphHandle(nodes.graph.clone()),
            AnimationTransitions::new(),
        ));
        player.play(nodes.walk).repeat();
        player.play(nodes.run).repeat();
    }
}
```

```rust
#[derive(Resource)]
struct LocomotionNodes {
    graph: Handle<AnimationGraph>,
    walk: AnimationNodeIndex,
    run: AnimationNodeIndex,
}

#[derive(Component)]
struct RunBlend(f32);

fn sync_blend(mut players: Query<(&mut AnimationPlayer, &RunBlend)>, nodes: Res<LocomotionNodes>) {
    for (mut player, blend) in &mut players {
        if let Some(active) = player.animation_mut(nodes.run) {
            active.set_weight(blend.0.clamp(0.0, 1.0));
        }
        if let Some(active) = player.animation_mut(nodes.walk) {
            active.set_weight(1.0 - blend.0.clamp(0.0, 1.0));
        }
    }
}
```

```rust
use std::time::Duration;

#[derive(Resource)]
struct LocomotionNodes {
    graph: Handle<AnimationGraph>,
    walk: AnimationNodeIndex,
    run: AnimationNodeIndex,
}

#[derive(Component)]
struct RunBlend(f32);

fn fade_to_run(
    nodes: Res<LocomotionNodes>,
    mut query: Query<(&mut AnimationPlayer, &mut AnimationTransitions, &RunBlend)>,
) {
    for (mut player, mut transitions, blend) in &mut query {
        if blend.0 > 0.5 {
            transitions.play(&mut player, nodes.run, Duration::from_millis(180));
        }
    }
}
```

```toml
[dependencies]
bevy = "0.20"
```

## Graph choices

| Need | Bevy approach |
| --- | --- |
| Blend clips | `AnimationGraph` plus `AnimationGraphHandle` |
| Gameplay mode | App or entity states stay on bevy-state-machines. The graph is not that state type. |
| Additive layer | `AnimationGraph::add_additive_blend` inserts `AnimationNodeType::Add`. Clip weights still go through `ActiveAnimation::set_weight`. |

## Scope

- Crossfades use `AnimationTransitions::play` with a `Duration`, as in `fade_to_run`.
- Persisting a graph is `SerializedAnimationGraph` plus `ron`. A 1D or 2D blend-space type is not part of `AnimationGraph`; blend with node weights.

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
| Per-entity data | `Component` + `Query` | A script field copied onto the entity |
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

- No AnimationTree, BlendSpace, or scene-tree state-machine types in Bevy code. WHY: `AnimationGraph`, `AnimationGraphHandle`, and `AnimationTransitions` are the documented Bevy pieces.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

Official links stay on bevy.org. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-animation](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-animation/SKILL.md) - Player and clips the graph drives.

#### Complements
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Gameplay mode is not an animation graph.
- [godot-animation-tree-mastery](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-animation-tree-mastery/SKILL.md) - Same topic on the Godot track.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
