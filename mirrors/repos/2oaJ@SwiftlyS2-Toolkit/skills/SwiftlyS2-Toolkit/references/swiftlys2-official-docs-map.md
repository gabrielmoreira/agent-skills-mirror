# SwiftlyS2 official docs navigation map

This file organizes `https://swiftlys2.net/docs/` into a public navigation map that is **suitable for fast agent lookup and second-stage online deep dives**.

The goal is not to copy the entire official site into the toolkit, but to:

- keep stable entry points
- distill “what this page is for” for each page
- compress the most important engineering semantics for SwiftlyS2 plugin development first
- avoid bloating the toolkit by stuffing in the full API Reference wholesale

## Usage rules

- **Installation**: keep the entry point, but this toolkit does not extract the full page content.
- **API Reference**: keep only slim navigation and lookup guidance; when detailed APIs are needed, the agent should enter `https://swiftlys2.net/docs/api/` online and fetch them on demand.
- **Development Flow**: the current official page is still a `todo` placeholder and should not be treated as reliable engineering guidance.

## Docs Root

- Main entry: `https://swiftlys2.net/docs/`
- Homepage positioning: introduces SwiftlyS2 as a CS2 server-side plugin framework based on Metamod:Source, highlighting capabilities such as Commands, Convars, Entity System, Events, GameEvents, Memory, Menus, Hooks, NetMessages, Profiler, Scheduler, Schemas, and Sounds.
- Homepage usage: suitable as a **capability overview and section entry**, but not as a detailed reference.

## Development section navigation

### 1. Getting Started

- URL: `https://swiftlys2.net/docs/development/getting-started/`
- Positioning: entry point for new plugin startup, template installation, and release workflow.
- Key points:
  - depends on `.NET 10.0 SDK`
  - creates plugin templates through `SwiftlyS2.CS2.PluginTemplate`
  - template versions may lag behind and require manual `PackageReference` updates
  - publish artifacts are generated under `build/publish`
  - the official docs explicitly recommend reading `Dependency Injection` before serious implementation begins
- Suitable for: creating new plugins, checking template project structure, and confirming the basic release flow.

### 2. Swiftly Core

- URL: `https://swiftlys2.net/docs/development/swiftly-core/`
- Positioning: the main entry explanation for `ISwiftlyCore`.
- Key points:
  - `ISwiftlyCore` is the central framework singleton
  - it gathers services such as Event, Engine, GameEvent, NetMessage, Helpers, Game, Command, EntitySystem, ConVar, Configuration, GameData, PlayerManager, Memory, Profiler, Trace, Scheduler, Database, Translation, Permission, Registrator, MenusAPI, and PluginManager
  - the official docs explicitly recommend sharing `ISwiftlyCore` through dependency injection
  - it is tightly coupled to plugin lifecycle and hot reload
- Suitable for: sorting service boundaries, locating core service entry points, and designing DI architecture.

### 3. Using attributes

- URL: `https://swiftlys2.net/docs/development/using-attributes/`
- Positioning: explains the valid boundary of the attribute registration mechanism.
- Key points:
  - attributes work directly by default only in the main class that inherits `BasePlugin`
  - if attributes are used in other classes, `Core.Registrator.Register(this)` must be called first
- Suitable for: explaining why `[Command]` or event attributes inside services / modules do not take effect.

### 4. Thread Safety

- URL: `https://swiftlys2.net/docs/development/thread-safety/`
- Positioning: the main-thread-sensitive API checklist.
- Key points:
  - calling thread-unsafe APIs from non-main threads may crash the server directly
  - Async variants execute immediately on the main thread and are scheduled to the next tick on non-main threads
  - the page explicitly lists main-thread-sensitive calls such as:
    - `IPlayer.Send* / Kick / ChangeTeam / SwitchTeam / TakeDamage / Teleport / ExecuteCommand`
    - `IGameEventService.Fire*`
    - `IEngineService.ExecuteCommand*`
    - `CEntityInstance.AcceptInput / AddEntityIOEvent / DispatchSpawn / Despawn`
    - `IPlayerManagerService.Send*`
    - `ICommandContext.Reply`
    - `CBaseModelEntity.SetModel / SetBodygroupByName`
    - `IEngineService.DispatchParticleEffect`
    - `CCSPlayerController.Respawn`
    - `Projectile.EmitGrenade`
    - `CPlayer_ItemServices.* / CPlayer_WeaponServices.*`
