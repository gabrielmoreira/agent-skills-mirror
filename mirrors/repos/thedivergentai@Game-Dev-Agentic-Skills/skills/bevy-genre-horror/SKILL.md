---
name: bevy-genre-horror
description: "Bevy 0.20 horror router: sanity, stalker suspicion, and light energy as ECS data, with lighting, audio, and navigation in the linked skills. Use when routing a horror game. Keywords: Bevy, Horror, sanity, stalker, ECS, router."
---

# Bevy Horror (thin router)

Genre router. Domain work lives in the Bevy skills below.

## When to use

Load this for sanity or detection as your components, plus lighting and audio.

## ECS shape

- **Components** hold the genre's per-entity flags as plain data. This file does not name new engine types.
- **Resources** hold run-wide counters (score, wave index, seed) via bevy-data-resources.
- **Systems** read those components on `Update` or the fixed timestep from bevy-master. Order them with `.chain()` when a later system must see the result.
- **Schedule:** gameplay mode changes go through bevy-state-machines. This file registers only the sanity, suspicion, and light systems.

## Routing

- [bevy-3d-lighting](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-3d-lighting/SKILL.md) - Darkness.
- [bevy-audio-systems](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-audio-systems/SKILL.md) - Stingers.
- [bevy-ai-navigation](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ai-navigation/SKILL.md) - Stalker policy.
- [bevy-mechanic-secrets](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-mechanic-secrets/SKILL.md) - Lore flags.

## Scope

Sanity, suspicion, and light energy live on components. Darkness, stingers, and stalker paths stay in the skills linked above.

| Call | Owner here | Leave to the linked skill |
| --- | --- | --- |
| Fear falls while the player is vulnerable | `Sanity` on `FixedUpdate` | A light or audio crate |
| The stalker has line of sight | `Stalker.sees_player` and `suspicion` | Pathfinding in bevy-ai-navigation |
| A held light spends energy | `LightCell.energy` | Spotlights in bevy-3d-lighting |

```toml
[dependencies]
bevy = "0.20"
```

```rust
#[derive(Component)]
#[require(Transform)]
struct Sanity {
    value: f32,
}

#[derive(Resource)]
struct SanityDrain(f32);

fn drain_sanity(time: Res<Time>, drain: Res<SanityDrain>, mut minds: Query<&mut Sanity>) {
    let step = drain.0 * time.delta_secs();
    for mut sanity in &mut minds {
        sanity.value = (sanity.value - step).max(0.0);
    }
}

pub struct SanityPlugin;

impl Plugin for SanityPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(SanityDrain(4.0))
            .add_systems(FixedUpdate, drain_sanity);
    }
}
```

```rust
#[derive(Component)]
struct Stalker {
    suspicion: f32,
    sees_player: bool,
}

fn raise_suspicion(time: Res<Time>, mut stalkers: Query<&mut Stalker>) {
    for mut stalker in &mut stalkers {
        if stalker.sees_player {
            stalker.suspicion = (stalker.suspicion + time.delta_secs()).min(1.0);
        } else {
            stalker.suspicion = (stalker.suspicion - time.delta_secs() * 0.25).max(0.0);
        }
    }
}

pub struct StalkerPlugin;

impl Plugin for StalkerPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(FixedUpdate, raise_suspicion);
    }
}
```

```rust
#[derive(Component)]
#[require(Transform)]
struct Sanity {
    value: f32,
}

#[derive(Component)]
struct LightCell {
    energy: f32,
}

fn spend_light(time: Res<Time>, mut lights: Query<&mut LightCell>) {
    for mut light in &mut lights {
        light.energy = (light.energy - time.delta_secs() * 2.0).max(0.0);
    }
}

fn spawn_player(mut commands: Commands) {
    commands.spawn((Sanity { value: 100.0 }, LightCell { energy: 40.0 }));
}

pub struct HorrorSetupPlugin;

impl Plugin for HorrorSetupPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Startup, spawn_player)
            .add_systems(FixedUpdate, spend_light);
    }
}

fn main() {
    App::new()
        .add_plugins(MinimalPlugins)
        .add_plugins(HorrorSetupPlugin)
        .run();
}
```

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
| Per-entity data | `Component` + `Query` | One mutable blob shared by every entity |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| Behavior a linked domain skill already owns | Keep this router to components and resources | A second implementation in this file |

Load [references/ecs-ownership.md](references/ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- Do not drain sanity on raw `Update`. WHY: fear and light energy are simulation and belong on `FixedUpdate`.
- No invented genre APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- Do not pick a physics or net crate here. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Official pages stay on the unversioned site.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - ECS ownership and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Spawn and query shape.

#### Complements
- [bevy-3d-lighting](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-3d-lighting/SKILL.md) - Darkness.
- [bevy-audio-systems](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-audio-systems/SKILL.md) - Stingers.
- [bevy-ai-navigation](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ai-navigation/SKILL.md) - Stalker policy.
- [bevy-mechanic-secrets](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-mechanic-secrets/SKILL.md) - Lore flags.

#### Downstream / consumers
- None. This router does not own a second implementation.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
