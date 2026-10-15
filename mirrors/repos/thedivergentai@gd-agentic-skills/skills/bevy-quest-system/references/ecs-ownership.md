# ECS ownership - bevy-quest-system

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |
| Quest definitions | `QuestCatalog` resource | insert in `Startup` |
| Runtime stage and counts | `QuestProgress` | one system on `Update` |
| Pickup or kill notice | `Message` via `MessageReader` | read in the writer system |

One system writes `QuestProgress`. Use the APIs linked from the skill. Do not invent crates or types.
