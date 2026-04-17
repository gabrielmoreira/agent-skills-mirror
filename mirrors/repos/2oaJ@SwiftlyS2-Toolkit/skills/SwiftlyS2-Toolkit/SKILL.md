---
name: SwiftlyS2-Toolkit
description: 'SwiftlyS2 toolkit for creating, modifying, auditing, planning, reviewing, and directly editing C#/.NET SwiftlyS2 plugins. Use when working on SwiftlyS2 plugins involving Commands, Events, Hooks, Modules, Workers, Services, high-frequency runtime loops, NetMessages, Schema access, or IPlayer lifecycle issues.'
argument-hint: 'Describe the plugin/task, target module or method, and whether historical behavior/reference extraction is required.'
user-invocable: true
disable-model-invocation: false
---

# SwiftlyS2-Toolkit

This is a general-purpose toolkit entry for **SwiftlyS2 C# / .NET plugin development**.

Its goal is not to bind itself to any specific workspace, but to provide a **publicly reusable** workflow, rule set, template collection, and reference navigation system.

## Public reference allowlist

The public docs, prompts, agents, and templates in this toolkit should, by default, reference only the following public sources:

1. SwiftlyS2 official documentation: `https://swiftlys2.net/docs/`
2. sw2-mdwiki: `https://github.com/himenekocn/sw2-mdwiki`
3. SwiftlyS2 official repository: `https://github.com/swiftly-solution/swiftlys2`

If the current workspace has workspace-specific mappings, local reference repositories, historical reference projects, or special rules, that information **may only be recorded in**:

- `./copilot-instructions.md`
- `./knowledge-base.md`

- If the workspace includes a local `sw2-mdwiki` checkout, it is strongly recommended to use it as a local reference repository to improve agent retrieval efficiency and accuracy.

## What this skill should produce

When using this skill, the preferred output should be one of the following:

- An implementation plan for a new plugin or new module
- A direct modification plan for an existing plugin
- A gap analysis for historical behavior alignment
- An audit of lifecycle, thread safety, high-frequency hooks, Schema, or Protobuf usage
- A method-level implementation plan

## When to use it

Use this skill when the task involves:

- SwiftlyS2 plugin development
- `Commands`, `Events`, `Hooks`, `Modules`, `Workers`, `Services`
- High-frequency runtime loops and state synchronization
- `Schema`, `NetMessages`, `Protobuf`, or `IPlayer` lifecycle handling
- High-frequency hooks, async workers, main-thread-sensitive APIs, or entity lifecycle handling
- Plugin migration, behavior alignment, structural audits, or method-level planning

## When not to use it

- Regular C# work unrelated to SwiftlyS2
- Pure frontend UI work
- A one-off tiny change that does not require architecture, lifecycle, or thread-boundary judgment

## Toolkit structure

### Entry documents

- `./SKILL.md`
- `./README.md`

### Reference documents

- `./references/swiftlys2-plugin-playbook.md`
- `./references/swiftlys2-kb-index.md`
- `./references/swiftlys2-official-docs-map.md`
- `./references/swiftlys2-asset-inventory.md`

### Templates and checklists

- `./assets/README.md`
- `./assets/development/getting-started/partial-plugin-template.cs.md`
- `./assets/development/using-attributes/attribute-registration-checklist.md`
- `./assets/development/swiftly-core/core-service-entrypoints.md`
- `./assets/development/commands/command-attribute-template.cs.md`
- `./assets/development/commands/command-service-template.cs.md`
- `./assets/development/commands/client-command-hook-template.cs.md`
- `./assets/development/menus/menu-template.cs.md`
- `./assets/development/netmessages/protobuf-handler-template.cs.md`
- `./assets/development/native-functions-and-hooks/hook-handler-template.cs.md`
- `./assets/development/configuration/config-hot-reload-template.cs.md`
- `./assets/development/convars/convar-template.cs.md`
- `./assets/development/core-events/lifecycle-checklist.md`
- `./assets/development/core-events/precache-resource-template.cs.md`
- `./assets/development/game-events/game-events-usage-notes.md`
- `./assets/development/shared-api/shared-interface-template.cs.md`
- `./assets/development/thread-safety/thread-sensitivity-checklist.md`
- `./assets/development/profiler/hotpath-gc-checklist.md`
- `./assets/development/entity/schema-write-checklist.md`
- `./assets/development/scheduler/scheduler-vs-worker-guide.md`
- `./assets/guides/dependency-injection/di-service-plugin-template.cs.md`
- `./assets/guides/dependency-injection/service-template.cs.md`
- `./assets/patterns/background-workers/worker-template.cs.md`
- `./assets/patterns/per-player-state/player-state-management-guide.md`
- `./assets/patterns/async-patterns/async-safety-guide.md`
- `./assets/patterns/service-factory/service-factory-template.cs.md`
- `./assets/workflows/planning/method-level-plan-template.md`
- `./assets/workflows/audit/audit-report-template.md`

### Paired prompts

- `../../prompts/SwiftlyS2-Toolkit-Plan.prompt.md`
- `../../prompts/SwiftlyS2-Toolkit-Audit.prompt.md`
- `../../prompts/SwiftlyS2-Toolkit-Edit.prompt.md`

## Task routing

### If the task is mainly “should we do this / how should this be broken down”

Open these first:

- `./references/swiftlys2-plugin-playbook.md`
- `../../prompts/SwiftlyS2-Toolkit-Plan.prompt.md`

### If the task is mainly “systematically find risks first”

Open these first:

- `./references/swiftlys2-plugin-playbook.md`
- `../../prompts/SwiftlyS2-Toolkit-Audit.prompt.md`
- `./assets/workflows/audit/audit-report-template.md`

