# Preline MCP - Tools Reference

Full parameter specs and placement rules for all 6 MCP tools.

---

## Tool 1: `components_list`

Browse available component sections and their component IDs.

**Input:**
- `section` (optional string) - pass the inferred section slug to get only that section. Omit to get all sections.

**When to pass section:** whenever the component type is known (e.g. `components_list({ section: "buttons" })`). Omitting section loads 300k+ characters - avoid unless you genuinely don't know the section.

**Returns:** JSON with section IDs, component IDs, titles, descriptions, and optional `relative` metadata.

---

## Tool 2: `single_component`

Get HTML/CSS/JS for one Preline component.

**Input:**
- `section` (required) - exact section slug from `components_list`. Never guess.
- `component` (required) - exact component ID from `components_list`. Never guess.
- `isUtilityBased` (optional, default: `false`) - convert design tokens to Tailwind utility classes
- `theme` (optional, default: `"default"`) - theme for utility conversion
- `parameters` (optional) - template-specific overrides

**Available themes:**

| Slug | Color |
|---|---|
| `default` | Blue |
| `harvest` | Amber |
| `retro` | Fuchsia |
| `moon` | Grayscale |
| `ocean` | Cyan |
| `bubblegum` | Pink |
| `cashmere` | Mauve |
| `autumn` | Amber/Orange |
| `olive` | Green |

**Examples:**
```
single_component({ section: "accordion", component: "accordion-basic-usage-example" })
single_component({ section: "alerts", component: "alerts-solid-color-variants", isUtilityBased: true })
single_component({ section: "datatables", component: "datatables-basic-usage-example" })
```

**Response sections:**
- `=== COMPONENT HTML ===` - main markup
- `<!-- CSS -->` - `<link>` and `<style>` tags
- `<!-- Scripts -->` - `<script src>` tags
- `<!-- Init -->` - initialization code
- Large responses are written to a temp file; read via the Read tool

---

## Tool 3: `component_documentation`

Get JavaScript API docs for plugin components.

**Input:**
- `component` (required) - plugin component name from the documented list

**Available documented components:**
accordion, advanced-datepicker, advanced-range-slider, advanced-select, carousel, collapse, combobox, copy-markup, datatable, dropdown, file-upload, input-number, layout-splitter, overlay, pin-input, remove-element, scroll-nav, scrollspy, stepper, strong-password, tabs, textarea-autoheight, theme-switch, toggle-count, toggle-password, tooltip, tree-view

**Returns:** API methods, events, data attributes, configuration options, integration examples.

---

## Tool 4: `blocks_categories`

List all block categories in a hierarchy.

**Input:** none

**Returns:** `mainSection → subSection → category` tree with block counts per category.

**Call first** when the user asks for blocks (ready-made page sections; users may also say "examples") or references a broad category.

---

## Tool 5: `blocks_in_category`

List block IDs within one category.

**Input:**
- `mainSection` (required) - top-level slug from `blocks_categories`
- `subSection` (required) - subsection slug from `blocks_categories`
- `category` (required) - category slug from `blocks_categories`

**Returns:** stable block IDs and slug/file mappings. Use IDs to call `single_block`.

---

## Tool 6: `single_block`

Get complete integration-ready HTML/CSS/JS for one block.

**Input:**
- `mainSection` (required)
- `subSection` (required)
- `category` (required)
- `block` (required) - exact ID from `blocks_in_category`. Accepts comma/newline-separated list (first is returned, rest marked as pending).
- `context` (optional) - insertion hint
- `isUtilityBased` (optional, default: `false`)
- `theme` (optional, default: `"default"`)

**Returns:** full block HTML with CSS/JS sections.

---

## Integration Placement Rules

### CSS (`<!-- CSS -->`)

```
✅ CORRECT
<head>
  ...
  <link rel="stylesheet" href="...">   ← immediately before </head>
</head>

❌ WRONG
<body>
  ...
  <link rel="stylesheet" href="...">   ← NEVER in <body>
</body>
```

### External Scripts (`<!-- Scripts -->`)

The `<!-- Scripts -->` label is a **response section marker only** - it does NOT indicate where to insert in the target file.

**Placement algorithm:**

1. Open the target file
2. Starting from `</body>`, scan **upward** line by line
3. Skip: blank lines, HTML comments (`<!-- ... -->`), non-structural tags (`</script>`, `</style>`, `</link>`, `</noscript>`), any non-HTML syntax
4. The **first structural closing tag** reached (`</main>`, `</section>`, `</div>`, `</footer>`, `</article>`, `</header>`, `</aside>`) is the **anchor**
5. Insert ALL `<script src>` tags on the line **immediately after** that anchor - nothing between the anchor and the scripts

```html
<!-- ✅ CORRECT - anchor is </main> -->
</main>
<script src="lib.js"></script>
</body>

<!-- ✅ CORRECT - anchor is </section> -->
</section>
<script src="lib.js"></script>
</body>

<!-- ❌ WRONG - non-structural content between anchor and scripts -->
</main>
<!-- any comment -->
<script src="lib.js"></script>
</body>
```

### Init (`<!-- Init -->`)

```html
<!-- Place immediately before </body> -->
<!-- Wrap in window.addEventListener unless block already contains <script> tags -->

<script>
window.addEventListener('load', () => {
  // init code here
});
</script>
</body>
```

If `<!-- Init -->` already contains `<script>` tags - insert as-is, do NOT wrap again.

---

## Smart Component Selection

`components_list` may include a `relative` object per component:

| Field | Meaning | When to prefer |
|---|---|---|
| `isSectionDefault: true` | Recommended showcase for the whole section | User request is vague, no specific variant mentioned |
| `category: "<slug>"` | Logical group (e.g. `"color-variants"`, `"states"`) | Use to filter by style group |
| `isCategoryDefault: true` | Recommended default within its category | Request implies a style group (e.g. "icon button", "loading state") |

**Exception for `isSectionDefault`:** if the component description mentions "multiple variants side by side" and the user wants a single element - skip it and pick a single-variant component. If no single-variant exists, use the default but extract only the one matching variant from the HTML.

---

## General Rules

- Customize **text content only** - never CSS classes or HTML structure
- Remove HTML comments before inserting into the target file
- For complex components (accordion, table, tree), insert the full structure
- For simple elements (button, input), insert one instance unless multiple are explicitly requested
