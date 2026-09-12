---
name: azure-pipelines-powershell
description: Author and review Azure Pipelines YAML that runs PowerShell safely, with correct expression phases, publication conditions, project-owned package versions, and no-network tests. Use when pipeline template expressions, macro/runtime variables, PowerShell quoting, package prereleases, or publish gates are involved.
---

Apply this guidance when authoring or reviewing Azure Pipelines YAML that runs
PowerShell, packs a project, or conditionally publishes output.

# Azure Pipelines PowerShell

## Keep the four evaluation languages separate

The same YAML can cross several evaluators. Identify the owner and time of every
substitution before changing quotes:

| Syntax | Evaluator and phase | Appropriate use |
|---|---|---|
| `${{ parameters.name }}` / `${{ variables.name }}` | Template expansion, before the run graph is finalized | Typed template parameters and compile-time structure |
| `$(name)` | Azure Pipelines macro expansion before a task runs | Task inputs and environment mappings |
| `$[ expression ]` | Azure Pipelines runtime expression | A complete variable value or runtime condition input |
| `$name`, `${name}`, `$env:NAME`, `$()` | PowerShell, after the task starts | PowerShell variables, environment values, and subexpressions |

`${parameters.name}` is a PowerShell braced variable, **not** an Azure template
parameter. Conversely, `$(Build.SourceBranch)` inside inline PowerShell is
rewritten by Azure before PowerShell parses the script. PowerShell quoting does
not create a trustworthy security boundary around Azure substitutions.

Template expansion cannot consume values that exist only after an agent starts,
including step output created during the run. Predefined variables also have
individual template-availability rules. Put branch, reason, dependency result,
and late output decisions in runtime `condition` expressions unless the value is
explicitly documented as available during template expansion.

Runtime `$[ ]` expressions must occupy the entire scalar value; do not embed one
inside a longer string:

```yaml
variables:
  isMain: $[eq(variables['Build.SourceBranch'], 'refs/heads/main')]
```

## Bind values; do not generate PowerShell source

Do not splice queue-time variables, branch names, commit messages, or other
untrusted pipeline values into inline PowerShell:

```yaml
# Avoid: the expanded value becomes PowerShell source code.
- pwsh: Write-Host 'Branch is $(Build.SourceBranch)'
```

Map runtime values through `env`, then validate and convert them inside
PowerShell. Use typed template parameters with an allowlist for trusted
configuration choices:

```yaml
parameters:
- name: configuration
  type: string
  default: Release
  values:
  - Debug
  - Release

steps:
- task: PowerShell@2
  inputs:
    targetType: inline
    pwsh: true
    script: |
      Set-StrictMode -Version 3.0
      $ErrorActionPreference = 'Stop'

      [long]$buildId = 0
      if (-not [long]::TryParse($env:PIPELINE_BUILD_ID, [ref]$buildId) -or $buildId -lt 1) {
          throw 'PIPELINE_BUILD_ID must be a positive integer.'
      }

      Write-Host "Building branch '$env:PIPELINE_SOURCE_BRANCH' as run $buildId."
  env:
    PIPELINE_BUILD_ID: $(Build.BuildId)
    PIPELINE_SOURCE_BRANCH: $(Build.SourceBranch)
    BUILD_CONFIGURATION: ${{ parameters.configuration }}
```

Secrets follow the same rule: map an Azure secret to an environment variable
for the one task that needs it. Never print it, place it in command text, or
enable credential persistence or broader job authorization as a shortcut.

## Gate every external publication explicitly

A custom `condition` replaces the default success check. A branch-only condition
can therefore run after failure or cancellation. A publication condition should
name all three intended facts:

```yaml
condition: >-
  and(succeeded(),
      eq(variables['Build.SourceBranch'], 'refs/heads/main'),
      ne(variables['Build.Reason'], 'PullRequest'))
```

- `succeeded()` preserves the successful-dependency requirement and is false
  when the relevant dependency is failed or canceled.
- `succeeded()` can include partially successful outcomes. Do not mark a failed
  test or packaging prerequisite `continueOnError` and assume this condition
  enforces stricter success. If warning/partial outcomes must block release,
  enforce that policy explicitly at the relevant dependency boundary.
- Compare the full ref, `refs/heads/main`, not `main`.
- Keep the non-PR check even though Azure Repos PR validation commonly uses a
  synthetic ref such as `refs/pull/123/merge`; the reason check documents and
  enforces the publication boundary.
- Do not use `Build.SourceBranchName` to infer the PR target. A synthetic PR ref
  can have `merge` as its final segment.
- `succeededOrFailed()` permits publication after failure, and `always()` can run
  after cancellation. Neither is appropriate for package publication.
- A child cannot run when its parent stage or job is skipped, even if the
  child's condition would otherwise be true.

Conditions are evaluated before their stage, job, or step starts. A variable set
inside a unit cannot affect that same unit's condition. Move the decision to an
earlier step/job and use the documented output-variable context when necessary.

## Let the project own the package version

Keep the stable version in the project or package manifest:

```xml
<PropertyGroup>
  <VersionPrefix>2.4.0</VersionPrefix>
</PropertyGroup>
```