- Suitable for: auditing async tasks, menu callbacks, background workers, and hot-path write-back inside hooks.

### 5. Commands

- URL: `https://swiftlys2.net/docs/development/commands/`
- Positioning: commands, command aliases, and client command / chat hooks.
- Key points:
  - use either `[Command]` or `Core.Command.RegisterCommand`
  - use either `[CommandAlias]` or `Core.Command.RegisterCommandAlias`
  - `registerRaw` controls whether the `sw_` prefix is skipped
  - built-in permission parameters are supported
  - client command and chat hooks both return `HookResult`
  - unload performs automatic cleanup, but manual `Unregister` / `Unhook` is also supported
- Suitable for: command-system design, chat interception, and client-command filtering.

### 6. Configuration

- URL: `https://swiftlys2.net/docs/development/configuration/`
- Positioning: plugin configuration initialization, loading, and hot reload.
- Key points:
  - entry point is `Core.Configuration`
  - supports initializing config files through templates
  - supports `InitializeJsonWithModel<T>` / `InitializeTomlWithModel<T>` to generate default config from C# models
  - `Configure(builder => ...)` can append `json/jsonc/toml` config sources
  - recommended to pair it with `IOptionsMonitor<T>`, including `reloadOnChange`
  - supports fluent method chaining
- Suitable for: config-model design, hot reload, and DI + Options patterns.

### 7. Translations

- URL: `https://swiftlys2.net/docs/development/translations/`
- Positioning: translation-resource organization and localization access.
- Key points:
  - translation files live under `resources/translations/*.jsonc`
  - use language-code naming such as `en.jsonc` and `zh-CN.jsonc`
  - common entry point: `Core.Translation.GetPlayerLocalizer(player)`
  - supports parameter placeholders such as `{0}` and `{1}`
  - missing keys default to returning the key itself
  - it is recommended to always provide `en.jsonc` as the fallback
  - consistent key naming is recommended: `category.subcategory.key`
- Suitable for: player-localized messages, command prompts, and menu-text internationalization.

### 8. Entity

- URL: `https://swiftlys2.net/docs/development/entity/`
- Positioning: entity creation, lookup, and handle safety.
- Key points:
  - use `Core.EntitySystem.CreateEntity<T>()` or create entities by designer name
  - all entities can be enumerated or filtered by class
  - the official docs explicitly warn that **holding raw entities long-term is very dangerous**
  - long-term tracking should use `CHandle<T>` / `GetRefEHandle(entity)`
  - `handle.Value` may be null, so check `handle.IsValid` first
- Suitable for: cross-frame entity tracking, preview entities, beam/worldtext, and delayed-task entity references.

### 9. Entity Key Values

- URL: `https://swiftlys2.net/docs/development/entitykeyvalues/`
- Positioning: type-safe key-value writes for `CEntityKeyValues`.
- Key points:
  - `CEntityKeyValues` implements `IDisposable`
  - provides `SetBool/SetInt32/SetUInt32/SetInt64/SetFloat/SetString/...`
  - also supports generic `Set<T>` and `Get<T>` access
  - unsupported types throw `InvalidOperationException`
- Suitable for: building entity keyvalues and configuring entity properties before spawn.

### 10. Game Events

- URL: `https://swiftlys2.net/docs/development/game-events/`
- Positioning: Game Event fire and hook behavior.
- Key points:
  - use `Core.GameEvent.Fire<T>` and `FireToPlayer`
  - supports `HookPre<T>` / `HookPost<T>`
  - `@event` is a temporary object for the current tick and must not be held across ticks
  - the official docs specifically warn that **many Source 2 game events are effectively obsolete and some do not work**
- Suitable for: use only when the relevant Game Event is confirmed to exist and behave correctly; do not assume all events are reliable.

### 11. Core Events

- URL: `https://swiftlys2.net/docs/development/core-events/`
- Positioning: SwiftlyS2’s own typed core-listener system.
- Key points:
  - a Core Event is not a Game Event
  - listeners are destroyed on hot reload / unload
  - each event argument type carries its own field set
  - detailed event lists can be found under `EventDelegates`
