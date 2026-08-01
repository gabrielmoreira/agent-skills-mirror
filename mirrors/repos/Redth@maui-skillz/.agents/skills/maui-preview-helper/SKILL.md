---
name: maui-preview-helper
description: >-
  Set up and manage .NET MAUI preview/dogfood environments across macOS, Windows, and Linux.
  USE FOR: installing a preview/CI .NET SDK + MAUI workloads, downloading Azure DevOps build
  artifacts (SDK installers, NuGet packages), building workload rollback files from a dotnet/maui
  branch, wiring NuGet.config to a local package source, installing prerelease VS Code VSIXes
  (C#, C# Dev Kit, .NET MAUI Dev Kit), setting preview project properties (SourceGen XAML Hot
  Reload, Mono vs CoreCLR), and looking up which preview/RC release to target. Triggers: "maui
  preview", "maui dogfood", "install maui workload", "rollback file", "sourcegen hot reload",
  "maui vsix", "preview sdk", "dogfood build". DO NOT USE FOR: general MAUI app coding/debugging,
  shipping-stable MAUI setup, or non-MAUI .NET workloads. INVOKES: pwsh scripts (Get-AzdoArtifact,
  New-WorkloadRollbackFile, Get-DotNetReleaseStatus), az, dotnet, darc, code CLIs.
source_repo: Redth/maui-skillz
---

# MAUI preview helper

Componentized helper for standing up and maintaining **.NET MAUI preview / dogfood**
environments. Seven **optional, composable** capabilities — do only what the user asks; each
maps to a reference doc with the depth.

## Operating principles

- **Agent-first / CLI-first.** Reason and drive `az` / `dotnet` / `code` / `darc` / `gh`
  directly. The bundled pwsh scripts exist only for the fiddly deterministic bits (AzDO artifact
  resolution, rollback-file construction, release tracker). Don't wrap what a CLI already does.
- **Pin exact versions.** A wrong SDK band cascades into wrong workloads and broken restores.
  When the user is vague, **look it up and offer a choice** — don't guess.
- **Match versions across layers:** the staged local MAUI package version == `<MauiVersion>` in
  the project == the `microsoft.net.sdk.maui` entry in the rollback file. Keep them identical.
- **Isolate the preview SDK** in a dedicated install dir (workloads are scoped to `DOTNET_ROOT`),
  so it never collides with a global install.
- **Cross-platform:** detect OS/arch and pick the right installer/VSIX/paths. Confirm the target
  platform when it's ambiguous (e.g. building for iOS from Windows).
- **Only install missing prereqs** for the capabilities in play, and ask before installing
  system tooling. See [references/prerequisites.md](references/prerequisites.md).
