# Download builds — SDK installers & NuGet packages

Pull the bits for a target release/build out of Azure DevOps: the right **SDK installer**
for the user's OS/arch, and the **NuGet packages** to stage as a local package source.

All downloads go through one script — [`scripts/Get-AzdoArtifact.ps1`](../scripts/Get-AzdoArtifact.ps1) —
which handles the two AzDO download shapes (whole-artifact zip vs single file) and the
public-vs-private auth split. Prefer it over hand-rolled `curl`; fall back to `az` CLI or
`curl` only if the script can't reach a build.

## Two ways to get a preview SDK onto the machine

### A) `dotnet-install` into a dedicated dir (usually best for CI/preview SDKs)

Preview SDK-band builds publish to blob storage and are installable by exact version. Install
into a **dedicated directory** so it never collides with a globally installed SDK, and so
workloads (which are scoped per-SDK-install) stay isolated:

```bash
# macOS / Linux
curl -fsSL https://dot.net/v1/dotnet-install.sh -o /tmp/dotnet-install.sh && chmod +x /tmp/dotnet-install.sh
/tmp/dotnet-install.sh --version 11.0.100-preview.5.26302.115 --install-dir "$HOME/.dotnet-maui-preview"
```
```powershell
# Windows
Invoke-WebRequest https://dot.net/v1/dotnet-install.ps1 -OutFile $env:TEMP\dotnet-install.ps1
& $env:TEMP\dotnet-install.ps1 -Version 11.0.100-preview.5.26302.115 -InstallDir "$env:USERPROFILE\.dotnet-maui-preview"
```

- `--version` accepts an exact 4-part preview version (`11.0.100-preview.5.26302.115`) or a
  channel. Use the exact `SdkVersion` from the release tracker.
- If `dotnet-install` can't find that exact version on the default (public) location, the build
  may be internal — fall through to option B (download the shipping installer from the build).
- **Why a dedicated dir:** the IDE launcher pins `DOTNET_ROOT` to it and workloads live under
  that dir. A matching global SDK is *not* enough for a launched VS Code / VS. See
  [project-properties.md](project-properties.md) for the launcher pattern.

### B) Download the shipping installer artifact for the user's OS/arch

When you must use a specific build's installer (internal build, or a `.pkg`/`.exe` the user
wants), list the shipping artifact and pick the file that matches this machine.

```bash
# 1. List installers in the build's shipping artifact, filtered to this machine
pwsh scripts/Get-AzdoArtifact.ps1 -Organization dnceng-public -Project public -BuildId <id> `
    -ArtifactName BlobArtifacts -List -Filter '*osx-arm64*'

# 2. Download the one you chose
pwsh scripts/Get-AzdoArtifact.ps1 -Organization dnceng-public -Project public -BuildId <id> `
    -ArtifactName BlobArtifacts -SubPath 'Sdk/<ver>/dotnet-sdk-<ver>-osx-arm64.pkg' -Destination ~/Downloads
```

> ⚠️ Artifact names vary by pipeline (`BlobArtifacts`, `Shipping`, `drop`, `PackageArtifacts`…).
> `-List` enumerates the files **inside one named artifact**, so it still needs the exact
> `-ArtifactName`. To discover which artifacts a build has, open the run's **Artifacts** tab in
> the AzDO web UI (or read the release tracker's `BuildStageContainer` / `BuildArtifactsUrl`).
> Then `-List` that artifact and narrow with `-Filter` — don't assume a fixed layout.

#### OS/arch → installer file map

| OS | arch | file pattern | how to run |
| --- | --- | --- | --- |
| macOS | arm64 (Apple silicon) | `*-osx-arm64.pkg` | `sudo installer -pkg <file> -target /` |
| macOS | x64 (Intel) | `*-osx-x64.pkg` | same |
| Windows | x64 | `*-win-x64.exe` | run the exe |
| Windows | arm64 | `*-win-arm64.exe` | run the exe |
| Linux | x64 | `*-linux-x64.tar.gz` | extract to install dir |
| Linux | arm64 | `*-linux-arm64.tar.gz` | extract to install dir |

Detect the machine: macOS/Linux `uname -m` (`arm64`/`aarch64` vs `x86_64`); Windows
`$env:PROCESSOR_ARCHITECTURE` (`ARM64` vs `AMD64`). Confirm the OS with the user if the build
targets a different platform than they're on (e.g. building for Windows from a Mac).

> A `.pkg`/`.exe` installs **globally** (not into a dedicated dir). For isolated preview
> testing, prefer option A. Use B when the user explicitly wants the installer or the SDK is
> only available as a build artifact.

## Stage NuGet packages as a local source

MAUI PR/CI builds publish a `PackageArtifacts` (sometimes `Shipping`) artifact full of
`.nupkg`s. Flatten them into a folder that you'll wire up as a local feed:

```bash
pwsh scripts/Get-AzdoArtifact.ps1 -Organization dnceng-public -Project public -BuildId <id> `
    -ArtifactName PackageArtifacts -Destination ~/NuGet/Source -Extract -FlattenNupkg
```

- `-FlattenNupkg` copies just the `.nupkg` files (drops the nested folder structure) so the
  folder works directly as a NuGet `packageSource`.
- Default local source dirs: `~/NuGet/Source` (macOS/Linux), `C:\NuGet\Source` (Windows) —
  or anywhere the user prefers. Remember the path; you'll add it to `NuGet.config`
  ([nuget-config.md](nuget-config.md)).
- After staging, note the **exact MAUI package version** present (e.g.
  `11.0.0-ci.pr34338.6.26312.9`) — the project's `<MauiVersion>` must match it exactly.
  `ls ~/NuGet/Source | grep -i Microsoft.Maui.Controls` reveals it.

## Layer branch/PR MAUI packages onto a base release

Sometimes a feature you're testing (e.g. **XAML-change Hot Reload**) only exists on a specific
`dotnet/maui` branch or PR, not in the base preview. Stage that branch's CI build **into the
same local source folder** as the base release, so restore sees one merged feed — then point
`<MauiVersion>` at the branch build.

```bash
# Stage the branch/PR build's MAUI packages alongside the base release packages
pwsh scripts/Get-AzdoArtifact.ps1 -Organization dnceng-public -Project public -BuildId <branch-build-id> `
    -ArtifactName PackageArtifacts -Destination ~/NuGet/Source -Extract -FlattenNupkg
```

Then:

- **Bump `<MauiVersion>` to the branch build's version** (find it:
  `ls ~/NuGet/Source | grep -i Microsoft.Maui.Controls` — pick the branch build's, which is
  newer/distinct from the base). Because `<MauiVersion>` drives all MAUI package references
  ([project-properties.md](project-properties.md)), this one change re-points the whole app at
  the branch bits — **don't** hardcode a different version on any explicit `PackageReference`.
