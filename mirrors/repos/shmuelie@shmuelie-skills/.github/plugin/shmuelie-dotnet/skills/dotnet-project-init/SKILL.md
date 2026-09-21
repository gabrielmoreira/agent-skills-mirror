---
name: dotnet-project-init
description: General .NET repository and application setup, Directory.Build.props, test runners, solution formats, CI, and project instructions
---

When working on projects related to .net project initialization, apply this domain knowledge.

# .NET Project Initialization — Domain Knowledge

## Directory.Build.props (Centralized Build Config)
- Place at repo root to share settings across all projects.
- Common properties to centralize:
  ```xml
  <Project>
    <PropertyGroup>
      <TargetFramework>net10.0-windows</TargetFramework>
      <Nullable>enable</Nullable>
      <ImplicitUsings>enable</ImplicitUsings>
      <LangVersion>preview</LangVersion>
      <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    </PropertyGroup>
  </Project>
  ```
- Use `<TargetFramework>` conditions in .targets (not .props) — they silently fail
  for single-targeting projects in .props due to evaluation order.
- For multi-platform apps (x64/ARM64), set `<Platforms>x64;ARM64</Platforms>`.
- Set `<RuntimeIdentifiers>win-x64;win-arm64</RuntimeIdentifiers>` for platform-specific builds.

## Project Configuration Patterns

### Modern .NET (10+)
- `global.json`: Include `"test": { "runner": "Microsoft.Testing.Platform" }` for .NET 10+
  test discovery with Microsoft.Testing.Platform runner.
- **MTP vs VSTest conflict**: The `global.json` MTP runner config requires the test project
  to use an MTP-compatible runner package. If using xUnit with `xunit.runner.visualstudio`
  (a VSTest adapter), you must either remove the test runner config from `global.json`
  or switch to `xunit.runner.mtp` for MTP compatibility.
- Test SDK: Use `Microsoft.NET.Test.Sdk` + MSTest/xUnit/NUnit + MTP runner package.
- For AOT-compatible projects: `<IsAotCompatible>true</IsAotCompatible>`.

### Assembly Version Access
Replace hardcoded version strings with runtime assembly metadata:
```csharp
// AOT-safe: use typeof(T).Assembly instead of Assembly.GetExecutingAssembly()
// Assembly.GetExecutingAssembly() relies on stack-frame reflection and is NOT AOT-safe
var version = typeof(MyClass).Assembly.GetName().Version;
var infoVersion = typeof(MyClass).Assembly
    .GetCustomAttribute<AssemblyInformationalVersionAttribute>()?
    .InformationalVersion;
```
This automatically reflects the `<Version>` set in the csproj.
`InformationalVersion` includes the SemVer string (e.g., `1.2.3+commit-sha`).

### WinUI 3 Projects
- SDK: `Microsoft.NET.Sdk` (not `Microsoft.NET.Sdk.WindowsDesktop`).
- TFM: `net10.0-windows10.0.22621` (or appropriate Windows SDK version).
- `<UseWinUI>true</UseWinUI>` enables WinUI 3 support.
- `<EnableMsixTooling>true</EnableMsixTooling>` for MSIX packaging.

### Solution Format Migration (.sln → .slnx)
- `dotnet sln migrate` converts a classic `.sln` to the newer XML `.slnx` format.
- The generated `.slnx` preserves solution folders, build dependencies, platform/config
  mappings, project deploy flags, and solution items.
- Validate it builds via MSBuild (which must accept `.slnx`) before deleting the old `.sln`.
- **Update CI workflows** that reference the `.sln` by name — the file name changes.

### Toolset Modernization (mixed C#/C++ solutions)
- Bumping to .NET 10 SDK often exposes stale native toolsets: a C++/WinRT project pinned to
  `PlatformToolset` **v143** can fail the full build until moved to **v145**.
- CppWinRT 3.0 changes proxy `.winmd` output — verify the metadata project still emits the
  expected proxy winmd after upgrading, since downstream WPF/UWP consumers depend on it.
- Investigate what's actually installed (`dotnet --list-sdks`, VS version, C++ toolset)
  before choosing "latest" — the environment dictates the achievable target.

### Windows Service Projects
- SDK: `Microsoft.NET.Sdk.Web` for ASP.NET-based services.
- Add `Microsoft.Extensions.Hosting.WindowsServices` for Windows service hosting.

### COM Server Projects
- `<EnableComHosting>true</EnableComHosting>` for COM server support.
- Platform-specific builds required (not AnyCPU).

## NuGet Package Patterns

Ordinary library dependencies generally flow to consumers; build/test-only tools
can be private. Do not copy specialized host/plugin dependency exclusions into
every library. Detailed package layout, dependency exposure, Source Link, and
symbols now belong to
[nuget-package-authoring](https://github.com/shmuelie/shmuelie-skills/blob/main/.github/plugin/shmuelie-nuget/skills/nuget-package-authoring/SKILL.md).

## CI Workflow Patterns (GitHub Actions)

### .NET Build + Test
```yaml
name: CI
on: [push, pull_request]
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '10.0.x'
      - run: dotnet restore
      - run: dotnet build --no-restore -c Release
      - run: dotnet test --no-build -c Release
```

### MSIX-Specific CI
- MSIX builds may require `msbuild` instead of `dotnet build`.
- Use `microsoft/setup-msbuild@v2` action.
- Build with `-p:Platform=x64` (or ARM64) — not AnyCPU.
- For tests: `dotnet test --project Tests.csproj -p:Platform=x64`.

### Multi-Platform Matrix
```yaml
strategy:
  matrix:
    platform: [x64, ARM64]
steps:
  - run: msbuild App.csproj -p:Platform=${{ matrix.platform }} -p:Configuration=Release
```

## copilot-instructions.md Pattern
- Always create `.github/copilot-instructions.md` in new repos.
- Include: build/test commands, architecture overview, key conventions, gotchas.
- Update when architecture changes significantly.

## Versioning and Changelog

Use [SemVer](https://semver.org/) and
[Keep a Changelog](https://keepachangelog.com/): keep `[Unreleased]` for ongoing
work, classify user-visible changes, and move released notes into dated sections.
Select major/minor/patch according to compatibility rather than commit count.
The detailed library procedure, templates, and publication gates belong to
[nuget-release](https://github.com/shmuelie/shmuelie-skills/blob/main/.github/plugin/shmuelie-nuget/skills/nuget-release/SKILL.md).
Application-specific build/MSIX guidance remains here.
