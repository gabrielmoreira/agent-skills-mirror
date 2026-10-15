# ECS ownership - bevy-turn-system

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |
| Speed and action points | `Fighter` component | the active entity's system |
| Order, index, round | `TurnClock` resource | `take_action` then `end_turn`, `.chain()` |

Do not rebuild the queue on every action. Do not invent crates or types.
