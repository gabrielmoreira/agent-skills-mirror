# UE5 Project Structure, Naming, and Version Control

Companion to [SKILL.md](SKILL.md). Layout on disk, layout in the Content Browser, module/plugin anatomy, VCS setup for binary assets, agent-friendly conventions, Windows path pitfalls.

## Disk layout (what each folder is)

```
D:\Dev\MyGame\
├── MyGame.uproject          ← JSON manifest: engine version, modules, plugins   [COMMIT]
├── Config\                  ← Default*.ini project settings (text)              [COMMIT]
│   ├── DefaultEngine.ini
│   ├── DefaultGame.ini
│   ├── DefaultInput.ini
│   └── DefaultEditor.ini
├── Content\                 ← all .uasset/.umap binary assets                   [COMMIT via LFS/P4]
├── Source\                  ← C++ (see module layout below)                     [COMMIT]
│   ├── MyGame.Target.cs
│   ├── MyGameEditor.Target.cs
│   └── MyGame\
│       ├── MyGame.Build.cs
│       ├── Public\          ← headers other modules may include
│       └── Private\         ← .cpp + internal headers
├── Plugins\                 ← project-local plugins (own code: commit; marketplace: policy call)
├── Binaries\                ← compiled DLLs/EXEs                                [IGNORE]
├── Intermediate\            ← UBT scratch, generated project files              [IGNORE]
├── Saved\                   ← logs, crashes, local config, autosaves            [IGNORE]
├── DerivedDataCache\        ← local shader/mesh derived data                    [IGNORE]
└── MyGame.sln               ← generated; regenerate any time                    [IGNORE]
```

Deleting `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/` is always safe (slow first re-open). It's the standard fix for "modules out of date" and mystery editor states.

### .uproject anatomy

```json
{
  "FileVersion": 3,
  "EngineAssociation": "5.4",
  "Modules": [
    { "Name": "MyGame",       "Type": "Runtime", "LoadingPhase": "Default",
      "AdditionalDependencies": [ "Engine" ] },
    { "Name": "MyGameEditor", "Type": "Editor",  "LoadingPhase": "PostEngineInit" }
  ],
  "Plugins": [
    { "Name": "GameplayAbilities", "Enabled": true },
    { "Name": "EnhancedInput",     "Enabled": true }
  ]
}
```

Module `Type` matters at package time: `Editor` modules are excluded from cooked builds — putting runtime gameplay in an editor module is a package-only crash. Plugins live in `Plugins/<Name>/<Name>.uplugin` with the same module schema plus optional `Content/`, and `"PlatformAllowList": ["Win64"]` style platform gating.

## Content Browser layout

Everything under one project-named root folder — prevents collisions when migrating assets or absorbing marketplace packs (which land as sibling top-level folders you can spot and quarantine instantly):

```
/Game (= Content\)
├── MyGame\
│   ├── Core\                ← GameMode, GameState, PlayerController BPs, GameInstance
│   ├── Characters\
│   │   ├── Hero\            ← BP_Hero, SK_Hero, ABP_Hero, textures, materials — folder-by-feature
│   │   └── Shared\          ← shared anim assets, base ABPs
│   ├── Weapons\
│   │   └── Rifle\           ← BP_Rifle, SM_Rifle, sounds, FX for the rifle together
│   ├── Input\               ← IA_* input actions, IMC_* mapping contexts
│   ├── Abilities\           ← GAS: GA_*, GE_*, gameplay cue assets
│   ├── UI\                  ← WBP_* widgets, fonts, UI textures
│   ├── Maps\                ← L_* levels (+ Maps\Test\ for dev maps excluded from cook)
│   ├── Data\                ← DT_* DataTables, DA_* DataAssets, CT_* curves
│   ├── Audio\
│   ├── VFX\                 ← NS_* Niagara systems
│   └── Art\                 ← genuinely shared meshes/materials/textures
│       ├── Materials\       ← M_ master materials, MI_ instances, MF_ functions
│       └── Environment\
└── (marketplace packs stay in their own top-level folders until curated)
```

Rules:

- **Folder-by-feature** for gameplay entities (everything about the rifle lives in `Weapons/Rifle/`); shared art by type under `Art/`.
- Developer sandboxes go in the built-in **Developers folder** (enable in Content Browser settings) — never in shipping paths.
- Test/gym maps under `Maps/Test/` and excluded from the packaged-maps list.
- After any restructure: **Fix Up Redirectors** on `/Game`, then commit the moves and deletions together.

