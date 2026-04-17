# SwiftlyS2 Plugin Agent Development Playbook

This playbook is the core engineering reference of `SwiftlyS2-Toolkit`, intended specifically to consolidate **publicly reusable** SwiftlyS2 development methodology.

Public evidence sources default to:

- SwiftlyS2 official documentation: `https://swiftlys2.net/docs/`
- The condensed docs navigation in this toolkit: `./swiftlys2-official-docs-map.md`
- sw2-mdwiki: `https://github.com/himenekocn/sw2-mdwiki`
- SwiftlyS2 official repository: `https://github.com/swiftly-solution/swiftlys2`

If a workspace also has local reference repositories, current project mappings, historical reference projects, or special experience, record them in `../../copilot-instructions.md` and `../../knowledge-base.md` instead of turning them into permanent hard dependencies here.

## 1. Three common architecture categories

### A. Modular gameplay plugins

Suitable for:

- plugins with substantial gameplay logic inside a single plugin
- plugins that need `Commands / Events / Hooks / Modules / Workers / Models`
- plugins that need player runtime state, state synchronization, and persistence to work together

Typical characteristics:

- the main plugin class is usually split into partials
- command, event, and hook entry points are layered separately from business modules
- high-frequency computation and background write-back are split into workers
- player runtime state has a unified state object instead of mirrored copies everywhere

### B. DI / service-oriented plugins

Suitable for:

- medium or large plugins
- cases needing interface → implementation layering
- cases needing explicit install / uninstall / initialize / cleanup lifecycle handling

Typical characteristics:

- uses `ServiceCollection` and `AddSwiftly(Core)`
- the root is responsible for composition
- services manage their own listeners, command registration, conditional hooks, and unload closure

### C. Hybrid architecture

Suitable for:

- plugins whose overall shape is more like modular gameplay
- but certain subsystems are better expressed as services
- cases where a modular gameplay body embeds a small number of DI / service capabilities

## 2. Main-thread and async boundaries

According to the official `Thread Safety` documentation, the following categories of operations should be treated as main-thread-sensitive by default:

- `IPlayer` messaging, control, movement, and entity-related calls
- `ICommandContext.Reply`
- `IGameEventService.Fire*`
- `IEngineService.ExecuteCommand*`
- `CEntityInstance.AcceptInput / DispatchSpawn / Despawn`
- `CBaseModelEntity.SetModel / SetBodygroupByName`
- `CCSPlayerController.Respawn`
- `CPlayer_ItemServices.*`
- `CPlayer_WeaponServices.*`

### Engineering rules

1. **Writing game state, entities, Schema, or protobuf should return to the main thread by default.**
2. **Background threads should mainly handle computation, encoding, disk IO, network IO, and batch processing.**
3. **When already in an async context, prefer `Async` APIs.**
4. **Do not bring `.Wait()`, `.Result`, synchronous joins, or blocking IO onto the main thread.**
5. **JSON encoding / decoding should go to background threads by default, not into hooks, runtime loops, or menu callbacks.**

## 3. Lifecycle closure

Any SwiftlyS2 plugin change should explicitly check at least:

- map load / unload
- player connect / disconnect
- start / stop of long-lived subsystems
- worker start / stop / flush / cancel

### Additional rules

- Delayed or async logic must not trust an old `IPlayer` by default.
- Map-level caches must be explicitly cleaned during map lifecycle events.
- Cross-object / cross-session two-way mappings must be atomically unbound when stopping.

## 4. `IPlayer` and bot / fakeclient identity

- Long-term identity for human players usually uses a stable player identifier.
- Bots / fakeclients must not casually rely on `SteamID`.
- In practice, a bot’s `SteamID` should be treated as fixed `0` and cannot be used as a reliable lookup key.
- For mixed bot-human storage, prefer `SessionId` as the runtime lookup key.
- Mixed storage must explicitly distinguish between human and bot identity-key strategies, instead of applying the human long-term identity strategy to bots by default.
- Any delayed task must revalidate that the player object is still valid before executing.

## 5. Long-lived entity tracking

- Across frames, delays, or maps, do not hold raw entity wrappers long-term.
- Prefer stable handle-based thinking.
- Perform validity checks before access.
- Be especially careful about entity-slot reuse in scenarios such as delayed destruction, preview entities, beams, or world text.

## 6. Hook hot paths

Common rules for high-frequency hooks:

1. filter irrelevant objects as early as possible
2. avoid unnecessary allocations
3. avoid JSON, IO, locks, and synchronous waiting
4. avoid high-frequency logging
5. prefer producer / consumer separation where appropriate
6. always remember the 64-tick frame budget

### `Span<T>` / `stackalloc` / `ref`

Consider them only when all of the following are true:

- the code is genuinely on a synchronous hot path
- the data volume is small and the lifetime is short
- it does not cross `await`
- it does not cross threads
- it does not get captured by closures or escape

If the benefit is unproven, do not misuse them just to look “more advanced”.

