---
title: XML documentation for .NET languages
applicability:
- When XML documentation comments are among what the work produces or assesses
x-claim-provenance:
- claim: C# documentation comments must be well-formed XML, the compiler verifies param names and cref targets and warns when they fail, see accepts cref, href, and langword, inheritdoc inherits comments from base members, while Visual Studio's automatic inheritance does not affect the generated XML file, remarks supplement the summary, and example shows how to use a member, commonly with code inside it.
  source: https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/xmldoc/recommended-tags
  scope: Page dated 2026-09-10.
- claim: In F#, a /// comment that does not start with < is taken whole as the summary, the compiler ignores XML documentation comments unless --warnon:3390 is set, cross-references must use the full XML signature and are never checked, include and inheritdoc are copied to the output without being processed, and tags the compiler does not list, such as example, may still be used.
  source: https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/xml-documentation
- claim: Visual Basic lists example, remarks, and code among its recommended documentation tags.
  source: https://learn.microsoft.com/en-us/dotnet/visual-basic/language-reference/xmldoc/recommended-xml-tags-for-documentation-comments
---

XML documentation for .NET languages is well-formed XML in the comment form accepted by the language; Markdown syntax is not interchangeable with that XML contract. Declarations remain the owner of machine-readable metadata they already expose, while XML documentation carries the human-facing contract and cross-language behavior that consumers still need.

`<param>`, `<typeparam>`, `<returns>`, and `<value>` describe their corresponding declaration elements. `<paramref>` and `<typeparamref>` refer to parameters and type parameters, `<see cref="...">` refers to resolvable members, and `<c>` marks non-reference inline code. `<code>` carries multiline code, `<remarks>` supplementary explanation, and `<example>` every example of use, with its code in a `<code>` element inside it.

Distinct documented failures remain distinct `<exception>` entries, including distinctions between failure before an asynchronous result is returned and failure while a task, async sequence, or lazy sequence runs.

Inherited documentation is semantically valid only when the inherited contract still applies unchanged and the configured generator actually expands the inheritance mechanism in use.

For C#, keyword references may be represented with `<see langword="...">` where the configured generator supports them; conditional nullability, deferred enumeration, trimming, and async disposal can all alter the caller-visible contract. For F#, `.fsi` declarations, implementation comments, compiled names, erased units of measure, and the public shape seen by other .NET languages can diverge and therefore need semantic agreement; the compiler checks XML only under `--warnon:3390`, takes a `///` comment that does not start with `<` as the whole summary, requires the full XML documentation signature in `cref` without ever checking it, and passes `<include>`, `<inheritdoc>`, and tags it does not list, such as `<example>`, through unprocessed, so their effect depends on configured tool support. For Visual Basic, `Option` settings and observable `Nothing`, `ByRef`, default-property, event, conversion, COM, and C#-consumer behavior can change what the documentation must explain.

Structured XML documentation lists have additional schema constraints described in [[guide:xml-lists]].
