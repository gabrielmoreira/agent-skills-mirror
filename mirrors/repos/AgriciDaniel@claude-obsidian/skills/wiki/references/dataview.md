# Optional Dataview reference

Use only when the user already has Dataview and requests a compatible query.
The portable core needs no community plugin. Prefer a native Base when it is
sufficient. Do not install Dataview as a side effect.

DQL resolves folder sources from the vault root, regardless of the dashboard
note's location. This original example lists canonical concepts under `wiki/`:

```dataview
TABLE type, status, updated
FROM "wiki"
WHERE type = "concept"
SORT file.name ASC
```

An empty table means no matching indexed notes only after the plugin is present,
enabled, and its index is current. Otherwise report unavailable or unverified.
The example uses stored properties, not a claim that properties are true.
Dataview's `file` fields are not Bases formula syntax.

The query is a declarative display example, not a Python executable test. Offline
checks validate its source scope and referenced properties against shipped
fixture notes. Native Dataview rendering still requires the plugin and a
versioned app observation; see [native-conformance.md](../../../docs/native-conformance.md).

Do not execute `dataviewjs` or imported queries during ingestion or normal
query/lint work. Preserve existing DQL and executable blocks byte-for-byte on
unrelated edits. DataviewJS can perform file and network operations.

Reference checked 2026-10-17: [Dataview documentation](https://blacksmithgu.github.io/obsidian-dataview/queries/query-types/)
and [README at the pinned commit](https://github.com/blacksmithgu/obsidian-dataview/blob/5ad0994ff384cbb797de382e7edff2388141b73a/README.md).
This recipe is independently written and imports no plugin code.
