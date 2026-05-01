# Test Generation Reference

## Purpose

Generate compilable, runnable test code from a test plan. Every test case in the plan becomes a real test method.

## Framework Detection

Detect the language and test framework from the project. If unclear, ask the user.

| Language | Default Framework | Mocking |
|----------|------------------|---------|
| **C#** | MSTest | Moq |
| **TypeScript/JavaScript** | Jest or Vitest | jest.mock / vi.mock |
| **Python** | pytest | unittest.mock / pytest-mock |
| **C++** | GoogleTest or TAEF | GMock or Detours |

## Constraints

### Structure
- Each test has exactly ONE assert concept (single responsibility).
- Test names follow: `MethodName_Scenario_ExpectedBehavior`.
- Tests are independent -- no shared mutable state, no ordering dependencies.
- Use Arrange-Act-Assert (AAA) pattern with explicit `// Arrange`, `// Act`, `// Assert` comments.
- **One test class per source class, one test file per test class.** Never combine tests for unrelated source classes in a single file. Test file name must match: `OrderService.cs` → `OrderServiceTests.cs`. If a source file has multiple public classes, each gets its own test file.

### File Naming (MANDATORY)
- File name = `<SourceClass>Tests.cs` (or `.ts`, `.py`, etc.). Nothing else.
- **NEVER prefix with tool, skill, or iteration identifiers** (e.g., `AutoCoverage_`, `Iter<N>_`, `Generated_`). Traceability goes in attributes/comments, not filenames.

### Coexistence with Existing Test Files (MANDATORY)
- If a test file already exists for the source class, add new methods to that class.
- If the existing class should not be modified, create `<SourceClass>ExtendedTests` in a separate file — never a tool-prefixed duplicate.

### Quality
- **Think before generating**: Before writing tests for any source file, read it fully and confirm you understand the behavioral contract. State assumptions about expected behavior explicitly. If ambiguity exists (e.g., does null input throw or return default?), resolve it from source code or existing tests — never guess silently. If a simpler test approach exists, use it.
- Every test MUST have at least one meaningful assertion.
- Assertions validate BEHAVIOR, not implementation details.
- Do not assert on internal/private state -- assert on public outputs and observable side effects.
- Prefer specific assertions (`Assert.AreEqual(expected, actual)`) over generic (`Assert.IsTrue(condition)`).
- Match the repository's existing test framework and mocking stack (for example MSTest/xUnit/NUnit in C#, Jest/Vitest in TS/JS, pytest in Python).
- If the repository is C# and already uses MSTest+Moq, follow that stack and its version-specific APIs.
- Negative/error path tests are REQUIRED.

### Safety
- Never generate tests that call real external services.
- All external dependencies must be mocked/stubbed.
- Tests must be deterministic -- no wall-clock time, random data, or network.
- **Never generate tests for methods containing unbounded `while` loops or gRPC/async stream consumers** (`IAsyncStreamReader`, `ChannelReader`, `IAsyncEnumerable` read loops). These deadlock test runners because the loop never terminates without a real cancellation or stream-completion signal. Skip these methods in planning and document the skip reason.

### Efficiency
- Reuse test helpers/builders -- do not duplicate setup logic.
- If complex setup is needed, extract a builder or fixture.
- Do not generate tests that duplicate behavior already validated by existing tests for the same class. Read existing tests first and only add tests for genuinely untested scenarios.
- Add a comment on each test method mapping it to its plan ID using the format `// TP-<SourceFile>-<ShortName>` (e.g., `// TP-OrderService-PaymentFailurePath`). `<SourceFile>` is the short source file name without extension or path; `<ShortName>` is a ≤5-word camel-case scenario description.

## MSTest Version Compatibility (MANDATORY for C#)

Before generating test code, **detect the MSTest version** used by the target test project. Check the `.csproj` for `<PackageReference Include="MSTest" />` or `<PackageReference Include="MSTest.TestFramework" Version="X.Y.Z" />`. Then look at existing test files to see which assertion patterns compile.

