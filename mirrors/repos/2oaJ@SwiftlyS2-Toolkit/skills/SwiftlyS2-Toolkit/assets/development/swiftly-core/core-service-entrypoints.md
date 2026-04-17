# SwiftlyS2 Core Service Entry Quick Reference

Official docs section:
- `Swiftly Core`

Use this when the agent already knows what it wants to do but is not yet sure which `ISwiftlyCore` service entry point to start from.

## High-frequency entry points

- `Core.Command`
  - command registration, aliases, client command/chat hooks
- `Core.Event`
  - Core Events, tick, map, player, and entity lifecycle listeners
- `Core.GameEvent`
  - Game Event fire / hook
- `Core.NetMessage`
  - typed netmessage send / hook
- `Core.EntitySystem`
  - entity creation, lookup, and handle acquisition
- `Core.ConVar`
  - cvar creation, lookup, and client replication
- `Core.Configuration`
  - plugin config initialization, config sources, and hot reload
- `Core.Translation`
  - localization and player-language localizers
- `Core.Permission`
  - permissions, groups, sub-permissions, and wildcards
- `Core.Scheduler`
  - NextTick, Delay, Repeat, StopOnMapChange
- `Core.Database`
  - global database connection
- `Core.Profiler`
  - lightweight performance sampling
- `Core.Registrator`
  - attribute registration on non-main-class objects
- `Core.Menus` / `Core.MenusAPI`
  - menu builders, open / close, and menu events

## Usage suggestions

- If the entry point is unclear, first determine whether the task is about commands, events, menus, entities, NetMessages, configuration, or cross-plugin interfaces.
- Then go to `references/swiftlys2-kb-index.md` for a scenario-oriented route.
- If a more specific official page is needed, continue into `references/swiftlys2-official-docs-map.md`.
