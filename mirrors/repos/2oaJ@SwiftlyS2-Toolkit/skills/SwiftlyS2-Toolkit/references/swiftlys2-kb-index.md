# SwiftlyS2 Knowledge Base Quick Index

This index is used for quickly locating **publicly citable** SwiftlyS2 reference entry points.

If the current workspace also has local reference repositories, project mappings, historical reference projects, or custom experience, record them in `../../knowledge-base.md` and `../../copilot-instructions.md` instead of writing them back here.

## 1. SwiftlyS2 official docs entry points

### Main entry points

- Docs Root: `https://swiftlys2.net/docs/`
- Docs Map (condensed navigation in this toolkit): `./swiftlys2-official-docs-map.md`
- API Reference: `https://swiftlys2.net/docs/api/`

### Main Development entry points

- Getting Started: `https://swiftlys2.net/docs/development/getting-started/`
- Swiftly Core：`https://swiftlys2.net/docs/development/swiftly-core/`
- Using attributes：`https://swiftlys2.net/docs/development/using-attributes/`
- Thread Safety：`https://swiftlys2.net/docs/development/thread-safety/`
- Commands：`https://swiftlys2.net/docs/development/commands/`
- Configuration：`https://swiftlys2.net/docs/development/configuration/`
- Translations：`https://swiftlys2.net/docs/development/translations/`
- Entity：`https://swiftlys2.net/docs/development/entity/`
- Entity Key Values：`https://swiftlys2.net/docs/development/entitykeyvalues/`
- Game Events：`https://swiftlys2.net/docs/development/game-events/`
- Core Events：`https://swiftlys2.net/docs/development/core-events/`
- Network Messages：`https://swiftlys2.net/docs/development/netmessages/`
- Menus：`https://swiftlys2.net/docs/development/menus/`
- Convars：`https://swiftlys2.net/docs/development/convars/`
- Native Functions and Hooks：`https://swiftlys2.net/docs/development/native-functions-and-hooks/`
- Scheduler：`https://swiftlys2.net/docs/development/scheduler/`
- Shared API：`https://swiftlys2.net/docs/development/shared-api/`
- Permissions：`https://swiftlys2.net/docs/development/permissions/`
- Profiler：`https://swiftlys2.net/docs/development/profiler/`
- Database：`https://swiftlys2.net/docs/development/database/`
- Sound Events：`https://swiftlys2.net/docs/development/soundevents/`
- Steamworks：`https://swiftlys2.net/docs/development/steamworks/`

### Main Guides entry points

- Dependency Injection: `https://swiftlys2.net/docs/guides/dependency-injection/`
- Development Flow (the current official page is still a placeholder `todo`): `https://swiftlys2.net/docs/guides/development-flow/`
- HTML Styling: `https://swiftlys2.net/docs/guides/html-styling/`
- Porting from CounterStrikeSharp: `https://swiftlys2.net/docs/guides/porting-from-css/`
- Terminologies: `https://swiftlys2.net/docs/guides/terminologies/`

### API Reference usage suggestions

- This toolkit does not embed a full extraction of the complete API Reference, to avoid unnecessary bloat.
- First read the API Reference slim navigation in `./swiftlys2-official-docs-map.md`.
- Then do online deep dives by section, such as `commands`, `netmessages`, `players`, `schemas`, or `services`.

## 2. Asset navigation for this toolkit

- Assets Root: `../assets/README.md`
- Development assets: `../assets/development/`
- Guides assets: `../assets/guides/`
- Non-official engineering patterns: `../assets/patterns/`
- Workflow templates: `../assets/workflows/`

## 3. sw2-mdwiki quick entry points

Repository: `https://github.com/himenekocn/sw2-mdwiki`

### Frequently consulted categories

- `SwiftlyS2/Shared/Players/IPlayer.md`
- `SwiftlyS2/Shared/Players/IPlayerManagerService.md`
- `SwiftlyS2/Shared/IInterfaceManager.md`
- `SwiftlyS2/Shared/ISwiftlyCore.md`
- `SwiftlyS2/Shared/Commands/ICommandContext.md`
- `SwiftlyS2/Shared/Commands/Command.md`
- `SwiftlyS2/Shared/Commands/CommandAlias.md`
- `SwiftlyS2/Shared/Events/`
- `SwiftlyS2/Shared/NetMessages/INetMessageService.md`
- `SwiftlyS2/Shared/ProtobufDefinitions/README.md`
- `SwiftlyS2/Shared/SchemaDefinitions/README.md`
- `SwiftlyS2/Shared/EntitySystem/IEntitySystemService.md`
- `SwiftlyS2/Shared/Menus/`
- `SwiftlyS2/Core/Menus/OptionsBase/`