- Suitable for: lifecycle listeners for maps, players, entities, ticks, hook callbacks, and similar flows.

### 12. Network Messages

- URL: `https://swiftlys2.net/docs/development/netmessages/`
- Positioning: typed protobuf net-message sending and hooks.
- Key points:
  - net messages are based on protobuf + message id
  - you can directly call `Core.NetMessage.Send<T>`
  - for high-frequency reuse, `Create<T>()` can be reused and released with `using`
  - supports client/server message hooks and corresponding unhook operations
  - see `ProtobufDefinitions` and `INetMessageService` for detailed types
- Suitable for: shake effects, sounds, HUD, and client/server network-message interception and sending.

### 13. Menus

- URL: `https://swiftlys2.net/docs/development/menus/`
- Positioning: complete menu system.
- Key points:
  - the entry point is `Core.Menus` / `IMenuManagerAPI`
  - supports a builder-style fluent API
  - built-in option types: `Button / Toggle / Slider / Choice / Text / Input / ProgressBar / Submenu`
  - supports hierarchical menus, dynamic content, global events, per-player validation, and formatting
  - supports `BeforeFormat` / `AfterFormat` / `Validating` / `Click` / `ValueChanged`
  - supports scrolling style, key overrides, freezing players, auto-close, and similar behaviors
- Suitable for: interactive menus, dynamic HUD menus, and permission-aware menus.

### 14. Convars

- URL: `https://swiftlys2.net/docs/development/convars/`
- Positioning: ConVar creation, lookup, replication to clients, and client-side queries.
- Key points:
  - `Core.ConVar.Create<T>()` / `Find<T>()`
  - assigning `.Value` enters the internal event queue and may not take effect immediately
  - for temporary immediate changes, prefer `.SetInternal(T value)`
  - supports `ReplicateToClient` and `QueryClient`
  - supports flag add/remove/update/query operations
- Suitable for: temporarily switching cvars, reading game convars, and querying client convars.

### 15. Native Functions and Hooks

- URL: `https://swiftlys2.net/docs/development/native-functions-and-hooks/`
- Positioning: signatures, addresses, delegates, function hooks, and mid-hooks.
- Key points:
  - signatures can be obtained from gamedata and then resolved into addresses
  - the delegate signature must strictly match the native signature
  - `Call()` goes through the current address, which may already be hooked by other mods; `CallOriginal()` uses the original call
  - supports both function hooks and mid-hook address hooks
  - mid-hooks can read and write registers, but incorrect changes can crash the server directly
  - hooks must always be uninstalled in matching pairs; the framework auto-cleans them on plugin unload
- Suitable for: advanced native calls, vtable functions, and Detour / MidHook-level extensions.

### 16. Scheduler

- URL: `https://swiftlys2.net/docs/development/scheduler/`
- Positioning: `NextTick` and tick-based timers.
- Key points:
  - `NextTick` schedules work to the next tick
  - `Delay / Repeat / DelayAndRepeat` use **game ticks** as the default unit
  - use the `*BySeconds` variants for second-based calls
  - returns a `CancellationTokenSource` that can be canceled
  - `StopOnMapChange(token)` can auto-cancel on map change
- Suitable for: main-thread delays, small periodic tasks, and automatic cleanup on map transitions.

### 17. Shared API

- URL: `https://swiftlys2.net/docs/development/shared-api/`
- Positioning: shared interfaces between plugins.
- Key points:
  - provide interfaces through `ConfigureSharedInterface`
  - consume interfaces through `UseSharedInterface`
  - interfaces should live in a separate contracts DLL shared by both provider and consumer
  - it is recommended for interfaces to inherit `IDisposable`
  - keys should use explicit naming and consider versioning
  - check `HasSharedInterface` before use
- Suitable for: cross-plugin shared services and exposing points, permission, or economy systems.

### 18. Permissions

- URL: `https://swiftlys2.net/docs/development/permissions/`
- Positioning: permission checks, groups, and sub-permissions.
- Key points:
  - `Core.Permission.PlayerHasPermission(steamId, permission)`
  - supports wildcard `*`
  - can `AddPermission` / `RemovePermission`
  - `permissions.jsonc` supports player groups and `__default`
  - supports `AddSubPermission(parent, child)` to form hierarchical permissions
  - recommended naming: `plugin.category.action`
