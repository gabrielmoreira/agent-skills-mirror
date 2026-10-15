# ECS ownership - bevy-asset-scenes

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |
| File bytes | `AssetServer` plus `Assets<T>` | load in `Startup`; read when `is_loaded_with_dependencies` is true |
| Strong handle kept alive | `Resource` such as `PropMesh` | insert once; dropping it unloads |
| Level identity | `LevelRoot` component | despawn that entity before `queue_spawn_scene` |

`spawn_scene` fails while dependencies are unloaded. `queue_spawn_scene` waits and spawns in `SpawnScene`, which runs after `Update`. Do not both immediate-spawn and queue the same scene in one system.