## Naming conventions (the standard prefix set)

`Prefix_BaseName_Variant_Suffix`, PascalCase, no spaces (spaces in asset names break some tooling and all command lines):

| Prefix | Type | | Prefix | Type |
|---|---|---|---|---|
| `BP_` | Blueprint (actor/object) | | `M_` | Material |
| `WBP_` | Widget Blueprint | | `MI_` | Material Instance |
| `ABP_` | Animation Blueprint | | `MF_` | Material Function |
| `SM_` | Static Mesh | | `T_` | Texture (`_D` diffuse, `_N` normal, `_ORM` packed) |
| `SK_` | Skeletal Mesh | | `NS_` | Niagara System |
| `A_`/`AM_`/`AS_` | Anim sequence/Montage/(aim)space | | `S_`/`SC_`/`SW_` | Sound / SoundCue / MetaSound-ish wave org |
| `L_` | Level/Map | | `DT_` | DataTable |
| `IA_` | Input Action | | `DA_` | Data Asset |
| `IMC_` | Input Mapping Context | | `CT_` | Curve Table / `Curve_` float curves |
| `GA_` | Gameplay Ability | | `GE_` | Gameplay Effect |
| `E` | C++ enum (`EWeaponState`) | | `F` | C++ struct (`FWeaponStats`) |

C++ classes keep engine prefixes: `A` actors, `U` UObjects/components, `F` structs, `E` enums, `I` interfaces, `S` Slate widgets. Module API macro: `MYGAME_API`.

## Source module layout (scaling past one module)

```
Source\
├── MyGame.Target.cs / MyGameEditor.Target.cs
├── MyGame\                      ← core runtime module
│   ├── MyGame.Build.cs
│   ├── Public\                  ← only headers meant for other modules
│   │   └── Weapons\WeaponBase.h
│   └── Private\
│       ├── MyGame.cpp           ← IMPLEMENT_PRIMARY_GAME_MODULE
│       └── Weapons\WeaponBase.cpp
├── MyGameEditor\                ← editor-only tooling (details customizations, validators)
└── MyGameTests\                 ← optional: automation-test module
```

- Mirror `Public/`/`Private/` subfolder trees; include paths are rooted at those folders (`#include "Weapons/WeaponBase.h"`).
- A header goes `Public/` only when another module includes it; default to `Private/`.
- Editor module guards: it can depend on `UnrealEd`; the runtime module never may.
- Promote to a **plugin** when a feature has its own content + could move projects: `Plugins/MyFeature/Source/MyFeature/…` + `Content/`.

## Version control

### Common ground

Commit: `Content/`, `Config/`, `Source/`, `Plugins/` (your own), `.uproject`, `.gitattributes`/`.gitignore` or P4 config.
Never commit: `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`, `.vs/`, `*.sln`, `.idea/`.

### Git + LFS (small teams / open source)

`.gitignore`:

```gitignore
Binaries/
DerivedDataCache/
Intermediate/
Saved/
.vs/
.idea/
*.sln
*.suo
*.opensdf
*.sdf
*.VC.db
*.VC.opendb
Plugins/**/Binaries/
Plugins/**/Intermediate/
```

`.gitattributes` — **must exist before the first asset is added**; LFS-ifying after the fact requires history rewriting:

```gitattributes
*.uasset filter=lfs diff=lfs merge=lfs -text lockable
*.umap   filter=lfs diff=lfs merge=lfs -text lockable
*.upk    filter=lfs diff=lfs merge=lfs -text lockable
*.udk    filter=lfs diff=lfs merge=lfs -text lockable
# common binary content sources if kept in-repo
*.fbx  filter=lfs diff=lfs merge=lfs -text
*.png  filter=lfs diff=lfs merge=lfs -text
*.tga  filter=lfs diff=lfs merge=lfs -text
*.psd  filter=lfs diff=lfs merge=lfs -text
*.wav  filter=lfs diff=lfs merge=lfs -text
*.exr  filter=lfs diff=lfs merge=lfs -text
```

