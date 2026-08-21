---
name: game-unreal-engine
version: 1.0.2
description: "Use when building games in Unreal Engine 5.x — C++ gameplay code, Blueprints, the Gameplay Framework (GameMode/Pawn/Character/PlayerController), Gameplay Ability System (GAS), Nanite/Lumen rendering, and editor/runtime plugins and modules. Triggers on UE5, UCLASS, UPROPERTY, AActor, UCharacterMovementComponent, .Build.cs, Nanite, Lumen, GAS. Not for Godot (use game-godot-master), Unity (use game-unity-engine), Blender asset authoring (use game-blender-asset-pipeline), or FMOD/Wwise audio (use game-fmod-wwise-integration)."
risk: safe
source: opus
date_added: 2026-06-27
---

# Unreal Engine 5

Architecture, C++/Blueprint patterns, rendering, and plugin development for Unreal Engine 5.x (targets 5.4–5.6). Windows host is primary (PowerShell). All commands assume a Windows development environment unless otherwise noted.

## When to Use

- Writing **C++ gameplay classes** (`AActor`, `APawn`, `ACharacter`, `UActorComponent`, `UObject`) and exposing them to Blueprints.
- Designing with the **Gameplay Framework**: `GameInstance`, `AGameModeBase`, `AGameStateBase`, `APlayerController`, `APlayerState`, `AHUD`.
- Implementing abilities/attributes with the **Gameplay Ability System (GAS)**.
- Tuning **Nanite** (virtualized geometry) and **Lumen** (dynamic GI/reflections).
- Building **editor or runtime plugins/modules**, custom `Slate`/`UMG` editor tooling, or `.Build.cs`/`.uproject` configuration.
- Replication and authority for **multiplayer** Unreal projects.

### Do Not Use

| If the task is… | Use instead |
|---|---|
| A Godot 4.x game | `game-godot-master` |
| A Unity C#/DOTS game | `game-unity-engine` |
| Authoring/rigging/exporting meshes in Blender | `game-blender-asset-pipeline` |
| FMOD or Wwise middleware integration | `game-fmod-wwise-integration` |
| Steam achievements/lobbies/workshop | `game-steamworks-sdk` |
| Hand-rolled SAT/Verlet/fluid math | `game-custom-physics-solvers` |

## Prerequisites

- **Unreal Engine 5.4–5.6** installed via the Epic Games Launcher or built from source. Source builds live at `C:\Program Files\Epic Games\UE_5.5` (Launcher) or your custom source path.
- **Visual Studio 2022** with the "Game development with C++" workload, including the Windows SDK and the latest MSVC toolchain.
- **.NET 6+ SDK** (required by UnrealBuildTool for `.Build.cs` compilation).
- Live Coding enabled (default in 5.4+). Legacy Hot Reload must be **disabled** — it is deprecated and corrupts editor state.
- For packaging: the appropriate platform toolchains installed (Windows SDK for Win64, etc.).

## Procedure

### 1. Engine Version Awareness

UE 5.4+ ships **Live Coding** (Ctrl+Alt+F11) as the default iterate-on-C++ path; legacy Hot Reload is deprecated and corrupts state — disable it. Nanite supports foliage and (5.5+) skinned meshes. `UE_5.5`+ uses the `FProperty` system (not the old `UProperty`). Always gate version-specific code with:

```cpp
#if ENGINE_MAJOR_VERSION == 5 && ENGINE_MINOR_VERSION >= 5
    // 5.5+ specific code
#endif
```

### 2. Gameplay Framework Ownership

| Class | Lifetime | Owns | Replicated? |
|---|---|---|---|
| `UGameInstance` | Whole process (survives level loads) | Save data, online subsystem, persistent managers | No (server-only logic) |
| `AGameModeBase` | Server only, per-level | Rules, spawning, win/lose | Exists only on server |
| `AGameStateBase` | Per-level, all clients | Match state, shared scores | Yes |
| `APlayerController` | Per-player | Input, camera, client RPC target | Owning client + server |
| `APlayerState` | Per-player, all clients | Player name, score, team | Yes |
| `APawn`/`ACharacter` | While possessed | Movement, collision, mesh | Yes |

**Rule of thumb:** gameplay rules live in C++ on the server; presentation lives in Blueprints on the client. Never put authoritative logic in a Blueprint that clients can run.

### 3. C++ Class Pattern

