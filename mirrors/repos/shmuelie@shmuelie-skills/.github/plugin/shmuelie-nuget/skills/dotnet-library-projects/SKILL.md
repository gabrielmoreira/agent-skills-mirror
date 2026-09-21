---
name: dotnet-library-projects
description: "Create and evolve SDK-style .NET library projects with explicit API, compatibility, framework, and test/consumer boundaries. Use for reusable libraries rather than application scaffolding or NuGet publication."
---

# .NET library projects

Decide the consumer contract before choosing frameworks. Identify supported
runtimes/platforms, public API and compatibility requirements, dependencies,
threading/lifetime rules, and whether trimming/AOT support is actually required.
Do not turn a cross-platform library into `net*-windows` by copying an app's
shared properties.

## Layout and ownership

```text
global.json
Directory.Build.props
src/Library/Library.csproj
tests/Library.Tests/Library.Tests.csproj
consumer/Consumer/Consumer.csproj
CHANGELOG.md
```

Use SDK-style projects and a released pinned SDK. Keep nullable/implicit-usings
and analyzer policy explicit, but do not require preview language features.
Shared settings belong in `Directory.Build.props`; use evaluation-order-aware
conditions rather than reading an unset project TFM too early.

Tests may use a project reference. A package-consumer smoke test must instead
use an exact `PackageReference` to the freshly packed library. Otherwise it
cannot detect missing assets or incorrect dependency metadata.

Use existing test conventions and a consistent runner. A .NET 10 `global.json`
MTP selection requires MTP-compatible test projects; a VSTest adapter alone does
not make a project compatible. The example uses the SDK-scaffolded MSTest
package and the default `dotnet test <project>` invocation, without forcing MTP.

## Public contract

- Prefer a small documented API over exposing implementation types.
- Document nullability, error behavior, cancellation, disposal/ownership, and
  concurrency where relevant. Validate inputs at the appropriate boundary.
- Treat changed signatures, public nullability, target-framework removal,
  serialized shapes, and observable behavior as compatibility decisions.
- Do not claim trimming/AOT support based on `IsAotCompatible` alone: publish
  and execute an actual consumer for each advertised mode/RID.
- Multi-target only for a supported consumer requirement, not as an automatic
  checklist. Keep platform-specific assets and dependencies conditional.

General repository/application setup stays in `dotnet-project-init`.
Use `nuget-package-authoring` for package layout and `nuget-release` for release
procedure. These are separable tasks, not authority to publish a new project.

## Canonical example

The [example](examples/README.md) contains one pure-managed `net10.0` library
with checked integer addition, tests, and a package consumer. It is intentionally
small enough that failures in project/packaging wiring are visible.

```powershell
pwsh -NoProfile -File .\examples\Test-Fixture.ps1 -ScratchRoot $env:TEMP
```

The fixture never installs a global SDK, edits the caller's Git configuration,
or publishes. It creates a synthetic local Git repo with a fictional remote
for build provenance, restores dependencies, and uses a unique scratch child.
Do not infer compatibility with older frameworks, Windows-specific libraries,
or Native AOT from this `net10.0` example.

When adopting it, choose the real package identity, author/license, repository,
API, version, and consumer requirements. Do not publish the fictional fixture.
