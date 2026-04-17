# SwiftlyS2-Toolkit Audit Prompt

Use the `SwiftlyS2-Toolkit` skill to perform a **general audit** on a SwiftlyS2 plugin project.

## Audit objective

When the user asks to “audit” a SwiftlyS2 plugin or subsystem, do not look only at code style. Cover:

1. whether the architecture matches the project size and responsibility
2. whether lifecycle handling is closed properly
3. whether there are main-thread risks, deadlock risks, or delayed references to invalid players
4. whether high-frequency hooks contain hotspots such as allocations, logging, IO, locks, or blocking
5. whether Schema / Protobuf follows thread and write-back rules
6. whether behavioral drift exists when historical implementations or old versions are present
7. whether the implementation shows awareness of the 64-tick server frame budget

## Mandatory rules

- Player-visible historical behavior differences must be listed separately and must not be hidden inside “optimization items”.
- Every risk must be labeled with a severity level: P0 / P1 / P2 / P3.
- Audit conclusions must be actionable rather than vague advice.
- If comment issues are found, evaluate them against the repository’s comment conventions. If there is no extra convention, review them against the standard of being meaningful and explaining non-obvious semantics.
- You must explicitly check for synchronous blocking and main-thread JSON overhead.
- If the audit recommends `Span<T>`, `ReadOnlySpan<T>`, `stackalloc`, or `ref`, you must audit their safety boundaries at the same time.
- If historical repositories exist in the workspace, they may only be treated as temporary experience sources and must not be assumed to exist forever.
- If mixed bot / human storage exists, identity-key design must be audited separately, with special focus on whether a bot’s `SteamID` is misused.

## Priority references

### Skill reference documents

- `./skills/SwiftlyS2-Toolkit/references/swiftlys2-plugin-playbook.md`
- `./skills/SwiftlyS2-Toolkit/references/swiftlys2-kb-index.md`
- `./skills/SwiftlyS2-Toolkit/references/swiftlys2-asset-inventory.md`

### Public sources

- SwiftlyS2 official documentation: `https://swiftlys2.net/docs/`
- Thread Safety: `https://swiftlys2.net/docs/development/thread-safety/`
- Native Functions and Hooks: `https://swiftlys2.net/docs/development/native-functions-and-hooks/`
- Network Messages: `https://swiftlys2.net/docs/development/netmessages/`
- Dependency Injection: `https://swiftlys2.net/docs/guides/dependency-injection/`
- sw2-mdwiki: `https://github.com/himenekocn/sw2-mdwiki`
- SwiftlyS2 official repository: `https://github.com/swiftly-solution/swiftlys2`

### Current workspace-specific references (if present)

If `./copilot-instructions.md` or `./knowledge-base.md` records local workspace mappings, current project constraints, or special rules, read them as needed; however, when outputting a public audit, do not turn those local paths or workspace-specific project names into permanent dependencies.

## Audit dimensions

### 1. Architecture audit
- Does the current structure look more like modular gameplay, DI/service, or a hybrid architecture?
- Is the layering clear?
- Is business logic being incorrectly pushed into the main class / command / event entry?
- Should parts be extracted into a module / service / worker / manager?

### 2. Lifecycle audit
- `OnClientPutInServer`
- `OnClientDisconnected`
- `OnMapLoad`
- `OnMapUnload`

Check especially:
- whether delayed logic still holds `IPlayer` after disconnect
- whether dirty state remains after map change

### 3. Thread-safety and async audit
- whether main-thread APIs are misused from background threads
- whether `lock` introduces main-thread waiting risk
- whether `.Wait()`, `.Result`, or synchronous blocking exists
- whether JSON serialization / deserialization happens on the main thread
- whether worker stop / flush / cancel is complete
- whether generation / session checks exist

### 4. High-frequency hook audit
- whether there are meaningless allocations
- whether there are logging hotspots
- whether IO / API calls exist
- whether heavy CPU work like JSON is mixed in
- whether human / bot / dead-state fast-path routing is done
- whether producer / consumer separation exists
- whether the code reflects 64-tick server budget awareness
- whether hot-path data movement could use `Span/ReadOnlySpan/stackalloc/ref`

### 5. Schema / Protobuf audit
- whether `Updated()` / `SetStateChanged()` is called after Schema writes
- whether protobuf / usercmd / entity handles are accessed from unsafe threads
- whether protobuf is snapshotted into plain models when needed

### 6. Bot / fakeclient identity-key audit
- whether `SteamID` is incorrectly used to look up bots / fakeclients
- whether it is clearly understood that a bot’s `SteamID` should practically be treated as `0`
- whether `SessionId` is preferred as the lookup key for mixed bot / human runtime state
- whether mixed storage correctly distinguishes human and bot identity keys

### 7. Historical-implementation alignment audit (if applicable)
- list historical reference methods
- list current target methods
- list behavioral differences and player impact

## Output format

### 1. Audit scope
- target repository / plugin
- audit type
- main reference sources used

### 2. Summary conclusions
- current architecture classification
- overall risk level
- the most critical 3–10 issues

### 3. Issue list
For each issue, output:
- **Level**: P0 / P1 / P2 / P3
- **Issue**
- **Impact**
- **Location** (file + method)
- **Reference basis** (docs / repository / historical method)
- **Suggested repair direction**
- **Whether performance-optimization boundaries must also be explained**
- **Whether it involves main-thread synchronous blocking or main-thread JSON overhead**

### 4. Suggested repair priority
- what should be fixed first
- what can be done in parallel
- what needs to be expanded into a method-level plan

### 5. Regression matrix
- build
- map load / unload
- connect / disconnect
- gameevent / event / hook related paths (if applicable)
- high-frequency hook stress points (if relevant)

## Example uses

- “Audit this SwiftlyS2 plugin’s thread safety and lifecycle closure.”
- “Audit the behavioral gap between the historical implementation and the current implementation, focusing on state synchronization / high-frequency loops / persistence paths.”
- “Audit whether a SwiftlyS2 plugin should continue using modular gameplay architecture or should be changed to DI/service architecture.”
- “Audit high-frequency Hook performance hotspots and give optimization directions, but do not edit code directly.”
