---
name: unreal-engine-5-development
version: 1.0.1
description: "Covers UE5.3–5.5 on Windows: C++ modules, Blueprints vs C++, Gameplay Framework/GAS intro, Enhanced Input, Nanite/Lumen, packaging, and Unreal Insights. Use when the task involves UE5, UObject, GameMode, Build.cs, BuildCookRun, or packaging Windows. Not for Godot/Unity, engine-agnostic game design (gameplay-and-design), deep AnimBP theory, or UE4 Hot Reload/Cascade/legacy input. Never cook from OneDrive or Documents paths (MAX_PATH failures)."
risk: safe
source: opus-skills-library
date_added: 2026-07-15
---

# Unreal Engine 5 Development

End-to-end UE5 workflow: bootstrap a C++ project, structure modules, split work between Blueprints and C++, build on the Gameplay Framework, wire Enhanced Input, use Nanite/Lumen deliberately, keep the Content Browser and version control sane, package a Windows Shipping build, and profile it. Written for UE 5.3–5.5 on Windows (PowerShell primary).

## Companion files

| File | Contents |
|---|---|
| [reference.md](reference.md) | UBT/UAT command lines, console/stat commands, UCLASS/UPROPERTY/UFUNCTION specifier tables, actor lifecycle order, config hierarchy, crash-pattern triage table, log/crash locations |
| [blueprints-vs-cpp.md](blueprints-vs-cpp.md) | Decision matrix, C++-base/BP-child pattern, exposing C++ to BP, BP performance realities, migration strategies |
| [project-structure.md](project-structure.md) | Disk + Content Browser layout, naming-prefix table, modules/plugins anatomy, Git LFS and Perforce setup, agent-friendly layouts, Windows path pitfalls |
| [examples.md](examples.md) | Complete compiling examples: Build.cs/Target.cs, GameMode stack, Character with Enhanced Input, GAS starter (ASC + AttributeSet + Ability), packaging scripts, automation test |

**When to load each reference:**
- Load [reference.md](reference.md) when running UBT/UAT commands, diagnosing crashes, profiling, or looking up UCLASS/UPROPERTY specifiers.
- Load [blueprints-vs-cpp.md](blueprints-vs-cpp.md) when deciding where a feature should live or migrating BP spaghetti to C++.
- Load [project-structure.md](project-structure.md) when setting up folder layout, version control, or hitting Windows path issues.
- Load [examples.md](examples.md) when writing Build.cs/Target.cs, a Character with Enhanced Input, GAS starter code, packaging scripts, or automation tests.

## When to Use

Activate when the task involves:

- **Creating or configuring a UE5 project** — .uproject, modules, Target.cs/Build.cs, plugins, engine version pinning.
- **Choosing Blueprints vs C++** for a feature, or refactoring BP spaghetti into a C++ base.
- **Gameplay Framework work** — GameMode, GameState, PlayerController, PlayerState, Pawn/Character, possession, replication-aware class placement, intro-level Gameplay Ability System (GAS).
- **Input** — Enhanced Input actions, mapping contexts, triggers/modifiers, rebinding.
- **Rendering decisions** — enabling/tuning Nanite, Lumen GI/reflections, Virtual Shadow Maps, and their content requirements.
- **Editor workflow** — Content Browser hygiene, redirectors, migration, DDC, Live Coding.
- **Version control for UE** — Git LFS attributes/locking or Perforce typemap for binary assets.
- **Packaging and shipping** — BuildCookRun, cook lists, Pak/IoStore, Shipping config, common packaging failures.
- **Profiling** — Unreal Insights, `stat` commands, GPU profiling, memreport.
- **Diagnosing crashes** — access violations, GC'd pointers, CDO/constructor pitfalls, assertion failures.

**Trigger keywords:** UE5, Unreal, Unreal Engine, Blueprint, UObject, AActor, UCLASS, UPROPERTY, GameMode, PlayerController, Enhanced Input, GAS, Gameplay Ability System, Nanite, Lumen, uproject, Build.cs, UnrealBuildTool, RunUAT, BuildCookRun, cook, pak, packaging Windows, Unreal Insights, stat unit, uasset, redirector.

