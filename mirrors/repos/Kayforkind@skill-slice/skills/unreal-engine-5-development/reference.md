# UE5 Reference — Commands, Specifiers, Lifecycle, Crash Triage

Companion to [SKILL.md](SKILL.md). Everything here assumes Windows, engine installed at `C:\Program Files\Epic Games\UE_5.4\` (adjust version), project at `D:\Dev\MyGame\MyGame.uproject`. Quote all paths.

## Key executables

| Tool | Path (relative to engine root) | Purpose |
|---|---|---|
| `UnrealEditor.exe` | `Engine\Binaries\Win64\` | Editor (GUI) |
| `UnrealEditor-Cmd.exe` | `Engine\Binaries\Win64\` | Headless editor — commandlets, automation, cooking |
| `Build.bat` / `Rebuild.bat` / `Clean.bat` | `Engine\Build\BatchFiles\` | UnrealBuildTool wrappers |
| `RunUAT.bat` | `Engine\Build\BatchFiles\` | Unreal Automation Tool — BuildCookRun, packaging |
| `UnrealInsights.exe` | `Engine\Binaries\Win64\` | Trace viewer |
| `UnrealVersionSelector.exe` | (installed) | Register engine, generate project files from Explorer |

## Agent command lines

Headless build/test/cook loop for CI or coding agents.

**Compile the editor target:**
```bat
"C:\Program Files\Epic Games\UE_5.4\Engine\Build\BatchFiles\Build.bat" ^
  MyGameEditor Win64 Development -project="D:\Dev\MyGame\MyGame.uproject" -waitmutex
```
Exit code 0 = success. Targets: `MyGame` (game), `MyGameEditor` (editor). Configs: `Debug`, `DebugGame`, `Development`, `Test`, `Shipping`.

**Regenerate project files:**
```bat
"C:\Program Files\Epic Games\UE_5.4\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe" ^
  -projectfiles -project="D:\Dev\MyGame\MyGame.uproject" -game -engine -progress
```

**Run automation tests headless (no GPU needed):**
```bat
"C:\Program Files\Epic Games\UE_5.4\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" ^
  "D:\Dev\MyGame\MyGame.uproject" ^
  -ExecCmds="Automation RunTests MyGame; Quit" ^
  -unattended -nopause -nullrhi -nosplash -log -ReportOutputPath="D:\Dev\MyGame\Saved\Automation"
```
Test filter is a prefix match on test names (`MyGame` runs everything registered under that group). JSON results land in `ReportOutputPath` (`index.json`); parse `"state": "Success" | "Fail"`.

**Cook only (fast content validation):**
```bat
"C:\Program Files\Epic Games\UE_5.4\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" ^
  "D:\Dev\MyGame\MyGame.uproject" -run=Cook -TargetPlatform=Windows -unattended -log
```

**Full package (build + cook + stage + pak + archive):**
```bat
"C:\Program Files\Epic Games\UE_5.4\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun ^
  -project="D:\Dev\MyGame\MyGame.uproject" -platform=Win64 -clientconfig=Shipping ^
  -build -cook -stage -pak -iostore -prereqs -archive -archivedirectory="D:\Builds\MyGame" ^
  -unattended -utf8output
```
Useful extra flags: `-clean` (full rebuild), `-nocompileeditor`, `-map=MapA+MapB` (override cook list), `-nodebuginfo` (skip PDBs in archive), `-cookflavor=` (platform texture variants). `-clientconfig=Test` for a profiling-friendly near-Shipping build.

**Run editor Python (editor scripting for agents):**
```bat
"...\UnrealEditor-Cmd.exe" "D:\Dev\MyGame\MyGame.uproject" ^
  -run=pythonscript -script="D:\Dev\MyGame\Tools\audit_assets.py" -unattended -log
