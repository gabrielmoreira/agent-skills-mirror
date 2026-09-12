# MSIX packaging and bundling troubleshooting

Use this for a .NET desktop application's MSIX build or bundle failure, not as
permission to install a package, change signing policy, or publish to the Store.
Record the project type, .NET/Windows App SDK versions, selected MSBuild and
Windows SDK, architecture, RID, and failing target/task first. Keep a binary log
local and review it before sharing; logs can contain paths and configuration.

## Diagnose the specific failing boundary

| Symptom | Check and scoped remedy |
|---|---|
| DesktopBridge or single-project MSIX packaging targets/tasks cannot load under `dotnet build` or `dotnet msbuild` | Use compatible **Visual Studio MSBuild** with the packaging workload/SDK installed. The .NET-hosted MSBuild and VS MSBuild are not interchangeable for these tasks. A non-packaging build may still support `dotnet build`. |
| `RuntimeIdentifier is required for native compilation` | Supply the intended `RuntimeIdentifier`, such as `win-x64`, consistently at restore and build. Align it with `Platform` and package payload architecture. Do not infer architecture from the host when cross-compiling. |
| A single-architecture build tries to restore foreign-architecture runtime packs | Inspect `RuntimeIdentifiers` as well as `RuntimeIdentifier`. For that one packaging invocation, constrain both to the intended RID; do not permanently delete the project's supported architectures. Missing packs still require a valid cache or authorized feed access. |
| `NETSDK1102: Optimizing assemblies for size is not supported for the selected publish configuration` | Inspect evaluated `SelfContained`, `PublishTrimmed`, `PublishAot`, and the actual target path. Trimming requires a supported self-contained publish. Some on-build packaging paths conflict with publish-oriented settings. A scoped `PublishTrimmed=false`/`PublishAot=false` build can diagnose that boundary, but changes the delivered artifact and is not a general Native AOT fix. |
| `'vswhere.exe' is not recognized` (sometimes surfaced through a native build exit such as `123`) | Inspect the command that actually failed. Some SDK/native-tool discovery paths invoke `vswhere` through PATH. Resolve the VS Installer directory and expose it only in the intended build shell; retain the selected toolchain. Do not assume every Native AOT version takes that path or that exit `123` alone identifies it. |
| `package with architecture already added` while bundling | Enumerate the input tree. `makeappx bundle /d` includes subfolders, so nested build outputs can contribute duplicate architecture packages. Use a new staging directory containing only selected payloads, or an explicit mapping file. |
| `0x80080215 - Non appx extensions are not allowed for payload packages targeting older platforms` | Inspect the **generated package manifest's** minimum target platform, not only the source project property. For this extension-compatibility failure, stage the payloads with `.appx` names before bundling. Do not raise the supported OS minimum or use `/nv` merely to bypass validation. |

Messages above are diagnostic search terms; wording and failing target vary by
SDK. A symptom is not proof of its cause. `.appx` and `.msix` are supported
package extensions, but changing a filename does not retarget binaries, repair
invalid content, establish runtime compatibility, or replace signing.

## Find a compatible Visual Studio MSBuild

This discovery-only PowerShell example prefers the latest installed non-preview
VS instance containing MSBuild. A repository pin may require a different
`vswhere` version filter. Include Build Tools instances with `-products '*'`.

```powershell
$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
if (-not (Test-Path -LiteralPath $vswhere -PathType Leaf)) {
    throw 'Install or locate the supported Visual Studio Installer discovery tool.'
}
$candidates = @(& $vswhere -latest -products '*' -requires Microsoft.Component.MSBuild `
    -find 'MSBuild\**\Bin\MSBuild.exe')