- Suitable for: command permissions, menu visibility, and module access control.

### 19. Profiler

- URL: `https://swiftlys2.net/docs/development/profiler/`
- Positioning: performance measurement and naming conventions.
- Key points:
  - `StartRecording` / `StopRecording`
  - you can also use `RecordTime` to manually record microsecond values
  - hierarchical names such as `Database.Players.Load` are recommended
- Suitable for: hot-path performance sampling and segmented timing for complex flows.

### 20. Database

- URL: `https://swiftlys2.net/docs/development/database/`
- Positioning: unified entry point for database connection configuration.
- Key points:
  - `Core.Database.GetConnection(key)` reads the global SwiftlyS2 `configs/database.jsonc`
  - falls back to the default connection when the key does not exist
  - the official docs recommend ORM / ADO.NET tools such as Dapper, FreeSql, and EF Core
  - the website warns that username/password/host/database in connection strings should not contain `@ : /`
- Suitable for: plugin database integration and global connection reuse.

### 21. Sound Events

- URL: `https://swiftlys2.net/docs/development/soundevents/`
- Positioning: sound-event creation and sending.
- Key points:
  - `SoundEvent` must be wrapped in `using` / disposed
  - recipients must be added before sending
  - can set `Name / Volume / Pitch / SourceEntityIndex`
  - can attach position and various field parameters
- Suitable for: custom prompt sounds, weapon sounds, and ambient-sound broadcasting.

### 22. Steamworks

- URL: `https://swiftlys2.net/docs/development/steamworks/`
- Positioning: streamlined Steamworks.NET integration (game-server side).
- Key points:
  - use it through `using SwiftlyS2.Shared.SteamAPI;`
  - includes Steam ID, authentication, server info, Workshop downloads, callback handling, and related features
  - callback references must be kept alive to avoid GC collection
  - verify that Steamworks initialized successfully before use
  - see the API Reference for the full `SteamAPI` signatures
- Suitable for: ownership checks, Workshop downloads, and reporting server information.

## Guides Navigation

### 1. Dependency Injection

- URL: `https://swiftlys2.net/docs/guides/dependency-injection/`
- Positioning: the official primary design pattern recommended by SwiftlyS2.
- Key points:
  - `ServiceCollection().AddSwiftly(Core)` is recommended
  - common injected objects: `ISwiftlyCore`, `ILogger<T>`, `IOptionsMonitor<T>`
  - if a service uses attributes, the object must be registered manually
- Suitable for: new plugin architecture, service layering, and Options patterns.

### 2. Development Flow

- URL: `https://swiftlys2.net/docs/guides/development-flow/`
- Current state: the official page body is still `todo`
- Usage advice: keep the entry for navigation, but **do not treat this page as a formal authority**.

### 3. HTML Styling

- URL: `https://swiftlys2.net/docs/guides/html-styling/`
- Positioning: Panorama UI HTML styling guide.
- Key points:
  - the official docs list common supported tags: `div`, `span`, `p`, `a`, `img`, `br`, `hr`, `h1-h6`, `strong`, `em`, `b`, `i`, `u`, `pre`
  - styling does not use standard `style="..."`; attributes are written directly, such as `color="red"`
  - prefer built-in classes such as `fontSize-l`, `fontSize-xl`, `fontWeight-bold`, and `CriticalText`
  - `class` and `color` can be combined, which fits the “dynamic color + fixed size/weight” pattern
  - official examples cover ready counters, countdowns, progress bars, score displays, and multi-line rules/help UI
  - complex layouts, deep nesting, and unconventional classes must be validated in-game
  - the docs also link to SteamDatabase Panorama style references, where you can continue with files such as `panorama_base.css` and `gamestyles.css`
- Suitable for: `SendCenterHTML`, center-screen prompts, menu formatting, and rich-text UI scenarios such as `BindingText` / `BeforeFormat` / `AfterFormat`.
- Detailed toolkit write-up: `../assets/guides/html-styling/README.md`

### 4. Porting from CounterStrikeSharp

- URL: `https://swiftlys2.net/docs/guides/porting-from-css/`
- Positioning: system guide for migrating from CounterStrikeSharp to SwiftlyS2.
- Key points:
  - compares `.csproj`, events, commands, menus, configuration, database, ConVar, listeners, GameData hooks, and migration order
  - emphasizes that SwiftlyS2 uses `.NET 10`
  - emphasizes using `Updated()` instead of CSS’s `SetStateChanged`
  - provides replacement guidance from utility classes to `Core.*` services
