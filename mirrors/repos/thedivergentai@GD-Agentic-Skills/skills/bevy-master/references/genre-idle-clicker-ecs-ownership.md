# ECS ownership - bevy-genre-idle-clicker

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |

The wallet is the app-wide resource. Generators stay on entities. One system writes the wallet.

```rust
#[derive(Resource)]
struct Wallet {
    coins: f64,
}

#[derive(Component)]
struct Generator {
    owned: u32,
}

fn boot(mut commands: Commands) {
    commands.insert_resource(Wallet { coins: 0.0 });
    commands.spawn(Generator { owned: 1 });
}
```
