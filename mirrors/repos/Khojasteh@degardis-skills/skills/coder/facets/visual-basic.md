---
title: Visual Basic
category: Language
guides:
- dotnet-xml-documentation
x-claim-provenance:
- claim: Option Strict On makes implicit narrowing conversions, late binding, and implicit Object typing compile-time errors; with Option Strict Off, the initial default, they compile and can fail at run time; a file without an Option Strict statement uses the project setting.
  source: https://learn.microsoft.com/en-us/dotnet/visual-basic/language-reference/statements/option-strict-statement
- claim: Option Compare Text makes string comparison case-insensitive using the system locale's sort order, while the default Binary compares character codes.
  source: https://learn.microsoft.com/en-us/dotnet/visual-basic/language-reference/statements/option-compare-statement
- claim: Assigning Nothing to a non-nullable value type sets its default value, to a nullable value type or reference type sets null, the empty string equals Nothing under the equality operator, and null checks should use Is Nothing or IsNot Nothing.
  source: https://learn.microsoft.com/en-us/dotnet/visual-basic/language-reference/nothing
---

Visual Basic compiles the same source differently depending on its `Option` settings, and a file's own `Option` statement overrides the project setting. With `Option Strict Off`, the initial default, implicit narrowing conversions and late binding compile and fail only at run time, and a declaration without a type becomes `Object`; `Option Strict On` turns all three into compile-time errors. `Option Compare Text` makes string comparison case-insensitive and dependent on the system locale, while the default `Binary` compares character codes, so the setting changes equality and sorting results. The effective language version, target frameworks, analyzers, conditional symbols, and C# or COM consumers decide the rest.

`Nothing` is the default value of a type, not only a null reference. Assigned to a non-nullable value type it produces that type's default, assigned to a nullable value type or a reference it produces null, and the empty string equals `Nothing` under `=`, which is why null checks use `Is Nothing` or `IsNot Nothing`. Narrowing and widening, `ByRef`, default properties, late binding, event ownership, async and cancellation, disposal, culture, and serialization are further behavioral contracts, and semantics run through overload resolution, case-insensitive binding, implicit and user-defined conversions, `CType`, `DirectCast`, and `TryCast`, equality, iterator and LINQ timing, exception filters, and synchronous versus asynchronous failure.

Lifecycle and ownership run through `Handles`, `AddHandler` and `RemoveHandler`, delegate lifetime, closures, cancellation, continuations, `Using`, COM release, and callbacks that outlive their owner. Public metadata, compiled names, XML literals, `My` services, reflection, generated designer code, trimming, COM, and cross-language consumption are emitted boundaries, and code is also reached indirectly through:

- designer and `My` generated regions and XML literals
- serializers, reflection names, and configuration
- COM registration, source generators, and trimming annotations
- late-bound calls and downstream C# consumers

Behavioral evidence covers `Nothing` across type categories, conversions under the configured `Option` settings, overload and default-property selection, `ByRef`, late binding, event cleanup, culture, XML, iteration, async cancellation, and disposal. Where source does not reveal the emitted surface, built-metadata and representative C# or COM consumer evidence settles it, and reflection, serialization, generated behavior, trimming, and each supported target are separate runtime surfaces. Performance evidence comes from release builds after configured runtime warmup, and an optimization must preserve conversion and null semantics, event lifetime, disposal, culture, serialization, and interoperation compatibility.