- Suitable for: migrating historical repositories, aligning CSS semantics, and planning structural migrations.

### 5. Terminologies

- URL: `https://swiftlys2.net/docs/guides/terminologies/`
- Positioning: unifies the concepts of managed / native / controller / pawn / player object / handle.
- Key points:
  - explains the managed vs native boundary
  - distinguishes controller, pawn, slot/playerId, and player object
  - explains entity-index ranges and the handle concept
  - distinguishes temporary vs permanent entities
- Suitable for: terminology alignment and reducing conceptual confusion during migration and audits.

## API Reference Quick Navigation

### Root entry

- API Root: `https://swiftlys2.net/docs/api/`

### Core entry points listed on the official homepage

- Core Object: `https://swiftlys2.net/docs/api/iswiftlycore/`
- Game Events: `https://swiftlys2.net/docs/api/gameevents/`
- Core Listeners: `https://swiftlys2.net/docs/api/events/`
- SteamWorks API: `https://swiftlys2.net/docs/api/steamapi/`
- Commands: `https://swiftlys2.net/docs/api/commands/`

### High-value categories visible in the homepage sidebar

- Memory: `https://swiftlys2.net/docs/api/memory/`
- Menus: `https://swiftlys2.net/docs/api/menus/`
- Natives: `https://swiftlys2.net/docs/api/natives/`
- NetMessages: `https://swiftlys2.net/docs/api/netmessages/`
- Permissions: `https://swiftlys2.net/docs/api/permissions/`
- Players: `https://swiftlys2.net/docs/api/players/`
- Plugins：`https://swiftlys2.net/docs/api/plugins/`
- ProtobufDefinitions：`https://swiftlys2.net/docs/api/protobufdefinitions/`
- Scheduler：`https://swiftlys2.net/docs/api/scheduler/`
- SchemaDefinitions：`https://swiftlys2.net/docs/api/schemadefinitions/`
- Schemas：`https://swiftlys2.net/docs/api/schemas/`
- Services：`https://swiftlys2.net/docs/api/services/`
- Sounds：`https://swiftlys2.net/docs/api/sounds/`
- SteamAPI：`https://swiftlys2.net/docs/api/steamapi/`
- StringTable：`https://swiftlys2.net/docs/api/stringtable/`
- Translation：`https://swiftlys2.net/docs/api/translation/`
- Helper：`https://swiftlys2.net/docs/api/helper/`
- Helpers：`https://swiftlys2.net/docs/api/helpers/`
- Misc：`https://swiftlys2.net/docs/api/misc/`

### Recommended online lookup flow

When the toolkit summary is not enough, prefer this lookup order:

1. First identify the relevant section, such as `Commands`, `Menus`, `NetMessages`, or `Schemas`
2. Open the corresponding API category page first instead of doing a blind site-wide search
3. Then drill into the specific interface, for example:
   - `ICommandService`
   - `ICommandContext`
   - `INetMessageService`
   - `IEntitySystemService`
   - `ISchedulerService`
   - `IInterfaceManager`
   - `IPermissionManager`
4. For generated types (such as protobuf, schema definitions, or game events), continue drilling down from the category page first

## Recommended reading paths

### Building a new plugin

1. `Getting Started`
2. `Dependency Injection`
3. `Swiftly Core`
4. `Thread Safety`
5. The relevant subsystem page (`Commands` / `Menus` / `Configuration` / `Translations` ...)

### Auditing an existing plugin

1. `Thread Safety`
2. `Core Events`
3. `Entity`
4. `Scheduler`
5. `Profiler`
6. The relevant subsystem page

### Building cross-plugin sharing

1. `Shared API`
2. `Dependency Injection`
3. `Permissions`
4. `IInterfaceManager` in the API Reference

### Building UI / menus / HUD

1. `Menus`
2. `HTML Styling`
3. `Translations`
4. `NetMessages`

### Doing migration work

1. `Terminologies`
2. `Porting from CounterStrikeSharp`
3. `Dependency Injection`
4. `Thread Safety`
5. The page for the original feature module
