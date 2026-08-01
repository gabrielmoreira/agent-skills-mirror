# Release lookup

Figure out **which release / build / versions** to target before downloading anything.
Do this first whenever the user hasn't pinned an exact SDK version, MAUI version, or
build id. If the user *has* specified everything, skip ahead to the relevant capability.

## Sources (in rough order of preference)

| Source | Gives you | Auth |
| --- | --- | --- |
| **.NET Release Tracker** (bundled script) | Active/upcoming releases: SDK & runtime versions, stage, release date, build stage container, build artifacts URL | `az login` (Microsoft tenant) — **internal**; falls back to public data automatically |
| **NuGet feeds** | Exact published package versions (preview / RC / CI) | Public feeds: none |
| **AzDO builds** | PR/CI drops: packages, shipping installers, VSIXes | Public org: none to download (`az` may be minted to list files); DevDiv: `az` token — **internal** |
| **darc** | The dependency/asset versions that make up a repo's build (e.g. MAUI's workload packs) | Maestro/BAR — **internal** (all-FTE) |

### When the tracker isn't available

`Get-DotNetReleaseStatus.ps1` never hard-fails. If `az` is missing, the user isn't signed in, or
the Release Tracker app isn't visible to their account, it falls back to public release metadata
(`builds.dotnet.microsoft.com`) and prefixes the output with a `> **Public release data**` banner
naming the reason. `-PublicOnly` forces that path.

The public fallback gives `Stage` (support phase), `RuntimeVersion`, `SdkVersion`, `ReleaseDate`,
and `Security` for every non-EOL channel. It **cannot** give `BuildStageContainer`,
`BuildArtifactsUrl`, or any unshipped preview — those are internal-only.

So when you see the public banner: pin versions from the public data, use `dnceng-public` builds
and public feeds, and **skip** the `devdiv` and darc paths rather than asking the user to
authenticate to them.

## Using the release tracker

```bash
pwsh scripts/Get-DotNetReleaseStatus.ps1
```

Requires `az login`. Prints one block per **active** release with these fields:

- `Name`, `Stage` (e.g. Preview 5, RC 1, GA), `RuntimeVersion`, `SdkVersion`, `ReleaseDate`, `Security`
- `BuildStageContainer` — the staging container name for that release's build drop
- `BuildArtifactsUrl` — where the build's artifacts live

> The standalone `dotnet-release-tracker` plugin exposes the same data. If it's
> installed, you can use it instead of the bundled copy — they call the same API.

### Offer a choice when the user was vague

If the user says "the current preview" / "latest MAUI preview" / "an upcoming release"
without an exact version:

1. Run the tracker.
2. Present the active releases as a short numbered list (Name + Stage + SdkVersion + ReleaseDate).
3. Ask which one to target (use the `ask_user` tool with the releases as choices).
4. Carry the chosen `SdkVersion` / `BuildStageContainer` / `BuildArtifactsUrl` into the
   download and NuGet-config steps.

Don't guess a version. A wrong SDK band cascades into wrong workloads and broken restores.

## Package feeds (memorize these)

| Feed | v3 index URL |
| --- | --- |
| nuget.org | `https://api.nuget.org/v3/index.json` |
| dotnet-public | `https://pkgs.dev.azure.com/dnceng/public/_packaging/dotnet-public/nuget/v3/index.json` |
| dotnet-tools | `https://pkgs.dev.azure.com/dnceng/public/_packaging/dotnet-tools/nuget/v3/index.json` |
| dotnet-eng (darc, arcade) | `https://pkgs.dev.azure.com/dnceng/public/_packaging/dotnet-eng/nuget/v3/index.json` |
| dotnetN (per-version preview, N = 9/10/11…) | `https://pkgs.dev.azure.com/dnceng/public/_packaging/dotnet{N}/nuget/v3/index.json` |

The per-version `dotnet{N}` feed is where **preview/RC** SDK-band packages (including MAUI
release packages) are published. Match the feed number to the target major version.

## AzDO builds

- **dnceng-public** (`https://dev.azure.com/dnceng-public`) — public. Whole-artifact **downloads
  are anonymous**; *listing* files or single-file fetches may mint an `az` token for the AzDO
  container service (the script does this automatically when `az` is available, else falls back to
  an anonymous zip download). So `az login` is optional here, never required. Most dotnet OSS
  CI/PR builds (runtime, sdk, maui, roslyn/C# extension) land here.
- **devdiv / DevDiv** (`https://dev.azure.com/devdiv`) — **private**, needs an `az` token.
  The internal **.NET MAUI VS Code VSIX** builds live here.

To find a build id: the release tracker's `BuildArtifactsUrl` often links to it; for a MAUI
PR, the PR's CI check links to the pipeline run; or ask the user for the build/PR number.

## When to reach for darc

Use `darc` when you need the **exact versions of the things a repo's build is composed of**
— e.g. "what android/iOS/maccatalyst pack versions does this MAUI branch/build use?" — to
build a workload rollback file. See [workloads.md](workloads.md). For simple "what SDK is in
preview N" questions, the release tracker is enough; darc is overkill.

## Stop signals

- Once you have a concrete `SdkVersion` (and, if relevant, a MAUI version + build id), stop
  looking. Don't enumerate every feed or every historical build.
- If the user already gave an exact version/build, don't run the tracker at all.
