---
name: bevy-ability-system
description: "Bevy ECS skill for abilities. Keywords: Bevy, ability, cooldown, ECS, gameplay."
---

# Bevy ability system

## When to use

Load this when an actor grants, cools down, or spends an ability. Combat resolution stays on bevy-combat-system.

## ECS shape

- **Components:** ability id, charges, and cooldown remaining on the caster.
- **Resources:** run-wide tables live in a resource (bevy-data-resources).
- **Systems:** mutate those components on `Update` or the fixed timestep. Use `.chain()` when damage must land before death.
- **Messages:** one-shot facts (hit, pickup, quest advance) go through bevy-events-messaging. This file does not add a new event type name.

## Ability choices

| Need | Bevy idiom |
| --- | --- |
| Ability definition | A `Resource` catalog plus a component row on the caster. |
| Cooldown | `remaining` stepped with `Time<Fixed>::delta_secs` in `FixedUpdate`. |
| Cast | `MessageWriter<CastAccepted>` after the cooldown and charge gates pass. |

## Scope

- Cooldowns, charges, and catalogs are components and resources. Combat damage stays on bevy-combat-system.
- Stacking status effects is a component list you tick on `FixedUpdate`.

## Examples

```toml
[package]
name = "abilities"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = "0.20"
```

Cooldown and charges share the caster. Tick, then accept the cast, on `FixedUpdate`.

```rust
#[derive(Component)]
struct Cooldown {
    remaining: f32,
    duration: f32,
}

#[derive(Component)]
struct Charges {
    current: u32,
    max: u32,
}

#[derive(Message)]
struct CastAccepted {
    caster: Entity,
}

fn tick_cooldowns(time: Res<Time<Fixed>>, mut query: Query<&mut Cooldown>) {
    let dt = time.delta_secs();
    for mut cooldown in &mut query {
        cooldown.remaining = (cooldown.remaining - dt).max(0.0);
    }
}

fn try_cast(
    mut casters: Query<(Entity, &mut Cooldown, &mut Charges)>,
    mut casts: MessageWriter<CastAccepted>,
) {
    for (entity, mut cooldown, mut charges) in &mut casters {
        if cooldown.remaining > 0.0 || charges.current == 0 {
            continue;
        }
        charges.current -= 1;
        cooldown.remaining = cooldown.duration;
        casts.write(CastAccepted { caster: entity });
    }
}

fn recharge(time: Res<Time<Fixed>>, mut casters: Query<(&Cooldown, &mut Charges)>) {
    let dt = time.delta_secs();
    for (cooldown, mut charges) in &mut casters {
        if cooldown.remaining <= 0.0 && charges.current < charges.max && dt > 0.0 {
            charges.current += 1;
        }
    }
}

pub struct AbilityPlugin;

impl Plugin for AbilityPlugin {
    fn build(&self, app: &mut App) {
        app.add_message::<CastAccepted>()
            .add_systems(FixedUpdate, (tick_cooldowns, try_cast, recharge).chain());
    }
}
```

The catalog is one resource. Live cooldown stays on the entity.

```rust
#[derive(Clone, Copy)]
struct AbilityDef {
    id: u32,
    cooldown: f32,
    cost: u32,
}

#[derive(Resource)]
struct AbilityCatalog {
    rows: Vec<AbilityDef>,
}

fn lookup(catalog: &AbilityCatalog, id: u32) -> Option<&AbilityDef> {
    catalog.rows.iter().find(|row| row.id == id)
}

#[derive(Component)]
struct Cooldown {
    remaining: f32,
    duration: f32,
}

#[derive(Component)]
struct Charges {
    current: u32,
    max: u32,
}

fn spawn_caster(mut commands: Commands, catalog: Res<AbilityCatalog>) {
    let def = lookup(&catalog, 1);
    let duration = def.map(|row| row.cooldown).unwrap_or(0.5);
    commands.spawn((
        Cooldown {
            remaining: 0.0,
            duration,
        },
        Charges { current: 2, max: 2 },
    ));
}
```

A shared lock sits in a resource so one system owns it.

```rust
#[derive(Message)]
struct CastAccepted {
    caster: Entity,
}

#[derive(Resource)]
struct GlobalCooldown {
    remaining: f32,
}

fn tick_gcd(time: Res<Time<Fixed>>, mut gcd: ResMut<GlobalCooldown>) {
    gcd.remaining = (gcd.remaining - time.delta_secs()).max(0.0);
}

fn arm_gcd(mut gcd: ResMut<GlobalCooldown>, mut casts: MessageReader<CastAccepted>) {
    for _cast in casts.read() {
        gcd.remaining = gcd.remaining.max(0.4);
    }
}
```

Register `CastAccepted` with `add_message` in the same plugin that adds `tick_gcd` and `arm_gcd`.

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
| Per-entity data | `Component` + `Query` | A value stored off the entity |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Check the official docs first | A made-up crate or API |

Load [references/ecs-ownership.md](ability-system-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No cooldown stored in a process-global static. WHY: the caster's `Cooldown` component and the catalog `Resource` are the owners.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Permalinks stay unversioned.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-combat-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-combat-system/SKILL.md) - Hit resolution.
- [bevy-input-handling](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-input-handling/SKILL.md) - Cast input.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md) - Tables and definitions.
- [bevy-events-messaging](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-events-messaging/SKILL.md) - One-shot facts.

#### Complements
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Mode flags.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