### Do not use

- **Godot or Unity-only tasks** — route to `godot-*` skills or Unity-specific guidance; nothing here transfers except general design.
- **Engine-agnostic game design** (loops, economy, level design intent) — that's `gameplay-and-design`; this skill is the UE5 *implementation* layer.
- **Deep animation graph authoring** — locomotion/IK/blend theory lives in `game-runtime-animation`; this skill covers only where AnimBP sits in the framework.
- **Shader/VFX authoring theory** — `game-technical-art-vfx`; here only Nanite/Lumen material constraints are covered.
- **UE4-era answers** — do not recommend Hot Reload, Cascade, legacy input (`UPlayerInput` bindings), or Blueprint nativization; all are deprecated/removed in UE5.

## Prerequisites

- **Unreal Engine 5.3–5.5** installed (Launcher or source build). Record exact version (e.g. 5.4.4) in README.
- **Visual Studio 2022** with C++ game development workload, Windows SDK 10.0.
- **Windows host** with short, space-free project path (e.g. `D:\Dev\MyGame`). Avoid OneDrive or Documents paths — cooking nests deep paths and hits Windows' 260-char `MAX_PATH`.
- **Git with Git LFS** (for version control) or **Perforce** (industry default for UE).
- **DX12-capable GPU** with SM6 support for Lumen/Hardware RT.

## Procedure

### 1. Project setup

1. **Pin the engine version.** Launcher engine for standard work; source build only if you must patch engine code. Record the exact version (e.g. 5.4.4) in the README — .uproject `EngineAssociation` decides what opens it.
2. **Start C++ even for BP-heavy teams.** Create from a C++ template (or add a C++ class to a BP project via *Tools → New C++ Class*, which generates `Source/` and the .sln). A C++ project can do everything a BP project can; the reverse costs a conversion later.
3. **Keep the path short and space-free.** `D:\Dev\MyGame`, not `~\OneDrive\My Documents\Unreal Projects\My Great Game`. Cooking nests deep paths and hits Windows' 260-char `MAX_PATH`; see [project-structure.md](project-structure.md#windows-path-pitfalls).
4. **Generate project files** after any Build.cs/Target.cs or file add/move: right-click .uproject → *Generate Visual Studio project files*, or:

   ```powershell
   & "C:\Program Files\Epic Games\UE_5.4\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe" -projectfiles -project="D:\Dev\MyGame\MyGame.uproject" -game -engine
   ```

5. **First-pass Project Settings** (all land in `Config/Default*.ini` — text, commit them):
   - *Maps & Modes*: default GameMode, editor + game default maps.
   - *Packaging*: "List of maps to include in a packaged build" — set it explicitly or you cook everything referenced.
   - *Rendering*: decide Nanite/Lumen/VSM now (§6); flipping later re-cooks and re-lights.
   - *Input*: confirm Enhanced Input plugin classes are the defaults (5.1+ default).

### 2. Modules

