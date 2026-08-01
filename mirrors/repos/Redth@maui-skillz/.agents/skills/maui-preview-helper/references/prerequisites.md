# Prerequisites

Detect what's missing and help install it. Only bootstrap the tools the chosen capabilities
actually need — don't install everything up front.

## What each capability needs

| Capability | Needs |
| --- | --- |
| Release lookup | `pwsh`, `az` (+ `az login`) for the tracker; `darc` only for cross-repo asset tracing |
| Download builds | `pwsh`; `az` (+ login) only for **devdiv** (private) builds |
| Workloads | the pinned `dotnet` (dedicated SDK dir); `pwsh` for the rollback script |
| NuGet config | `dotnet` (to verify with `restore` / `nuget list source`) |
| VS Code VSIX | `code` (or `code-insiders`) on PATH; `az` (+ login) for the MAUI Dev Kit VSIX |
| Project properties | `dotnet` to build/verify |

**pwsh 7+** is the baseline for every bundled script (they use PowerShell 7 syntax).

## Detect

```bash
for t in pwsh az dotnet code darc gh; do
  if command -v "$t" >/dev/null 2>&1; then echo "$t: $(command -v $t)"; else echo "$t: MISSING"; fi
done
az account show >/dev/null 2>&1 && echo "az: logged in" || echo "az: NOT logged in"
```
```powershell
'pwsh','az','dotnet','code','darc','gh' | ForEach-Object {
  $c = Get-Command $_ -ErrorAction SilentlyContinue
  "{0}: {1}" -f $_, ($(if ($c) { $c.Source } else { 'MISSING' }))
}
```

## Install (prefer the platform package manager; confirm before installing)

| Tool | macOS | Windows | Linux |
| --- | --- | --- | --- |
| pwsh 7+ | `brew install --cask powershell` | `winget install Microsoft.PowerShell` | [pkg install docs](https://learn.microsoft.com/powershell/scripting/install/installing-powershell-on-linux) |
| az CLI | `brew install azure-cli` | `winget install Microsoft.AzureCLI` | `curl -sL https://aka.ms/InstallAzureCLIDeb \| sudo bash` |
| VS Code (`code`) | `brew install --cask visual-studio-code` | `winget install Microsoft.VisualStudioCode` | distro package / [docs](https://code.visualstudio.com/docs/setup/linux) |
| gh CLI | `brew install gh` | `winget install GitHub.cli` | [install docs](https://github.com/cli/cli#installation) |
| .NET SDK | `dotnet-install` script into a dedicated dir — see [download-builds.md](download-builds.md) | same | same |
| darc | `dotnet tool install -g Microsoft.DotNet.Darc --prerelease --add-source https://pkgs.dev.azure.com/dnceng/public/_packaging/dotnet-eng/nuget/v3/index.json` | same | same |

Prefer the user's existing package manager if different (e.g. `choco`/`scoop` on Windows,
`apt`/`dnf` on Linux). Always ask before installing system-wide tooling.

## Auth

- **`az login`** — Microsoft **tenant** account; needed for the release tracker and any **devdiv**
  (private) artifact (MAUI VSIX, internal builds). For **public `dnceng-public`** builds,
  whole-artifact downloads are anonymous, but file *listing* / single-file fetches may still use an
  `az` token (minted automatically when present) — so `az login` is optional but recommended even
  for public builds.
- **Non-Microsoft accounts** — signing in with a personal or other-tenant account is *not* enough
  for the tracker or `devdiv`; those resources simply aren't visible. That's expected, not a
  misconfiguration. The release tracker detects it and falls back to public data
  ([release-lookup.md](release-lookup.md)); `devdiv` artifacts have no public equivalent. Don't
  loop on `az login` trying to fix it.
- **`darc`** — `darc authenticate` (PAT) or browser flow; Maestro/BAR access requires .NET team
  membership (all-FTE) and cannot be granted externally. `gh auth login` is auto-detected by darc
  for GitHub ops.
- **`code` not on PATH** — in VS Code run *Shell Command: Install 'code' command in PATH*
  (Command Palette), or call the binary directly (macOS:
  `"/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"`).

## PATH for the pinned SDK

After installing the preview SDK into a dedicated dir, that dir must come **first** on PATH for
the session/IDE that should use it, and `DOTNET_ROOT` should point at it — otherwise a global
`dotnet` shadows it and workloads resolve from the wrong place. The old dogfood scripts generate
a launcher that exports `DOTNET_ROOT` / `DOTNET_MSBUILD_SDK_RESOLVER_CLI_DIR` / `PATH` before
launching the IDE; replicate that when the user wants VS Code/VS to pick up the pinned SDK. See
the launcher recipe in [project-properties.md](project-properties.md).

## Stop signals

- Install only what the selected capabilities require. Don't install `darc` for a simple
  download, or `az` for a public-only flow.
- If a tool is already present and (where relevant) authenticated, move on — don't reinstall or
  re-login.
- If the user isn't Microsoft-internal, **stop** at the internal boundary: don't install `darc`,
  don't retry `az login`, and don't chase `devdiv` artifacts. Take the public path or say plainly
  that there isn't one.