if ($LASTEXITCODE -ne 0 -or $candidates.Count -eq 0) {
    throw 'No matching Visual Studio MSBuild found.'
}
$msbuild = $candidates | Select-Object -First 1
if (-not (Test-Path -LiteralPath $msbuild -PathType Leaf)) {
    throw 'The discovered MSBuild path is unavailable.'
}
```

Finding MSBuild does not prove the Windows packaging workload, C++ tools, target
SDK or runtime packs are installed. Check those for the actual .NET/WinAppSDK
versions. If a native discovery command needs the Installer directory on PATH,
add it to that build shell only and restore the caller's environment afterward;
do not globally rewrite PATH or switch an already-loaded toolchain in place.

## Scope an individual packaging build

After setting `$msbuild` above, this **illustrative invocation** targets an
existing fictional single-project MSIX app. Substitute the real project and
supported platform/RID pair; it is not a buildable sample application:

```powershell
$project = '.\src\ExampleApp\ExampleApp.csproj'
if (-not (Test-Path -LiteralPath $project -PathType Leaf)) {
    throw 'Select the existing single-project MSIX application.'
}
$buildArgs = @(
    $project, '/restore', '/t:Build', '/p:Configuration=Release',
    '/p:Platform=x64', '/p:RuntimeIdentifier=win-x64',
    '/p:RuntimeIdentifiers=win-x64', '/p:GenerateAppxPackageOnBuild=true',
    '/p:AppxBundle=Never'
)
& $msbuild @buildArgs
if ($LASTEXITCODE -ne 0) { throw "Packaging build failed: $LASTEXITCODE" }
```

Do not set one fixed RID on a solution-wide multi-architecture bundle build.
Build each intended architecture in its supported environment/output directory.
For the specific `NETSDK1102` diagnostic experiment, append
`/p:PublishAot=false` and `/p:PublishTrimmed=false` only if a non-AOT,
non-trimmed artifact is acceptable. Keep this separate from the intended AOT
release path and exercise the resulting application before accepting the change.

An x64+arm64 bundle needs both builds' dependencies available. If the foreign
runtime pack cannot be restored in an offline or restricted environment, produce
the supported single-architecture artifact there and assemble the multi-arch
bundle in an environment with both validated packages. Do not label an x64-only
package as an arm64 or multi-architecture artifact.

## Stage precisely the intended bundle

1. Create a **new, empty, user-owned** staging directory. Never clean a shared
   build-output tree with an indiscriminate recursive delete.
2. Copy only the chosen packages, one application payload per intended
   architecture, with matching package identity/publisher and appropriate
   versions/resources. Keep duplicate copies and old bundles out of the tree.
3. If the older-platform extension error above occurs, use `.appx` destination
   names for those copied payloads; preserve originals and package bytes.
4. Run the Windows SDK's resolved `makeappx.exe` with validation enabled and
   no-overwrite behavior, e.g. `makeappx bundle /d <staging> /p <output> /no`.
   Substitute actual paths as separate shell arguments and put output outside
   the staging tree. Use `/bv` for an explicit four-part bundle version if
   reproducible release versioning is required.
5. Check exit status, then inspect the generated bundle manifest and selected
   payloads. A successful bundle does not prove installation or launch; exercise
   each supported architecture/OS/signing path on an authorized test machine.

## Evidence and verification

| Case | Evidence that distinguishes a fix from a workaround |
|---|---|
| Wrong build engine | The failing packaging task runs under the compatible VS MSBuild, not just a renamed executable. |
| Restore scope mismatch | Restore/build logs agree on the target RID and no unwanted runtime-pack requests remain. |
| Publish-property conflict | The intended JIT/AOT, self-contained and trimming behavior is documented and preserved or deliberately changed. |
| Nested duplicate payloads | The staging inventory and bundle manifest contain exactly the intended architectures. |
| Older-platform extension rejection | The same package bytes with supported names bundle without disabling semantic validation; supported-OS installation is still exercised separately. |

References: [WinUI 3 CI builds](https://learn.microsoft.com/windows/apps/package-and-deploy/ci-for-winui3),
[vswhere MSBuild discovery](https://github.com/microsoft/vswhere/wiki/Find-MSBuild),
[trimming self-contained apps](https://learn.microsoft.com/dotnet/core/deploying/trimming/trim-self-contained),
[MakeAppx](https://learn.microsoft.com/windows/msix/package/create-app-package-with-makeappx-tool),
and [MSIX bundle overview](https://learn.microsoft.com/windows/msix/package/bundling-overview).
The installed `makeappx bundle /?` is authoritative for that SDK's options.
