---
name: bevy-ecs-composition
description: "Compose Bevy 0.20 entities from small components and systems. Use when spawning tuples with Commands, filtering Query with With, ordering writers with chain, or attaching ChildOf. Keywords: Bevy, ECS, Component, Query, Commands, chain, ChildOf."
---

# Bevy ECS composition

## When to use

Load this when gameplay data should be split across small components and systems, instead of one type that owns everything. The Quick Start ECS page is the source for the names below.

## ECS shape

- **Components** are Rust structs that derive `Component`. The ECS page splits `Person` and `Name` so more than one kind of entity can carry a name.
- **Entities** are spawned with `Commands` in a `Startup` system. The page spawns a tuple of components: `commands.spawn((Person, Name(...)))`.
- **Systems** are functions. `Query<&Name, With<Person>>` reads names on entities that also have `Person`. `Query<&mut Name, With<Person>>` writes. Register with `add_systems`.
- **Schedule:** `Startup` runs once. `Update` runs afterward. Systems run in parallel unless you call `.chain()`. The page chains `update_people` before `greet_people` and leaves an unrelated system outside the chain.

Spawn a tuple of components. A parent and child use `ChildOf`. Change detection uses `Changed`.

## Composition choices

| Need | Bevy idiom |
| --- | --- |
| Has-a parts on one object | Several `Component` structs on one entity |
| Behavior | A system function over a `Query` |
| Spawn at start | `Commands` in a `Startup` system |
| Ordered steps | `.chain()` on the systems that depend on each other |
| Parent and child | `ChildOf` on the child entity |

## Scope

- Tuple spawn, `ChildOf`, `Changed`, and `.chain()` are in the examples below.
- Editor widget trees are out of scope. Composition here is entities, components, and systems.

```toml
[package]
name = "ecs-composition"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = "0.20"
```

People carry a name. Greeting runs after the rename, in one chain.

```rust
#[derive(Component)]
struct Person;

#[derive(Component)]
struct Name(String);

fn spawn_people(mut commands: Commands) {
    commands.spawn((Person, Name("Ada".to_string())));
    commands.spawn(Name("crate".to_string()));
}

fn update_people(mut people: Query<&mut Name, With<Person>>) {
    for mut name in &mut people {
        name.0.push('!');
    }
}

fn greet_people(people: Query<&Name, With<Person>>) {
    for name in &people {
        let _label = name.0.as_str();
    }
}

fn count_names(names: Query<&Name>) {
    let _total = names.iter().count();
}

pub struct PeoplePlugin;

impl Plugin for PeoplePlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Startup, spawn_people).add_systems(
            Update,
            (update_people, greet_people).chain(),
        );
        app.add_systems(Update, count_names);
    }
}
```

`count_names` only reads `Name` and stays outside the chain that writes it.

Parent, child, and a system that runs when a name changes.

```rust
#[derive(Component)]
struct Name(String);

fn spawn_family(mut commands: Commands) {
    let parent = commands.spawn(Name("parent".to_string())).id();
    commands.spawn((Name("child".to_string()), ChildOf(parent)));
}

fn on_rename(renamed: Query<&Name, Changed<Name>>) {
    for name in &renamed {
        let _label = name.0.as_str();
    }
}

pub struct FamilyPlugin;

impl Plugin for FamilyPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Startup, spawn_family)
            .add_systems(Update, on_rename);
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
| Per-entity data | `Component` + `Query` | One struct that stores every entity's fields |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Read the linked Bevy pages | A made-up crate or API |

Load [references/ecs-ownership.md](ecs-composition-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No single component that stores every behavior for an entity. WHY: composition is small components plus systems that query them.
- No `Bundle` API that this file did not open. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No third-party crates. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Official links stay on the unversioned learn pages.

### Official Documentation
- [Quick Start: ECS](https://bevy.org/learn/quick-start/getting-started/ecs/)  -  `Component`, `Query`, `With`, `Commands`, `Startup`, `Update`, and `.chain()`.
- [Apps](https://bevy.org/learn/quick-start/getting-started/apps/)  -  `App` holds the `World` and the `Schedule`.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Who owns which piece of state.
- [bevy-project-foundations](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-project-foundations/SKILL.md)  -  Crate and `App` shell.

#### Complements
- [bevy-data-resources](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md)  -  App-wide data that should not be a component.
- [bevy-events-messaging](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-events-messaging/SKILL.md)  -  Cross-system notices that are not a shared component.

#### Downstream / consumers
- [bevy-character-movement](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-character-movement/SKILL.md)  -  Movement components and systems on the fixed timestep.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Bevy router.