- `lockable` + `git lfs lock` is the point: uassets can't merge, so exclusive checkout is the only safe concurrency model. Enable the editor's **Revision Control → Git (with LFS)** integration so opening an asset checks out/locks it.
- Symptom of a broken LFS clone: assets fail with *"Corrupt data found"* and the .uasset on disk is a ~130-byte text pointer → `git lfs install && git lfs pull`.
- GitHub LFS quotas are small for game content; budget for a real LFS host (Azure DevOps has free unlimited-ish LFS, or self-host) on anything art-heavy.

### Perforce (industry default, mid+ teams)

- Typemap so assets are binary + exclusive-checkout — run `p4 typemap` and include:

```
TypeMap:
    binary+w //depot/....exe
    binary+w //depot/....dll
    binary+w //depot/....pdb
    binary+l //depot/....uasset
    binary+l //depot/....umap
    binary+l //depot/....upk
    binary+l //depot/....udk
    binary+l //depot/....ubulk
```

- Editor: Revision Control → Perforce; artists work entirely through in-editor checkout/submit.
- Use streams (`//MyGame/main`, `//MyGame/dev-*`, `//MyGame/release-*`); binary assets don't branch-merge, so keep asset work on main and code on branches.

### One File Per Actor (OFPA)

World Settings → *Use External Actors* (default on for new UE5 levels, and the basis of World Partition). Each placed actor serializes to its own tiny file under `Content\__ExternalActors__\` — multiple people edit one map without fighting over a single .umap lock. Commit `__ExternalActors__\` and `__ExternalObjects__\` like any content. Trade-off: thousands of small files — Perforce handles it natively; on Git prefer fewer, larger commits and shallow clones.

## Agent-friendly layouts

Conventions that make a UE project workable for coding agents (and CI):

1. **Logic in `Source/`, not graphs** — agents can read, diff, and patch C++; they cannot parse .uasset BP graphs. The C++-base/BP-child split in [blueprints-vs-cpp.md](blueprints-vs-cpp.md) is the enabling pattern.
2. **Content as text where possible** — DataTables imported from `Tools/Data/*.csv` committed beside the code; gameplay tags in `Config/DefaultGameplayTags.ini`; curves via curve tables from CSV. The uasset becomes a derived artifact; the CSV is the reviewable truth.
3. **Deterministic headless loop** — `Build.bat` → automation tests via `UnrealEditor-Cmd.exe -nullrhi` → `-run=Cook` as the agent's compile/test/validate cycle (exact commands in [reference.md](reference.md#agent-command-lines)). Exit codes + `Saved\Logs\*.log` are the feedback channel.
4. **Editor Python for asset queries** — with the Python plugin, an agent can list/audit/fix assets it can't read raw: `unreal.EditorAssetLibrary.list_assets("/Game")`, batch-set Nanite flags, find missing references. Keep scripts in `Tools/` in the repo.
5. **Stable names, no spaces** — every asset/map name ends up in a command line eventually.
6. **A `Docs/ARCHITECTURE.md`** naming the GameMode/Controller/Pawn classes, module map, and where each system lives — the agent's entry map, since UE has no single "main".

## Windows path pitfalls

- **MAX_PATH = 260 chars** still bites cooking/staging: cook paths look like `<Project>\Saved\Cooked\Windows\<Project>\Content\<your\deep\folders>\Asset.uasset` — your project path + content depth counts double. Keep the project root short (`D:\Dev\MyGame`), keep Content folder depth shallow (≤ 4–5 levels), keep asset names reasonable. Windows long-path registry opt-in helps some tools but not all of the pipeline — treat 260 as the real budget.
- **No spaces in the project path or project name.** Batch files, UAT args, and third-party tools mis-split them eventually. `MyGame`, not `My Game`.
- **Project name ≤ ~20 chars** keeps generated target/binary names and cook paths sane (and matches other-platform limits if you ever leave Windows).
- **Don't put projects in OneDrive/Dropbox-synced folders** — sync fights the editor over Saved/Intermediate file locks and corrupts DDC.
- Use `Subst` or junctions (`mklink /J D:\Dev\MG D:\Dev\SomeLongerCheckoutPath`) as an emergency shortener for path-limit cook failures.
- In PowerShell, quote and prefer `&` call operator: `& "C:\Program Files\Epic Games\UE_5.4\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun ...`; in .bat use `^` for line continuation (examples in [reference.md](reference.md)).
