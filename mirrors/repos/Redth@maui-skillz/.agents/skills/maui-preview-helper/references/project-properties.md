# Project properties & IDE settings (living document)

> **This is a living document.** The property/settings *groups* below change as previews evolve
> — new toggles get added, defaults flip, old ones retire. Treat each group as a named, dated
> recipe. When the user is testing a feature, apply the matching group; when a preview changes,
> update the group here. Confirm the current toggle set with the user if a build is newer than
> the dates below.

## Where properties go

- **`Directory.Build.props`** at the repo/solution root — applies to every project. Best for
  dogfooding a whole solution. Create it if absent; MSBuild imports it automatically.
- **`.csproj`** `<PropertyGroup>` — single project only. Fine for a one-off sample.
- Prefer `Directory.Build.props` unless the user explicitly wants one project changed. Both use
  the same `<PropertyGroup>` MSBuild syntax.

## `<MauiVersion>` is the single source of truth

`<MauiVersion>` must **exactly** match the MAUI package version you staged in the local source
([download-builds.md](download-builds.md)). Set it here alongside the feature toggles.

The .NET MAUI SDK reads `$(MauiVersion)` and **implicitly** pins every MAUI package reference
(`Microsoft.Maui.Controls`, `Microsoft.Maui.Controls.Compatibility`, `Microsoft.Maui.Essentials`,
etc.) to it. So in most projects you **don't** add explicit `<PackageReference>`s for MAUI at all
— just set `<MauiVersion>`.

- **If a project *does* declare an explicit MAUI `PackageReference`, its `Version` must be
  `$(MauiVersion)` — never a hardcoded literal.** A literal that diverges from `<MauiVersion>`
  causes NuGet downgrade/conflict errors (NU1605) or silently restores a different build than the
  one you staged. Point every MAUI reference at the property:

  ```xml
  <!-- ✅ correct: property is the source of truth -->
  <PackageReference Include="Microsoft.Maui.Controls" Version="$(MauiVersion)" />
  <!-- ❌ wrong: a literal that can drift from <MauiVersion> -->
  <PackageReference Include="Microsoft.Maui.Controls" Version="11.0.0-preview.6.26357.77" />
  ```

- When you bump to a layered branch build ([download-builds.md](download-builds.md)), change
  **only** `<MauiVersion>` — every `$(MauiVersion)` reference follows automatically.
- Audit for stray literals before restoring:
  `grep -rEn 'Include="Microsoft\.Maui' --include=*.csproj --include=*.props .` and confirm each
  `Version` is `$(MauiVersion)`.

---

## Group: XAML SourceGen Hot Reload (.NET 11 Preview 5+ era)

Testing the source-generated XAML inflator + incremental Hot Reload.

**Required core — these three properties define the group.** All must be set together; the
feature does nothing if any is missing:

```xml
<MauiXamlInflator>SourceGen</MauiXamlInflator>
<MauiXamlHotReload>SourceGen</MauiXamlHotReload>
<EnableMauiIncrementalHotReload>true</EnableMauiIncrementalHotReload>
```

Full group (core props + the version/runtime context they need):

```xml
<PropertyGroup>
  <MauiVersion>11.0.0-ci.pr34338.6.26312.9</MauiVersion>   <!-- match your local source -->
  <!-- required core -->
  <MauiXamlInflator>SourceGen</MauiXamlInflator>
  <MauiXamlHotReload>SourceGen</MauiXamlHotReload>
  <EnableMauiIncrementalHotReload>true</EnableMauiIncrementalHotReload>
  <!-- CoreCLR is the default in .NET 11 Preview 5. -->
  <UseMonoRuntime>false</UseMonoRuntime>
</PropertyGroup>
```

**Runtime caveat (important):**
- `MauiXamlInflator=SourceGen` / `MauiXamlHotReload=SourceGen` enable the new source-generated
  XAML path. Setting `MauiXamlHotReload=SourceGen` emits **`MAUI1002`** — it is explicitly
  "experimental and not yet fully implemented" as of Preview 6.