```
Requires the *Python Editor Script Plugin* enabled. `init_unreal.py` in `Content/Python/` auto-runs at editor startup.

**Launch packaged/PIE-style game with flags:**
```bat
MyGame.exe -log -windowed -ResX=1280 -ResY=720 -trace=default,counters -statnamedevents
"...\UnrealEditor.exe" "D:\Dev\MyGame\MyGame.uproject" MapName -game -log      &rem uncooked standalone
"...\UnrealEditor.exe" "D:\Dev\MyGame\MyGame.uproject" MapName -server -log    &rem dedicated server (uncooked)
```

## Log & crash locations (Windows)

| What | Where |
|---|---|
| Editor/game log | `<Project>\Saved\Logs\MyGame.log` (previous runs get timestamped backups) |
| Packaged game log | `%LOCALAPPDATA%\MyGame\Saved\Logs\` (Shipping) or staged `Saved\Logs` |
| Crash dumps + context | `<Project>\Saved\Crashes\UECC-Windows-<GUID>\` — `CrashContext.runtime-xml`, `.dmp`, log copy |
| Cook output | `<Project>\Saved\Cooked\Windows\` |
| Automation reports | `<Project>\Saved\Automation\` (with `-ReportOutputPath`) |
| MemReports | `<Project>\Saved\Profiling\MemReports\` |
| Insights traces | `%LOCALAPPDATA%\UnrealEngine\Common\UnrealTrace\Store\` (or `-tracefile=` path) |

Grep priorities in a log: `Fatal`, `Error:`, `Ensure condition failed`, `Warning:`, `LogCook`, `AppCrashed`.

## Config hierarchy

INI files layer bottom-up; later wins. All are text — commit `Config/`.

```
Engine\Config\BaseEngine.ini                → engine defaults
Engine\Config\Windows\WindowsEngine.ini     → platform layer
<Project>\Config\DefaultEngine.ini          → your project (COMMIT)
<Project>\Config\Windows\WindowsEngine.ini  → project+platform (COMMIT)
<Project>\Saved\Config\Windows\Engine.ini   → local machine scratch (NEVER commit)
```

Same pattern for `Game.ini`, `Input.ini`, `Editor.ini`. Key sections you'll touch in `DefaultEngine.ini`:

```ini
[/Script/EngineSettings.GameMapsSettings]
GameDefaultMap=/Game/Maps/L_MainMenu.L_MainMenu
GlobalDefaultGameMode=/Game/Core/BP_MyGameMode.BP_MyGameMode_C

[/Script/Engine.RendererSettings]
r.GenerateMeshDistanceFields=True          ; required for software Lumen
r.DynamicGlobalIlluminationMethod=1        ; 1=Lumen, 0=None, 2=Screen Space
r.ReflectionMethod=1                       ; 1=Lumen
r.Shadow.Virtual.Enable=1                  ; VSM (pairs with Nanite)
r.DefaultFeature.AutoExposure.ExtendDefaultLuminanceRange=True

