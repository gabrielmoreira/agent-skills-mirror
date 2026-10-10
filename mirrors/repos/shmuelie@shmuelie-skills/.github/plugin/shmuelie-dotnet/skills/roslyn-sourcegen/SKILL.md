---
name: roslyn-sourcegen
description: Roslyn incremental source generators, equatable pipelines, AdditionalFiles including Windows Message Compiler .mc catalogs, analyzer diagnostics, tests, and NuGet packaging
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

### Windows Message Compiler (`.mc`) catalogs → partial exceptions

Treat a catalog as a stateful message language, not a flat string list. The
following names, texts, options, and generated API are **invented**; the
generator contract is an example to adapt, not a built-in Roslyn feature.
Consult the [Windows message text file syntax][mc-syntax] for the MC rules.

```xml
<PropertyGroup>
  <McLanguage>English</McLanguage>
  <McInclude>DEMO_MISSING;0xC3450010</McInclude>
</PropertyGroup>
<ItemGroup>
  <AdditionalFiles Include="Messages\Sample.mc" />
  <CompilerVisibleProperty Include="McLanguage" />
  <CompilerVisibleProperty Include="McInclude" />
</ItemGroup>
```

Read `build_property.McLanguage` and `build_property.McInclude` from
`context.AnalyzerConfigOptionsProvider.GlobalOptions`. Filter
`AdditionalTextsProvider` to `.mc` (case-insensitively) and combine each
file's parsed model with the options before emission. For per-file overrides,
publish metadata with `CompilerVisibleItemMetadata` for `AdditionalFiles` and
read `build_metadata.AdditionalFiles.McLanguage` via `GetOptions(file)`; document
whether it takes precedence over the global property. Require a selected
language when the input has multiple language blocks; never silently choose
one translation. Use `RegisterSourceOutput` for generated public exception
APIs. An absent include list means *all* messages; otherwise split
on `;`, trim, and match symbolic names or **full unsigned 32-bit** codes (for
example, `0xC3450010`), not just the low 16-bit message ID. Reject unknown or
ambiguous selectors instead of silently dropping messages. Make the parser's
output and option models structurally equatable, and propagate cancellation.

```text
SeverityNames=(Success=0x0 Error=0x3)
FacilityNames=(Demo=0x345)
LanguageNames=(English=0x409:MSG00409 French=0x40c:MSG0040C)

MessageId=0x10
Severity=Error
Facility=Demo
SymbolicName=DEMO_BUSY
Language=English
Resource %1!s! is busy.
.
Language=French
La ressource %1!s! est occupée.
.

MessageId=+1
SymbolicName=DEMO_MISSING
Language=English
Resource %1!s! is missing.
.
Language=French
La ressource %1!s! est absente.
.

MessageId=
Severity=Success
SymbolicName=DEMO_READY
Language=English
Resource %1!s! is ready.
.
Language=French
La ressource %1!s! est prête.
.
```

Parse `SeverityNames`, `FacilityNames`, and `LanguageNames` tables before
resolving messages. `MessageIdTypedef` and `OutputBase` affect MC header output,
not the numeric code. Per the [Microsoft MC message definitions][mc-syntax],
if the tables are absent, MC's first-message defaults are
`Severity=Success` (0), `Facility=Application` (0xFFF), and
`Language=English`; omitted severity/facility on later messages inherit the
last specified values, **not** `Error`. `MessageId=+n` adds to the previous ID
*for the effective facility*; empty `MessageId=` advances by one for that
facility. Check the 16-bit ID, 2-bit severity, and 12-bit facility ranges.
In this example the effective codes are `0xC3450010`, `0xC3450011`, and
`0x03450012` respectively: `(severity << 30) | (facility << 16) | id`.
Keep the entire 32-bit value as `uint` until emitting the exception's signed
`int` HResult. Do not substitute `HRESULT_FROM_WIN32`, truncate to `ushort`,
or use checked `Convert.ToInt32(uint)`:

```csharp
namespace Demo.Messages;

public partial class DemoMissingException : System.Exception
{
    public const uint MessageCode = 0xC3450011u;
    public DemoMissingException(string resource)
        : base($"Resource {resource} is missing.")
    {
        HResult = unchecked((int)MessageCode);
    }
}
```

