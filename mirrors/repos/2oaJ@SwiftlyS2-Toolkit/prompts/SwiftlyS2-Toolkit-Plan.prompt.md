# SwiftlyS2-Toolkit Plan Prompt

Use the `SwiftlyS2-Toolkit` skill to generate an **actionable, method-level implementation plan with reference sources** for SwiftlyS2 plugin tasks.

## Goal

When the user wants to create, modify, optimize, refactor, migrate, or audit a SwiftlyS2 plugin project:

- first identify the task type and target plugin
- then determine which architecture should be referenced
- then output a method-level plan and regression matrix
- if historical implementations or older versions exist, treat them as **temporary experience sources** for extracting behavior and design experience

## Mandatory rules

1. If the task requires behavior to stay consistent with a historical implementation, **all player-visible capabilities are core features** and must not be marked as deferrable.
2. The current project’s architectural boundaries must be preserved. Do not simply roll back the directory structure for “quick alignment”.
3. Every plan must be detailed down to:
   - file
   - method
   - reference source
   - modification action
   - regression point
4. When high-frequency hooks, Schema, Protobuf, or `IPlayer` lifecycle are involved, thread / lifecycle boundaries must be stated explicitly.
5. All code comments must follow the repository’s existing conventions. If there is no additional convention, comments must remain meaningful and must not add noise.
6. You must consider the CS2 server’s 64-tick frame budget and avoid producing plans that would slow the main thread.
7. If the plan suggests using `Span<T>`, `ReadOnlySpan<T>`, `stackalloc`, or `ref` for hot-path optimization, it must also describe the safety boundaries clearly.
8. If historical repositories exist in the workspace, they may only be used as temporary references and must not be written in as long-term dependencies.
9. If the task involves mixed bot / human storage, the identity-key strategy must be explicitly designed. By default, prefer `SessionId` as the runtime lookup key, and do not treat a bot’s `SteamID` as a stable key.

## Reference materials (must be prioritized before generating the plan)

### Reference documents inside the skill

- `./skills/SwiftlyS2-Toolkit/references/swiftlys2-plugin-playbook.md`
- `./skills/SwiftlyS2-Toolkit/references/swiftlys2-kb-index.md`
- `./skills/SwiftlyS2-Toolkit/references/swiftlys2-asset-inventory.md`

### Public sources

- SwiftlyS2 official documentation: `https://swiftlys2.net/docs/`
- Getting Started: `https://swiftlys2.net/docs/development/getting-started/`
- Dependency Injection: `https://swiftlys2.net/docs/guides/dependency-injection/`
- Thread Safety: `https://swiftlys2.net/docs/development/thread-safety/`
- Native Functions and Hooks: `https://swiftlys2.net/docs/development/native-functions-and-hooks/`
- Network Messages: `https://swiftlys2.net/docs/development/netmessages/`
- Swiftly Core: `https://swiftlys2.net/docs/development/swiftly-core/`
- sw2-mdwiki: `https://github.com/himenekocn/sw2-mdwiki`
- SwiftlyS2 official repository: `https://github.com/swiftly-solution/swiftlys2`

### Current workspace-specific references (if present)

If `./copilot-instructions.md` or `./knowledge-base.md` records local workspace mappings, current project constraints, or special rules, read them as needed; however, when outputting a public plan, do not turn those local paths or workspace-specific project names into permanent dependencies.

## Architecture classification rules

### If it is a gameplay / state synchronization / player runtime plugin

Prefer classifying it as:

- **modular gameplay architecture**
- typical layering: `Commands + Events + Hooks + Modules + Workers + Services + Models`

### If it is an infra / manager / system / global capability plugin

Prefer classifying it as:

- **DI / service architecture**
- typical layering: `ServiceCollection + interface / implementation + install / uninstall`

### If it has characteristics of both sides

It may be classified as:

- **hybrid architecture**

## Required special experience to extract

If the task involves the following areas, the plan must explicitly state the handling principles:

### 1. Async and concurrency
- which logic must run on the main thread
- which logic can run in the background
- whether queue / flush / cancel / generation checks are needed
- whether map unload / plugin unload needs draining
- whether there are risks from `lock`, blocking waits, or main-thread waiting

### 2. High-frequency hooks
- whether humans / bots / dead states should be filtered early
- whether allocations and logging should be reduced
- whether producer / consumer separation should be used
- which stage is responsible for sampling, and which stage is responsible for computation or write-back

### 3. Schema reads and writes
- whether `Updated()`, `SetStateChanged()`, or native sync methods are needed
- whether snapshots should be taken on the main thread before asynchronous consumption

### 4. Protobuf / NetMessages
- whether reads and writes must stay on the main thread
- whether they should be converted immediately into plain models before asynchronous handling
- whether typed protobuf / hook / send / create / dispose behavior is involved

### 5. `IPlayer` lifecycle
- how connect / disconnect / map change / player-state reconstruction will be closed properly
- which identity key will manage this feature’s state
- if bots / fakeclients are involved, whether `SessionId` is explicitly used as the runtime lookup key
- whether the code incorrectly relies on a bot’s `SteamID`
- whether detach / cleanup / generation checks are needed to prevent stale writes
- whether delayed code may reference a destroyed `IPlayer`

## Output format

### 1. Task classification
- task type: create / modify / optimize / refactor / migrate / audit
- target plugin
- recommended architecture reference: modular gameplay / DI-service / hybrid

### 2. Key constraints
- player-visible behavior requirements
- thread-safety requirements
- lifecycle closure requirements
- historical implementation alignment requirements (if any)
- 64-tick performance budget requirements
- safety boundaries for using `Span`, `ReadOnlySpan`, `stackalloc`, and `ref` (if relevant)
- comment and code-style requirements

### 3. Method-level implementation plan
For each gap / subtask, output:
- **Gap**
- **Impact**
- **Reference source** (docs / repository / method)
- **Target file**
- **Target method**
- **Concrete modification steps**
- **Thread / lifecycle boundaries to watch**
- **Performance optimization boundaries to watch**
- **Regression validation points**

### 4. Validation matrix
At minimum cover:
- build
- map load / unload
- connect / disconnect
- key state-transition paths (if relevant)
- bots / long-lived runtime state (if relevant)
- persistence / state recovery / cross-module synchronization (if relevant)

## Example uses

- “Add a DI-based state synchronization module to a SwiftlyS2 plugin and generate a method-level plan.”
- “Audit a SwiftlyS2 plugin’s RuntimeLoop and Hook hot path and give me an optimization plan.”
- “Migrate behavioral experience from a historical SwiftlyS2 plugin into the new architecture, and all core features must remain non-deferrable.”
- “Choose between modular gameplay and DI/service architecture for a new plugin and give me a landing plan.”
