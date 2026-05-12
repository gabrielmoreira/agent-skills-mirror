---
name: dt-app-notebooks
description: Work with Dynatrace notebooks - create, modify, query, and analyze notebook JSON. Derives from the dt-app-dashboards skill with notebook-specific differences documented here.
license: Apache-2.0
---

# Dynatrace Notebook Skill

## How to Use This Skill

Notebooks and dashboards are structurally similar. **Follow the `dt-app-dashboards` skill for all workflows** (creating, modifying, querying, analyzing), applying the differences documented below.

### Mandatory Create/Update Workflow

1. Load domain skills BEFORE generating queries — do not invent DQL
2. Validate ALL queries via `dtctl query '<DQL>' --plain` before adding to the notebook
3. **Always set `"autoSelectVisualization": true`** in `visualizationSettings` unless the user explicitly requests a specific visualization type
4. **ALWAYS deploy via `deploy_notebook.sh`** — never use `dtctl apply` directly:
   ```
   bash scripts/deploy_notebook.sh notebook.json
   ```
   The script validates the notebook first and blocks deployment on errors. Skipping it risks deploying broken notebooks.
   On successful deployment, the local file is deleted.
5. When updating an existing notebook: **download first** with `dtctl get notebook <id> -o json --plain > notebook.json`, modify, then deploy. Never reconstruct from scratch or inject an `id` manually.

## Notebook JSON Structure

```json
{
  "name": "My Notebook",
  "type": "notebook",
  "content": {
    "version": "7",
    "defaultTimeframe": { "from": "now()-2h", "to": "now()" },
    "sections": [
      { "id": "uuid-1", "type": "markdown", "markdown": "# Title\nContext" },
      {
        "id": "uuid-2", "type": "dql", "title": "Query Section", "showInput": true,
        "state": {
          "input": { "value": "fetch logs | summarize count()" },
          "visualization": "table",
          "visualizationSettings": { "autoSelectVisualization": true, "chartSettings": {} },
          "querySettings": {
            "maxResultRecords": 1000, "defaultScanLimitGbytes": 500,
            "maxResultMegaBytes": 1, "defaultSamplingRatio": 10, "enableSampling": false
          }
        }
      }
    ]
  }
}
```

## Key Differences from Dashboards

### Document Structure

| Aspect | Dashboard | Notebook |
|--------|-----------|----------|
| `type` | `"dashboard"` | `"notebook"` |
| `content.version` | `21` (number) | `"7"` (string) |
| Content blocks | `tiles` (object map) + `layouts` (object map) | `sections` (ordered array) |
| Variables | `content.variables[]` with query, csv, text types | **None** |
| Layout/grid | 24-unit grid via `layouts` with x, y, w, h | **None** — sections render top-to-bottom in array order |
| Default timeframe | Controlled by UI time picker | `content.defaultTimeframe` object with `from`/`to` |

### Section Types vs Tile Types

Dashboards have two tile types (`markdown`, `data`). Notebooks have three section types:

- **`markdown`** — Same concept. Fields: `id`, `type`, `markdown`
- **`dql`** — Equivalent to dashboard `data` tiles, but query and visualization are nested inside `state` (see table below)

### Query & Visualization Path Mapping

| Field | Dashboard tile | Notebook DQL section |
|-------|---------------|---------------------|
| Query string | `tile.query` | `section.state.input.value` |
| Visualization type | `tile.visualization` | `section.state.visualization` |
| Visualization settings | `tile.visualizationSettings` | `section.state.visualizationSettings` |
| Query settings | `tile.querySettings` | `section.state.querySettings` |
| Section-specific timeframe | N/A (UI picker controls all tiles) | `section.state.input.timeframe` |

### Notebook-Only Section Properties

- `autoSelectVisualization` (boolean, in `visualizationSettings`) — when `true`, Dynatrace automatically selects the best visualization type for the query result. **Prefer `true` when the user has no specific visualization preference.** When set to `false`, you must explicitly set `state.visualization` to the desired type.
- `showTitle` (boolean) — show/hide section title
- `showInput` (boolean, default `true`) — show/hide query editor. Always set to `true` unless explicitly requested otherwise.
- `height` (number, px) — section height (default ~400)
- `drilldownPath` — navigation path for drilldown interactions
- `filterSegments` — section-level filter segments
- `davis` — Davis AI copilot configuration

### Available Visualizations

Notebooks support: `table`, `lineChart`, `areaChart`, `barChart`, `categoricalBarChart`, `pieChart`, `donutChart`, `singleValue`, `bandChart`, `histogram`, `honeycomb`, `raw`, `recordView`

### What Does NOT Apply from the Dashboard Skill

- **Variables** — Notebooks have no variables. Ignore all variable sections: types, substitution patterns (`$Var`, `array($Var)`), dependency resolution, variable validation.
- **Layouts/grid** — No positioning system. Section order in the array = display order. No `x`, `y`, `w`, `h`.
- **Tile ID / Layout ID matching** — Not applicable (no layouts object).
- **UI timeframe picker warnings** — Notebooks don't have a dashboard-style time picker that controls all queries. Instead, `content.defaultTimeframe` sets the default, and each section can override via `section.state.input.timeframe`. Hardcoded time filters in queries are acceptable in notebooks.
- **Variable substitution in queries** — Not applicable.

## Validation & Deployment

Use the scripts in `scripts/`:

- **`notebook-validator.js`** — Validates notebook structure and executes all DQL queries. Run via:
  ```
  cat notebook.json | jq '{notebook: .}' | dtctl exec function -f scripts/notebook-validator.js --data - --plain | jq -r .result
  ```
  Or by notebook ID: `echo '{"notebookId":"<id>"}' | dtctl exec function -f scripts/notebook-validator.js --data - --plain | jq -r .result`

- **`deploy_notebook.sh`** — Validates then deploys:
  ```
  bash scripts/deploy_notebook.sh notebook.json
  bash scripts/deploy_notebook.sh --dry-run notebook.json
  ```

## Related Skills

- **dt-app-dashboards** — Base skill for all workflows; this skill documents only the differences
- **dt-dql-essentials** — DQL query syntax, functions, and optimization