### MSTest v4+ (latest / no version pinned)
1. **Exception testing**: Use `Assert.ThrowsExactly<T>()` -- NEVER `Assert.ThrowsException<T>()` (removed) or `[ExpectedException]` (removed)
2. **Data-driven tests**: Use `[TestMethod]` with `[DataRow]` -- NEVER `[DataTestMethod]` (obsolete, causes MSTEST0044 warning)
3. **Obsolete APIs**: Check for `[Obsolete]` attributes on methods being tested. Do NOT call obsolete methods -- use the recommended replacement
4. **Warnings as errors**: Avoid ALL patterns that produce warnings (CS0618 obsolete, MSTEST0044, etc.)

### MSTest v2/v3 (explicit older version)
1. Use `Assert.ThrowsException<T>()` (not ThrowsExactly)
2. `[DataTestMethod]` is valid
3. `[ExpectedException]` may still work but is discouraged

### How to Detect
Grep an existing test file for `ThrowsExactly` vs `ThrowsException`. If `ThrowsExactly` is found, it is v4+. If `ThrowsException` is found, it is v2/v3. If neither exists, check the package version. When in doubt, **follow the patterns in existing test files** -- they are the ground truth.

## Namespace and Type Verification (MANDATORY)

Before generating test code, **read the actual source files** to verify types. Never assume names from documentation or memory.

1. **Verify namespaces** -- Read the source file's `namespace` declaration. Assembly names often differ from namespaces.
2. **Verify property/method names** -- Read the class declaration. Property names are frequently different from what you would guess.
3. **Verify enum vs bool vs string** -- If a config property looks boolean, read the interface to confirm. It may be an enum.
4. **Verify nested vs top-level types** -- Enums/classes that appear nested in documentation may actually be top-level types.
5. **Check `InternalsVisibleTo`** -- If the method under test is `internal`, verify the test project's assembly name is in the `InternalsVisibleTo` list.

## Moq Expression Tree Limitations

When using Moq on .NET Framework (net462/net472), expression trees cannot contain calls to methods with optional parameters. This is a C# compiler limitation, not a Moq bug.

- `mock.Verify(x => x.Log(It.IsAny<string>()))` **fails** if `Log()` has optional params like `(string msg, params object[] args)`
- **Workaround 1**: Assert on the result/state instead of verifying mock calls
- **Workaround 2**: Use `mock.Setup(...)` with `Callback(...)` to capture arguments, then assert on captured values
- **Workaround 3**: Use `It.Is<T>(predicate)` with explicit types instead of `It.IsAny<T>()`
- **Detection**: If you see `CS0854: An expression tree may not contain a call or invocation that uses optional arguments`, simplify the Verify/Setup expression

## XML Doc Comments / Class-Level Summaries (MANDATORY)

Every generated test class MUST have a doc comment describing **what behavior** the tests cover — not how/when they were generated. One to three sentences. **NEVER include** iteration numbers, line ranges, or generic text like "Auto-generated tests".

```csharp
// GOOD:
/// <summary>
/// Tests for ParseDeploymentBuckets covering valid multi-bucket input, empty lists, and malformed descriptors.
/// </summary>

// BAD:
/// <summary>
/// Iteration 10 coverage tests — targets ParseDeploymentBuckets (lines 51-58).
/// </summary>
```

```python
# GOOD:
"""Tests for calculate_total covering discounts, tax edge cases, and empty carts."""

# BAD:
"""Auto-generated tests."""
```

```typescript
// GOOD:
/** Tests for parseConfig() covering valid YAML, missing required fields, and encoding errors. */

// BAD:
/** Iteration 3 coverage tests — targets parseConfig (lines 12-30). */
```

## Traceability & Metadata (MANDATORY)

Every generated test class MUST include attributes/metadata identifying it as auto-generated. Place on the **class declaration** (not individual methods). Match the repo's test framework:

### C# (NUnit)
```csharp
[TestFixture]
[Category("AutoGenerated")]
[Category("CopilotSkill:autocoverage")]
public class MyTests
```

### C# (MSTest)
```csharp
[TestClass]
[TestCategory("AutoGenerated")]
[TestCategory("CopilotSkill:autocoverage")]
public class MyTests
```

### C# (xUnit)
```csharp
[Trait("Category", "AutoGenerated")]
[Trait("Category", "CopilotSkill:autocoverage")]
public class MyTests
```

Assembly-level metadata at the top of each test file:

```csharp
// Auto-generated by: autocoverage skill
// Source: <relative path to the file under test>
```

Optional structured properties:
```csharp
[TestProperty("Generator", "CopilotSkill:autocoverage")]
[TestProperty("GeneratorVersion", "1.0")]
[TestProperty("Model", "<model name>")]
```

### TypeScript/JavaScript (Jest/Vitest)

```typescript
/**
 * @generated autocoverage skill
 * @generationDate <YYYY-MM-DD>
 * @model <model name>
 * @skillVersion 1.0
 * @source <relative path to the file under test>
 */
describe('[AutoGenerated] MyComponent', () => { ... });
```

### Python (pytest)

```python
# Auto-generated by: autocoverage skill
# Generation date: <YYYY-MM-DD>
# Model: <model name>
# Skill version: 1.0
# Source: <relative path to the file under test>

import pytest

pytestmark = [
    pytest.mark.auto_generated,
    pytest.mark.copilot_skill("autocoverage"),
]
```

### General Rules
- **Always include**: `AutoGenerated` category/tag, skill name, generation date, model name, source file path.
- **Never omit** the `AutoGenerated` category -- this is the primary filter for distinguishing hand-written from generated tests.

## Repo Coding Standards Compliance

Before generating test code, check for linter/formatter configs:

- **C#**: `.editorconfig`, `Directory.Build.props` (analyzers, `TreatWarningsAsErrors`), `.globalconfig`
- **TypeScript/JavaScript**: `.eslintrc.*`, `.prettierrc.*`, `biome.json`, `tsconfig.json`
- **Python**: `pyproject.toml`, `.flake8`, `setup.cfg`

Generated tests must:
- Match the repo's formatting (indentation, line length, brace placement)
- **Honor max line length** -- check `.editorconfig` `max_line_length` and CI pipeline scripts for line-length validation. Break long lines by splitting string literals, chaining method calls across lines, or extracting intermediate variables. This is a frequent CI gate failure.
- Pass all linter/analyzer rules without suppressions
- Pass any custom CI lint checks (line-length validators, style scripts) discovered in Stage 0
- Follow the same import/using conventions
- Not introduce `#pragma warning disable` unless the source code itself uses them
- Compile with zero warnings (especially when `TreatWarningsAsErrors` is enabled)

## Project File Rules (MANDATORY for new .csproj)

### Test Type Determination

Before creating a test project, determine the test type:
1. Explicit user intent ("create unit tests" vs "create E2E tests")
2. Project name/path conventions (`.Tests.`, `.UnitTests.`, `.E2E.`)
3. Package/tooling signals (Playwright/Selenium = E2E, MSTest+Moq only = Unit)
4. Test behavior (full stack = E2E, isolated mocks = Unit)

### Required Properties

**Unit Test projects**: Add inside a `PropertyGroup`:
```xml
<ProjectUsageType>UnitTest</ProjectUsageType>
```

**End-to-End Test projects**: Add inside a `PropertyGroup`:
```xml
<ProjectUsageType>EndtoEndTest</ProjectUsageType>
```

### Rules
- If property already exists, do not duplicate.
- If property exists with a conflicting value, report the conflict and stop.
- Preserve existing formatting/style in the project file.
- If multiple `PropertyGroup` sections exist, prefer the group where related test/project metadata already lives.

### Placement Rule
**NEVER create a new .csproj in the same folder where another project already exists.**

Discover the repo's existing test project convention first:
1. Search for existing `*.Tests.csproj` or `*.UnitTests.csproj` and note their location relative to source projects.
2. Place the new test project following the same pattern. Common conventions:
   - `test/MyService.Tests/MyService.Tests.csproj` (separate test root)
   - `src/MyService.Tests/MyService.Tests.csproj` (sibling under src)
   - `tests/MyService.Tests/MyService.Tests.csproj` (plural test root)
3. If no existing test projects, prefer `test/` or `tests/` root if present, else sibling under `src/`.
4. List the target directory before creating to verify no other `.csproj` exists.

## Output

Produce ONLY the test code file(s) -- complete with all imports, ready to compile and run. Include a comment block at the top listing all plan IDs covered.

If multiple files are needed, clearly separate them:
```
// --- FILE: tests/OrderProcessorTests.cs ---
```
