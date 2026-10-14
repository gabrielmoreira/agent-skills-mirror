---
name: bevy-testing-patterns
description: "Bevy ECS skill for Cargo tests around Bevy work. Keywords: Bevy, cargo test, Rust, libtest."
---

# Bevy testing patterns

## When to use

Load this when a Bevy crate needs unit or integration tests. The Cargo book page for `cargo test` is the source. Check the Bevy docs for `App::update` inside `#[test]` before writing that harness.

## ECS shape

- **Command:** `cargo test` compiles and runs unit tests, integration tests, and documentation tests. `cargo test name_filter` runs names that contain the filter. Arguments after `--` go to libtest (`cargo test -- --help`).
- **What runs:** functions annotated with `#[test]`. The harness runs them in multiple threads. The working directory for each test is the package root, so relative paths resolve from that root no matter where you invoked Cargo.
- **Scope:** default `cargo test` covers the lib, bins as unit tests, integration tests, and doc tests, and it builds examples. `--lib` limits to the library. `harness = false` on a target means you supply `main`.
- **Profile:** the `test` profile is the default. `--profile=debug` keeps debug info. `-- --no-capture` shows test output.
- **Bevy types inside a test:** not specified here. Do not copy an `App::new()` test from an old discussion. Bevy's own crates contain `#[cfg(test)]` modules. Check those helpers before treating them as a public guide.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Run the suite | `cargo test` from the package |
| One test name | `cargo test name_filter` |
| See prints | `cargo test -- --no-capture` |
| Scene-tree test runner | No twin. GdUnit stays on the Godot skill |

## Scope

- Check docs.rs `latest` for a page that shows `App`, `MinimalPlugins`, and `app.update()` inside `#[test]` before writing that harness.
- Check the docs for headless frame capture, golden images, and input injection for tests before writing them.
- Doctest working-directory rules differ from unit tests (workspace root for `rustdoc` compile). Do not assume a doctest can read `assets/` the same way.

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

- No GdUnit, GUT, or Godot test-runner types. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No `App::update` test recipe this file did not open. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No third-party Bevy test crates. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/)  -  Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/)  -  Unversioned API index.
- [cargo test](https://doc.rust-lang.org/cargo/commands/cargo-test.html)  -  `#[test]`, filters, libtest args, package root as cwd.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch. Examples are not the test harness.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Who owns which piece of state.
- [bevy-project-foundations](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-project-foundations/SKILL.md)  -  The Cargo package `cargo test` runs against.

#### Complements
- [godot-testing-patterns](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-testing-patterns/SKILL.md)  -  Godot counterpart. GdUnit stays there.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Bevy router.
