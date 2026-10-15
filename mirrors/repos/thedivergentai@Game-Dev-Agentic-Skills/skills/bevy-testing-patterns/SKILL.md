---
name: bevy-testing-patterns
description: "Tests Bevy schedule logic with cargo test, MinimalPlugins, and app.update(). Use for unit tests of systems, resources, and .chain() order. Keywords: Bevy, cargo test, MinimalPlugins, world, libtest."
---

# Bevy testing patterns

## When to use

Load this when a Bevy crate needs unit or integration tests. `cargo test` runs `#[test]` functions. A headless `App` with `MinimalPlugins` is the harness for schedule logic.

## ECS shape

- **Command:** `cargo test` compiles and runs unit tests, integration tests, and documentation tests. `cargo test name_filter` runs names that contain the filter. Arguments after `--` go to libtest (`cargo test -- --help`).
- **What runs:** functions annotated with `#[test]`. The harness runs them in multiple threads. The working directory for each test is the package root, so relative paths resolve from that root no matter where you invoked Cargo.
- **Scope:** default `cargo test` covers the lib, bins as unit tests, integration tests, and doc tests, and it builds examples. `--lib` limits to the library. `harness = false` on a target means you supply `main`.
- **Profile:** the `test` profile is the default. `--profile=debug` keeps debug info. `-- --no-capture` shows test output.
- **Bevy types inside a test:** build an `App`, insert the resource, add the system, call `update`, then read `world()`. Keep the window out of the harness with `MinimalPlugins`.

## How to run

| Need | Command |
| --- | --- |
| Whole suite | `cargo test` from the package |
| One name | `cargo test name_filter` |
| Printed output | `cargo test -- --no-capture` |

Pure logic stays a normal `#[test]` with no `App`.

```rust
fn score_after_pickup(score: u32, value: u32) -> u32 {
    score.saturating_add(value)
}

#[test]
fn pickup_adds_points() {
    assert_eq!(score_after_pickup(1, 2), 3);
}
```

Schedule tests own a headless app. `world()` is shared for the assert, so the query that writes `Score` has already finished.

```rust
#[derive(Resource, Default)]
struct Score(u32);

fn add_point(mut score: ResMut<Score>) {
    score.0 += 1;
}

#[test]
fn one_update_adds_a_point() {
    let mut app = App::new();
    app.add_plugins(MinimalPlugins)
        .insert_resource(Score(0))
        .add_systems(Update, add_point);
    app.update();
    assert_eq!(app.world().resource::<Score>().0, 1);
}
```

Spawn in `Startup`, then step `Update` once. The test reads the component through a one-off system result stored on a resource the test inserts, or through `world()`.

```rust
#[derive(Component)]
struct Marker;

fn spawn_marker(mut commands: Commands) {
    commands.spawn(Marker);
}

#[test]
fn startup_spawns_one_marker() {
    let mut app = App::new();
    app.add_plugins(MinimalPlugins)
        .add_systems(Startup, spawn_marker);
    app.update();
    let count = app.world().query::<&Marker>().iter(app.world()).count();
    assert_eq!(count, 1);
}
```

Two writers of the same component are chained inside the test the same way they are chained in the game plugin.

```rust
#[derive(Resource)]
struct Wallet(i32);

fn earn(mut wallet: ResMut<Wallet>) {
    wallet.0 += 5;
}

fn spend(mut wallet: ResMut<Wallet>) {
    wallet.0 -= 2;
}

#[test]
fn earn_then_spend() {
    let mut app = App::new();
    app.add_plugins(MinimalPlugins)
        .insert_resource(Wallet(0))
        .add_systems(Update, (earn, spend).chain());
    app.update();
    assert_eq!(app.world().resource::<Wallet>().0, 3);
}
```

## Scope

- The harness above is `MinimalPlugins`, `app.update()`, and `world()`. It does not capture frames or inject window input.
- Doctest working-directory rules differ from unit tests. Do not assume a doctest can read `assets/` the same way a `#[test]` can. The package root is the unit-test working directory.

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
| Per-entity data | `Component` + `Query` | A free-floating struct outside the `World` |
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

- No scene-tree test runner in this crate. WHY: schedule tests use `MinimalPlugins`, `app.update()`, and `world()`.
- No frame-capture or input-injection harness. WHY: this skill tests schedules with `MinimalPlugins` and `app.update()`.
- No third-party Bevy test crates. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20**.

### Official Documentation
- [cargo test](https://doc.rust-lang.org/cargo/commands/cargo-test.html)  -  `#[test]`, filters, libtest args, package root as cwd.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch. Examples are not the test harness.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Who owns which piece of state.
- [bevy-project-foundations](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-project-foundations/SKILL.md)  -  The Cargo package `cargo test` runs against.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Bevy router.
