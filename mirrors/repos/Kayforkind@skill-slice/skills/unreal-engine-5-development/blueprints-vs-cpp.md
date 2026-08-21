# Blueprints vs C++ — Decision Guide

Companion to [SKILL.md](SKILL.md). The question is never "which is better" — it's **which layer owns which responsibility**. UE5 is designed for a hybrid: C++ foundations, Blueprint composition.

## The default architecture

```
C++ base class            ← systems, state, math, tick logic, replication, save data
   │  exposes: UPROPERTY knobs, BlueprintCallable API, BlueprintImplementableEvent hooks
   ▼
Blueprint subclass         ← assigns meshes/sounds/curves, tunes numbers, cosmetic reactions
   │  references: content assets (safe here — BPs live in /Game with the assets)
   ▼
Placed instances / spawns  ← per-instance overrides only
```

One BP subclass per C++ gameplay class, even if it starts empty (`BP_PlayerCharacter : APlayerCharacterBase`). Designers get a surface to work on without touching code; programmers never hardcode asset paths; agents get all logic in diffable text.

## Decision matrix

| Concern | C++ | Blueprint |
|---|---|---|
| Game systems (inventory, damage, save, abilities) | **✔ always** | — |
| Tick / per-frame math, loops over many actors | **✔** (BP VM ~10× slower per node) | ✖ |
| Replication, RPCs, `GetLifetimeReplicatedProps` | **✔** (BP replication exists but is limited/opaque) | avoid |
| Anything needing engine APIs not exposed to BP | **✔** (containers beyond TArray/TMap basics, async, low-level traces) | ✖ |
| Interfaces/base classes other code depends on | **✔** — a BP-only base can't be referenced from C++ | ✖ |
| Binding data: which mesh, sound, montage, curve | ✖ never hardcode | **✔** |
| Tuning numbers designers iterate on | expose knob in C++ | **✔ set values** |
| Cosmetic reactions (muzzle flash, camera shake, UI ping) | hook via BIE | **✔ implement** |
| UI widget layout + animation | UserWidget C++ base for logic | **✔ visuals in WBP** |
| Level-specific one-off scripting (door opens, trigger a cinematic) | overkill | **✔ Level BP sparingly** |
| Rapid prototype of an unproven mechanic | later | **✔ first**, port when proven |
| Anim graphs, state machines | AnimInstance C++ base for variables | **✔ graph in AnimBP** |

Tie-breakers: if it needs **diffing/code review**, if it's **hot-path**, if it's **shared infrastructure** → C++. If it's **asset wiring or feel-tuning** → BP.

## Performance realities

- The BP VM interprets node-by-node; a graph doing math per tick for 200 actors is a real cost. The same logic compiled in C++ is effectively free at that scale. **Blueprint nativization was removed in UE5** — there is no "compile my BPs to C++" escape hatch anymore; heavy BP logic must be ported by hand.
- Cost is per-node-execution, not per-BP-existing. An event-driven BP that runs 3 nodes on overlap is fine forever.
- `BlueprintPure` functions re-execute **per connected pin use** — a pure node feeding 5 inputs runs 5 times. Cache into a variable in the graph, or make it impure.
- **Casting in BP loads the cast-target class into memory** as a hard reference. `Cast to BP_Boss` inside a common widget drags the boss (mesh, sounds, everything) into memory whenever the widget loads. Prefer interfaces or C++ base-class casts.
- Tick in BP is the worst combination — VM cost × per-frame. Convert BP ticks to timers or events first when profiling shows game-thread pressure.

## Exposing C++ to Blueprints — the toolkit

