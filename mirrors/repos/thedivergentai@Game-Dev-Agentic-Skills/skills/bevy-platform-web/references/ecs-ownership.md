# ECS ownership - bevy-platform-web

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |
| Canvas id and fit | `Window` on `PrimaryWindow` | `Startup` via `WindowPlugin`, or `Update` if retargeting |
| Backend | Cargo `webgl2` or `webgpu` | compile time; not a component |

`webgl2` and `webgpu` conflict. Enable one. `clipboard_image` is unavailable on wasm. Use the APIs linked from the skill. Do not invent crates or types.