In this illustrative contract, generate all exception types in
`Demo.Messages`, matching the consumer partial declaration and reflection
lookups in the tests below. The generated type must remain `partial` so a
consumer can extend it without modifying generated code. Define a deterministic
symbolic-name → type-name rule (here `DEMO_MISSING` → `DemoMissingException`)
and diagnose invalid C#
identifiers, duplicate effective codes, and resulting type-name collisions
across all `.mc` inputs. Each `Language=name` starts text terminated by a line
containing only `.`; another language block can follow for the same message.
Do not treat a period inside a sentence as a terminator. `%1` and `%1!s!`
refer to the first insertion (MC insertions are **1-based**). If converting
supported string insertions to .NET formatting, escape literal `{` and `}`,
convert `%1` → `{0}`, and handle `%%` as a literal `%`. MC also defines
`%.`, `%!`, `%0`, `%n`, `%b`, `%r`, and `!format!` specifiers with
Windows/`wsprintf` semantics; do **not** pass those verbatim to
`string.Format`. Either implement each supported escape/specifier deliberately
or report an error at the offending token (including unsupported numeric
formats or `*` width/precision). Escape generated C# string literals with
`SyntaxFactory.Literal` or equivalent.

Report bad tables, unknown names, unterminated/duplicate language blocks,
overflow, unsupported insertions, and code/type collisions with diagnostic
locations in the input `.mc`: use the original `AdditionalText.Path`,
`TextSpan`, and `SourceText.Lines.GetLinePositionSpan(span)` with
`Location.Create(path, span, lineSpan)`. For ambiguous language selection,
point at the language table or a competing `Language=` block. Invalid global
MSBuild options may lack a source span; report a configuration diagnostic
instead of inventing a catalog position.

#### Generator-driver contract tests

In a `net8.0` MSTest project referencing `Basic.Reference.Assemblies.Net80`
and Roslyn C#, use the catalog above as `McText` (a verbatim/raw test string).
The following *test harness* assumes the illustrative `McExceptionGenerator`
implementation and the type names/constructors above (paste the synthetic
catalog into a `const string McText` in the test class):