```cpp
UCLASS(Abstract, Blueprintable)
class MYGAME_API AWeaponBase : public AActor
{
    GENERATED_BODY()
public:
    // 1. Knobs — designers tune in the BP child's defaults
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Weapon", meta=(ClampMin="0"))
    float Damage = 20.f;

    // 2. Content slots — BP child assigns assets; C++ never hardcodes paths
    UPROPERTY(EditDefaultsOnly, Category="Weapon|FX")
    TObjectPtr<USoundBase> FireSound;

    UPROPERTY(EditDefaultsOnly, Category="Weapon")
    TSoftObjectPtr<UStaticMesh> WorldMeshSoft;   // soft = loaded on demand, path is data

    // 3. Callable API — BP can drive the system
    UFUNCTION(BlueprintCallable, Category="Weapon")
    virtual void Fire();

    // 4. BP-implementable hook — cosmetics only, C++ never depends on it running
    UFUNCTION(BlueprintImplementableEvent, Category="Weapon", meta=(DisplayName="On Fired"))
    void OnFired(const FVector& MuzzleLocation);

    // 5. Native event — C++ default, BP may override/extend
    UFUNCTION(BlueprintNativeEvent, Category="Weapon")
    bool CanFire() const;
    virtual bool CanFire_Implementation() const;   // the C++ body

    // 6. Delegate — other BPs/widgets bind without coupling
    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAmmoChanged, int32, NewAmmo);
    UPROPERTY(BlueprintAssignable, Category="Weapon")
    FOnAmmoChanged OnAmmoChanged;
};
```

Guidelines per mechanism:

- **BlueprintImplementableEvent (BIE)**: fire-and-forget cosmetic hooks. C++ must remain correct if the BP never implements it. No return values you rely on.
- **BlueprintNativeEvent (BNE)**: when there's a sensible default the BP might specialize. Costs a virtual dispatch + name lookup; don't put on ultra-hot paths.
- **BlueprintAssignable delegates**: the decoupling backbone — UI binds to gameplay without gameplay knowing UI exists. Prefer over BPs polling state.
- **BlueprintCallable + `UPARAM(ref)`** for out-params; **`meta=(ExpandEnumAsExecs="Result")`** to give BP users multiple exec output pins for enum results.
- **UFUNCTION(CallInEditor)**: buttons in the Details panel — cheap in-editor tooling.
- **UInterface** (`UINTERFACE(BlueprintType)` + `meta=(CannotImplementInterfaceInBlueprint)` when C++-only): cross-cutting contracts (`IInteractable`) callable on anything without casting.

## Data-driven beats both

Before writing either C++ or BP logic for content variation, reach for data:

- **UDataAsset / UPrimaryDataAsset** — typed asset instances (`UDA_WeaponConfig`) referenced by soft pointer; PrimaryDataAsset participates in the Asset Manager for chunking/loading.
- **UDataTable** — rows of a `FTableRowBase` struct, **importable from CSV/JSON kept in the repo** — the most agent-friendly content format in UE: the source of truth is text, the uasset is a build artifact.
- **UCurveFloat/Vector** — designer-editable response curves instead of magic formulas.
- **GameplayTags** (`DefaultGameplayTags.ini` or table-sourced) — hierarchical labels replacing bool/enum sprawl; the backbone of GAS.

## Blueprint hygiene (when BP is the right tool)

- Event-driven, not tick-driven. If a BP has Event Tick, justify it in a comment node.
- Graphs read left→right, one responsibility per event; collapse to functions/macros past ~15 nodes.
- Use **BP function libraries** for shared graph logic; **BP interfaces** instead of Cast chains.
- Comment boxes name *intent*, not mechanics.
- Circular hard references between BPs (A references B references A) inflate load times and can deadlock cooks — break with interfaces, soft refs, or a C++ base.
- Keep Level Blueprints nearly empty — they're unmergeable per-map singletons; anything reusable goes in an actor BP.

## Migration: BP prototype → C++ production

1. Profile first (`stat game`, Insights) — port what's hot or structural, not everything.
2. Create the C++ base class matching the BP's role; move variables as UPROPERTYs (same names/categories keep designer muscle memory).
3. **Reparent the BP** (Class Settings → Parent Class → new C++ class). Instantly the BP child keeps all asset refs and placed instances remain valid.
4. Move logic function-by-function: delete the BP nodes, implement in C++, expose as BlueprintCallable if graphs still call it. Compile + test per function, not per class.
5. Leave cosmetic event chains in BP, now triggered by BIE hooks from C++.
6. Watch for: BP-only constructs (timelines → `FTimeline` in C++ or keep in BP), latent nodes (Delay → timers), `GetAllActorsOfClass` habits (→ maintained registries/subsystems).