```cpp
// PickupCoin.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PickupCoin.generated.h"

class USphereComponent;

UCLASS()
class MYGAME_API APickupCoin : public AActor
{
    GENERATED_BODY()
public:
    APickupCoin();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Coin")
    int32 Value = 10;

    UFUNCTION(BlueprintCallable, Category = "Coin")
    void Collect(class AMyCharacter* By);

protected:
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USphereComponent> Trigger;   // use TObjectPtr, not raw UPROPERTY*

    UFUNCTION()
    void OnOverlap(UPrimitiveComponent* Overlapped, AActor* Other,
                   UPrimitiveComponent* OtherComp, int32 BodyIndex,
                   bool bFromSweep, const FHitResult& Sweep);
};
```

```cpp
// PickupCoin.cpp
#include "PickupCoin.h"
#include "Components/SphereComponent.h"

APickupCoin::APickupCoin()
{
    PrimaryActorTick.bCanEverTick = false;   // don't tick what doesn't need it
    Trigger = CreateDefaultSubobject<USphereComponent>(TEXT("Trigger"));
    SetRootComponent(Trigger);
    Trigger->OnComponentBeginOverlap.AddDynamic(this, &APickupCoin::OnOverlap);
}
```

**HARD RULE:** Any pointer to a `UObject` held by a `UObject` **must** be a `UPROPERTY()` (or `TObjectPtr` in a `UPROPERTY`), or the garbage collector will free it out from under you.

### 4. Blueprint vs C++ Decision

| Put in C++ | Put in Blueprint |
|---|---|
| Core systems, math-heavy logic, networking/replication | Per-actor tuning, VFX/audio cue wiring |
| Anything performance-critical or ticking every frame | Designer-facing variables and event graphs |
| Base classes meant to be extended | Rapid prototyping, level scripting |
| Save/load, persistence | One-off UI bindings |

**Pattern:** Write a C++ base class with `BlueprintImplementableEvent`/`BlueprintNativeEvent` hooks, then subclass it in Blueprint for designer iteration. Blueprint nativization was **removed** in UE5 — do not plan around it.

### 5. Nanite & Lumen

- **Nanite**: Enable per-mesh for high-poly static geometry. It removes manual LODs and draw-call cost but is not free for masked/translucent materials. Keep opaque. Use `r.Nanite.Visualize` and the Nanite "fallback mesh" for collision (Nanite geometry has no per-triangle collision — author a simple collision primitive).
- **Lumen**: Dynamic GI. Use **Hardware Ray Tracing** Lumen for reflections quality, **Software** Lumen for broad hardware support. Watch `r.Lumen.ScreenProbeGather.Quality`. For 60+ fps on console, cap Lumen with `r.Lumen.HardwareRayTracing.LightingMode` and use distance-field-driven settings.
- Profile with **Unreal Insights** and the `stat GPU`, `stat unit`, `ProfileGPU` (Ctrl+Shift+,) console commands before optimizing — never guess.

### 6. Plugin & Module Structure

```
MyPlugin/
├── MyPlugin.uplugin
└── Source/
    ├── MyPluginRuntime/
    │   ├── MyPluginRuntime.Build.cs
    │   ├── Public/
    │   └── Private/
    └── MyPluginEditor/          # editor-only module, "Type": "Editor"
        ├── MyPluginEditor.Build.cs
        ├── Public/
        └── Private/
```

```csharp
// MyPluginRuntime.Build.cs
using UnrealBuildTool;
public class MyPluginRuntime : ModuleRules
{
    public MyPluginRuntime(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine" });
        PrivateDependencyModuleNames.AddRange(new[] { "Slate", "SlateCore" });
    }
}
```

**HARD RULE:** Editor-only code must live in an `"Type": "Editor"` module and be wrapped with `#if WITH_EDITOR`, or packaged shipping builds fail to compile.

### 7. Replication Essentials

```cpp
// In header
UPROPERTY(ReplicatedUsing = OnRep_Health)
float Health = 100.f;

// In .cpp
void AMyCharacter::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const
{
    Super::GetLifetimeReplicatedProps(Out);
    DOREPLIFETIME(AMyCharacter, Health);
}
UFUNCTION(Server, Reliable) void ServerFire();   // client → server
UFUNCTION(NetMulticast, Unreliable) void MulticastPlayFX();  // server → all
```

Server validates, server mutates, clients react in `OnRep_`. Mark cosmetic RPCs `Unreliable`; mark state-changing RPCs `Reliable` (sparingly — reliable spam stalls the channel).