- **Mono on iOS is NOT supported in .NET 11** — `<UseMonoRuntime>true</UseMonoRuntime>` on a
  `net11.0-ios` TFM fails the build with **`NETSDK1242`** ("Building iOS projects with the Mono
  runtime is not supported in .NET 11.0 and later"). This supersedes the earlier P5-era guidance
  that iOS SourceGen HR needed Mono. Keep `UseMonoRuntime=false` on all platforms in .NET 11.
  ⚠️ Note the condition applies to the whole multi-TFM evaluation: an iOS-conditioned
  `UseMonoRuntime=true` will break `dotnet restore` even when you only build Android.
- On Android / Mac Catalyst / Windows, keep CoreCLR (`UseMonoRuntime=false`).

### Field notes — `dotnet watch` XAML Hot Reload (Preview 6, 2026-07, live-verified on Android)

Tested `11.0.100-preview.6.26356.105` SDK + MAUI `11.0.0-preview.6.26357.77`, Android API 36
emulator, driven by `maui devflow` for UI assertions:

- **C# Hot Reload works** under `dotnet watch` — method-body edits apply live, state preserved
  (verified: edited a `Clicked` handler string, tapped, saw the new text with the counter intact).
- **XAML Hot Reload does NOT live-apply** under `dotnet watch` (CLI, no IDE) — neither with the
  default inflator nor with `MauiXamlInflator/MauiXamlHotReload=SourceGen`. A `Label.Text` edit and
  a `CollectionView` `DataTemplate` edit both left the running UI unchanged, **even after
  re-navigating** to rebuild the page.
- ⚠️ `dotnet watch` prints **"🔥 C# and Razor changes applied"** for a saved `.xaml` file — this is
  **misleading**: it reflects the generated C# delta being accepted, not the visual tree updating.
  Do not treat that message as proof the XAML reloaded; verify the actual control (DevFlow
  `ui query`/`assert`, or eyes on the screen).
- Practical guidance for now: XAML live reload in .NET MAUI is IDE-mediated (VS / VS Code push XAML
  diffs to the in-app agent). Under a plain `dotnet watch` loop, expect only C# Hot Reload to take
  effect; restart the app to pick up XAML changes.

### Field notes — dotnet/maui **PR #34338** (Incremental XAML Hot Reload) — 2026-07-08, Android

Layered PR #34338 (`feature/xaml-incremental-hotreload`) CI build **1499577** →
MAUI `11.0.0-ci.pr34338.7.26358.63`, on SDK `11.0.100-preview.6.26356.105`, with the SourceGen HR
group above enabled. This PR **changes the base-Preview-6 verdict** — XAML now hot-reloads under a
plain `dotnet watch` loop (no IDE):

- ✅ **Build is clean** — `MauiXamlHotReload=SourceGen` no longer emits `MAUI1002` on this build
  (the feature is promoted out of "experimental/not implemented").
- ✅ **`Label.Text` XAML edit live-applies** under `dotnet watch` — a saved `.xaml` `Text` change
  updated the on-screen label with **no restart** (DevFlow `ui query` confirmed the new text).
  This did **not** work on base `preview.6.26357.77`.
- ⚠️ **`CollectionView` `DataTemplate` edit is patched live but existing cells aren't re-inflated.**
  A saved `DataTemplate` change did **not** update already-realized/virtualized cells in place.
  But the template delegate **is** hot-reloaded in-process: force cells to re-realize (e.g.
  `Items.Clear()` + re-add, **no restart/rebuild**) and the new cells render the updated template
  (verified: `Fruit: {0}` purple → `Item » {0} ⭐` blue after a re-realizing tap).
- Note: adding new statements to a method body was treated as a **rude edit** once and forced a
  full rebuild/redeploy (`DeployToDevice`, new PID) — normal for some C# edits under `dotnet watch`.
- ℹ️ On restart the DevFlow agent re-bound the **same** port (9223); re-run
  `adb -s <emu> forward tcp:9223 tcp:9223` after any redeploy before querying.

> When this PR merges into the release branch, fold these results into the main field notes above
> and drop the base-P6 "does NOT live-apply" verdict for the `Label` case.

---

## Group: (add new preview feature groups here)

When a new preview introduces toggles (e.g. a new interpreter, trimming mode, AOT flag, a
renamed property), append a dated group with: the property block, what it enables, and any
runtime/platform caveats. Keep retired groups briefly with a "retired in <version>" note so
older dogfood setups still make sense.

---

---

## Launch the IDE with the pinned SDK

Project properties and workloads only take effect if the IDE (or terminal) actually uses the
**dedicated preview SDK dir** ([download-builds.md](download-builds.md)), not a global `dotnet`.
Launch the IDE from a shell whose `DOTNET_ROOT` and `PATH` point at that dir so the SDK resolver,
workloads, and MSBuild all resolve from it.

```bash
# macOS / Linux — SDK installed at ~/.dotnet-maui-preview
export DOTNET_ROOT="$HOME/.dotnet-maui-preview"
export DOTNET_MSBUILD_SDK_RESOLVER_CLI_DIR="$DOTNET_ROOT"
export PATH="$DOTNET_ROOT:$PATH"
dotnet --version                        # confirm it's the pinned preview SDK
code /path/to/workspace                 # inherits the env (code-insiders for Insiders)
```
```powershell
# Windows (PowerShell)
$env:DOTNET_ROOT = "$env:USERPROFILE\.dotnet-maui-preview"
$env:DOTNET_MSBUILD_SDK_RESOLVER_CLI_DIR = $env:DOTNET_ROOT
$env:PATH = "$env:DOTNET_ROOT;$env:PATH"
dotnet --version
code C:\path\to\workspace               # or: devenv your.sln  (Visual Studio)
```

- `DOTNET_MSBUILD_SDK_RESOLVER_CLI_DIR` pins the MSBuild SDK resolver to the dedicated dir — the
  key that makes IDEs (which don't inherit ad-hoc interactive PATH tweaks) pick it up.
- **Launch the IDE from this shell** so it inherits the env; a GUI/Dock/Start-menu launch won't
  have it. Save the exports as a small launcher script the user runs each time.
- Only add these to the shell profile if the user wants the pinned SDK as their session default —
  otherwise keep it scoped to the launcher so it can't shadow their normal `dotnet`.

---

## VS Code settings — scope matters

VS Code settings are **scope-sensitive**. Writing a machine-scoped key into workspace settings
silently does nothing. Split them correctly:

### Workspace (`<repo>/.vscode/settings.json`) — window/resource-scoped only

```jsonc
{
  "dotnet.debug.hotReloadXAML": false
}
```
`dotnet.debug.hotReloadXAML` is window-scoped, so it belongs in (and works from) the workspace.
Turn it **off** when testing the SourceGen HR path so the two HR mechanisms don't conflict.

### User / machine (`User/settings.json`) — machine-scoped keys

```jsonc
{
  "csharp.experimental.debug.hotReload": true,
  "csharp.debug.hotReloadVerbosity": "diagnostic"
}
```
These two are **machine-scoped** — VS Code ignores them in workspace settings, so they must go in
the **User** settings.json. The verbosity enum value is the singular **`"diagnostic"`** (not
`"diagnostics"`, which is silently invalid).

User settings.json locations:
- macOS: `~/Library/Application Support/Code/User/settings.json`
- Linux: `~/.config/Code/User/settings.json`
- Windows: `%APPDATA%\Code\User\settings.json`
- Insiders: replace `Code` with `Code - Insiders`.

Merge into existing JSON — never clobber the user's other settings. (jq or a small Python/pwsh
JSON read-modify-write is safer than regex.)

---

## Visual Studio (Windows) — unified settings.json

Modern VS reads a unified `settings.json`. The equivalent HR verbosity key:

```jsonc
{
  "debugging.hotReload.hotReloadVerbosityLevel": "diagnostic"
}
```

Set project properties the same way (`Directory.Build.props` / `.csproj`) — those are
IDE-agnostic.

---

## Verify

- `dotnet build` the project with the pinned SDK — a wrong `MauiVersion` or missing local source
  surfaces here.
- In VS Code, the Output/Debug console HR verbosity should reflect `diagnostic` once the
  machine-scoped keys are in the **User** settings.
- If XAML edits don't appear under `dotnet watch` (CLI), that's expected in Preview 6 — only C#
  Hot Reload applies without an IDE; restart the app to pick up XAML. See the P6 field notes above.

## Stop signals

- Apply the **one** group the user is testing; don't stack unrelated toggles.
- Don't invent property names — if a needed toggle isn't in a group here, ask the user or check
  the MAUI PR/release notes rather than guessing.