Set task automatic versioning to `off`. The pipeline may supply a validated
prerelease suffix for nonrelease builds, but it should not replace the project's
stable version with a date, counter, or build number. This keeps local and CI
packs consistent.
For .NET projects, `VersionSuffix` composes with `VersionPrefix`; an explicitly
set `Version` can override that composition. Inspect the produced package's
version rather than assuming a suffix property changed its identity.

NuGet and PowerShell module packages have different constraints:

- Modern NuGet supports SemVer 2 versions such as `2.4.0-preview.12+sha.abcdef0`.
  Dot-separated prerelease labels and build metadata require SemVer 2-capable
  clients. NuGet normalization removes build metadata for version matching, so
  metadata is not a unique package identity.
- A broadly compatible NuGet suffix such as `pr123` avoids SemVer 2-only dot
  syntax. Confirm the destination repository and oldest supported client before
  choosing a richer suffix.
- PowerShellGet module prereleases keep a three-integer `ModuleVersion` and put
  an ASCII alphanumeric/hyphen label in
  `PrivateData.PSData.Prerelease`. That label does not support `.` or `+`.
  Do not pass an SDK-style `VersionSuffix` pattern into a module manifest.

## Complete build, pack, and artifact gate

After copying `examples\PackageVersion.ps1` to
`eng\PackageVersion.ps1` in the consuming repository, this fragment is complete
for an existing fictional `Fabrikam.Tools` project and test project. It performs
no registry or feed write. Automatic test-result publication is disabled here
so the final task is the only publication step shown. The referenced project
files are prerequisites, not files generated by this example.

```yaml
parameters:
- name: configuration
  type: string
  default: Release
  values: [Debug, Release]

steps:
- task: DotNetCoreCLI@2
  displayName: Test
  inputs:
    command: test
    publishTestResults: false
    projects: tests/Fabrikam.Tools.Tests/Fabrikam.Tools.Tests.csproj
    arguments: --configuration ${{ parameters.configuration }}

- task: PowerShell@2
  displayName: Select package suffix
  inputs:
    targetType: inline
    pwsh: true
    script: |
      Set-StrictMode -Version 3.0
      $ErrorActionPreference = 'Stop'
      . (Join-Path $env:BUILD_SOURCESDIRECTORY 'eng\PackageVersion.ps1')

      [long]$buildId = 0
      if (-not [long]::TryParse($env:PIPELINE_BUILD_ID, [ref]$buildId)) {
          throw 'PIPELINE_BUILD_ID must be an integer.'
      }

      $channel = Get-PackageChannel `
          -BuildReason $env:PIPELINE_BUILD_REASON `
          -SourceBranch $env:PIPELINE_SOURCE_BRANCH
      $suffix = New-PackageVersionSuffix -Channel $channel -BuildId $buildId
      Write-Host "##vso[task.setvariable variable=PackageVersionSuffix]$suffix"
  env:
    PIPELINE_BUILD_ID: $(Build.BuildId)
    PIPELINE_BUILD_REASON: $(Build.Reason)
    PIPELINE_SOURCE_BRANCH: $(Build.SourceBranch)

- task: DotNetCoreCLI@2
  displayName: Pack
  inputs:
    command: pack
    packagesToPack: src/Fabrikam.Tools/Fabrikam.Tools.csproj
    configuration: ${{ parameters.configuration }}
    packDirectory: $(Build.ArtifactStagingDirectory)/packages
    versioningScheme: off
    buildProperties: VersionSuffix=$(PackageVersionSuffix)

- task: PublishPipelineArtifact@1
  displayName: Publish release package artifact
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'), ne(variables['Build.Reason'], 'PullRequest'))
  inputs:
    targetPath: $(Build.ArtifactStagingDirectory)/packages
    artifact: Fabrikam.Tools-packages
```

If a repository later adds a registry push, keep it in a separate task with the
same condition. Do not hide network writes inside the version helper or its
tests.

## Test the deterministic boundary locally

Run the included no-network cases without assuming Pester is installed:

```powershell
pwsh -NoProfile -File .github/plugin/shmuelie-devenv/skills/azure-pipelines-powershell/examples/Test-PackageVersion.ps1
pwsh -NoProfile -File scripts/Test-Marketplace.ps1
```

These tests prove the PowerShell channel and suffix transformations only. They
do **not** prove Azure DevOps template expansion, macro substitution, runtime
conditions, hosted-agent behavior, or remote service permissions. Validate
those boundaries in a nonpublishing pipeline before enabling a real write.

## Public references

- [Define variables](https://learn.microsoft.com/azure/devops/pipelines/process/variables?view=azure-devops)
- [Expressions](https://learn.microsoft.com/azure/devops/pipelines/process/expressions?view=azure-devops)
- [Pipeline conditions](https://learn.microsoft.com/azure/devops/pipelines/process/conditions?view=azure-devops)
- [Predefined variables](https://learn.microsoft.com/azure/devops/pipelines/build/variables?view=azure-devops)
- [DotNetCoreCLI@2 pack inputs](https://learn.microsoft.com/azure/devops/pipelines/tasks/reference/dotnet-core-cli-v2?view=azure-pipelines)
- [NuGet package versioning](https://learn.microsoft.com/nuget/concepts/package-versioning)
- [PowerShell prerelease module versions](https://learn.microsoft.com/powershell/gallery/concepts/module-prerelease-support?view=powershellget-3.x)