### 8. Building on Windows (PowerShell)

```powershell
# Generate project files (source build or Launcher)
& "C:\Program Files\Epic Games\UE_5.5\Engine\Build\BatchFiles\GenerateProjectFiles.bat" "C:\Projects\MyGame\MyGame.uproject"

# Build Development (Editor) from command line
& "C:\Program Files\Epic Games\UE_5.5\Engine\Build\BatchFiles\Build.bat" MyGameEditor Win64 Development -Project="C:\Projects\MyGame\MyGame.uproject" -WaitMutex

# Package a Shipping build
& "C:\Program Files\Epic Games\UE_5.5\Engine\Build\BatchFiles\Build.bat" MyGame Win64 Shipping -Project="C:\Projects\MyGame\MyGame.uproject" -WaitMutex
```

After header changes, do a full editor restart — Live Coding handles `.cpp` changes but header/signature changes require restart.

## Pitfalls

1. **Raw `UObject*` without `UPROPERTY`**: Silent GC crashes. Always `UPROPERTY()`/`TObjectPtr`.
2. **Ticking everything**: Set `PrimaryActorTick.bCanEverTick = false` by default; prefer timers/events.
3. **Hard references bloating memory**: Reference assets via `TSoftObjectPtr`/`TSoftClassPtr` and async-load, or a single Blueprint drags hundreds of MB into memory.
4. **Casting in Blueprint to heavy classes**: Creates hard load dependencies. Use interfaces (`UInterface`) instead.
5. **Legacy Hot Reload**: Corrupts the editor's CDO/state. Use Live Coding; do a full editor restart after header changes.
6. **Logic in the GameMode that clients need**: GameMode exists only on the server — clients see `nullptr`. Put shared state in GameState.
7. **Nanite on translucent/masked materials**: Performance cliff; keep Nanite for opaque.
8. **Blocking the game thread with sync asset loads**: Use `FStreamableManager::RequestAsyncLoad`.
9. **Forgetting `DOREPLIFETIME`**: A replicated `UPROPERTY` without a `GetLifetimeReplicatedProps` entry silently never replicates.
10. **Editor module in a shipping build**: If `WITH_EDITOR` guards are missing or an Editor-typed module is referenced by runtime code, the shipping package will fail to compile.

## Verification

- [ ] Project compiles via Live Coding (Ctrl+Alt+F11) and from a clean `Build.bat` run (no Hot Reload).
- [ ] Every `UObject*` member is a `UPROPERTY`/`TObjectPtr`.
- [ ] Authoritative logic runs server-side; clients react via `OnRep_`/RPC.
- [ ] Editor-only code is in an Editor module / `#if WITH_EDITOR`.
- [ ] Nanite meshes have authored collision primitives; Lumen settings profiled with `stat GPU`.
- [ ] Asset references use soft pointers where the asset is optional/large.
- [ ] Shipping package builds without editor-module errors.

### Checkable Commands

```powershell
# Verify clean build succeeds
& "C:\Program Files\Epic Games\UE_5.5\Engine\Build\BatchFiles\Build.bat" MyGameEditor Win64 Development -Project="C:\Projects\MyGame\MyGame.uproject" -WaitMutex
# Expected: "BUILD SUCCESSFUL" in output

# Verify shipping package compiles
& "C:\Program Files\Epic Games\UE_5.5\Engine\Build\BatchFiles\Build.bat" MyGame Win64 Shipping -Project="C:\Projects\MyGame\MyGame.uproject" -WaitMutex
# Expected: "BUILD SUCCESSFUL" with no WITH_EDITOR errors

# In-editor console checks
# stat GPU       → confirm Lumen/Nanite cost within budget
# stat unit      → confirm frame time breakdown
# ProfileGPU     → detailed GPU pass timings
```

## Related Skills

- `game-unity-engine` — Cross-engine counterpart for Unity C#/DOTS projects.
- `game-blender-asset-pipeline` — Authoring and exporting the meshes/rigs Unreal imports.
- `game-fmod-wwise-integration` — Audio middleware that plugs into UE via the FMOD/Wwise UE plugin.
- `game-steamworks-sdk` — Online services for Unreal builds via the Online Subsystem.

## References

- Unreal Engine 5.x C++ API and Gameplay Framework documentation (Epic Games).
- Gameplay Ability System (GAS) documentation and community references.
- Unreal Insights profiling documentation.