### If the task is mainly “edit code directly”

Open these first:

- `../../prompts/SwiftlyS2-Toolkit-Edit.prompt.md`
- `./assets/README.md`
- The template or checklist closest to the relevant subsystem

### If the task is mainly “find reference entry points”

Open these first:

- `./references/swiftlys2-kb-index.md`
- `./references/swiftlys2-official-docs-map.md`
- `./README.md`

## Architecture categories

### 1. Modular gameplay plugins

Suitable when:

- A single plugin contains a large amount of gameplay logic
- It needs `Commands + Events + Hooks + Modules + Workers + Models`
- It needs per-player runtime state, state synchronization, persistence, and multi-module coordination

### 2. DI / service-oriented plugins

Suitable when:

- The plugin is medium or large in size
- It needs clear interface / implementation / install / uninstall lifecycles
- It needs `ServiceCollection`, dependency injection, self-owned listeners, and command registration inside services

### 3. Hybrid architecture

Suitable when:

- The plugin is mainly gameplay-module-oriented, but some subsystems fit services better
- The modular core needs to be augmented with a small number of installable and uninstallable services

## Core operating rules

### 1. Historical implementations are only temporary experience sources

- If the task requires behavior alignment, historical implementations may be referenced.
- But historical implementations must not become long-term dependencies of the future solution.

### 2. Silent drift is forbidden

- If the user explicitly requires historical alignment, legacy compatibility, or player-visible consistency, every difference must be explicitly explained or explicitly fixed.

### 3. Lifecycle closure is a hard requirement

At minimum, explicitly check:

- map load / unload
- player connect / disconnect

### 4. Main-thread / async boundaries must be explicit

According to the official SwiftlyS2 `Thread Safety` documentation, the following operations should be treated as main-thread-sensitive by default:

- Many message and entity operations on `IPlayer`
- `ICommandContext.Reply`
- `IGameEventService.Fire*`
- `IEngineService.ExecuteCommand*`
- `CEntityInstance.AcceptInput / DispatchSpawn / Despawn`
- `CBaseModelEntity.SetModel / SetBodygroupByName`
- `CCSPlayerController.Respawn`
- `CPlayer_ItemServices.*`
- `CPlayer_WeaponServices.*`

When in an async context, prefer the corresponding `Async` APIs instead of mechanically wrapping everything in `NextTick` / `NextWorldUpdate`.

### 5. For high-frequency hooks, prioritize safety before speed

- Filter irrelevant objects as early as possible
- Control allocations and logging
- Avoid JSON, IO, blocking waits, and unbounded lock contention
- Prefer a producer / consumer separation mindset
- Keep a 64-tick frame-budget mindset

### 6. `IPlayer` lifecycle has extremely high priority

- `IPlayer` objects may be destroyed after disconnect
- Delayed tasks, async callbacks, menu callbacks, and background worker writebacks must revalidate or reacquire the object
- Do not assume bots / fakeclients can reuse the same identity-key strategy as real players
- When bots and real players are stored together, prefer `SessionId` as the runtime lookup key
- Bot `SteamID` values are not reliable and should, in practice, be treated as fixed `0`; do not use them as stable bot lookup keys

### 7. For long-lived entity tracking, think in handles first

- Across frames, delays, or maps, do not hold raw entity wrappers long-term
- Prefer storing entities as `CHandle<T>` and validate before access

### 8. `Span` / `stackalloc` / `ref` should only be used when there is evidence

- Suitable for synchronous hot paths and small data transfers
- Must not cross `await`
- Must not cross threads
- Must not be captured by closures or escape the synchronous stack frame
- Do not introduce dangling references or shared-buffer risks just to avoid one copy

### 9. Treat menu callbacks as async contexts

- Review `Click`, `ValueChanged`, and `Submenu` callbacks as async-context code by default
- Prefer `BindingText` for dynamic display text

### 10. JSON and synchronous blocking are high-risk by default

- `.Wait()`, `.Result`, synchronous joins, and blocking IO should be treated as high-risk by default
- JSON serialization / deserialization should, by default, run in the background rather than inside hooks, runtime loops, menu callbacks, or main-thread periodic tasks

## Recommended reading order

### For planning

1. `./SKILL.md`
2. `./references/swiftlys2-plugin-playbook.md`
3. `../../prompts/SwiftlyS2-Toolkit-Plan.prompt.md`
4. `./assets/workflows/planning/method-level-plan-template.md`

### For auditing

1. `./SKILL.md`
2. `./references/swiftlys2-kb-index.md`
3. `../../prompts/SwiftlyS2-Toolkit-Audit.prompt.md`
4. `./assets/workflows/audit/audit-report-template.md`

### For direct code edits

1. `./SKILL.md`
2. `../../prompts/SwiftlyS2-Toolkit-Edit.prompt.md`
3. Relevant subsystem templates / checklists

## Output requirements

### If the user wants a plan

The output must include at least:

- Task classification
- Target plugin / subsystem
- Whether historical behavior alignment is involved
- A method-level plan
- Thread / lifecycle boundaries
- A regression matrix

### If the user wants an audit

The output must include at least:

- Risk levels
- File / method-level locations
- Evidence
- Repair directions
- Regression recommendations

### If the user requests direct editing

The output must include at least:

- Files and methods changed
- Why the change was made this way
- Validation results
- Which requirements were directly validated and which still need additional validation

## Examples

- “Add a DI-based state synchronization module for a SwiftlyS2 plugin.”
- “Audit a plugin’s RuntimeLoop and hook hot paths.”
- “Migrate player-visible behavior from a historical SwiftlyS2 plugin into the current architecture.”
- “Fix thread-sensitive calls inside menu callbacks and land the code directly.”