## 4. SwiftlyS2 official repository entry

Repository: `https://github.com/swiftly-solution/swiftlys2`

### Structure at a glance

- `src/`: C++ core framework
- `managed/src/`: C# managed layer
- `natives/`: native definitions
- `generator/`: code generation tools
- `plugin_files/`: plugin/package assets

## 5. Decide first, then check the docs

- **I want to register commands / aliases / chat hooks** → `Commands`
- **I want to listen to map / player / entity lifecycle** → `Core Events`
- **I want to write high-frequency hooks / native hooks / movement sampling** → `Native Functions and Hooks`
- **I want to send typed protobuf / netmessages** → `Network Messages`
- **I want to build cross-plugin interfaces** → `Shared API`
- **I am deciding between await / NextTick / thread-sensitive APIs** → `Thread Safety`
- **I am sorting out controller / pawn / player / entity handle concepts** → `Terminologies` + `Entity`

## 6. Scenario-oriented index (detailed version)

### I want to write commands

#### 1) I want to write partial / attribute commands

- Read the official docs first:
	1. `Commands`
	2. `Using attributes`
	3. `Thread Safety`
- Then read local assets:
	- `../assets/development/commands/command-attribute-template.cs.md`
	- `../assets/development/using-attributes/attribute-registration-checklist.md`
- Common APIs / keywords:
	- `ICommandContext`
	- `[Command]`
	- `[CommandAlias]`
	- `Reply` / `ReplyAsync`
- Common pitfalls:
	- using attributes on non-main-class objects without calling `Core.Registrator.Register(this)`
	- piling business logic directly into command entry points
	- misusing synchronous thread-sensitive APIs in async contexts

#### 2) I want to write service-owned commands

- Read the official docs first:
	1. `Commands`
	2. `Dependency Injection`
	3. `Thread Safety`
- Then read local assets:
	- `../assets/development/commands/command-service-template.cs.md`
	- `../assets/guides/dependency-injection/service-template.cs.md`
- Common APIs / keywords:
	- `RegisterCommand`
	- `RegisterCommandAlias`
	- `UnregisterCommand`
	- `HookClientChat`
	- `HookClientCommand`
- Common pitfalls:
	- not saving the `Guid`
	- registering commands in the root while assuming the service will clean them automatically
	- inconsistent cleanup paths for aliases and the primary command

#### 3) I want to add permissions to commands

- Read the official docs first:
	1. `Commands`
	2. `Permissions`
- Then read local assets:
	- `../assets/development/permissions/README.md`
	- `../assets/development/commands/command-attribute-template.cs.md`
- Common pitfalls:
	- applying only UI restrictions without real permission checks
	- leaving wildcard / sub-permission relationships unclear

### I want to write menus

#### 1) I want menu entry points / submenus / save flows

- Read the official docs first:
	1. `Menus`
	2. `Thread Safety`
- Then read local assets:
	- `../assets/development/menus/menu-template.cs.md`
	- `../assets/development/thread-safety/thread-sensitivity-checklist.md`
- Common APIs / keywords:
	- `IMenuManagerAPI`
	- `ButtonMenuOption`
	- `ToggleMenuOption`
	- `ChoiceMenuOption`
	- `SubmenuMenuOption`
- Common pitfalls:
	- blocking IO directly inside callbacks
	- failing to revalidate the player after `await`
	- storing state inside the menu instead of runtime / service layers

#### 2) I want dynamic text with `BindingText`

- Read the official docs first:
	1. `Menus`
	2. `HTML Styling` (if the text includes HTML)
- Then read local assets:
	- `../assets/development/menus/menu-template.cs.md`
	- `../assets/guides/html-styling/README.md`
- Common pitfalls:
	- refreshing `Text` manually instead of using binding
	- placing heavy computation or heavy IO inside binding evaluation

### I want to write hooks

#### 1) I want typed core events / high-frequency runtime hooks

- Read the official docs first:
	1. `Core Events`
	2. `Thread Safety`
	3. `Profiler`
- Then read local assets:
	- `../assets/development/native-functions-and-hooks/hook-handler-template.cs.md`
	- `../assets/development/thread-safety/thread-sensitivity-checklist.md`
	- `../assets/development/profiler/hotpath-gc-checklist.md`
