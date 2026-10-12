---
name: bevy-testing-patterns
description: "Docs-first stub for Cargo tests around Bevy work. Godot counterpart: godot-testing-patterns. Not a GdUnit port. Keywords: Bevy, cargo test, Rust, libtest."
---

# Bevy testing patterns (docs-first stub)

Not a full port. Tests here are Cargo's test harness. There is no GdUnit twin.

## When to use

Load this when a Bevy crate needs unit or integration tests. The Cargo book page for `cargo test` (opened 2026-10-11) is the source. A current Bevy "how to `App::update` inside `#[test]`" page was not opened, so that recipe stays a gap.

## ECS shape

- **Command:** `cargo test` compiles and runs unit tests, integration tests, and documentation tests. `cargo test name_filter` runs names that contain the filter. Arguments after `--` go to libtest (`cargo test -- --help`).
- **What runs:** functions annotated with `#[test]`. The harness runs them in multiple threads. The working directory for each test is the package root, so relative paths resolve from that root no matter where you invoked Cargo.
- **Scope:** default `cargo test` covers the lib, bins as unit tests, integration tests, and doc tests, and it builds examples. `--lib` limits to the library. `harness = false` on a target means you supply `main`.
- **Profile:** the `test` profile is the default. `--profile=debug` keeps debug info. `-- --no-capture` shows test output.
- **Bevy types inside a test:** not specified here. Do not copy an `App::new()` test from an old discussion. Bevy's own crates contain `#[cfg(test)]` modules; their helpers were not opened as a public guide.

## Godot idea to Bevy idiom

| Idea | Bevy idiom (idea only) |
| --- | --- |
| Run the suite | `cargo test` from the package |
| One test name | `cargo test name_filter` |
| See prints | `cargo test -- --no-capture` |
| Scene-tree test runner | No twin. GdUnit stays on the Godot skill |

## Gaps

- No docs.rs `latest` page was opened that shows `App`, `MinimalPlugins`, and `app.update()` inside `#[test]`. Do not invent that harness.
- Headless frame capture, golden images, and input injection for tests were not opened.
- Doctest working-directory rules differ from unit tests (workspace root for `rustdoc` compile). Do not assume a doctest can read `assets/` the same way.


## Expert Knowledge Delta

Library target in prose: **Bevy 0.20.0**. Lattice URLs stay unversioned.

Opened canon only: `Component`, `Resource`, `Query`, `Commands`, `Startup`, `Update`, `Fixed` / `FixedMain` (`bevy::time`), `.chain()`, `Plugin`, `DefaultPlugins`, `MinimalPlugins`. Messages and observers are an ownership slot. This file does not invent their struct APIs. Systems run in parallel unless `.chain()` orders the ones that conflict.

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
| An API this skill did not open | A Gaps row | A fabricated crate (solver, navmesh module, net, XR) |

Load `references/a-gate-notes.md` for the same table plus the gap rule.

## NEVER

- Do not put `/0.20.0/` in lattice URLs. WHY: permalinks stay on `latest`. The 0.20.0 pin belongs in prose once.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: those rows are gaps, blocked, or revisit.

- No GdUnit, GUT, or Godot test-runner types. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No `App::update` test recipe this file did not open. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No third-party Bevy test crates. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No Creation Station content. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No umbrella skill over Godot and Bevy. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- Do not mark this row `ported`. It is `docs_mapped`. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/)  -  Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/)  -  Unversioned API index.
- [cargo test](https://doc.rust-lang.org/cargo/commands/cargo-test.html)  -  `#[test]`, filters, libtest args, package root as cwd.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch. Examples are not the test harness.

### Related Skills

#### Prerequisites
- [bevy-master](../SKILL.md)  -  Who owns which piece of state.
- [bevy-project-foundations](project-foundations.md)  -  The Cargo package `cargo test` runs against.

#### Complements
- [godot-testing-patterns](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-testing-patterns/SKILL.md)  -  Godot counterpart. GdUnit stays there.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](../SKILL.md)  -  Bevy router.
