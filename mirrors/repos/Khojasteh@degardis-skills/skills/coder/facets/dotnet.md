---
title: .NET
category: Runtime and platform
x-claim-provenance:
- claim: The CLI searches for global.json from the current working directory and MSBuild's SDK resolver from the solution or project directory, both upward through ancestors; without global.json the highest installed SDK is used; a specified version without rollForward uses the patch policy; the documentation recommends rollForward disable when package lock files are used.
  source: https://learn.microsoft.com/en-us/dotnet/core/tools/global-json
  scope: .NET Core 3.1 SDK and later; page dated 2026-03-05.
- claim: Under central package management a PackageReference takes its version from the nearest Directory.Packages.props, VersionOverride takes precedence, and transitive pinning promotes a transitive package to an explicit dependency in a packed library.
  source: https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management
- claim: Trim warnings indicate code that may change behavior or crash after trimming, a trimmed app should produce no trim warnings, and pragma or SuppressMessage suppressions are not seen by the trimmer.
  source: https://learn.microsoft.com/en-us/dotnet/core/deploying/trimming/fixing-warnings
- claim: AnalysisLevel defaults to latest, so upgrading the .NET SDK brings its latest code-analysis rules and default severities unless AnalysisLevel is pinned.
  source: https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/overview
---

.NET build behavior comes from the evaluated project, not the project file's text. The SDK that builds it is selected by the nearest `global.json`, which the CLI searches for upward from the working directory and MSBuild upward from the solution or project directory. Without one, the highest installed SDK is used, and a pinned version without a `rollForward` policy rolls forward only to later patches; the SDK documentation recommends an exact match when package lock files are in use, so the SDK and the dependency graph stay in lockstep. The target-framework set, runtime identifiers, workloads, lock or restore policy, build properties, and deployment mode decide the rest.

Under central package management a `PackageReference` takes its version from the nearest `Directory.Packages.props`, a `VersionOverride` on the reference takes precedence, and transitive pinning can promote a transitive package to a direct dependency, which a packed library then declares to its own consumers. Where the version of a package comes from is therefore a property of the repository layout, not of the project that references it.

Compatibility is several separate claims — compile-time, runtime, binary, reflection, serialization, trimming or ahead-of-time compilation, native interop, and cross-target — and a reference assembly and a runtime implementation prove different things. Trimming removes code that static analysis does not see being used, so reflection-based code can change behavior or crash once trimmed. A trimmed app is expected to produce no trim warnings, and `#pragma warning disable` or `SuppressMessage` does not silence them, because the trimmer reads compiled assemblies.

New diagnostics after an SDK or package move need interpretation. `AnalysisLevel` defaults to `latest`, so a newer SDK can enable new code-analysis rules and change default severities with no code change, so such warnings are not by themselves evidence of a defect in the changed code, while diagnostics caused by a moved dependency's changed annotations are part of that move's compatibility surface.

The evaluated project and its generated assets include:

- restore graphs and compile versus runtime asset selection
- reference versus implementation assemblies, analyzers, and source generators
- binding redirects where applicable and conditional target branches

Behavior also travels outside ordinary call paths, through public metadata, attributes, reflection names, serializers, dependency injection, configuration binding, native libraries, COM, dynamic loading, single-file extraction, trimming roots, and runtime-generated code. Targets and package ownership are set indirectly through central props and targets, SDK imports, package sources, global SDK pins, workload and runtime configuration, publish profiles, and downstream assemblies.

Build and runtime evidence comes from the repository's configured restore, build, test, and publish path for each affected target, runtime identifier, and deployment combination, not from a locally installed default SDK. Emitted assemblies, dependency manifests, publish output, and consumer builds settle public metadata, serialization shape, native loading, trimming, or cross-language behavior that source compilation cannot, and runtime evidence comes from the produced artifact in its intended environment, including the startup, reflection, serialization, interop, globalization, and deployment boundaries the change touches.