[/Script/WindowsTargetPlatform.WindowsTargetSettings]
DefaultGraphicsRHI=DefaultGraphicsRHI_DX12
-D3D12TargetedShaderFormats=PCD3D_SM5
+D3D12TargetedShaderFormats=PCD3D_SM6      ; SM6 required by Nanite/Lumen
```

## Reflection specifier tables

### UCLASS (common)

| Specifier | Effect |
|---|---|
| `Blueprintable` / `NotBlueprintable` | Allow/deny BP subclassing |
| `BlueprintType` | Usable as a BP variable type |
| `Abstract` | Cannot be placed/spawned directly |
| `Config=Game` | Class can read `UPROPERTY(Config)` values from INI |
| `Within=OuterClass` | Must be created inside given outer |
| `meta=(BlueprintSpawnableComponent)` | Component appears in Add Component menu |

### UPROPERTY

| Specifier | Effect |
|---|---|
| `EditAnywhere` | Editable on archetype *and* instances |
| `EditDefaultsOnly` | Editable on BP defaults/archetype only — default for tuning knobs |
| `EditInstanceOnly` | Editable only on placed instances |
| `VisibleAnywhere` | Read-only display (right choice for component pointers) |
| `BlueprintReadOnly` / `BlueprintReadWrite` | BP graph get / get+set |
| `Category="X"` | Details-panel grouping (always set it) |
| `Replicated` / `ReplicatedUsing=OnRep_X` | Network replication (+ implement `GetLifetimeReplicatedProps`) |
| `Transient` | Never serialized (runtime cache) |
| `Config` | Loaded from INI (with `UCLASS(Config=...)`) |
| `meta=(ClampMin="0.0", ClampMax="1.0")` | Editor value clamps |
| `Instanced` | Sub-object edited inline (with `UCLASS(EditInlineNew)` on the type) |

Pointer choices: `TObjectPtr<T>` for members (UE5 style, replaces raw `T*` in headers), `TWeakObjectPtr<T>` for non-owning refs that may die, `TSoftObjectPtr<T>` / `TSoftClassPtr<T>` for assets to load on demand (agent-friendly: path is data, not code).

### UFUNCTION

| Specifier | Effect |
|---|---|
| `BlueprintCallable` | BP can call (execution pin) |
| `BlueprintPure` | BP can call, no exec pin — **no side effects**, re-evaluated per pin use |
| `BlueprintImplementableEvent` | Declared in C++, body implemented in BP only |
| `BlueprintNativeEvent` | C++ default body (`FuncName_Implementation`), BP may override |
| `Server` / `Client` / `NetMulticast` + `Reliable`/`Unreliable` | RPCs (`WithValidation` adds `_Validate`) |
| `CallInEditor` | Button in Details panel — great for tooling |
| `Exec` | Console command (on exec-routed classes: PlayerController, GameMode, CheatManager) |

## Actor lifecycle order

```
C++ Constructor            ← CDO + every instance; NO world access, only CreateDefaultSubobject / defaults
PostInitProperties
(Deserialize / spawn transform applied)
OnConstruction / BP Construction Script   ← re-runs on every editor tweak; keep idempotent & cheap
PreInitializeComponents
InitializeComponent (per component)
PostInitializeComponents   ← earliest point all components exist
BeginPlay                  ← world is live; bind timers/delegates here
    [Tick × N]
EndPlay(Reason)            ← unbind, clear timers
BeginDestroy → IsReadyForFinishDestroy → FinishDestroy   (GC, async)
```

Networking inserts: `PossessedBy` (server), `OnRep_PlayerState` / `OnRep_Owner` (client) — the two places to init possession-dependent systems (input contexts, GAS `InitAbilityActorInfo`).

GameMode flow per player: `PreLogin → Login → PostLogin → HandleStartingNewPlayer → RestartPlayer → SpawnDefaultPawnFor → Possess`.

## Profiling commands

Console (` key; unavailable in Shipping — use Test config):

| Command | Shows |
|---|---|
| `stat unit` | Frame / Game / Draw / GPU / RHIT ms — **always start here** |
| `stat fps` | FPS + frame ms |
| `stat game` | Game-thread tick breakdown |
| `stat scenerendering` | Draw calls, visible primitives |
| `stat gpu` | Live GPU pass timings |
| `stat nanite` | Nanite cluster/culling stats |
| `stat streaming` | Texture streaming pool pressure |
| `stat memory` | High-level memory by tag |
| `ProfileGPU` | One-frame GPU capture (with `r.ProfileGPU.ShowUI 1`) |
| `memreport -full` | Dump full memory report to Saved/Profiling |
| `stat startfile` / `stat stopfile` | Legacy .ue4stats capture |
| `obj list class=StaticMeshComponent` | Count live objects (leak hunting) |
| `DumpTicks` | Everything registered to tick, with rates |

Scalability CVar groups (0–3, cine=4): `sg.ViewDistanceQuality`, `sg.ShadowQuality`, `sg.GlobalIlluminationQuality`, `sg.ReflectionQuality`, `sg.TextureQuality`, `sg.EffectsQuality`, `sg.PostProcessQuality`, `sg.FoliageQuality`. Test min-spec by forcing all to 0.

