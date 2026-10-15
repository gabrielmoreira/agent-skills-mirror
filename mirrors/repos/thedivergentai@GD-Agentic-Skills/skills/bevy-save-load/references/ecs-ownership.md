# ECS ownership - bevy-save-load

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |

`Progress` is the app-wide slot. One system writes it. Disk I/O stays in that system when a request resource exists.

```rust
#[derive(Resource)]
struct Progress {
    coins: u32,
}

fn grant_coin(mut progress: ResMut<Progress>) {
    progress.coins = progress.coins.saturating_add(1);
}
```
