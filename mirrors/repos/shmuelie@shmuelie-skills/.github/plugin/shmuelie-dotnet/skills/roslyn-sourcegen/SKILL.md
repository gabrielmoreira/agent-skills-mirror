---
name: roslyn-sourcegen
description: Roslyn incremental source generators, IIncrementalGenerator pipeline design, equatable models, testing patterns, analyzer diagnostics, and NuGet packaging
---

When working on C# Roslyn source generators or analyzers, apply this domain knowledge.

# Roslyn Source Generators — Domain Knowledge

## IIncrementalGenerator (preferred over ISourceGenerator)
- Always implement `IIncrementalGenerator`, never the legacy `ISourceGenerator`.
- Entry point is `Initialize(IncrementalGeneratorInitializationContext context)`.
- Use `ForAttributeWithMetadataName<T>` to find types decorated with a specific attribute —
  this is the most efficient filter and avoids scanning all syntax nodes.
- Structure the pipeline: extraction (parsing) in `Select`/`SelectMany`, emission in
  `RegisterSourceOutput` or `RegisterImplementationSourceOutput`.
- `RegisterImplementationSourceOutput` is preferred when the generated code doesn't affect
  the public API — it allows the IDE to skip re-running the generator on every keystroke.

## Equatable Pipeline Models (critical for performance)
- All model types flowing through the pipeline **must** implement structural equality.
- Use `sealed record` types for all pipeline models.
- For collections, wrap `ImmutableArray<T>` in an `EquatableArray<T>` that implements
  `IEquatable<EquatableArray<T>>` using `SequenceEqual`. This is the Roslyn cookbook's
  #1 recommendation for collection-bearing models.
- Without equatable models, the generator re-runs on every keystroke, destroying IDE
  performance.

## CancellationToken Propagation
- All parsing/extraction methods must accept and periodically check `CancellationToken`.
- The token comes from `SourceProductionContext.CancellationToken` or the transform's
  cancellation token parameter.
- Long-running parsing (e.g., WSDL/XSD files) should check cancellation between major steps.

## Project Structure
- Target `netstandard2.0` — Roslyn hosts require this.
- Set `<EnforceExtendedAnalyzerRules>true</EnforceExtendedAnalyzerRules>` in the csproj.
- Reference `Microsoft.CodeAnalysis.CSharp` with `PrivateAssets="all"`.
- Use [PolySharp](https://github.com/Sergio0694/PolySharp) for polyfills (`IsExternalInit`,
  `RequiredMemberAttribute`, `CompilerFeatureRequiredAttribute`, etc.) when using modern
  C# features in netstandard2.0.
- Separate concerns into distinct projects:
  - **Attributes/Metadata** project (netstandard2.0) — marker attributes consumers reference.
  - **Analyzer** project (netstandard2.0) — diagnostics and code fixes.
  - **Source Generator** project (netstandard2.0) — the `IIncrementalGenerator`.
  - **Tests** project (net8.0+) — unit tests using `CSharpGeneratorDriver`.
- Centralize `DiagnosticDescriptor` declarations in a dedicated static class (e.g., `DiagnosticRules`
  or `MyGeneratorDiagnostics`), following the CsWinRT `WinRTRules` pattern.

## NuGet Packaging
- The attributes project is the package consumers reference.
- Bundle the analyzer/generator DLL into the NuGet package:
  ```xml
  <None Include="..\MyGenerator\bin\$(Configuration)\netstandard2.0\MyGenerator.dll"
        PackagePath="analyzers\dotnet\cs" Pack="true" Visible="false" />
  ```
- Add MSBuild `.targets` files under `build\` and `buildTransitive\` for any MSBuild properties
  the generator needs:
  ```xml
  <None Include="My.targets" PackagePath="buildTransitive\netstandard2.0" Pack="true" />
  <None Include="My.targets" PackagePath="build\netstandard2.0" Pack="true" />
  ```
- Set `ReferenceOutputAssembly="false"` on the `ProjectReference` to the analyzer project
  so consumers don't get a runtime dependency.

## Reading Additional Files
- Use `context.AdditionalTextsProvider` to access files added via `<AdditionalFiles Include="..." />`.
- Filter by extension: `.Where(f => Path.GetExtension(f.Path).Equals(".wsdl", ...))`.
- Access MSBuild properties via `context.AnalyzerConfigOptionsProvider` and
  `GlobalOptions.TryGetValue("build_property.PropertyName", out var value)`.
- Extract MSBuild property access into extension methods (a `ConfigHelper` pattern).

## Testing Source Generators
- Use `CSharpGeneratorDriver.Create(new MyGenerator())` to run the generator in tests.
- Two-stage compilation pattern:
  1. Compile input source into a `CSharpCompilation`.
  2. Run the generator driver against the compilation.
  3. Assert on the generated `SyntaxTree` outputs.
- Reference `Basic.Reference.Assemblies.Net80` (or appropriate version) for framework
  metadata references in tests.
- Use `Microsoft.CodeAnalysis.CSharp.Analyzer.Testing.MSTest` for analyzer/code fix tests.
- Test pattern:
  ```csharp
  GeneratorDriver driver = CSharpGeneratorDriver.Create(new MyGenerator())
      .WithUpdatedParseOptions(parseOptions);
  driver.RunGeneratorsAndUpdateCompilation(compilation,
      out Compilation output, out ImmutableArray<Diagnostic> diagnostics);
  // Assert diagnostics.IsEmpty
  // Assert on output.SyntaxTrees
  ```
- Use `<ASSEMBLY_VERSION>` placeholders in expected output for `GeneratedCodeAttribute`
  version strings, replaced dynamically in the test harness.

## Analyzer Patterns
- Use `[DiagnosticAnalyzer(LanguageNames.CSharp)]` with `RegisterSymbolAction` or
  `RegisterSyntaxNodeAction`.
- Common diagnostic categories for source generators:
  - **Error**: unsupported constructs (e.g., generic types when not supported).
  - **Warning**: annotations that have no effect (e.g., attribute on non-public member).
  - **Info**: unnecessary annotations (e.g., `[Version(1)]` when 1 is the default).
- Always provide a code fix companion where possible.

## Handling Nested Types
- When generating code for nested types, wrap generated output in `partial` containing
  type declarations matching the nesting hierarchy:
  ```csharp
  partial class Outer
  {
      partial class Inner
      {
          public interface IInner { ... }
          partial class Target : IInner { }
      }
  }
  ```
- Walk `ContainingType` chain to build the nesting stack.

## Common Pitfalls
- **String escaping in generated code**: use `SyntaxFactory.Literal()` or `SymbolDisplay`
  for safe identifier/string emission.
- **Accessibility filtering**: always check `member.DeclaredAccessibility` — don't assume
  all members should be processed.
- **Parameter modifiers**: preserve `ref`, `out`, `in`, `params` in generated method
  signatures — these are silently dropped if not explicitly handled.
- **Async return types**: handle `Task`, `Task<T>`, `ValueTask<T>` correctly in generated
  code.
- **File-scoped namespaces**: support both block-scoped and file-scoped namespace
  declarations in input source.
