# SwiftlyS2-Toolkit Edit Prompt

Use the `SwiftlyS2-Toolkit` skill to directly handle **add feature / modify feature / remove feature** scenarios in SwiftlyS2 plugins.

This prompt is meant for requests where the user explicitly wants to **land code changes directly**, rather than first doing a full audit or producing a long-form plan.

## Applicable scenarios

Prefer this prompt when the user asks for things like:

- “add a feature”
- “modify this feature”
- “remove this feature”
- “edit the code directly”
- “wire this logic in”
- “fix this feature, but don’t start with a huge plan”

## Goal

Even in direct-edit scenarios, keep SwiftlyS2 agent development quality high:

- first identify the feature type and owning subsystem
- then locate the entry point, state ownership, thread boundaries, and lifecycle closure
- then make the minimum necessary change
- finally perform build / error checking / regression validation

## Editing risk levels

### P0: plan or audit first before editing
- spans multiple subsystems and the boundaries are unclear
- involves broad behavioral drift in long-lived runtime state / persistence / cross-module state synchronization
- has clear historical-alignment requirements, but method-level mapping is not yet done
- continuing with direct edits is likely to damage the current architectural boundaries

### P1: direct editing is allowed, but with strong constraints
- high-frequency hooks
- schema / entity write-back
- protobuf / usercmd
- dense use of thread-sensitive APIs
- map lifecycle / disconnect cleanup / automatically controlled entity lifecycle

### P2: standard direct-edit scenarios
- menus
- commands
- localized service logic
- localized worker flow
- single-module behavior fixes

### P3: low-risk direct-edit scenarios
- small conditional fixes
- dynamic text binding
- small cleanups without behavioral drift

## Mandatory rules

1. Do not force every “direct edit” request to become a full audit.
2. But before editing, you must complete at least one round of **minimum necessary localization**.
3. If the task requires consistency with a historical implementation, all player-visible capabilities are core and must not be silently removed.
4. Direct editing must still preserve the current architecture boundaries. Do not shove logic back into the main class or write across layers just for convenience.
5. When thread-sensitive APIs are involved:
   - prefer `Async` variants in async contexts
   - do not default to `NextTick` / `NextWorldUpdate` as a blanket fallback
6. Treat menu `Click` / `ValueChanged` delegates as async-context logic.
7. For dynamic menu text, evaluate `BindingText` first.
8. If bots / fakeclients / auto-controlled entities or mixed bot-human storage are involved, do not directly equate bot identity keys with human identity strategy.
9. On hot paths or in high-frequency data passing, if SwiftlyS2 / the current API already provides parameters by `ref`, prefer continuing to use `ref`; if small high-frequency data passing is needed, you may evaluate `Span<T>` / `ReadOnlySpan<T>`, but do not misuse them across `await` or thread boundaries.
10. All comments must follow the repository’s existing conventions. If there is no extra convention, they must be meaningful and explain non-obvious intent.
11. High-risk changes must include build and scenario-regression notes.
12. If mixed bot / human storage is involved, prefer `SessionId` as the runtime lookup key by default, and do not treat a bot’s `SteamID` as a reliable primary key.

## Minimum navigation before use

Based on task content, prioritize these supporting assets:

### Command-related
- `./skills/SwiftlyS2-Toolkit/assets/development/commands/command-attribute-template.cs.md`
- `./skills/SwiftlyS2-Toolkit/assets/development/commands/command-service-template.cs.md`
- `./skills/SwiftlyS2-Toolkit/assets/development/commands/client-command-hook-template.cs.md`
- `./skills/SwiftlyS2-Toolkit/assets/development/using-attributes/attribute-registration-checklist.md`

### Menu-related
- `./skills/SwiftlyS2-Toolkit/assets/development/menus/menu-template.cs.md`
- `./skills/SwiftlyS2-Toolkit/assets/development/thread-safety/thread-sensitivity-checklist.md`

### Hook / runtime / hot-path work
- `./skills/SwiftlyS2-Toolkit/assets/development/native-functions-and-hooks/hook-handler-template.cs.md`
- `./skills/SwiftlyS2-Toolkit/assets/development/thread-safety/thread-sensitivity-checklist.md`
- `./skills/SwiftlyS2-Toolkit/assets/development/profiler/hotpath-gc-checklist.md`

### Schema / entity write-back
- `./skills/SwiftlyS2-Toolkit/assets/development/entity/schema-write-checklist.md`
- `./skills/SwiftlyS2-Toolkit/assets/development/thread-safety/thread-sensitivity-checklist.md`

### Configuration / ConVar
- `./skills/SwiftlyS2-Toolkit/assets/development/configuration/config-hot-reload-template.cs.md`
- `./skills/SwiftlyS2-Toolkit/assets/development/convars/convar-template.cs.md`

### Worker / async persistence / background tasks
- `./skills/SwiftlyS2-Toolkit/assets/development/scheduler/scheduler-vs-worker-guide.md`
- `./skills/SwiftlyS2-Toolkit/assets/patterns/background-workers/worker-template.cs.md`
- `./skills/SwiftlyS2-Toolkit/assets/patterns/async-patterns/async-safety-guide.md`
- `./skills/SwiftlyS2-Toolkit/assets/development/core-events/lifecycle-checklist.md`