## 7. Schema / NetMessages / Protobuf

### Schema

- Writes should happen on the main thread.
- Add notifications such as `Updated()` / `SetStateChanged()` when needed.
- If asynchronous chains need the data, capture a safe snapshot on the main thread first.

### NetMessages / Protobuf

According to the official `Network Messages` documentation:

- network messages are based on typed protobuf
- sending, hook, and unhook all have explicit APIs
- they are best read on the main thread as early as possible, converted into plain models, and only then passed into async pipelines

### Native Functions and Hooks

According to the official `Native Functions and Hooks` documentation:

- the source of signatures and address resolution must be clear
- delegate prototypes must match exactly
- hooks must be unloadable in matched pairs
- mid-hooks are powerful but high-risk; incorrect register modification will crash the server directly

## 8. Menu callbacks

Menu callbacks should be reviewed as async-context code by default:

- `Click`
- `ValueChanged`
- `Submenu` construction callbacks

Recommended rules:

- evaluate `BindingText` first for dynamic text
- prefer `Async` APIs inside callbacks
- after wait points, revalidate player / pawn / runtime objects
- menus are UI shells, so state reads and writes should be pushed down into modules / services where possible

## 9. Worker / Scheduler

### Scenarios better suited for Scheduler

- lightweight, low-frequency, main-thread-safe periodic tasks

### Scenarios better suited for background workers or cancelable async loops

- disk / network IO
- JSON encoding / decoding
- batch processing
- intensive polling
- ongoing work that must not block the main thread

### Mandatory checks

- whether Start / Stop / Flush / Cancel are paired properly
- whether there are dangling fire-and-forget tasks
- whether objects and generations are revalidated before write-back

## 10. DI recommendations

According to the official `Dependency Injection` documentation:

- new plugins should prefer DI
- `ServiceCollection` + `AddSwiftly(Core)` is the basic entry point
- service constructors can inject `ISwiftlyCore`, logging, configuration, and similar dependencies
- if a service uses attribute-based registration, it requires explicit registration

Add three more engineering rules:

1. the root is responsible for composition, not for owning all local listener state
2. commands, events, and hooks registered by a service should be unloaded by that service itself
3. conditional hooks should explicitly maintain start / stop state instead of staying permanently installed and idling in callbacks

## 11. Configuration hot reload

### Standard initialization flow

```csharp
Core.Configuration.InitializeJsonWithModel<Config>("config.jsonc", "Main")
    .Configure(builder => builder.AddJsonFile("config.jsonc", optional: false, reloadOnChange: true));

var monitor = ServiceProvider.GetRequiredService<IOptionsMonitor<Config>>();
Config = monitor.CurrentValue;
monitor.OnChange(newConfig => { Config = newConfig; /* optional side effects */ });
```

### Engineering rules

1. **Fields on Config classes must have default values** so that the first serialization produces a complete config file.
2. **Use JSONC format** (`config.jsonc`) so comments are supported for maintainability.
3. **Handle side effects inside hot-reload callbacks**: scheduler restarts, cache cleanup, service reconnection, and similar logic.
4. **Do not do blocking IO inside hot-reload callbacks**.

See the template: `../assets/development/configuration/config-hot-reload-template.cs.md`.

## 12. ConVar

According to the official `Convars` documentation:

- ConVars are used for server parameters that can be adjusted immediately at runtime.
- Create them with `Core.ConVar.CreateOrFind()`, which is idempotent and reentrant.
- Supports bool / int / float / string types, and int/float support min/max range constraints.

### ConVar vs Config split

- **ConVar**: immediate console tuning by administrators, runtime switches, temporary fine-tuning.
- **Config**: structured configuration, nested objects, arrays, persistent default values.
- **Mixed use**: use ConVar for switches / fine-tuning, and Config for structured defaults.

### Declarative organization

It is recommended to declare them together in a partial file such as `MyPlugin.ConVars.cs`, using the `required` modifier to force initialization:

```csharp
public required IConVar<bool> ConVar_Enable { get; set; }
public required IConVar<int> ConVar_Limit { get; set; }
```

### Range conventions

- `-1` = unlimited
- `0` = disabled
- `>0` = specific numeric value

See the template: `../assets/development/convars/convar-template.cs.md`.

## 13. Per-player state management

### Pattern gradient

1. **Lightweight key-value**: `ConcurrentDictionary<ulong, T>` (single-value state, small plugins)
2. **Runtime state object**: `ConcurrentDictionary<ulong, PlayerRuntime>` (multi-field state, medium plugins)
3. **With DB restoration**: async restore from DB on connect, persistence on disconnect
4. **Slot array + generation counter**: `PlayerState?[64]` + generation counter (large gameplay plugins, O(1) lookup in high-frequency hooks)

### Identity-key strategy

- long-term human storage → `SteamID (ulong)`
- bot / fakeclient → `SessionId` (bot SteamID is fixed at 0)
- lookups inside high-frequency hooks → O(1) slot array

### Cleanup timing