1. One game module (`Source/MyGame/`) is fine until it isn't. Split when you have an editor-only layer (custom editor tooling → separate `MyGameEditor` module, `"Type": "Editor"` in .uproject) or a reusable subsystem you'll test/ship independently.
2. `Build.cs` rules: engine deps you `#include` in **headers** go in `PublicDependencyModuleNames`; .cpp-only deps go private. Missing module → linker error `unresolved external symbol`; see [examples.md](examples.md#buildcs) for a canonical file.
3. `IWYU`: include exactly what you use (`#include "GameFramework/Character.h"`, not monolithic headers). `PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;` is the modern default.
4. Prefer **plugins** (`Plugins/MyFeature/`) for anything two projects might share; a plugin is just modules + .uplugin with its own Content.

### 3. Blueprints vs C++ — the one-paragraph rule

**C++ owns systems, data flow, tick-heavy logic, and anything an agent must diff/review; Blueprints own composition, tuning, and glue.** The default architecture is a C++ base class per gameplay concept exposing `UPROPERTY(EditDefaultsOnly)` knobs and `BlueprintImplementableEvent`/`BlueprintNativeEvent` hooks, with a BP subclass that assigns assets and cosmetic reactions. Full decision matrix, exposure specifiers, and migration recipes: [blueprints-vs-cpp.md](blueprints-vs-cpp.md).

Minimal flavor — the C++-base/BP-child contract this skill defaults to:

```cpp
UCLASS(Abstract)
class MYGAME_API AWeaponBase : public AActor
{
    GENERATED_BODY()
public:
    UPROPERTY(EditDefaultsOnly, Category="Weapon")
    float Damage = 20.f;

    UFUNCTION(BlueprintCallable, Category="Weapon")
    void Fire();                       // logic in C++

    UFUNCTION(BlueprintImplementableEvent, Category="Weapon")
    void OnFired();                    // cosmetics in BP child (muzzle flash, sound)
};
```

### 4. Gameplay Framework

Place logic by **authority and lifetime**, not convenience:

| Class | Exists where | Lifetime | Put here |
|---|---|---|---|
| `AGameModeBase`/`AGameMode` | **Server only** | Per map load | Rules, spawning, win/lose, match flow. Never client UI. |
| `AGameStateBase` | Server + replicated to all | Per map load | Shared match data all clients need (time, phase, scores list) |
| `APlayerController` | Server + owning client | Per player, survives pawn death | Input handling, UI ownership, camera, "the player's will" |
| `APlayerState` | Server + replicated to all | Per player, survives pawn death & (with care) travel | Name, score, team, per-player replicated stats |
| `APawn`/`ACharacter` | Server + all clients | Disposable, possess/unpossess | Physical body: movement, mesh, collision, health *component* |
| `UGameInstance` | Local, one per running game | Whole session, survives map travel | Settings, session/party state, subsystem host |
| Subsystems (`UGameInstanceSubsystem`, `UWorldSubsystem`) | Match their outer | Automatic | Singleton-style managers without singleton pitfalls |

Rules of thumb:

- Anything that must survive the pawn dying goes on Controller/PlayerState, not the Pawn.
- Anything that must survive map travel goes on GameInstance or its subsystems.
- GameMode logic never runs on clients — if a client needs to see it, replicate via GameState/PlayerState.
- Possession flow: `GameMode::PostLogin → RestartPlayer → SpawnDefaultPawnFor → Controller::Possess → Pawn::PossessedBy / OnRep_PlayerState (client)`. Bind input and init ability systems at the right end of this chain (see GAS below).

**GAS intro (when a stats/abilities/buffs system is needed):** enable the *GameplayAbilities* plugin; give the avatar an `UAbilitySystemComponent` (ASC) + `UAttributeSet`; for player characters put the ASC on **PlayerState** (survives respawn) and call `InitAbilityActorInfo(PlayerState, Character)` in `PossessedBy` (server) *and* `OnRep_PlayerState` (client); drive all stat changes through `GameplayEffect`s, never by setting attributes directly; gate/annotate everything with GameplayTags. Adopt GAS when you have ≥ 2 of: buffs/debuffs, cooldowns+costs, damage-over-time, networked ability prediction. Skip it for a single health float. Starter code: [examples.md](examples.md#gas-starter).

### 5. Enhanced Input

Legacy input bindings are deprecated. The pipeline is:

1. **`UInputAction` assets** (IA_Move `Vector2D`, IA_Look `Vector2D`, IA_Jump `bool`) — one per abstract verb.
2. **`UInputMappingContext`** (IMC_Default) maps hardware keys → actions, with **modifiers** (Swizzle for WASD→2D, Negate, Dead Zone) and **triggers** (Pressed, Hold, Tap).
3. Add the context in `SetupPlayerInputComponent` (or `OnPossess`) via `UEnhancedInputLocalPlayerSubsystem::AddMappingContext(IMC, Priority)`.
4. Bind with `UEnhancedInputComponent::BindAction(IA, ETriggerEvent::Triggered, this, &AMyCharacter::Move)`; handlers take `const FInputActionValue&`.
5. Contexts stack by priority — add IMC_Vehicle at higher priority when entering a car, remove on exit. Rebinding UIs swap key mappings inside the context (`UEnhancedInputUserSettings` in 5.3+).

Full character example: [examples.md](examples.md#character-enhanced-input).

### 6. Nanite & Lumen — practical use

**Nanite** (virtualized geometry for static meshes):

1. Enable per-mesh (Static Mesh editor → Nanite Settings → Enable) or in bulk (right-click → Nanite → Enable). Project must have it on (default in new 5.x projects, `r.Nanite=1`).
2. Use for: dense static geometry, kitbashed environments, megascans. **Not for:** translucent materials, meshes needing vertex-paint-driven deformation beyond WPO limits, most skeletal meshes (experimental in 5.5), aggregates like foliage cards where masked overdraw dominates.
3. Material limits: opaque or masked only; World Position Offset works (5.1+) but costs; no vertex interpolator tricks that need real vertices.
4. Nanite pairs with **Virtual Shadow Maps** (`r.Shadow.Virtual.Enable=1`) — non-VSM shadows on Nanite fall back and look/perform worse.
5. Debug: viewport *Show → Nanite Visualization → Overdraw/Triangles*; `stat nanite`.

**Lumen** (dynamic GI + reflections):

1. Requires SM6 + DX12 on Windows (Project Settings → Platforms → Windows → Default RHI = DX12; Targeted Shaders SM6). If packaged game renders black/no-GI, check these first.
2. **Software** ray tracing (default) uses **mesh distance fields** — keep *Generate Mesh Distance Fields* on; meshes scaled non-uniformly or paper-thin lose GI quality. **Hardware** RT (`r.Lumen.HardwareRayTracing=1`) is higher quality if the GPU allows.
3. Content rules: interiors need closed geometry (light leaks come from open backfaces); emissive materials do contribute but noisily — prefer real lights for key lighting; avoid huge single meshes (distance field resolution is per-mesh).
4. Cost control: *Lumen Scene Detail*, *Final Gather Quality* via `PostProcessVolume`; scalability group `sg.GlobalIlluminationQuality`.
5. Fallback story: if you must support DX11/low-end, decide **early** — Lumen off means baked lightmaps (Lightmass) or SSGI, i.e. different authoring. Don't discover this at ship.

### 7. Editor workflow & Content Browser hygiene

1. **Never move/rename assets in Windows Explorer.** Only in the Content Browser; UE tracks references by object path. After moves: right-click folder → **Fix Up Redirectors** (redirectors left behind break farm cooks and confuse everyone).
2. No loose assets in `/Content` root; follow the folder scheme in [project-structure.md](project-structure.md).
3. Check references before delete (right-click → *Reference Viewer*), and *Size Map* to find what's bloating cooks.
4. **Migrate** (right-click → Migrate) to copy assets between projects with dependencies — never file-copy uassets.
5. **Live Coding** (Ctrl+Alt+F11) patches function-body changes while the editor runs. Header/class-layout changes (new UPROPERTY, changed signatures) require closing the editor and rebuilding — Live Coding "success" after a layout change can corrupt in-memory state and produce phantom bugs; when in doubt, restart.
6. Set up a **shared DDC** on a team (network path in `DefaultEngine.ini` `[DerivedDataBackendGraph]`) — otherwise every machine recompiles every shader.
7. Editor eating your evening: `r.ShaderCompiler` jobs pile up on first open; that's normal, don't kill it mid-compile.

### 8. Version control

Binary assets make VCS a first-class design problem — full setup in [project-structure.md](project-structure.md#version-control):

1. **Commit:** `Content/`, `Config/`, `Source/`, `Plugins/` (own code), `.uproject`. **Ignore:** `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`, `.vs/`, `*.sln`.
2. **Git**: mandatory **Git LFS** for `*.uasset`, `*.umap` + **file locking** (uassets are unmergeable; two people editing one asset = one loses). Use the editor's Revision Control integration so checkouts lock.
3. **Perforce**: the industry default for UE; set the **typemap** so uasset/umap are `binary+l` (exclusive checkout).
4. Enable **One File Per Actor (OFPA)** on levels with multiple editors — turns one giant .umap into many tiny per-actor files, killing most map lock contention.

### 9. Packaging a Windows Shipping build

1. Sanity-pass Project Settings → Packaging: build config **Shipping**, *Use Pak File* + *Use IoStore* on, cook-map list explicit, *Full Rebuild* off for iteration.
2. Package via UI (Platforms → Windows → Package Project) or, for CI/agents, **UAT**:

   ```powershell
   & "C:\Program Files\Epic Games\UE_5.4\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun `
     -project="D:\Dev\MyGame\MyGame.uproject" -platform=Win64 -clientconfig=Shipping `
     -build -cook -stage -pak -iostore -archive -archivedirectory="D:\Builds\MyGame"
   ```

3. Shipping config strips `UE_LOG` verbosity below Warning by default, disables the console and most `stat` commands, and removes `check()`s only if configured — **test in Shipping before release day**, not just Development. Keep a `Test` config build around: Shipping-like perf, but with stats.
4. Classic packaging failures and fixes are tabled in [reference.md](reference.md#packaging-failures): cook errors from unfixed redirectors, un-cooked referenced maps, path length blowups, plugin modules missing Win64 whitelist, blueprint compile errors that only surface in cook.
5. First run of a packaged build lives in `Saved/Logs` *of the staged build dir* — pass `-log` to get a console window when debugging.

### 10. Profiling

1. **Frame budget first:** `stat unit` — is it Game (CPU game thread), Draw (render thread), GPU, or RHIT bound? Optimize the bound thread only.
2. **CPU:** Unreal Insights — launch game with `-trace=default,counters -statnamedevents`, open the .utrace in *UnrealInsights.exe*. Wrap suspect code in `TRACE_CPUPROFILER_EVENT_SCOPE(MyScope)`.
3. **GPU:** `ProfileGPU` console command (needs `r.ProfileGPU.ShowUI 1` for detail) or Insights GPU track; `stat gpu` for live numbers.
4. **Memory:** `memreport -full` dumps to `Saved/Profiling/MemReports`; watch texture group budgets and unbounded actor counts.
5. **Common wins:** tick fewer things (`PrimaryActorTick.bCanEverTick=false` by default, timers over per-frame checks), pool spawns, cap shadow-casting local lights, verify Nanite overdraw view, and check `stat streaming` for texture thrash.
6. Full command table: [reference.md](reference.md#profiling-commands). Cross-engine methodology: `game-performance-profiling`.

### 11. Crash patterns — top offenders

Triage table with symptoms → causes → fixes in [reference.md](reference.md#crash-patterns). The big five:

1. **Access violation reading 0x0** — unchecked pointer. Guard with `IsValid(Obj)` (checks pending-kill, not just null); never trust `GetWorld()`, `GetOwner()`, cast results.
2. **GC'd object accessed** — raw `UObject*` member without `UPROPERTY()` is invisible to the garbage collector and becomes a dangling pointer within ~60s. Every UObject pointer member must be `UPROPERTY()` (or `TWeakObjectPtr` checked before use).
3. **Constructor doing runtime work** — constructors run on the **CDO** at engine startup: no `GetWorld()`, no spawning, no timers, no other actors. Use `BeginPlay`/`PostInitializeComponents`.
4. **Ensure/check assertion text** — read it; `check(...)` failures name the condition and file. `Ensure` continues (logged), `check` crashes. Fix the invariant, don't delete the check.
5. **Editor-works/package-crashes** — usually editor-only code paths (`#if WITH_EDITOR` leaks), assets excluded from cook, or plugin missing from the target platform list.

### 12. Agent-friendly workflow (working on UE5 as a coding agent)

1. **Prefer C++ and text assets**: an agent can read/diff `Source/`, `Config/*.ini`, `.uproject`, DataTable CSV/JSON sources — it cannot meaningfully read `.uasset` binaries. Keep logic where you can see it; keep BP graphs thin (see [blueprints-vs-cpp.md](blueprints-vs-cpp.md)).
2. **Headless verification loop**: compile with UBT, run automation tests, cook-validate:

   ```powershell
   # Compile
   & "C:\Program Files\Epic Games\UE_5.4\Engine\Build\BatchFiles\Build.bat" MyGameEditor Win64 Development -project="D:\Dev\MyGame\MyGame.uproject"

   # Run automation tests headlessly
   & "D:\Dev\MyGame\Binaries\Win64\UnrealEditor-Cmd.exe" "D:\Dev\MyGame\MyGame.uproject" -ExecCmds="Automation RunTests MyGame; Quit" -unattended -nopause -nullrhi -log

   # Cook-validate
   & "C:\Program Files\Epic Games\UE_5.4\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun -project="D:\Dev\MyGame\MyGame.uproject" -platform=Win64 -cook -skipbuild -skipstage -skippackage
   ```

   Full commands: [reference.md](reference.md#agent-command-lines).
3. **Read logs, not vibes**: `Saved\Logs\MyGame.log`, crash contexts in `Saved\Crashes\`. Grep for `Error:`, `Warning:`, `Ensure condition failed`, `Fatal`.
4. **Windows paths in commands**: quote everything, prefer short project roots, use backtick (`` ` ``) line continuation in PowerShell and `^` in .bat — mixed examples in [reference.md](reference.md).

## Pitfalls

### NEVER Do (Expert Anti-Patterns)

- **NEVER hold a `UObject*` member without `UPROPERTY()`** — silent GC dangling pointer, the classic UE crash.
- **NEVER do world/spawn/timer work in a C++ constructor** — it runs on the CDO. `BeginPlay` is your earliest safe world access.
- **NEVER move or rename uassets outside the editor** — breaks every reference; use Content Browser + Fix Up Redirectors.
- **NEVER commit `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`** — hundreds of MB of regenerable churn.
- **NEVER put uassets in Git without LFS + locking** — binary, unmergeable; someone's work gets destroyed.
- **NEVER ship logic in GameMode that clients need** — GameMode doesn't exist on clients; replicate via GameState/PlayerState.
- **NEVER `Cast<>` and dereference without a null check** — failed casts return nullptr, they don't throw.
- **NEVER Tick when an event/timer/delegate works** — default new actors/components to no-tick and justify every tick you enable.
- **NEVER trust Live Coding across header changes** — restart the editor after layout changes.
- **NEVER leave rendering-mode decisions (Lumen/Nanite/DX12) until late** — they change content authoring, min-spec, and cook output.
- **NEVER hardcode asset paths in C++ (`FObjectFinder` in gameplay logic)** — use `TSoftObjectPtr` UPROPERTYs or data assets; hardcoded paths break on every content move.
- **NEVER package first time on release day** — package Shipping weekly from day one; cook failures compound.

### Common gotchas

- **Live Coding "success" after header changes** can corrupt in-memory state and produce phantom bugs. When in doubt, restart the editor.
- **Shipping config strips `UE_LOG` below Warning** — you won't see your Info logs in a Shipping build. Test with Development or Test config first.
- **Unfixed redirectors break farm cooks** — always run Fix Up Redirectors after asset moves before committing.
- **Path length blowups** — Windows `MAX_PATH` is 260 chars; cooking nests deep temp paths. Keep project roots short.
- **Plugin modules missing Win64 whitelist** — packaging fails if your plugin's .uplugin doesn't list Win64 under TargetPlatforms.
- **Blueprint compile errors only surface in cook** — always cook-test before shipping; editor-only compilation can mask errors.

## Verification

- [ ] Project opens from a short, space-free Windows path; `EngineAssociation` matches the pinned engine version.
- [ ] `Source/` exists (C++ project); Build.cs deps split public/private correctly; project files regenerate cleanly.
- [ ] Every UObject pointer member is `UPROPERTY()` (or checked `TWeakObjectPtr`); no world access in constructors.
- [ ] Logic placed per the framework table: server rules in GameMode, replicated shared state in GameState/PlayerState, session state in GameInstance.
- [ ] Input goes through Enhanced Input (InputActions + MappingContexts); no legacy axis/action bindings added.
- [ ] Nanite/Lumen/DX12/SM6 decisions recorded in `DefaultEngine.ini` and content authored to their constraints (opaque/masked Nanite materials, closed interiors for Lumen).
- [ ] Content Browser follows the naming/folder scheme; zero unresolved redirectors (Fix Up Redirectors run).
- [ ] VCS ignores Binaries/Intermediate/Saved/DDC; uassets under LFS with locking, or Perforce typemap `binary+l`.
- [ ] A Shipping (or Test) build packages via `RunUAT BuildCookRun` without cook errors and boots on a clean machine.
- [ ] `stat unit` checked; the bound thread identified before optimizing; an Insights trace captured at least once.
- [ ] Automation smoke test runs headlessly via `UnrealEditor-Cmd.exe` and passes.

### Checkable commands

```powershell
# Verify project files regenerate
& "C:\Program Files\Epic Games\UE_5.4\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe" -projectfiles -project="D:\Dev\MyGame\MyGame.uproject" -game -engine

# Verify compilation
& "C:\Program Files\Epic Games\UE_5.4\Engine\Build\BatchFiles\Build.bat" MyGameEditor Win64 Development -project="D:\Dev\MyGame\MyGame.uproject"

# Verify headless automation test
& "D:\Dev\MyGame\Binaries\Win64\UnrealEditor-Cmd.exe" "D:\Dev\MyGame\MyGame.uproject" -ExecCmds="Automation RunTests MyGame; Quit" -unattended -nopause -nullrhi -log

# Verify Shipping package
& "C:\Program Files\Epic Games\UE_5.4\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun `
  -project="D:\Dev\MyGame\MyGame.uproject" -platform=Win64 -clientconfig=Shipping `
  -build -cook -stage -pak -iostore -archive -archivedirectory="D:\Builds\MyGame"

# Check logs for errors
Select-String -Path "D:\Dev\MyGame\Saved\Logs\MyGame.log" -Pattern "Error:|Fatal|Ensure condition failed"
```

## Examples

Complete, compiling examples live in [examples.md](examples.md): module Build.cs/Target.cs, GameMode/GameState/PlayerState stack, a full `ACharacter` with Enhanced Input, a GAS starter (ASC on PlayerState + AttributeSet + one ability), BuildCookRun packaging scripts (batch + PowerShell), and a functional automation test.

## Related skills

- [game-performance-profiling](../game-performance-profiling/SKILL.md) — engine-agnostic profiling methodology behind §10.
- [game-player-controller](../game-player-controller/SKILL.md) / [game-input-handling](../game-input-handling/SKILL.md) — controller feel and input design that Enhanced Input implements.
- [game-runtime-animation](../game-runtime-animation/SKILL.md) — the animation-graph theory behind AnimBPs.
- [game-technical-art-vfx](../game-technical-art-vfx/SKILL.md) — shader/VFX authoring feeding Nanite/Lumen-compatible materials.
- [game-assets-pipeline](../game-assets-pipeline/SKILL.md) — DCC-to-engine import flow upstream of the Content Browser.
- [game-3d-rendering](../game-3d-rendering/SKILL.md) — general 3D rendering concepts under Nanite/Lumen.
- [gameplay-and-design](../gameplay-and-design/SKILL.md) — what to build; this skill is how, in UE5.
- [git-workflow](../git-workflow/SKILL.md) — general git practice under the LFS/locking layer here.