### DI / service
- `./skills/SwiftlyS2-Toolkit/assets/guides/dependency-injection/di-service-plugin-template.cs.md`
- `./skills/SwiftlyS2-Toolkit/assets/guides/dependency-injection/service-template.cs.md`
- `./skills/SwiftlyS2-Toolkit/assets/patterns/service-factory/service-factory-template.cs.md`

### Resource precache / lifecycle
- `./skills/SwiftlyS2-Toolkit/assets/development/core-events/precache-resource-template.cs.md`
- `./skills/SwiftlyS2-Toolkit/assets/development/core-events/lifecycle-checklist.md`

### Player runtime state
- `./skills/SwiftlyS2-Toolkit/assets/patterns/per-player-state/player-state-management-guide.md`

### When higher-level engineering rules are needed
- `./skills/SwiftlyS2-Toolkit/references/swiftlys2-plugin-playbook.md`
- `./skills/SwiftlyS2-Toolkit/references/swiftlys2-kb-index.md`
- `./skills/SwiftlyS2-Toolkit/references/swiftlys2-asset-inventory.md`

## Direct-edit workflow

### 1. Determine the task type first
- **Add**: new capability, entry point, configuration, or flow
- **Modify**: adjust existing logic, fix a bug, or change behavior
- **Remove**: remove a feature, clean up an entry point, or delete dead branches

### 2. Then determine the risk level
- Is the current task P0 / P1 / P2 / P3?
- If it is P0, switch to `plan` or `audit` first
- If it is P1 / P2 / P3, continue with the direct-edit workflow

### 3. Perform minimum necessary localization
At minimum, answer:
- Where is the entry file / method?
- Which module / service / runtime context owns the state?
- Does it involve commands, menus, events, hooks, workers, schema, or protobuf?
- Does it involve `IPlayer` / `Pawn` / entity lifecycle?
- Does it involve thread-sensitive APIs?
- Does it involve bot / fakeclient identity lookup or mixed-storage key design?
- If bots / fakeclients are involved, is `SteamID` being mistakenly treated as a reliable key, and should it use `SessionId` instead?
- Is there avoidable high-frequency object copying that requires evaluating `ref` / `Span`?

### 4. Choose the appropriate assets
- command (attribute) → command attribute template + attribute checklist
- command (service-owned) → command service template
- command (client command hook) → client-command-hook-template + hook-handler-template
- menu → menu template + thread checklist
- hook → hook template + thread checklist + hotpath checklist
- schema → schema checklist
- worker → scheduler-vs-worker guide + worker template + lifecycle checklist
- service / DI → service template / DI template
- service factory / keyed DI → service-factory-template + di-service-plugin-template
- config / hot configuration reload → config-hot-reload-template
- convar → convar-template
- precache / resource precache → precache-resource-template + lifecycle-checklist
- per-player state / player runtime → player-state-management-guide
- async safety → async-safety-guide + lifecycle-checklist

### 5. Requirements during implementation
- make the smallest possible change
- do not alter unrelated formatting
- do not copy-paste logic across layers
- do not introduce “temporary TODO logic” into the main flow
- re-check whether player / entity is valid across every `await` / delayed task
- if this is only dynamic text updating, prefer `BindingText`
- for thread-sensitive calls in async contexts, prefer `Async` APIs
- if it is on a hot path, also check whether avoidable copying, boxing, or temporary array allocations can be removed

### 6. Validation requirements
At minimum perform:
- file problem checks
- build of the target plugin (if the change is actual code rather than documentation only)

Add based on risk:
- map load / unload
- connect / disconnect
- key state-transition paths (if relevant)
- bots / long-lived runtime state
- persistence / state recovery / cross-module synchronization

## Output format

### 1. Task determination
- type: add / modify / remove
- risk level: P0 / P1 / P2 / P3
- target plugin / subsystem
- entry-point localization
- primary state ownership

### 2. Editing strategy
- toolkit assets used
- why the implementation was done this way
- thread / lifecycle boundaries that need attention

### 3. Actual changes
List by file:
- **File**
- **Method / area**
- **What changed**
- **Why it changed this way**

### 4. Validation results
- problem-check results
- build result (if applicable)
- regression points covered
- high-risk scenarios not yet executed but still recommended

## When not to continue direct editing

If any of the following is true, switch to plan or audit thinking first:

- the change spans multiple subsystems and the behavior boundaries are unclear
- there is a clear need for historical behavior alignment, but the gap has not yet been clarified
- it involves broad drift in long-lived runtime state / persistence / state synchronization
- state ownership cannot be confirmed, so continuing would likely damage architecture boundaries

## Example uses

- “Directly add a settings menu to this SwiftlyS2 plugin and wire in the save logic.”
- “Change this command’s permission and prompts without touching other behavior.”
- “Remove the old reward entry and complete the cleanup logic.”
- “Convert the existing menu to dynamic text binding with BindingText.”
- “Change this thread-sensitive synchronous call into a more appropriate async-safe approach.”
