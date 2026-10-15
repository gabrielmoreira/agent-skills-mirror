# ECS ownership - bevy-genre-simulation

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |

```rust
#[derive(Component)]
struct Hunger {
    value: f32,
}

#[derive(Resource)]
struct SimClock {
    hour: f32,
    paused: bool,
}

fn read_sim(clock: Res<SimClock>, agents: Query<&Hunger>) {
    if clock.paused {
        return;
    }
    for hunger in &agents {
        let _value = hunger.value + clock.hour;
    }
}
```
