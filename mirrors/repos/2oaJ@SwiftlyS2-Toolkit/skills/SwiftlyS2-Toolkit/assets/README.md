# SwiftlyS2 Toolkit Assets Navigation

This directory reorganizes the SwiftlyS2 experience assets accumulated in the workspace according to the semantics of the **SwiftlyS2 official Development / Guides** sections.

The goal is not to duplicate the official docs, but to help the agent, when facing a real task:

1. first find the correct official topic
2. then land on the closest local template / checklist for that topic
3. and finally combine it with `references/swiftlys2-official-docs-map.md` for deeper online lookup

## Directory structure

### `development/`

Local assets aligned to the official `https://swiftlys2.net/docs/development/` section.

### `guides/`

Local assets aligned to the official `https://swiftlys2.net/docs/guides/` section.

### `patterns/`

Engineering patterns derived from maintenance experience that do not fit cleanly into a single official page.

### `workflows/`

Workflow templates for planning, auditing, implementation, and similar tasks that do not map to a single official page.

## Official topic -> local asset mapping

| Official topic | Local asset | Purpose |
| --- | --- | --- |
| Getting Started | `development/getting-started/partial-plugin-template.cs.md` | partial / modular plugin skeleton |
| Using attributes | `development/using-attributes/attribute-registration-checklist.md` | attribute registration boundaries and self-check |
| Swiftly Core | `development/swiftly-core/core-service-entrypoints.md` | routing for common `ISwiftlyCore` services |
| Commands | `development/commands/command-attribute-template.cs.md` | attribute command template |
| Commands | `development/commands/command-service-template.cs.md` | service-owned command template |
| Commands | `development/commands/client-command-hook-template.cs.md` | `ClientCommandHookHandler` interception template |
| Menus | `development/menus/menu-template.cs.md` | menus, `BindingText`, async callbacks |
| Network Messages | `development/netmessages/protobuf-handler-template.cs.md` | typed protobuf / netmessage template |
| Native Functions and Hooks | `development/native-functions-and-hooks/hook-handler-template.cs.md` | high-frequency hook / native hook template |
| Configuration | `development/configuration/config-hot-reload-template.cs.md` | Config + `IOptionsMonitor` hot reload |
| Configuration | `development/configuration/README.md` | configuration entry guidance |
| ConVars | `development/convars/convar-template.cs.md` | ConVar creation, ranges, and flags |
| Thread Safety | `development/thread-safety/thread-sensitivity-checklist.md` | thread-sensitive API review |
| Profiler | `development/profiler/hotpath-gc-checklist.md` | hot-path / GC / performance review |
| Entity | `development/entity/schema-write-checklist.md` | schema write-back and entity-validity review |
| Core Events | `development/core-events/lifecycle-checklist.md` | lifecycle-closure review |
| Core Events | `development/core-events/precache-resource-template.cs.md` | `OnPrecacheResource` template |
| Scheduler | `development/scheduler/scheduler-vs-worker-guide.md` | routing between Scheduler and background workers |
| Shared API | `development/shared-api/shared-interface-template.cs.md` | provider / consumer / contracts template |
| Game Events | `development/game-events/game-events-usage-notes.md` | usage-boundary notes for Game Events |
| Translations | `development/translations/README.md` | translation-resource entry guidance |
| Permissions | `development/permissions/README.md` | permissions and permission-group entry guidance |
| Dependency Injection | `guides/dependency-injection/di-service-plugin-template.cs.md` | DI plugin skeleton |
| Dependency Injection | `guides/dependency-injection/service-template.cs.md` | service skeleton |
| Terminologies | `guides/terminologies/README.md` | terminology routing for controller / pawn / player / handle |
| HTML Styling | `guides/html-styling/README.md` | Panorama HTML styling entry |

## Non-official but frequently used engineering patterns

- `patterns/background-workers/worker-template.cs.md`
  - background queues, `Task.Run`, `CancellationTokenSource`, and Flush / Cancel / Stop semantics
  - **Note**: this is not the same thing as the official `Scheduler`; read `development/scheduler/scheduler-vs-worker-guide.md` first
- `patterns/per-player-state/player-state-management-guide.md`
  - four per-player state-management tiers: lightweight dictionary → runtime object → DB restore → slot array + generation counter
- `patterns/async-patterns/async-safety-guide.md`
  - safe `.Forget()` launch patterns, `StopOnMapChange`, generation-counter invalidation strategy, and reacquiring `IPlayer`
- `patterns/service-factory/service-factory-template.cs.md`
  - factory pattern, keyed singleton, multi-implementation traversal, and strategy selection

## Workflow templates

- `workflows/planning/method-level-plan-template.md`
- `workflows/audit/audit-report-template.md`

## Migration notes (old path -> new path)

- `swiftlys2-partial-plugin-template.cs.md` -> `development/getting-started/partial-plugin-template.cs.md`
- `swiftlys2-di-service-plugin-template.cs.md` -> `guides/dependency-injection/di-service-plugin-template.cs.md`
- `swiftlys2-service-template.cs.md` -> `guides/dependency-injection/service-template.cs.md`
- `swiftlys2-command-handler-template.cs.md` ->
  - `development/commands/command-attribute-template.cs.md`
  - `development/commands/command-service-template.cs.md`
- `swiftlys2-menu-template.cs.md` -> `development/menus/menu-template.cs.md`
- `swiftlys2-hook-handler-template.cs.md` -> `development/native-functions-and-hooks/hook-handler-template.cs.md`
- `swiftlys2-protobuf-handler-template.cs.md` -> `development/netmessages/protobuf-handler-template.cs.md`
- `swiftlys2-schema-write-checklist.md` -> `development/entity/schema-write-checklist.md`
- `swiftlys2-thread-sensitivity-checklist.md` -> `development/thread-safety/thread-sensitivity-checklist.md`
- `swiftlys2-hotpath-gc-checklist.md` -> `development/profiler/hotpath-gc-checklist.md`
- `swiftlys2-lifecycle-checklist.md` -> `development/core-events/lifecycle-checklist.md`
- `swiftlys2-worker-template.cs.md` -> `patterns/background-workers/worker-template.cs.md`
- `swiftlys2-method-level-plan-template.md` -> `workflows/planning/method-level-plan-template.md`
- `swiftlys2-audit-report-template.md` -> `workflows/audit/audit-report-template.md`

## Usage suggestions

- If you want the official-doc storyline: start with `../references/swiftlys2-official-docs-map.md`
- If you want a task-oriented entry point: start with `../references/swiftlys2-kb-index.md`
- If you want to jump directly to a template / checklist: use the mapping table in this README