- **Degrade gracefully for external users.** Several sources are Microsoft-internal (Release
  Tracker, darc/Maestro, `devdiv` builds). Detect that **before** routing a user toward them,
  take the public path when one exists, and say plainly when one doesn't — never surface a raw
  401/403 or tell someone to `az login` for something they can't be granted. See
  [Access tiers](#access-tiers).

## Capabilities → route to the right reference

| # | Capability | Use when the user wants to… | Reference |
| --- | --- | --- | --- |
| 1 | **Release lookup** | find/choose which preview/RC/CI release, SDK version, or build to target | [release-lookup.md](references/release-lookup.md) |
| 2 | **Download builds** | pull an SDK installer for their OS/arch and/or stage CI NuGet packages as a local source | [download-builds.md](references/download-builds.md) |
| 3 | **Workloads** | install the MAUI workload via a workload-set version **or** a rollback file (from a maui branch + overrides) | [workloads.md](references/workloads.md) |
| 4 | **NuGet.config** | wire a workspace to the local source + the feeds the release needs | [nuget-config.md](references/nuget-config.md) |
| 5 | **VS Code VSIX** | install prerelease C# / C# Dev Kit / .NET MAUI Dev Kit extensions per arch | [vscode-extensions.md](references/vscode-extensions.md) |
| 6 | **Project properties** | toggle preview features (SourceGen XAML HR, Mono/CoreCLR) + IDE settings | [project-properties.md](references/project-properties.md) *(living doc)* |
| 7 | **Prerequisites** | detect/install pwsh, az, dotnet, code, darc; handle auth & PATH | [prerequisites.md](references/prerequisites.md) |

**Load a reference before acting on its capability** — each has the exact URL patterns, script
invocations, gotchas, and stop signals. Don't rely on this router alone for the details.

## Access tiers

Not everything here is reachable outside Microsoft. Establish the tier **once, up front**, then
route accordingly — don't discover it via a 401 halfway through a setup.

| Source | Needs | If unavailable |
| --- | --- | --- |
| **.NET Release Tracker** | Microsoft tenant (`az login`) | **Automatic fallback** — `Get-DotNetReleaseStatus.ps1` switches to public release metadata and labels the output. Force with `-PublicOnly`. |
| **`dnceng-public` builds** | nothing | already public |
| **`dotnet{N}` / `dotnet-public` feeds** | nothing | already public |
| **`devdiv` builds** (MAUI Dev Kit VSIX, internal drops) | Microsoft tenant + `az` token | **No public equivalent.** Use the Marketplace prerelease, or ask the user for a downloaded `.vsix`. Say so — don't loop on auth. |
| **darc / Maestro (BAR)** | .NET team membership (all-FTE) | Build the rollback file from the public `dotnet/maui` branch (`Rollback.in.json` + `Versions.props`) and ask the user for `microsoft.net.sdk.maui` explicitly. |

Detect before routing:

```bash
az account show >/dev/null 2>&1 && echo "az: signed in" || echo "az: not signed in"
pwsh scripts/Get-DotNetReleaseStatus.ps1 | head -3   # leading lines name the source actually used
```

If the release output is headed **"Public release data"**, treat the session as external: skip
`devdiv` and `darc` entirely, and target only shipped/announced releases. Unshipped previews are
internal-only — don't imply they're obtainable.

## Typical end-to-end flow (full dogfood setup)

Most requests are a subset of this. Adapt to what the user asked for.

1. **Prereqs** — detect missing tools for the capabilities you'll use; install/authenticate.
2. **Release lookup** — resolve the exact SDK version + MAUI version + build id(s); if vague,
   run the tracker and let the user pick.
3. **Download** — install the preview SDK into a dedicated dir; stage the build's NuGet packages
   into a local source folder; note the exact MAUI package version.
4. **NuGet.config** — point the workspace at the local source + `dotnet{N}` / `dotnet-public`.
5. **Workloads** — install into the pinned SDK via workload set **or** a rollback file
   (`New-WorkloadRollbackFile.ps1` from the maui branch, with `-MauiVersion`/overrides).
6. **Project properties** — set `<MauiVersion>` + the feature group the user is testing
   (Directory.Build.props or .csproj), plus VS Code / VS settings at the correct scope.
7. **VS Code VSIX** — install C# → C# Dev Kit → .NET MAUI Dev Kit for this OS/arch.
8. **Verify** — `dotnet workload list`, `dotnet restore`/`build`, `code --list-extensions`.

## Bundled scripts (in `scripts/`)

- **`Get-AzdoArtifact.ps1`** — resolve + download any AzDO artifact (whole zip / single file /
  list), public or devdiv-authenticated; `-Extract`, `-FlattenNupkg`. Powers capabilities 2 & 5.
- **`New-WorkloadRollbackFile.ps1`** — build a rollback JSON from a dotnet/maui branch's
  `Rollback.in.json` + `Versions.props`, with `-Band` / `-MauiVersion` / `-Override`. Capability 3.
- **`Get-DotNetReleaseStatus.ps1`** + **`ReleaseTrackerApi.ps1`** — bundled .NET Release Tracker
  (capability 1). Needs `az login`. If the standalone `dotnet-release-tracker` plugin is
  installed, you may use it instead — same API.

`Get-AzdoArtifact.ps1` and `New-WorkloadRollbackFile.ps1` emit a one-line `[SKILL_SUMMARY] {json}`
with structured results — **reason over that**, don't just echo it. (The bundled release-tracker
script prints human-readable release blocks instead of a summary line; parse those directly.)

