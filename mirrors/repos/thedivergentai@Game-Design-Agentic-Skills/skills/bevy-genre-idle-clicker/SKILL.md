---
name: bevy-genre-idle-clicker
description: "Route a Bevy 0.20 idle clicker: one Wallet resource, generator entities, click on Update, offline bank capped in hours. Keywords: Bevy, idle, clicker, Wallet, Generator, offline, chain, ECS."
---

# Bevy Idle clicker (thin router)

Genre router. Domain work lives in the Bevy skills below.

## When to use

Load this for currencies that tick while the app runs.

## ECS shape

- **Components** hold the genre's per-entity flags as plain data. This file does not name new engine types.
- **Resources** hold run-wide counters (score, wave index, seed) via bevy-data-resources.
- **Systems** read those components on `Update` or the fixed timestep from bevy-master. Order them with `.chain()` when a later system must see the result.
- **Schedule:** gameplay mode changes go through bevy-state-machines. Do not invent a genre plugin.

## Routing

- [bevy-economy-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-economy-system/SKILL.md) - Currencies.
- [bevy-ui-layout](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ui-layout/SKILL.md) - Click target.
- [bevy-input-handling](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-input-handling/SKILL.md) - Click.
- [bevy-save-load](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-save-load/SKILL.md) - Offline progress.

## Examples

```toml
[dependencies]
bevy = "0.20"
serde = { version = "1", features = ["derive"] }
```

The wallet is one resource. Generators add coins on `Update` from `Time::delta_secs`.

```rust
#[derive(Resource)]
struct Wallet {
    coins: f64,
    per_second: f64,
}

fn tick_income(time: Res<Time>, mut wallet: ResMut<Wallet>) {
    wallet.coins += wallet.per_second * f64::from(time.delta_secs());
}

fn click(
    mouse: Res<ButtonInput<MouseButton>>,
    mut wallet: ResMut<Wallet>,
) {
    if mouse.just_pressed(MouseButton::Left) {
        wallet.coins += 1.0;
    }
}

fn install_income(app: &mut App) {
    app.insert_resource(Wallet {
        coins: 0.0,
        per_second: 2.5,
    })
    .add_systems(Update, (tick_income, click).chain());
}
```

Each building is an entity. One system writes the wallet so the generators cannot race each other.

```rust
#[derive(Component)]
struct Generator {
    rate: f64,
    owned: u32,
}

#[derive(Resource)]
struct Wallet {
    coins: f64,
    per_second: f64,
}

fn generators_to_wallet(
    gens: Query<&Generator>,
    mut wallet: ResMut<Wallet>,
    time: Res<Time>,
) {
    let mut rate = 0.0;
    for building in &gens {
        rate += building.rate * f64::from(building.owned);
    }
    wallet.per_second = rate;
    wallet.coins += rate * f64::from(time.delta_secs());
}
```

`tick_income` and `generators_to_wallet` both write `Wallet`. Run only one of them, or `.chain()` them if a later system must see the sum.

Offline progress stores a unix second, then banks elapsed time the next time the resource is inserted.

```rust
use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Resource, Clone, Serialize, Deserialize)]
struct IdleClock {
    last_unix: u64,
    per_second: f64,
    banked: f64,
}

fn bank_offline(mut clock: ResMut<IdleClock>) {
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(clock.last_unix);
    let elapsed = now.saturating_sub(clock.last_unix).min(8 * 60 * 60);
    clock.banked += clock.per_second * elapsed as f64;
    clock.last_unix = now;
}

#[derive(Resource)]
struct Wallet {
    coins: f64,
}

fn claim(mut clock: ResMut<IdleClock>, mut wallet: ResMut<Wallet>) {
    wallet.coins += clock.banked;
    clock.banked = 0.0;
}
```

`bank_offline` and `claim` both mutate `IdleClock`, so chain them. Persistence of the struct belongs on bevy-save-load.

## Scope

- Currencies, the click, and the layout route to the skills in Routing.
- Cap offline time in the resource (the example caps at eight hours) so a bad clock cannot mint unbounded coins.

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
| Per-entity data | `Component` + `Query` | A field stored off the entity |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Use the examples in this skill | A made-up crate or API |

Load [references/ecs-ownership.md](references/ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- Do not let `tick_income` and `generators_to_wallet` both add `Wallet.coins` unless they are `.chain()`ed or only one is installed. WHY: unordered systems run in parallel and one income write is dropped.
- Do not leave offline elapsed uncapped. WHY: a clock jump mints unbounded coins into the wallet resource.
- No invented genre APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- Do not pick a physics or net crate here. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Official pages stay on the unversioned `latest` branch.

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
- [godot-genre-idle-clicker](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-genre-idle-clicker/SKILL.md) - Idle clicker on the Godot engine, same depth.
- [bevy-economy-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-economy-system/SKILL.md) - Currencies.
- [bevy-ui-layout](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ui-layout/SKILL.md) - Click target.
- [bevy-input-handling](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-input-handling/SKILL.md) - Click.
- [bevy-save-load](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-save-load/SKILL.md) - Offline progress.

#### Downstream / consumers
- None. This router does not own a second implementation.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