State must be removed in `OnClientDisconnected`, map caches must be cleaned in `OnMapLoad/Unload`, and everything must be cleared in `Unload()`.

### Concurrency safety

- prefer `TryAdd` / `TryRemove` / `GetOrAdd` / `AddOrUpdate`
- avoid two-step writes such as `ContainsKey + Add` and `ContainsKey + Remove`
- use the `AddOrUpdate` merge predicate to prevent state downgrade

See the guide: `../assets/patterns/per-player-state/player-state-management-guide.md`.

## 14. Async safety patterns

### `.Forget()` pattern

When starting async work from a synchronous entry point (command, event callback), use `.Forget(Logger, "Context")` instead of `_ = Task`:

```csharp
OnMyCommandAsync(context).Forget(Logger, "MyPlugin.OnMyCommand");
```

### StopOnMapChange

`Core.Scheduler.StopOnMapChange(cts)` binds a `CancellationTokenSource` to the map lifecycle so that it is canceled automatically during map changes.

### Re-acquire `IPlayer` after async boundaries

After any `await`, `IPlayer` must be reacquired via `SteamID` and validated with `Valid()`.

### Generation Counter

Before async write-back, use a generation counter (`Interlocked.Increment` + `Volatile.Read`) to validate that the state is still current.

See the guide: `../assets/patterns/async-patterns/async-safety-guide.md`.

## 15. Service Factory / Keyed Service / Multi-Implementation

### Factory pattern

Use it when one feature interface has multiple strategy implementations selected by name or configuration at runtime.

### Keyed Singleton

Manage multiple independent configuration instances of the same interface through `AddKeyedSingleton` + `GetRequiredKeyedService`.

### Multi-implementation resolution with `GetServices<T>()`

When all implementations must be iterated and invoked (such as multiple trigger types), use `sp.GetServices<T>()` to retrieve them all.

### Batch lifecycle management

All services share `Install() / Uninstall()`, with exception isolation so one failure does not affect the others.

See the template: `../assets/patterns/service-factory/service-factory-template.cs.md`.

## 16. GameEvent Pre vs Post

### Pre Hook (`HookMode.Pre`)

- triggers before the event takes effect
- may return `HookResult.Stop` to intercept the event
- suitable for blocking propagation, modifying final behavior, or conditionally canceling

### Post Hook (`HookMode.Post`)

- triggers after the event takes effect
- suitable for follow-up processing based on event results (logging, rewards, state updates)
- common pattern: Post Hook + `DelayBySeconds` to wait for state stabilization before acting

### Engineering rules

- If you are unsure whether to use Pre or Post, prefer Post because it is safer.
- Interception in a Pre Hook must be confirmed as genuinely necessary.
- Entity operations in Post Hooks often need `NextTick` / `DelayBySeconds` to wait for state stabilization.

## 17. ClientCommandHookHandler

### Suitable scenarios

- globally intercepting client commands (`jointeam`, `radio`, `buy`, etc.)
- performing permission checks or behavior replacement at the earliest stage of command processing

### Key points

- pair it with `[Command("xxx", registerRaw: true)]` to ensure low-level recognition
- `HookResult.Stop` blocks the command, `HookResult.Continue` allows it
- the raw `commandLine` string must be parsed manually

See the template: `../assets/development/commands/client-command-hook-template.cs.md`.

## 18. OnPrecacheResource

- triggers early in map load for precaching models, sounds, and particle resources
- resources that are not precached will fail silently when used in calls like `SetModel` or `EmitSound`
- supports both static resources and dynamically configured resources
- in multi-service setups, each service may register its own resources

See the template: `../assets/development/core-events/precache-resource-template.cs.md`.

## 19. Cross-plugin command jumps

Mid-sized and large plugin hubs may jump to another plugin’s menu through `player.ExecuteCommand("sw_target-plugin-command")`:

- loose coupling: no direct dependency on another plugin’s code
- may close the current menu before jumping using `CloseAfterClick = true`
- the target command must already be registered and available to the current player

## 20. Comments and output

- Comments should explain intent, thread boundaries, lifecycle reasoning, and engine limitations.
- Avoid noisy comments.
- Planning, audit, and implementation records should land at method level whenever possible.

## 21. Public reference entry points

- Docs Map: `./swiftlys2-official-docs-map.md`
- Getting Started: `https://swiftlys2.net/docs/development/getting-started/`
- Swiftly Core: `https://swiftlys2.net/docs/development/swiftly-core/`
- Dependency Injection: `https://swiftlys2.net/docs/guides/dependency-injection/`
- Thread Safety: `https://swiftlys2.net/docs/development/thread-safety/`
- Native Functions and Hooks: `https://swiftlys2.net/docs/development/native-functions-and-hooks/`
- Network Messages: `https://swiftlys2.net/docs/development/netmessages/`
- sw2-mdwiki: `https://github.com/himenekocn/sw2-mdwiki`
- SwiftlyS2 official repository: `https://github.com/swiftly-solution/swiftlys2`