- Common pitfalls:
	- doing JSON / IO / high-frequency logging on hot paths
	- failing to filter players / pawns / fakeclients
	- stuffing complex logic directly into the hook callback

#### 2) I want native function hooks / mid-hooks

- Read the official docs first:
	1. `Native Functions and Hooks`
	2. `Thread Safety`
- Then read local assets:
	- `../assets/development/native-functions-and-hooks/hook-handler-template.cs.md`
- Common pitfalls:
	- delegate prototype mismatch
	- not understanding the difference between `Call()` and `CallOriginal()`
	- corrupting registers in mid-hooks

### I want to write NetMessages / Protobuf

#### 1) I want to send typed netmessages

- Read the official docs first:
	1. `Network Messages`
	2. `Thread Safety`
- Then read local assets:
	- `../assets/development/netmessages/protobuf-handler-template.cs.md`
- Common APIs / keywords:
	- `Core.NetMessage.Send<T>`
	- `Core.NetMessage.Create<T>`
	- `Recipients`
- Common pitfalls:
	- forgetting to dispose reusable messages
	- using magic numbers instead of typed APIs

#### 2) I want to hook client / server messages

- Read the official docs first:
	1. `Network Messages`
	2. `INetMessageService` in API Reference
- Then read local assets:
	- `../assets/development/netmessages/protobuf-handler-template.cs.md`
	- `../assets/development/thread-safety/thread-sensitivity-checklist.md`
- Common pitfalls:
	- passing protobuf handles directly to background threads
	- not distinguishing between client-message and server-message hooks

### I want to write Shared API

#### 1) I want to provide a shared interface

- Read the official docs first:
	1. `Shared API`
	2. `Dependency Injection`
- Then read local assets:
	- `../assets/development/shared-api/shared-interface-template.cs.md`
	- `../assets/guides/dependency-injection/di-service-plugin-template.cs.md`
- Common pitfalls:
	- not using a contracts DLL
	- overly vague key naming
	- not considering versioning

#### 2) I want to consume a shared interface

- Read the official docs first:
	1. `Shared API`
- Then read local assets:
	- `../assets/development/shared-api/shared-interface-template.cs.md`
- Common pitfalls:
	- not calling `HasSharedInterface(...)` first
	- assuming the provider has already loaded
	- continuing to hold old interface references after unload

### I want to write Scheduler / Worker / background tasks

#### 1) I want to decide between Scheduler and a background worker

- Read the official docs first:
	1. `Scheduler`
	2. `Thread Safety`
- Then read local assets:
	- `../assets/development/scheduler/scheduler-vs-worker-guide.md`
	- `../assets/patterns/background-workers/worker-template.cs.md`
	- `../assets/development/core-events/lifecycle-checklist.md`
- Common pitfalls:
	- treating a background worker as if it were Scheduler
	- accessing main-thread-sensitive APIs directly from worker threads
	- having no stop / flush / cancel lifecycle closure

## 7. Recommended lookup keywords

### Lifecycle

- `OnClientPutInServer`
- `OnClientDisconnected`
- `OnMapLoad`
- `OnMapUnload`

### Commands

- `ICommandContext`
- `Command`
- `CommandAlias`
- `Reply`

### Hooks / movement

- `OnClientProcessUsercmds`
- `OnMovementServicesRunCommandHook`
- `DynamicHook`
- `MidHookContext`

### NetMessages / Protobuf

- `INetMessageService`
- `ITypedProtobuf`
- `IProtobufAccessor`

### Shared API

- `IInterfaceManager`
- `ConfigureSharedInterface`
- `UseSharedInterface`
- `HasSharedInterface`

### Schema / Entity

- `IEntitySystemService`
- `AcceptInput`
- `DispatchSpawn`
- `Despawn`
- `Updated`

### Menus

- `IMenuAPI`
- `IMenuOption`
- `ButtonMenuOption`
- `ToggleMenuOption`
- `SliderMenuOption`
- `SubmenuMenuOption`
- `BindingText`

## 8. Usage suggestions

- **Choose the scenario first, then choose the reference source.**
- **Read the official docs and mdwiki first, then decide whether workspace-specific additions are needed.**
- **For official details, enter through `swiftlys2-official-docs-map.md` first and only then drill down online as needed.**
- **For local templates and checklists, enter through `../assets/README.md` first instead of guessing filenames.**
- **Public docs should cover API and framework boundaries; the workspace knowledge base should cover workspace-specific experience.**
