## List structure

Choose the list type for the relationship between its items:

- Use `type="bullet"` for independent items whose order has no meaning.
- Use `type="number"` when position communicates a required sequence,
  precedence, or ranking.
- Use `type="table"` when related values are clearer as rows and columns.

In a bullet or numbered list, `<description>` contains the item text. Add
`<term>` when a short label, name, or key makes unordered items easier to scan:

```xml
<list type="bullet">
    <item>
        <term>Transient failure</term>
        <description>The operation can be retried.</description>
    </item>
    <item>
        <term>Permanent failure</term>
        <description>The operation requires corrective action.</description>
    </item>
</list>
```

For an unlabeled item, `<description>` alone is sufficient:

```xml
<list type="number">
    <item><description>Open the connection.</description></item>
    <item><description>Execute the command.</description></item>
</list>
```

In a table, each `<term>` or `<description>` is a cell, so a header or row can
contain as many columns as needed. Every table must include a `<listheader>`,
and every `<item>` must contain the same number of cells in the same order as
the header:

```xml
<list type="table">
    <listheader>
        <term>Value</term>
        <term>Retry behavior</term>
        <term>Typical use</term>
    </listheader>
    <item>
        <term>0</term>
        <description>Does not retry the operation.</description>
        <description>Operations that cannot fail transiently.</description>
    </item>
    <item>
        <term>-1</term>
        <description>Retries the operation indefinitely.</description>
        <description>Services that must recover automatically.</description>
    </item>
</list>
```

Keep `<term>` and `<description>` content phrasing-level: text and inline tags
such as `<c>`, `<see>`, and `<paramref>` are allowed, but block tags such as
`<para>`, `<list>`, and `<code>` are not. A missing table header or a block
nested in a table cell can produce broken structure when XML documentation is
converted to Markdown.

Do not add a `<term>` that merely repeats its description, and do not remove a
useful term solely because a list is bulleted or numbered.
