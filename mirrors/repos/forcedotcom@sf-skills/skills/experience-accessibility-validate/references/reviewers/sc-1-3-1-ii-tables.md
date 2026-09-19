## SC 1.3.1 - Info and Relationships (Level A)

Information, structure, and relationships conveyed through presentation can be programmatically determined or are available in text.

## SC: 1.3.1 (ii) - Tables Only

For every `<table>` element in the source, apply the criteria below and produce one fix entry per violation. Other SC 1.3.1 concerns (lists, regions, form-labels, groups) are out of scope — they are owned by sibling reviewers.

### Structural criteria

For each `<table>`, verify:

- Contains at least one `<tr>` element.
- Each `<tr>` contains one or more cells appropriate to its content: `<th>` for headers and `<td>` for data. A header-only row containing only `<th>` cells is valid.
- Header content (if present) is marked up with `<th>` (typically in the first `<tr>` or inside `<thead>`).
- All data content is inside `<td>` cells; all header content is inside `<th>` cells.
- The table is either a recognizable data table (`<tr>`, `<td>`, plus `<th>` when headers exist) or a layout table (no relationships across rows and columns).

### Header-association criteria

- **Simple data tables** with headers in the first row or column: `<th>` without `scope` is sufficient.
- **Simple data tables** with headers NOT in the first row or column: every `<th>` must carry a valid `scope` (`row` / `col` / `rowgroup` / `colgroup`) matching the header's role.
- **Irregular tables** with headers spanning rows or columns may use explicitly defined row or column groups with `scope="rowgroup"` or `scope="colgroup"`. Do not require `id` + `headers` solely because a table uses `rowspan`, `colspan`, or multiple header levels when groups and `scope` express the relationships.
- **Complex tables** whose data-cell relationships are too complex to identify using `<th>` alone or `<th>` with `scope` must provide programmatically determinable header-to-cell associations. Use `id` + `headers` attributes (see H43), or simplify the table so `<th>` and `scope` can express the relationships. Complex cases include tables whose headers repeat or change partway through the table or whose data cells are associated with three or more headers. When `id` + `headers` is used, verify that every `<th>` `id` is unique within the component and every id in a cell's `headers` attribute resolves to an actual `<th>`.

### Accessible-name criterion

Providing an accessible name (via `aria-label`, `aria-labelledby`, or `<caption>`) is a best practice but not a violation when absent. Do not produce a fix entry purely for a missing accessible name.

### Layout-table criterion

When a table's content has no row/column relationships, classify it as a layout table. Layout tables should not use `<th>` or `scope`; emit a fix entry if they do.

### Output contract

For each violation, produce one entry with: file + line number, which criterion above failed, and the corrected markup snippet. If every table satisfies the criteria, produce an empty list.

- For each issue found, provide a separate, detailed report.
- Keep issues concise, avoid duplicated issues or unnecessary or non-applicable problems.
- Assume that any imported functionality works as expected and was already analyzed.
- Components do not supplement or provide global functionalities.