Insights launch args: `-trace=default,counters,memory` `-statnamedevents` `-tracefile="D:\traces\run1.utrace"`. In code: `TRACE_CPUPROFILER_EVENT_SCOPE(Name)`, `SCOPED_NAMED_EVENT(Name, FColor::Red)`.

## Crash patterns

| Symptom | Likely cause | Fix |
|---|---|---|
| `EXCEPTION_ACCESS_VIOLATION reading 0x0000...0` | Deref of nullptr: failed `Cast<>`, `GetWorld()` off-world object, component not found | Guard with `IsValid()`; `check()` invariants early so the crash names itself |
| Crash seconds/minutes in, pointer "was valid before" | **GC'd UObject** held by raw non-UPROPERTY member | Mark member `UPROPERTY()`; or `TWeakObjectPtr` + `.IsValid()` each use |
| Crash at editor startup loading your module | Constructor/CDO doing runtime work; static initializer touching engine systems | Move to `BeginPlay`/`PostInitializeComponents`; constructors only set defaults + `CreateDefaultSubobject` |
| `Assertion failed: <expr>` + file/line | A `check()` caught a broken invariant | Read the expression; fix the caller, never delete the check |
| `Ensure condition failed` (no crash, logged) | Soft invariant violated | Same as above — treat as a bug, it's telling you pre-crash |
| Infinite hang on BP compile / placing actor | Recursive Construction Script or event graph loop | Audit ConstructionScript; no spawning-self patterns |
| `Array index out of bounds` | Modifying a TArray while ranged-for iterating; stale index | Iterate backwards for removal, or collect-then-remove |
| Crash only in packaged build | `WITH_EDITOR` code leaking, editor-only module dep in runtime module, asset not cooked | Wrap editor code in `#if WITH_EDITOR`; check Build.cs deps; verify cook list |
| Black screen / no GI in package | DX12/SM6 not set for target, Lumen unsupported on machine | Verify RHI + shader format config; provide scalability fallback |
| Cook fails `Couldn't save package ... path too long` | Windows MAX_PATH during staging | Shorten project root/asset paths; see project-structure.md |
| `Corrupt data found, please verify your installation` on asset load | uasset committed without LFS (pointer file on disk) or truncated binary | `git lfs pull`; verify `.gitattributes` predates the add; re-save asset |
| `Modules are out of date / rebuild from source` popup | Binaries stale vs. engine/source version | Rebuild editor target; delete `Binaries/` + `Intermediate/` if mismatched engine |
| LNK2019 unresolved external on engine type | Module missing from Build.cs dependency lists | Add the owning module (e.g. `"UMG"`, `"GameplayAbilities"`, `"EnhancedInput"`) |
| Editor crash on hot iteration after header change | Live Coding applied over changed class layout | Close editor, full rebuild; only trust Live Coding for function bodies |

## Packaging failures

| Cook/stage error | Fix |
|---|---|
| `LogRedirectors` / references to `/Game/..._Redirector` | Content Browser → Fix Up Redirectors on `/Game`, resave, recook |
| Map referenced but not cooked (`Couldn't find file for package`) | Add to Packaging → maps list, or reference maps via `TSoftObjectPtr<UWorld>` |
| Plugin module fails to load in package | `.uplugin`: add `"PlatformAllowList": ["Win64"]` (or remove denylist); mark `"Type": "Runtime"` not `"Editor"` |
| BP compile errors surfacing only in cook | Editor tolerated dirty BPs; run *Blueprint Compilation* on all (or `-run=CompileAllBlueprints`) and fix |
| Shipping build silently missing logs/console | Expected — Shipping strips them; use `-log` arg for a window, or package Test config for diagnosis |
| Huge package size | Check Size Map on startup map; audit *Cook everything* accidentally on; strip editor-only content; confirm Pak+IoStore compression on |
| Prereqs missing on clean machine (VCRedist) | Package with `-prereqs` or ship the `Engine\Extras\Redist` installer |
