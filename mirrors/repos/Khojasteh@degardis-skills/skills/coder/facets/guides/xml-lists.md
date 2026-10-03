---
title: List structure in XML documentation
applicability:
- When a list in XML documentation comments is among what the work produces or assesses
x-claim-provenance:
- claim: The list tag takes type bullet, number, or table, uses listheader to define the heading row of a table or definition list, and structures items with term and description elements.
  source: https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/xmldoc/recommended-tags
  scope: Page dated 2026-09-10.
---

The project's configured XML documentation generator determines the accepted schema and supported containers. List content remains well-formed XML nested within the member's supported summary, remarks, returns, value, or comparable container.

A bullet list has this structure:

```xml
<list type="bullet">
  <item><description>First item.</description></item>
  <item><description>Second item.</description></item>
</list>
```

Where the configured consumer supports it, `type="number"` represents ordered steps using the same item structure.

A two-column table has this structure:

```xml
<list type="table">
  <listheader>
    <term>Value</term>
    <description>Meaning</description>
  </listheader>
  <item>
    <term>alpha</term>
    <description>The first supported value.</description>
  </item>
</list>
```

The `term` and `description` structure is inherently two-column. Content that needs more columns or nested records therefore depends on a different representation supported by the configured consumer. Consumer-specific list types, elements, and rendering behavior remain configuration-dependent and are established by the configured documentation generator.