## Key facts (details in references)

- AzDO orgs: **dnceng-public** (public — whole-artifact downloads are anonymous; file listing /
  single-file fetches may still mint an `az` token, done automatically when `az` is present) vs
  **devdiv/DevDiv** (private, always needs an `az` token; resource
  `499b84ac-1321-427f-aa17-267ca6975798`).
- Preview package feeds are `dotnet{N}` (N = major, e.g. `dotnet11`) on dnceng/public.
- Rollback file = flat JSON `{ "manifest.id": "version/sdk-band" }`; the `microsoft.net.sdk.maui`
  version is only knowable from the CI build (supply it explicitly).
- **`<MauiVersion>` is the single source of truth** — the SDK pins all MAUI package refs to it.
  Any explicit MAUI `PackageReference` must use `Version="$(MauiVersion)"`, never a literal
  ([project-properties.md](references/project-properties.md)).
- **XAML SourceGen Hot Reload** needs three props together: `MauiXamlInflator=SourceGen`,
  `MauiXamlHotReload=SourceGen`, `EnableMauiIncrementalHotReload=true`. Keep `UseMonoRuntime=false`
  everywhere — **Mono on iOS is unsupported in .NET 11** (`NETSDK1242`), superseding the old P5
  "iOS HR needs Mono" guidance ([project-properties.md](references/project-properties.md)).
- **Layering a branch/PR MAUI build** onto a base release: stage its nupkgs into the **same**
  local source and bump only `<MauiVersion>` ([download-builds.md](references/download-builds.md)).
- **Authenticated feeds** (401 on restore): mint an `az` token for the feed's org (resource
  `499b84ac-…`) or a Packaging-read PAT; wire via `packageSourceCredentials`, never commit it
  ([nuget-config.md](references/nuget-config.md)).
- VS Code HR settings `csharp.experimental.debug.hotReload` / `csharp.debug.hotReloadVerbosity`
  are **machine-scoped** → User settings.json; verbosity value is singular `"diagnostic"`.

## Stop signals

- Do **only** the requested capabilities — don't run a full setup when asked for one piece.
- Once the target versions are pinned, stop looking them up; once `dotnet restore`/`workload
  list` shows the intended versions, stop reconfiguring.
- Download one installer/VSIX per OS/arch, not the whole matrix.
- Ask the user (don't guess) when a version, branch, build id, target platform, or the MAUI
  manifest version is unknown.

<!-- BEGIN skill-reflect nudge -->

## Improve This Skill

**For the agent:** If this skill was used during the session and you or the user
encountered friction — unexpected failures, stale guidance, repeated workarounds, or
unclear routing — you may offer a brief skill-quality review at a natural stopping
point (on task completion, before `/clear`, or when the user asks what to do next):

> "This session used **maui-preview-helper**. Want me to capture privacy-safe feedback for the
> skill author using `skill-reflect`?"

If the user says **yes**, invoke the `skill-reflect` skill. Pass this skill's identity
so attribution is exact — **the nudge carries context**. Include the skill name (and
optionally its source repo) when invoking:

    Run skill-reflect. Skill used this session: maui-preview-helper (source repo: Redth/maui-skillz).

Rules — never deviate:
- **Consent-first.** Offer; never run automatically. `skill-reflect` runs only on the
  user's explicit yes.
- **Only on friction.** Routine, smooth sessions need no review.
- **Nothing leaves the machine** without a second consent step inside `skill-reflect`.

<!-- END skill-reflect nudge -->