- The branch packages may pull transitive deps that only live on **darc feeds**
  (`https://pkgs.dev.azure.com/dnceng/public/_packaging/darc-pub-dotnet-<repo>-<hash>/...`).
  Read the branch's `NuGet.config`
  (`curl -fsSL https://raw.githubusercontent.com/dotnet/maui/<branch>/NuGet.config`) and add any
  `darc-pub-*` feeds it lists to your workspace `NuGet.config`
  ([nuget-config.md](nuget-config.md)) and to `--source` on any workload command.
  - ⚠️ **The `<hash>` in a darc feed URL changes from build to build on the same branch.** A feed
    that worked for an earlier build can miss packs for a newer one (restore fails on a runtime/SDK
    pack). When you **re-layer a newer build**, diff the branch `NuGet.config`'s darc URLs against
    your workspace config and **update the hashes** — don't assume they're stable. Observed in one
    session: the macios feed moved `…-macios-e6aeff4e` → `…-macios-90e2eb7a` between two builds of
    the same PR while the dotnet feed hash stayed put. Update only the ones that changed.
- **Verify the layer actually resolved.** Scope restore to the one TFM you're testing so it doesn't
  drag in other platforms' packs (and their darc feeds): `dotnet restore -p:TargetFramework=net11.0-android`.
  (Use `-p:TargetFramework=` — the `-f`/`--framework` flag is build/run-only and errors on
  `restore` with "Project file does not exist. Switch: …".) Then confirm the branch build won,
  not the base:
  ```bash
  grep -o '"microsoft.maui.controls/[^"]*"' obj/project.assets.json | head -1
  # -> "microsoft.maui.controls/11.0.0-ci.pr34338.7.26358.63"  (the branch build, not the base)
  ```
- **Workloads too:** if the branch bumped the MAUI **manifest** (`microsoft.net.sdk.maui`),
  rebuild/override the rollback file with the branch build's MAUI manifest version
  ([workloads.md](workloads.md)) so the installed workload matches the layered packages.
- If a base and branch build publish the **same** `Microsoft.Maui.*` version, the folder feed is
  ambiguous — prefer distinct CI versions, or stage the branch build into a **separate** local
  source listed **first** in `NuGet.config`.

> A private/internal branch build's `PackageArtifacts` may require an authenticated download
> (`-Organization devdiv`) and its feeds may need a token — see
> [nuget-config.md](nuget-config.md) *Private / authenticated feeds*.

## Finding the build id

- Release tracker `BuildArtifactsUrl` → the build/drop for a release.
- A MAUI PR: open the PR's CI check → the AzDO pipeline run URL ends in `?buildId=<id>` (org
  `dnceng-public`, project `public`).
- Ask the user for the PR or build number if it isn't derivable.

> ⚠️ **A red overall PR/CI status does NOT mean the packages are missing.** The `maui-pr` run
> routinely shows **FAILURE** because a Helix/unit/integration-test job or Build Analysis failed,
> while the package-producing jobs (Build Windows / macOS) succeeded and still published
> `PackageArtifacts`. Don't skip a build just because the check is red — confirm the artifact
> exists, then use it:
> ```bash
> curl -fsSL "https://dev.azure.com/dnceng-public/public/_apis/build/builds/<id>/artifacts?api-version=7.1-preview.5" \
>   | python3 -c "import sys,json;[print(a['name']) for a in json.load(sys.stdin)['value']]"
> # or: Get-AzdoArtifact.ps1 ... -ArtifactName PackageArtifacts -List -Filter '*Microsoft.Maui.Controls.1*'
> ```
> If `PackageArtifacts` is present, the build is usable. Prefer the **latest** such build on the
> branch (its CI version sorts highest, e.g. `…pr34338.7.26358.63` > `…pr34338.6.26324.47`).

## Stop signals

- Download **one** installer (the matching os/arch) — don't fetch the whole matrix.
- Stage packages once; don't re-download if `~/NuGet/Source` already has the target version.
- If `-List` shows the artifact you expected, stop exploring other artifact names.
