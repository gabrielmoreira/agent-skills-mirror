---
name: bevy-mechanic-secrets
description: "Bevy ECS skill for secrets and discovery flags. Keywords: Bevy, secrets, discovery, flags, ECS."
---

# Bevy secrets mechanic

## When to use

Load this when the player uncovers optional flags that must persist.

## ECS shape

- **Components:** a secret id and a found-set resource you define.
- **Resources:** run-wide tables live in a resource (bevy-data-resources), not an autoload.
- **Systems:** mutate those components on `Update` or the fixed timestep. Use `.chain()` when damage must land before death.
- **Messages:** one-shot facts (hit, pickup, quest advance) go through bevy-events-messaging. This file does not add a new event type name.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Secret id | A component on the world object. |
| Found set | A resource of ids. |
| Persist | Hand the set to bevy-save-load. |

## Scope

Secret ids, a discovered set, look-at checks, and timed input sequences are components and resources you own. Persistence of that set belongs on bevy-save-load.

## Examples

```toml
[dependencies]
bevy = "0.20"
serde = { version = "1", features = ["derive"] }
```

Discovering a secret inserts its id once. A later system can hand `Discovered` to the save skill.

```rust
use serde::{Deserialize, Serialize};
use std::collections::HashSet;

#[derive(Component)]
struct Secret {
    id: u32,
    radius: f32,
}

#[derive(Component)]
struct Seeker;

#[derive(Resource, Default, Serialize, Deserialize)]
struct Discovered {
    ids: HashSet<u32>,
}

fn discover(
    seekers: Query<&Transform, With<Seeker>>,
    secrets: Query<(&Transform, &Secret)>,
    mut found: ResMut<Discovered>,
) {
    for seeker in &seekers {
        for (tf, secret) in &secrets {
            if seeker.translation.distance(tf.translation) <= secret.radius {
                found.ids.insert(secret.id);
            }
        }
    }
}

fn look_at_secret(
    seekers: Query<&Transform, With<Seeker>>,
    secrets: Query<(&Transform, &Secret)>,
    mut found: ResMut<Discovered>,
) {
    for seeker in &seekers {
        let forward = seeker.forward().as_vec3();
        for (tf, secret) in &secrets {
            let to = tf.translation - seeker.translation;
            let dist = to.length();
            if dist < 0.001 || dist > 6.0 {
                continue;
            }
            if (to / dist).dot(forward) > 0.98 {
                found.ids.insert(secret.id);
            }
        }
    }
}
```

A sequence matcher keeps a rolling window. The classic up-up-down-down-left-right-left-right pattern unlocks when the tail matches before the window expires.

```rust
#[derive(Resource)]
struct SequenceSecret {
    pattern: Vec<KeyCode>,
    heard: Vec<KeyCode>,
    time_left: f32,
    window: f32,
    unlocked: bool,
}

impl Default for SequenceSecret {
    fn default() -> Self {
        Self {
            pattern: vec![
                KeyCode::ArrowUp,
                KeyCode::ArrowUp,
                KeyCode::ArrowDown,
                KeyCode::ArrowDown,
                KeyCode::ArrowLeft,
                KeyCode::ArrowRight,
                KeyCode::ArrowLeft,
                KeyCode::ArrowRight,
            ],
            heard: Vec::new(),
            time_left: 0.0,
            window: 2.5,
            unlocked: false,
        }
    }
}

#[derive(Resource, Default)]
struct Discovered {
    ids: std::collections::HashSet<u32>,
}

fn match_sequence(time: Res<Time>, keys: Res<ButtonInput<KeyCode>>, mut seq: ResMut<SequenceSecret>) {
    if seq.unlocked {
        return;
    }
    let dt = time.delta_secs();
    seq.time_left = (seq.time_left - dt).max(0.0);
    if seq.time_left == 0.0 {
        seq.heard.clear();
    }
    let watched = [
        KeyCode::ArrowUp,
        KeyCode::ArrowDown,
        KeyCode::ArrowLeft,
        KeyCode::ArrowRight,
    ];
    for key in watched {
        if keys.just_pressed(key) {
            seq.heard.push(key);
            seq.time_left = seq.window;
        }
    }
    if seq.heard.len() > seq.pattern.len() {
        let extra = seq.heard.len() - seq.pattern.len();
        seq.heard.drain(0..extra);
    }
    if seq.heard == seq.pattern {
        seq.unlocked = true;
        seq.heard.clear();
    }
}

#[derive(Resource)]
struct ProgressUnlock {
    cleared: u32,
    total: u32,
    unlocked: bool,
}

fn unlock_by_progress(mut progress: ResMut<ProgressUnlock>, mut found: ResMut<Discovered>) {
    if progress.unlocked || progress.total == 0 {
        return;
    }
    if progress.cleared * 100 / progress.total >= 80 {
        progress.unlocked = true;
        found.ids.insert(9001);
    }
}

pub struct SecretsPlugin;

impl Plugin for SecretsPlugin {
    fn build(&self, app: &mut App) {
        app.init_resource::<Discovered>()
            .init_resource::<SequenceSecret>()
            .insert_resource(ProgressUnlock {
                cleared: 0,
                total: 10,
                unlocked: false,
            })
            .add_systems(Update, (match_sequence, unlock_by_progress));
    }
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
| Per-entity data | `Component` + `Query` | A Godot node script |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Check the official docs first | A made-up crate or API |

Load [references/ecs-ownership.md](mechanic-secrets-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No Godot node, resource, or signal types for this mechanic. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

- No Godot types in Bevy code. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- `bevy crate` - API reference and Cargo feature list.
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-save-load](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-save-load/SKILL.md) - Persist flags.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md) - Tables and definitions.
- [bevy-events-messaging](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-events-messaging/SKILL.md) - One-shot facts.

#### Complements
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Mode flags.
- [godot-mechanic-secrets](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-mechanic-secrets/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
