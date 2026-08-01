# VS Code extensions (VSIX)

Install matching prerelease/internal builds of the three extensions MAUI dogfooding needs, per
the machine's OS/arch:

| Extension | id | Source | Auth |
| --- | --- | --- | --- |
| C# | `ms-dotnettools.csharp` | dnceng-public build, `Packages` artifact, `VSIX_Prerelease` channel | none |
| C# Dev Kit | `ms-dotnettools.csdevkit` | Marketplace (prerelease) — usually just install by version | none |
| .NET MAUI Dev Kit | `ms-dotnettools.dotnet-maui` | **devdiv** build, `VSIX` artifact | `az` token |

All VSIX downloads go through [`scripts/Get-AzdoArtifact.ps1`](../scripts/Get-AzdoArtifact.ps1).
Install with the VS Code CLI: `code --install-extension <file> --force` (use `code-insiders`
for Insiders). If `code` isn't on PATH, run VS Code's *Shell Command: Install 'code' command in
PATH* first — see [prerequisites.md](prerequisites.md).

> **Auth nuance:** downloading a VSIX is a whole-artifact zip fetch — **anonymous** on
> `dnceng-public`. *Listing* (`-List`) or single-file extraction may mint an `az` token for the
> AzDO container service even on public orgs (the script does this automatically when `az` is
> present, else falls back to an anonymous zip download). So `az login` is optional for the C#
> VSIX but recommended; it's **required** only for the devdiv MAUI Dev Kit VSIX.

## OS/arch → VSIX platform token

`code`/`darwin`/`win32`/`linux` + `arm64`/`x64`. Detect: macOS/Linux `uname -m` (`arm64`/`aarch64`
→ arm64, else x64); Windows `$env:PROCESSOR_ARCHITECTURE` (`ARM64` → arm64, else x64).

## C# extension (public org)

VSIX file name: `csharp-{darwin|win32|linux}-{arm64|x64}-{version}.vsix`. It lives under the
`Packages` artifact in a channel subfolder (`VSIX_Prerelease` for prereleases):

```bash
# List to discover the exact file/version in the build
pwsh scripts/Get-AzdoArtifact.ps1 -Organization dnceng-public -Project public -BuildId <csharpBuild> `
    -ArtifactName Packages -List -Filter '*csharp-darwin-arm64*'

# Download the chosen VSIX (subPath is channel + filename, relative to the artifact root)
pwsh scripts/Get-AzdoArtifact.ps1 -Organization dnceng-public -Project public -BuildId <csharpBuild> `
    -ArtifactName Packages -SubPath 'VSIX_Prerelease/csharp-darwin-arm64-<version>.vsix' `
    -Destination /tmp
code --install-extension /tmp/csharp-darwin-arm64-<version>.vsix --force
```

> The `Packages` artifact may be a **Container** or a **PipelineArtifact** depending on the
> pipeline run. Either works: `-List` automatically falls back to downloading the artifact zip and
> enumerating it, and `-SubPath` extracts from the zip regardless. No flags to change.

## C# Dev Kit (Marketplace prerelease)

Usually no AzDO download needed — install the prerelease build straight from the Marketplace:

```bash
code --install-extension ms-dotnettools.csdevkit@<version> --pre-release --force
```

Only fetch a Dev Kit VSIX from a build if the user needs a specific unpublished one.

## .NET MAUI Dev Kit (devdiv, auth required)

VSIX file name: `dotnet-maui-{darwin|win32|linux}-{arm64|x64}-{version}.vsix`, at the **root** of
the `VSIX` artifact in a **devdiv/DevDiv** build. Needs an `az` token — pass `-RequireAuth`:

```bash
pwsh scripts/Get-AzdoArtifact.ps1 -Organization devdiv -Project DevDiv -BuildId <mauiVsixBuild> `
    -ArtifactName VSIX -List -Filter '*dotnet-maui-darwin-arm64*'          # discover version

pwsh scripts/Get-AzdoArtifact.ps1 -Organization devdiv -Project DevDiv -BuildId <mauiVsixBuild> `
    -ArtifactName VSIX -SubPath 'dotnet-maui-darwin-arm64-<version>.vsix' `
    -Destination /tmp -RequireAuth
code --install-extension /tmp/dotnet-maui-darwin-arm64-<version>.vsix --force
```

Requires `az login` **in the Microsoft tenant** — `devdiv` is internal, so this VSIX has no public
equivalent. If `az` is missing or unauthenticated, install it and sign in
([prerequisites.md](prerequisites.md)).

If the user simply **isn't Microsoft-internal**, stop here instead of looping on auth — `devdiv`
access can't be granted to them. Offer instead:

- the Marketplace prerelease — `code --install-extension ms-dotnettools.dotnet-maui --pre-release`
- a `.vsix` they already have → `code --install-extension <path>`

The C# and C# Dev Kit VSIXes above come from `dnceng-public` and remain available either way, so
only this one step degrades.

## Finding the VSIX build ids

- Ask the user, or take them from the release/PR you're dogfooding.
- The C# VSIX build is a `dnceng-public` run of the C# extension pipeline; the MAUI VSIX build is
  a `devdiv` run. Both the build id **and** the version string change every PR build — always
  `-List` first to read the current version rather than assuming a pinned one.

## Order of operations

Install **C# → C# Dev Kit → .NET MAUI Dev Kit** (MAUI Dev Kit depends on the other two). Then
apply the machine/user VS Code settings from [project-properties.md](project-properties.md).

## Stop signals

- Install the **one** VSIX per extension matching this OS/arch — not the whole matrix.
- If `-List` shows the expected file, stop probing other artifacts/channels.
- Don't reinstall an extension that `code --list-extensions --show-versions` shows at the target
  version already.
