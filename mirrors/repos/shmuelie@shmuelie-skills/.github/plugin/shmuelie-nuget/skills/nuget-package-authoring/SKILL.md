---
name: nuget-package-authoring
description: "Author and inspect NuGet library packages: metadata, package assets, dependencies, XML docs, Source Link, portable symbols, and clean consumption. Use for dotnet pack and package layout problems, not permission to publish."
---

# NuGet library package authoring

Use an SDK-style library with the intended target frameworks. Inspect the
effective build properties and produced package, not just one project file.
Shared imports, configuration, and `PackageVersion` overrides can change output.

```powershell
dotnet msbuild .\src\Library\Library.csproj -nologo -p:Configuration=Release -getProperty:PackageId,PackageVersion,TargetFrameworks
dotnet pack .\src\Library\Library.csproj -c Release -o .\artifacts -p:ContinuousIntegrationBuild=true
```

## Metadata and assets

Set package ID/version, description, author, the chosen license expression/file,
README, repository URL/type, XML documentation, and optional icon. Include the
actual README/license/icon files with correct `Pack` and `PackagePath` metadata.
Do not invent a license for a consuming repository.

Use portable PDBs and `SymbolPackageFormat=snupkg` with `IncludeSymbols=true`
where symbols are intended. SDK-provided Source Link support requires correct
Git remote/source metadata; verify source URLs and commit information. A PDB's
existence alone does not prove source retrieval works.

Inspect the `.nuspec`, `lib/<tfm>/` and any `ref/`, `runtimes/`, `build/`, or
`analyzers/` assets that the package actually needs. Do not include test binaries,
secrets, checkout paths, unrelated output, or a platform-specific runtime by
accident. XML docs should accompany the public assembly.

## Dependency exposure

- Normal library dependencies generally flow to consumers. `PrivateAssets=all`
  is appropriate for build/test/analyzer tooling only when consumers do not
  require those assets.
- Do not hide a runtime dependency merely to make the dependency list smaller.
- `ExcludeAssets=runtime` is a special host/plugin scenario, not a default for
  ordinary libraries. Prove the host supplies the excluded assembly.
- Test projects can reference libraries normally; do not copy host-specific
  exclusion settings into test projects.
- Check framework-conditional dependency groups and public types from external
  assemblies. Package compilation is not a consumer-compatibility proof.

Roslyn analyzer packaging remains in `roslyn-sourcegen`; package icons remain
in `icon-assets`. This skill covers the generic library package, not every
specialized package kind.

## Prove consumption

Copy `templates/Test-LibraryPackage.ps1` to `eng/package/` and adapt the
canonical example's `package-policy.json`. The CI and release templates both
invoke it. For each framework, declare assemblies and expected dependencies
with explicit `id`, `version`, `include`, and `exclude` strings (empty strings
mean those attributes are absent). An empty dependency list means none are
allowed, not that dependency inspection is skipped.

The policy enforces a GitHub repository/commit, README, chosen license,
author/description, framework assembly set, XML documentation, matching portable
symbols, and Source Link coverage for every non-embedded source document at the
reviewed commit. It targets pure-managed `lib/<tfm>` packages. It does
not silently accept extra native, reference, or analyzer assembly layouts;
adapt and review the inspector for specialized package types.

Use the single [canonical example](../dotnet-library-projects/examples/README.md).
Restore its console consumer from the just-produced local feed into an empty
cache, with an exact package version and no project reference. Inspect
`project.assets.json` and execute it; a previously cached or public package must
not satisfy the smoke test.

The example has no runtime package dependencies, so the consumer needs only the
local feed. For a real library with transitive packages, use NuGet package-source
mapping so the library ID maps only to the local feed and dependencies map to
approved feeds. Do not add a public feed that can silently substitute the
library under test.

Inspect symbols and Source Link separately; never claim a successful pack proves
NuGet.org symbol ingestion. Use `nuget-release` only when publication is requested.

`examples/Test-PackageInspection.ps1` takes the built canonical archives and
checks controlled corruptions (missing metadata/docs/symbols, source mismatch,
unexpected dependencies/frameworks, and absent Source Link). The canonical
fixture invokes it automatically; it never contacts a feed.

References: [package creation](https://learn.microsoft.com/nuget/create-packages/creating-a-package-dotnet-cli),
[Source Link](https://learn.microsoft.com/dotnet/standard/library-guidance/sourcelink),
[symbols](https://learn.microsoft.com/nuget/create-packages/symbol-packages-snupkg).