```csharp
using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Threading;
using Basic.Reference.Assemblies;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.Diagnostics;
using Microsoft.CodeAnalysis.Text;
using Microsoft.VisualStudio.TestTools.UnitTesting;

[TestClass]
public class McGeneratorTests
{
    [TestMethod]
    public void SelectedMessagesCompileAndPreserveHResults()
    {
        // McText is the synthetic .mc catalog printed above.
        const string consumer = """
            namespace Demo.Messages;
            public partial class DemoMissingException
            {
                public string Area => "consumer";
            }
            """;
        var parseOptions = new CSharpParseOptions(LanguageVersion.Latest);
        var input = CSharpCompilation.Create(
            "SyntheticMcTests",
            new[] { CSharpSyntaxTree.ParseText(consumer, parseOptions) },
            Net80.References.All,
            new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary));
        GeneratorDriver driver = CSharpGeneratorDriver.Create(
            generators: new[] { new McExceptionGenerator().AsSourceGenerator() },
            additionalTexts: new AdditionalText[] { new MemoryMc("Messages/Sample.mc", McText) },
            parseOptions: parseOptions,
            optionsProvider: new McOptions());
        driver = driver.RunGeneratorsAndUpdateCompilation(
            input, out var output, out var generatorDiagnostics);

        Assert.IsFalse(generatorDiagnostics.Any(d => d.Severity == DiagnosticSeverity.Error),
            string.Join("\n", generatorDiagnostics));
        var generated = string.Join("\n", driver.GetRunResult().GeneratedTrees);
        StringAssert.Contains(generated, "DemoBusyException");
        StringAssert.Contains(generated, "DemoMissingException");
        Assert.IsFalse(generated.Contains("DemoReadyException")); // include filter
        using var dll = new MemoryStream();
        var emit = output.Emit(dll);
        Assert.IsTrue(emit.Success, string.Join("\n", emit.Diagnostics));
        var assembly = Assembly.Load(dll.ToArray());

        var busy = (Exception)Activator.CreateInstance(
            assembly.GetType("Demo.Messages.DemoBusyException", true)!, "book")!;
        Assert.AreEqual("Resource book is busy.", busy.Message);
        Assert.AreEqual(unchecked((int)0xC3450010u), busy.HResult);

        var missingType = assembly.GetType("Demo.Messages.DemoMissingException", true)!;
        var missing = (Exception)Activator.CreateInstance(missingType, "book")!;
        Assert.AreEqual("Resource book is missing.", missing.Message);
        Assert.AreEqual(unchecked((int)0xC3450011u), missing.HResult);
        Assert.AreEqual("consumer", missingType.GetProperty("Area")!.GetValue(missing));
    }

    [TestMethod]
    public void EmptyMessageIdAdvancesWithinFacility()
    {
        var input = CSharpCompilation.Create(
            "SyntheticMcReady",
            references: Net80.References.All,
            options: new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary));
        GeneratorDriver driver = CSharpGeneratorDriver.Create(
            generators: new[] { new McExceptionGenerator().AsSourceGenerator() },
            additionalTexts: new AdditionalText[] { new MemoryMc("Messages/Sample.mc", McText) },
            optionsProvider: new McOptions(include: "DEMO_READY"));
        driver = driver.RunGeneratorsAndUpdateCompilation(
            input, out var output, out var generatorDiagnostics);
        Assert.IsFalse(generatorDiagnostics.Any(d => d.Severity == DiagnosticSeverity.Error),
            string.Join("\n", generatorDiagnostics));
        using var dll = new MemoryStream();
        var emit = output.Emit(dll);
        Assert.IsTrue(emit.Success, string.Join("\n", emit.Diagnostics));
        var type = Assembly.Load(dll.ToArray()).GetType(
            "Demo.Messages.DemoReadyException", true)!;
        var ready = (Exception)Activator.CreateInstance(type, "book")!;
        Assert.AreEqual("Resource book is ready.", ready.Message);
        Assert.AreEqual(0x03450012, ready.HResult); // Success inherits Demo facility, ID 0x12
    }

    [TestMethod]
    public void MultilingualCatalogWithoutSelectionHasSourceDiagnostic()
    {
        var input = CSharpCompilation.Create(
            "SyntheticMcDiagnostics",
            references: Net80.References.All,
            options: new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary));
        GeneratorDriver driver = CSharpGeneratorDriver.Create(
            generators: new[] { new McExceptionGenerator().AsSourceGenerator() },
            additionalTexts: new AdditionalText[] { new MemoryMc("Messages/Sample.mc", McText) },
            optionsProvider: new McOptions(language: null, include: null));
        var result = driver.RunGenerators(input).GetRunResult();
        var diagnostic = result.Diagnostics.Single(d => d.Id == "MCGEN001");
        Assert.AreEqual(DiagnosticSeverity.Error, diagnostic.Severity);
        Assert.AreEqual("Messages/Sample.mc", diagnostic.Location.GetLineSpan().Path);
        Assert.IsTrue(diagnostic.Location.GetLineSpan().StartLinePosition.Line >= 0);
    }

    private sealed class MemoryMc(string path, string content) : AdditionalText
    {
        public override string Path => path;
        public override SourceText GetText(CancellationToken cancellationToken = default)
            => SourceText.From(content);
    }

    private sealed class McOptions(
        string? language = "English", string? include = "DEMO_MISSING;0xC3450010")
        : AnalyzerConfigOptionsProvider
    {
        private readonly AnalyzerConfigOptions values = new McValues(language, include);
        public override AnalyzerConfigOptions GlobalOptions => values;
        public override AnalyzerConfigOptions GetOptions(SyntaxTree tree) => values;
        public override AnalyzerConfigOptions GetOptions(AdditionalText file) => values;

        private sealed class McValues(string? language, string? include) : AnalyzerConfigOptions
        {
            public override bool TryGetValue(string key, out string value)
            {
                string? option = key switch
                {
                    "build_property.McLanguage" => language,
                    "build_property.McInclude" => include,
                    _ => null
                };
                value = option ?? "";
                return option is not null;
            }
        }
    }
}
```

`MCGEN001` above is an illustrative diagnostic ID for ambiguous language;
replace it with the ID in the implementation. The first test exercises
`MessageId=+1` (`0xC3450011`); the second exercises empty `MessageId=` after
it (`0x03450012`). **Additional cases to implement** include changing
facilities between relative/automatic IDs, first-message defaults
(`MessageId=0x1` without severity/facility resolves to
`0x0FFF0001`, not an error code), explicit French selection, no language on
multilingual input (shown above), malformed/unterminated blocks, unsupported
`%1!d!`, and collisions across files. Assert each diagnostic's ID, severity,
`.mc` path, and line span; assert that invalid inputs do not emit broken C#.
For each valid variant, compile the updated output, instantiate the selected
exception, check its formatted message and **signed** `HResult`, and compile
the consumer's partial extension alongside it. A generator diagnostic alone
does not establish that generated code compiles or behaves correctly.

[mc-syntax]: https://learn.microsoft.com/en-us/windows/win32/eventlog/message-text-files

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
