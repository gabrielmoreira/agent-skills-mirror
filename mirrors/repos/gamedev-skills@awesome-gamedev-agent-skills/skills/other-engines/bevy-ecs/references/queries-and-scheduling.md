# Bevy queries & scheduling detail (0.16+)

Depth behind the ECS skill: query filters and access, schedules and ordering,
states, change detection, and the `Commands` lifecycle. Verify any borderline API
against the docs for your pinned Bevy version — minor releases move things.

## Query anatomy

A `Query<D, F>` has a **data** part `D` (what you read/write) and an optional
**filter** part `F` (which entities, without fetching their data).

```rust
// Data: read Name, write Transform. Filter: must have Player, must NOT have Frozen.
Query<(&Name, &mut Transform), (With<Player>, Without<Frozen>)>
```

Common filters:

- `With<T>` / `Without<T>` — entity has / lacks a component (no data fetched).
- `Added<T>` — `T` was added since this system last ran.
- `Changed<T>` — `T` was added or mutably accessed since last run (change detection).
- `Or<(...)>` — combine filters disjunctively.

Optional and entity access in the data part:

```rust
Query<(Entity, &Transform, Option<&Velocity>)>  // Entity id; Velocity may be absent
```

### Single-entity access

For a query you expect to match exactly one entity (e.g. the player), `single()`
and `single_mut()` return a `Result` in 0.16+ (they replaced the older
`get_single`/panicking `single`):

```rust
fn read_player(q: Query<&Transform, With<Player>>) {
    if let Ok(transform) = q.single() {
        // exactly one Player matched
    }
}
```

Iterating with `for x in &query` is always valid and the safest default.

## Avoiding conflicting access

Two systems can run in parallel only if their data accesses don't conflict. Two
queries **within one system** that both mutably touch the same component will panic
at startup. Fixes:

1. **Disjoint with filters** — `With<Player>` vs `Without<Player>` guarantees the
   sets never overlap, so both can be `&mut`.
2. **`ParamSet`** — when sets *can* overlap, access them one at a time:

```rust
fn swap(mut set: ParamSet<(
    Query<&mut Transform, With<A>>,
    Query<&mut Transform, With<B>>,
)>) {
    for mut t in &mut set.p0() { /* ... */ }
    for mut t in &mut set.p1() { /* ... */ }
}
```

## Schedules and ordering

Built-in schedules you'll use most:

- `Startup` — once, before the first `Update`.
- `Update` — every frame.
- `FixedUpdate` — fixed timestep; use it for physics/gameplay that needs
  determinism (read `time.delta_secs()` here too; it's the fixed step).
- `PreUpdate` / `PostUpdate` — around `Update` for setup/teardown ordering.

Ordering within a schedule:

```rust
// Explicit pairwise order.
app.add_systems(Update, (input, movement, collision).chain());

// Named constraints.
app.add_systems(Update, movement.before(collision));
app.add_systems(Update, camera_follow.after(movement));
```

### System sets

Group systems into a `SystemSet` to order whole phases and attach shared run
conditions:

```rust
#[derive(SystemSet, Debug, Clone, PartialEq, Eq, Hash)]
enum GameSet { Input, Logic, Render }

app.configure_sets(Update, (GameSet::Input, GameSet::Logic, GameSet::Render).chain());
app.add_systems(Update, read_input.in_set(GameSet::Input));
app.add_systems(Update, (move_units, resolve).in_set(GameSet::Logic));
```

### Run conditions

```rust
app.add_systems(Update, pause_menu.run_if(in_state(AppState::Paused)));
app.add_systems(Update, autosave.run_if(on_timer(Duration::from_secs(30))));
```

## States

`States` model app-wide modes (menu, playing, paused). Use `OnEnter`/`OnExit`
schedules for transition logic and `in_state` to gate `Update` systems.

```rust
#[derive(States, Default, Debug, Clone, PartialEq, Eq, Hash)]
enum AppState { #[default] Menu, Playing }

app.init_state::<AppState>()
   .add_systems(OnEnter(AppState::Playing), spawn_level)
   .add_systems(OnExit(AppState::Playing), cleanup_level)
   .add_systems(Update, gameplay.run_if(in_state(AppState::Playing)));

// Transition from a system:
fn start(mut next: ResMut<NextState<AppState>>) { next.set(AppState::Playing); }
```

## Change detection

`Changed<T>` / `Added<T>` filters and the `Ref<T>`/`Mut<T>` wrappers let systems
react only to modified data — cheaper than recomputing every frame. Note: writing
through a `&mut T` marks it changed even if the value is identical; guard with a
value check if that matters.

## Commands lifecycle

`Commands` queue structural changes (spawn, despawn, insert/remove components,
insert resources). They are **deferred** and applied at the next sync point
(end of the schedule stage), so:

- An entity spawned this frame is not in queries until a later system/stage.
- `commands.entity(e).despawn()` removes the entity; in 0.16+ this also removes its
  children (the old explicit `despawn_recursive` was folded in).

```rust
fn spawn_bullet(mut commands: Commands) {
    let id = commands.spawn((Bullet, Transform::default())).id();
    commands.entity(id).insert(Velocity(Vec2::Y * 500.0));
}
```

For immediate, exclusive access to the whole `World` (one-off setup, complex
queries), use an exclusive system `fn(&mut World)` — it can't run in parallel, so
use sparingly.

## Events / messages — version caution

Bevy's buffered-event and observer APIs were reworked around 0.16→0.17 (including
naming changes for buffered "messages" vs observer "events"). If you need
event-style communication between systems, look up the exact `EventReader`/
`EventWriter` (or message/observer) API for your pinned version rather than
copying an example from a different release.
