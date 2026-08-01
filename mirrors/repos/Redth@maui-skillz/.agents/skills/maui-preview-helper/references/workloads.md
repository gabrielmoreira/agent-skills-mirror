# Workloads

Install the MAUI workload (android/iOS/maccatalyst/macos/tvos + mono/emscripten) at versions
that match the preview SDK. There are **two mechanisms** — pick based on what the user gives you.

> Workloads are scoped to the **SDK install directory** (packs + metadata live under
> `DOTNET_ROOT`). Install them into the same dedicated preview SDK dir from
> [download-builds.md](download-builds.md), and always point commands at that `dotnet`.

## Decision: workload set vs rollback file

| You have… | Use | How |
| --- | --- | --- |
| A **workload set version** (e.g. `9.0.100-preview.7.24414.1`) that's on a known feed | **Workload set** | `dotnet workload install maui --version <set>` |
| A **MAUI repo branch** (e.g. `net9.0`, `main`, a PR branch) and/or explicit pack overrides | **Rollback file** | build JSON from the branch, then `--from-rollback-file` |
| Nothing specific ("just install latest for this SDK") | Loose manifests | `dotnet workload install maui` (updates each manifest to latest compatible) |

Ask the user which they want if it's ambiguous. Dogfood/CI scenarios almost always use a
**rollback file** because it pins exact CI pack versions that aren't in a published set.

## Mechanism A — Workload set version

```bash
# Optional: switch to workload-set update mode (default on 9.0+)
"$DOTNET" workload config --update-mode workload-set

"$DOTNET" workload install maui --version 9.0.100-preview.7.24414.1 \
    --source ~/NuGet/Source \
    --source https://pkgs.dev.azure.com/dnceng/public/_packaging/dotnet9/nuget/v3/index.json \
    --source https://api.nuget.org/v3/index.json
```

- The set version format tracks the SDK band: `8.0.400`, `9.0.201`, `9.0.100.2`
  (4-part = explicit workload-set patch), `9.0.100-preview.7.24414.1` (preview).
- You can also pin it in `global.json` → `{ "sdk": { "workloadVersion": "<set>" } }`, which
  forces workload-set mode for anything under that dir.
- `--source` **overrides** nuget.config sources for the operation and must point at feeds that
  have both the manifests **and** the packs. List your **local staged source first** (e.g.
  `~/NuGet/Source` from [download-builds.md](download-builds.md)), then the `dotnet{N}` preview
  feed (N tracks the SDK major — `dotnet9` for a 9.0.x band, `dotnet11` for 11.0.x) + nuget.org.

## Mechanism B — Rollback file

A rollback file is a **flat JSON** object mapping lowercased manifest IDs to `version/sdk-band`:

```json
{
  "microsoft.net.sdk.android": "35.0.80/9.0.100",
  "microsoft.net.sdk.ios": "18.0.9617/9.0.100",
  "microsoft.net.sdk.maccatalyst": "18.0.9617/9.0.100",
  "microsoft.net.sdk.macos": "15.0.9617/9.0.100",
  "microsoft.net.sdk.maui": "9.0.80-ci.net9/9.0.100",
  "microsoft.net.sdk.tvos": "18.0.9617/9.0.100",
  "microsoft.net.workload.mono.toolchain.net8": "9.0.5/9.0.100",
  "microsoft.net.workload.mono.toolchain.current": "9.0.5/9.0.100",
  "microsoft.net.workload.emscripten.net8": "9.0.5/9.0.100",
  "microsoft.net.workload.emscripten.current": "9.0.5/9.0.100"
}
```

Apply it:

```bash
"$DOTNET" workload install maui --from-rollback-file ./rollback.json \
    --source ~/NuGet/Source \
    --source https://pkgs.dev.azure.com/dnceng/public/_packaging/dotnet9/nuget/v3/index.json \
    --source https://api.nuget.org/v3/index.json
# (dotnet workload update --from-rollback-file <file> also works)
```

- The value is `manifestPackageVersion/sdkFeatureBand`. If you omit `/band`, the SDK infers the
  band from the running SDK — **prefer specifying it** to avoid surprises.
- The rollback manifest version is the **manifest NuGet package version**, which (for
  android/ios/etc.) equals the pack version property in MAUI's `Versions.props`.

### Constructing a rollback file from a MAUI branch

