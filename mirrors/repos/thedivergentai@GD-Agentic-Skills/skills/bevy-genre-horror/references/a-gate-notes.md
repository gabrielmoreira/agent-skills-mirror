# A-gate notes — bevy-genre-horror

Moved decision depth for this docs-first skill. Opened canon only.

Library pin in prose: Bevy **0.20.0**. Do not version lattice URLs.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |

If the API was not opened on the skill's Official Documentation list, leave a Gaps row. Networking stays blocked until 2026-11-11. XR stays revisit until 2026-11-11. No Avian, Rapier, or nav-module invention.