The [`New-WorkloadRollbackFile.ps1`](../scripts/New-WorkloadRollbackFile.ps1) script does this:
it reads `Rollback.in.json` (the placeholder template) and `eng/Versions.props` from a
`dotnet/maui` branch, substitutes each `@Property@`, and writes the JSON.

```bash
pwsh scripts/New-WorkloadRollbackFile.ps1 -Branch net9.0 -OutFile ./rollback.json

# Override a single manifest's pack version (e.g. a newer iOS) — supersedes the branch value:
pwsh scripts/New-WorkloadRollbackFile.ps1 -Branch net9.0 -OutFile ./rollback.json `
    -Override 'microsoft.net.sdk.ios=18.2.9000'
```

How it works (and why it needs help sometimes):

1. Fetch `src/Workload/Microsoft.NET.Sdk.Maui.Manifest/Rollback.in.json` from the branch — this
   is the authoritative list of which manifest IDs exist and which property feeds each one
   (it differs by branch: `net9.0` has emscripten entries; `main` uses different mono props).
2. Fetch `eng/Versions.props`; resolve each `@Property@` (following simple `$(Other)` aliases).
3. Substitute to produce `version/band` values.
4. Apply any `-Override id=version` the user supplied **last**, so explicit input wins.

> ⚠️ **The `microsoft.net.sdk.maui` version (`@VERSION@`) is not statically knowable** from the
> repo — it's the MAUI package's own build version and only exists after a CI build. The script
> fills the *form* from `Versions.props` (e.g. `9.0.80-ci.net9`) but you usually must set the
> exact MAUI manifest version yourself via `-Override microsoft.net.sdk.maui=<exact>/<band>`,
> taken from the CI build you're dogfooding (the same build you staged packages from in
> [download-builds.md](download-builds.md)). If unsure, ask the user for the MAUI version.

> 💡 **Most reliable: use the rollback the CI build already embedded.** MAUI CI builds ship a
> ready-made rollback at `metadata/rollbacks/*_rollback.json` inside the
> `Microsoft.NET.Sdk.Maui.Manifest-*.nupkg`. If you staged that package
> ([download-builds.md](download-builds.md)), extract and use it directly — no reconstruction and
> no `@VERSION@` guesswork:
>
> ```bash
> # A .nupkg is a zip; pull the embedded rollback out of the staged manifest package.
> pkg=$(ls ~/NuGet/Source/Microsoft.NET.Sdk.Maui.Manifest-*.nupkg | head -1)
> unzip -o "$pkg" 'metadata/rollbacks/*_rollback.json' -d /tmp/maui-rollback
> rb=$(ls /tmp/maui-rollback/metadata/rollbacks/*_rollback.json | head -1)
> "$DOTNET" workload install maui --from-rollback-file "$rb" \
>     --source ~/NuGet/Source \
>     --source https://api.nuget.org/v3/index.json
> ```

### When to use darc

`darc` can resolve exact asset versions across repos, but for building a rollback file you
**don't need it** — reading `Versions.props` + `Rollback.in.json` from the branch (what the
script does) is enough and needs no auth. Reach for `darc get-dependencies` / `get-asset` only
when the branch's props reference versions you need to trace to another repo's build. Install:
`dotnet tool install -g Microsoft.DotNet.Darc --prerelease --add-source https://pkgs.dev.azure.com/dnceng/public/_packaging/dotnet-eng/nuget/v3/index.json`.

## Verify

```bash
"$DOTNET" workload list          # shows installed workloads + versions
"$DOTNET" workload --version      # workload set version (or manifests hash)
```

Confirm the installed android/ios/etc. versions match the rollback/set you intended.

## Common pitfalls

- **Wrong SDK targeted.** If `dotnet` resolves to a global install, workloads land in the wrong
  place. Always invoke the pinned `$DOTNET` (dedicated dir) or set `DOTNET_ROOT` first.
- **Missing packs on the feed.** A `--from-rollback-file` install fails if a pinned version
  isn't on any `--source`. Point `--source` at the exact CI/preview feed that produced it.
- **Band mismatch.** The `/band` must be the SDK feature band the workload manifests were built
  for (e.g. `9.0.100`, `10.0.100`, or a preview band `9.0.100-preview.7`), not the full SDK
  version.

## Stop signals

- Once `dotnet workload list` shows the target versions, stop — don't reinstall or try the
  other mechanism.
- Don't hand-maintain the manifest ID list; let the script read it from the branch template so
  it stays correct across branches.
