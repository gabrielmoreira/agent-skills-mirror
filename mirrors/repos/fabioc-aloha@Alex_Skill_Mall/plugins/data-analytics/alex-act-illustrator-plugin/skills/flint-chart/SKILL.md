---
name: flint-chart
description: "Use when the user wants to visualize data — from 'which chart should I use?' to 'render this'. Helps pick the right chart from the analytical question (comparison / trend / distribution / relationship / proportion / flow / KPI), then authors a ChartAssemblyInput and renders via the flint-chart-mcp server (Vega-Lite / ECharts / Chart.js). Transform data before Flint; style tweaks after Flint."
lastReviewed: 2026-07-25
---

# flint-chart: pick, author, and render a chart

## What you produce (and what you do NOT)

Your output is the **spec**: the `chart_spec` and `semantic_types` of a
`ChartAssemblyInput`. You reference data columns **by name**. The host
passes the resulting input to `assembleVegaLite`, `assembleECharts`,
or `assembleChartjs` to get a backend spec.

**You write the input spec, not the output spec.** And critically:

- **DO** emit `chart_spec` (chart type, channel→field mapping, properties)
  and `semantic_types` (field → semantic type).
- **Reference columns by name.** How `data` itself gets bound depends on
  the situation — a URL, a host-side variable, or embedded rows (see "How
  data gets bound"). Embedding is fine for small tables; just don't
  re-serialize a _large_ dataset by hand, since that risks truncation and
  silent value corruption and wastes tokens.
- **Transform data before Flint.** If the requested chart needs aggregation,
  filtering, joins, pivots, derived columns, or long/wide reshaping beyond
  Flint's built-in static-series fold, use a coding, notebook, SQL, or data tool
  first. Then author the Flint spec against the transformed table.
- **Style after Flint, only when needed.** Author structure in Flint. For a
  presentation tweak Flint does not express (a reference line, annotation, or
  shaded band), use the Vega-Lite escape hatch — see "Post-Flint style
  customization". Never feed edited Vega-Lite JSON back to `render_chart`.
- **Look at what you rendered.** A chart with a collapsed scale, a merged color
  scale, or an empty data binding renders as a valid image that tells the wrong
  story — `validate_chart` cannot catch that. Load the `render-verify` skill
  after rendering, and always after a post-Flint Vega-Lite edit.

## Verify Flint is available before rendering

Before you promise to render a chart, confirm the tools exist. If they don't,
install them (or ask the user to). Failing loudly early is cheaper than
authoring a spec no one can render.

### For MCP rendering (default in this skill)

1. **Check for the `flint` MCP server.** Look in your available tool inventory
   for `render_chart`, `compile_chart`, `validate_chart`, `list_chart_types`,
   or `create_chart_view`. If any of them are present, the server is registered
   and reachable — skip to step 4.

2. **If the tools are missing, `flint-chart-mcp` is not registered.** Ask the
   user to add it, or add it yourself if you can edit their workspace config.

   **Put the file in the right place — this is the single most common failure.**

   | Host                         | Path                          | Top-level key |
   | ---------------------------- | ----------------------------- | ------------- |
   | **VS Code** (workspace)      | `.vscode/mcp.json`            | `servers`     |
   | Claude Code / Claude Desktop | `.mcp.json` at workspace root | `servers`     |
   | Cursor                       | `.cursor/mcp.json`            | `servers`     |
   | GitHub Copilot CLI           | `~/.copilot/mcp-config.json`  | `mcpServers`  |

   The schema is identical across the first three, which is exactly why the
   wrong path looks like it should work. **VS Code never reads a workspace-root
   `.mcp.json`** — and it reports no error, because it isn't parsing a broken
   file, it's reading no file at all. If a user says "I added the config and
   nothing happened," check the path before anything else.

   **Copilot CLI differs twice over:** different path _and_ a different
   top-level key (`mcpServers`, not `servers`). A `servers` block pasted there
   fails just as silently. Prefer telling the user to run `/mcp add` inside a
   CLI session and let it write the file. The path is overridable via
   `$COPILOT_HOME`.

   Always **merge** into any existing config rather than overwriting it —
   clobbering the file destroys whatever other servers the user had.

   ```jsonc
   // .vscode/mcp.json (VS Code) — merge with any existing "servers" map
   {
     "servers": {
       "flint": {
         "type": "stdio",
         "command": "npx",
         "args": ["-y", "--prefer-offline", "flint-chart-mcp@0.4.1"],
       },
     },
   }
   ```

   - `"type": "stdio"` is optional in some hosts but always declare it —
     omitting it makes transport-related failures harder to diagnose.
   - `--prefer-offline` uses the npm cache first. If absent, npm contacts only
     the configured registry for the exact `0.4.1` package.
   - Do not run version-discovery commands, pass `--registry`, edit `.npmrc`,
     or fall back to a public tarball. Missing packages fail closed.
   - **`ETARGET` / "No matching version found" on a version the registry does
     carry** is a stale cached packument, not a missing package.
     `--prefer-offline` served the old metadata. Run the same command **once
     without `--prefer-offline`** to refresh it, then restore the flag. Do not
     conclude the version is unavailable and do not add `--registry`.
   - **Air-gapped:** an administrator may preinstall exact
     `flint-chart-mcp@0.4.1` through the approved registry, then change
     `"command": "npx"` to `"command": "flint-chart-mcp"` with empty args.
   - **Hardened deployment** (only inline `data.values` accepted, no local
     `data.url` files): append `"--disable-file-reference"` to `args`.

3. **After adding, the host must reload for MCP servers to spawn.** VS Code:
   `Ctrl+Shift+P` → "Developer: Reload Window". Claude Desktop / Cursor:
   restart the app.

4. **Verify.** Call `list_chart_types` with `{ "backend": "vegalite" }`. If it
   returns the chart catalog, the server is up.

5. **If the tools still do not appear, isolate which half is broken before
   guessing.** The server and the client fail identically from chat. If the
   user has the plugin repo checked out, `node scripts/verify-install.mjs`
   does this in one step; otherwise probe the server yourself — pipe a
   handshake plus a `tools/list` into the binary over stdio and read the
   response. A `serverInfo` block followed by a `tools` array proves the server
   is healthy and the fault is config, trust, or session staleness. Then work
   down this list:
   1. **Trust prompt.** VS Code will not start a local stdio server until you
      approve it. `Ctrl+Shift+P` → **MCP: List Servers** → pick `flint` →
      **Start**, and watch for the approval dialog.
   2. **Server output.** Same menu → **Show Output**. Startup crashes surface
      there and nowhere else.
   3. **Restart the chat session.** A window reload is not always enough — the
      agent's tool inventory can stay stale until the session itself restarts.
   4. **HTTP transport only:** an HTTP server needs OAuth authorization after
      starting, which is a separate step from trust. A server can be
      configured and started yet still unauthorized.

6. **For deeper MCP config** — HTTP transport, allowed-host lists, deployment
   patterns, full CLI reference — see the canonical MCP doc:
   <https://microsoft.github.io/flint-chart/#/mcp>. Point the user there for
   anything beyond the stdio install path documented above.

### For project code integration

Only needed if the user asked you to write code that **imports** `flint-chart`
directly (not to render via MCP).

1. **Check the project's `package.json`** for `flint-chart` in `dependencies`
   or `devDependencies`. If present, skip to step 3.

2. **If missing, use the project's approved dependency workflow.** Preserve its
  lockfile and configured registry; never probe another registry or select a
  newer package version automatically. The Flint library version must match
  the project's approved compatibility decision.

   ```bash
  npm install --save-exact flint-chart@0.4.1
   ```

  Add renderer peer dependencies only through the same project dependency
  policy; do not use this skill to discover or upgrade their versions.

3. **Import in code:**

   ```ts
   import {
     assembleChartjs,
     assembleECharts,
     assembleVegaLite,
   } from "flint-chart";
   const spec = assembleVegaLite(input); // or assembleECharts / assembleChartjs
   ```

### For Python

Not yet published to PyPI (as of 2026-07-24). Use the npm package or MCP
server for released workflows until the Python release lands.

## When the user wants more than a spec

First decide which workflow the user is asking for:

- **Spec authoring only:** return a `ChartAssemblyInput` or its
  `semantic_types` + `chart_spec` pieces. Do not install packages or write
  renderer code unless asked.
- **MCP chart output:** if Flint MCP tools are available, **default to
  `create_chart_view`** whenever the user asks to see a chart — it opens an
  interactive, live-rendered view with a customization panel, and it validates
  the spec for you. Only fall back to `render_chart` (PNG/SVG) when the host has
  no App UI support or the user explicitly wants a static image. Use
  `validate_chart` to check a spec without rendering, `compile_chart` when the
  user wants backend-native JSON, and `list_chart_types` when you need the
  supported chart catalog.
- **Project integration, only when the user asks for code:** add Flint to an
  app, notebook, script, or agentic product, install/import the library, and
  call an assembler in code. Keep the same `ChartAssemblyInput` contract, then
  let the host render the backend result.

For MCP clients, the server uses an exact cache-first package:

```bash
npx -y --prefer-offline flint-chart-mcp@0.4.1
```

For JavaScript or TypeScript projects, use the approved project dependency
workflow and preserve the lockfile:

```bash
npm install --save-exact flint-chart@0.4.1
```

Do not add or upgrade renderer dependencies unless the user explicitly requests
project integration and approves the project's dependency changes.

Then compile with the requested backend:

```ts
import {
  assembleChartjs,
  assembleECharts,
  assembleVegaLite,
} from "flint-chart";

const vegaLiteSpec = assembleVegaLite(input);
const echartsOption = assembleECharts(input);
const chartjsConfig = assembleChartjs(input);
```

Python support is planned for a later release. Until the PyPI package is
published, use the npm package or MCP server for released workflows.

```ts
interface ChartAssemblyInput {
  // Bound by the HOST or by you, depending on the situation (see below).
  data: { values: any[] } | { url: string };
  semantic_types?: Record<string, string>; // field → semantic type  ← you write this
  chart_spec: {
    //                        ← you write this
    chartType: string; // e.g. "Scatter Plot"
    encodings: Record<string, EncodingValue>; // channel → { field, ... } (or array)
    baseSize?: { width: number; height: number }; // target layout size, default 400×320
    canvasSize?: { width: number; height: number }; // optional hard ceiling on stretch
    chartProperties?: Record<string, any>; // per-chart tuning (optional)
  };
  options?: Record<string, any>; // global layout options (rarely needed)
}
```

## How data gets bound

Use the binding mode that matches the runtime. Do not mix them.

1. **Direct MCP rendering: embed rows.** When calling `render_chart`,
   `compile_chart`, or `validate_chart`, the tool arguments are JSON. If the
   data is small or already transformed by another tool, pass it as
   `data: { values: [...] }`. Do not pass runtime variable names in
   MCP tool calls — the MCP server cannot see your local variables.
2. **Direct MCP rendering: reference a local file.**
   The `flint-chart-mcp` server can load `data: { url: "..." }` from local
   `.json`, `.csv`, or `.tsv` files. By default any local file the agent can
   name is readable (relative paths resolve against the working directory); a
   hardened deployment may reject local file references entirely via
   `--disable-file-reference` (or `FLINT_MCP_DISABLE_FILE_REFERENCE`), in which
   case pass rows inline with `data.values`. Remote URL
   fetching is disabled. If the data must be transformed first, use a
   coding/data tool to write a small prepared file, then reference that file.
3. **Generated application or notebook code: bind runtime variables.** If the
   user asks you to add Flint to code, write normal data-loading code first and
   pass a real runtime value, e.g. `data: { values: rows }`, to
   `assembleVegaLite`, `assembleECharts`, or `assembleChartjs`. This variable
   pattern is for generated code, not for MCP tool calls.

For spec-only answers, return the `semantic_types` and `chart_spec` pieces and
state how the host should bind data. In the worked examples below, `data` is
shown as `{ values: [] }` to signal "host binds this" — focus on `chart_spec`
and `semantic_types`.

## Data transformation before charting

Flint is a chart compiler, not a data-wrangling layer. If the chart needs grouped
totals, time buckets, filters, joins, pivots, derived ratios, or a long-form
table, transform the data first with a host tool, then bind the prepared table
(see "How data gets bound"). Pick semantic types and channels for the transformed
columns, not for columns that no longer exist.

**Sanity-read the values first — don't chart blind.** Inspect the actual data
with your data tool (distinct values per category column, min/max per measure),
not just the column names, and watch for:

- **Embedded totals.** A category column may mix an aggregate level with its
  parts (e.g. `all` alongside `cage-free`/`caged`, or a `Total` region). Charting
  the total with its parts double-counts and flattens the parts — keep one or the
  other on a stacked/grouped/colored channel, not both.
- **Units.** Check whether a rate is a fraction (0–1) or already a percent
  (0–100) before tagging it `Percentage`; don't scale twice.
- **One real entity.** If your breakdown column has a single distinct value, the
  per-group chart collapses to one mark — the intended breakdown is likely a
  different column.

## Post-Flint style customization

Stay at the Flint level for structure (data, chart type, channels, transforms,
sizing, properties) — Flint specs stay portable and regenerate safely. Drop to
backend JSON only after a valid Flint chart exists, and only for a narrow
presentation change Flint does not expose (exact axis/legend/mark styling,
titles, annotations, reference lines, layout polish). Never use it to change the
data, chart type, field mappings, or transforms — fix those upstream.

For a Vega-Lite-specific style tweak:

1. Author and validate the Flint `ChartAssemblyInput`.
2. Render or inspect the Flint chart first, when possible.
3. Call `compile_chart` with `backend: "vegalite"`.
4. Make the smallest necessary style/presentation edit to the returned
   Vega-Lite spec.
5. Render the edited spec in the host environment with a Vega-Lite renderer.

This edited Vega-Lite spec is no longer a portable Flint spec. Do not send it to
`render_chart`; use `render_chart` only for Flint `ChartAssemblyInput`.

**Verification is mandatory here.** Once you leave the Flint level, the MCP
server's validation no longer protects you — an edited spec can render a
plausible-looking chart that is silently wrong. Load the `render-verify` skill:
open the result, read its console errors, and check it against the failure
catalog before declaring it done.

## Publication config preset (books, reports, exec-facing)

When the render target is a book chapter, a print report, or an exec-facing
document, three settings routinely need to be pinned across every chart in the
artifact so the visuals read as one voice. This is a Vega-Lite `config` block
you can drop into the compiled spec (via Step 3 semantic types →
`compile_chart` → backend edit as described above).

> **Print variant of the constellation brand palette.** The categorical range
> below (blue-800 / amber-700 / green-700 / gray-500 / red-700) is the
> **print-quality variant** of the Alex ACT `chart.categorical` palette. The
> **screen variant** (`#10b981` / `#0ea5e9` / `#f59e0b` / `#8b5cf6` / `#ef4444`)
> lives in [`.github/config/brand-palette.json`](https://github.com/fabioc-aloha/Alex_ACT_Core/blob/main/.github/config/brand-palette.json)
> in `Alex_ACT_Core`. Same 5-role semantic categorical, deeper contrast for
> paper.

Pin this once at the top of the artifact's chart set; regenerated charts
inherit it without per-chart overrides.

```json
{
  "config": {
    "background": "transparent",
    "font": "Inter, system-ui, sans-serif",
    "axis": {
      "labelColor": "#6b7280",
      "titleColor": "#1f2937",
      "gridColor": "#e5e7eb",
      "labelFontSize": 12,
      "titleFontSize": 13
    },
    "title": {
      "color": "#1f2937",
      "fontSize": 18,
      "fontWeight": 700,
      "anchor": "middle"
    },
    "range": {
      "category": ["#1e40af", "#b45309", "#15803d", "#6b7280", "#b91c1c"]
    }
  }
}
```

**Semantic discipline in the categorical range** — the palette carries meaning
across the artifact, so use each color only for its assigned role:

- `#1e40af` (blue-800) — correct / principled / primary emphasis
- `#b45309` (amber-700) — Composition family / warning / footer takeaway
- `#15803d` (green-700) — approval / correction
- `#6b7280` (gray-500) — muted / de-emphasised
- `#b91c1c` (red-700) — rejection / critique / target line

**Report typography scale** for the HTML surrounding the chart (not the chart
itself):

| Role                       | Style                                                             |
| -------------------------- | ----------------------------------------------------------------- |
| Report title               | 18pt / 700 / `#1f2937`                                            |
| Section header             | 14pt / 700 / `#1f2937`                                            |
| Body copy                  | 15-16px / `#1f2937` (text) or `#6b7280` (asides)                  |
| REJECTED / APPROVED badges | 12pt / 700 white on red-700 or green-700, `rx="3"` 80x20 pill    |

Print-legibility floor for figures embedded in the artifact: 12px at a 640
viewBox is 5.93pt — the instructional minimum. For the full print-legibility
grammar (formula, `data-print-role` markers, text-fits ladder), the Tailwind
semantic palette, and the composition idioms (BEFORE/AFTER paired panels,
numbered critique callouts, family-band abstracts, 5-Visual Rule dashboards),
see the [`print-svg-style-guide`](../print-svg-style-guide/SKILL.md) skill.
For the engineering discipline that emits SVGs conforming to that guide
(hand-authored `.mjs` generators, `data-sha256` audit hash, dataset-first with
contract tests, dataset inversion), see the
[`figure-generator`](../figure-generator/SKILL.md) skill.

Adapted from _The Defensible Decision_ (Fabio Correa) via the
`dd-book-illustrator` skill in Alex_DDA.

## Attribution

Chart-selection framework (§0 below) distilled from standard visualization
literature — Cole Nussbaumer Knaflic (_Storytelling with Data_), Andy Kirk
(_Data Visualisation_), Stephen Few (_Show Me the Numbers_, _Information
Dashboard Design_), Wexler / Shaffer / Cotgreave (_Big Book of Dashboards_). For
per-chart design tips and the full 48-chart catalog, see _The Defensible
Decision_ chart gallery: <https://www.thedefensibledecision.com/gallery/chart-gallery.html>.
For live examples of every Flint `chartType` across all backends, organized by
semantic category (Bar & Column / Line & Area / Scatter & Points / Distributions
/ Circular & Radial / Tables & Multi-Dimensional / Maps), see the canonical
Flint gallery at <https://microsoft.github.io/flint-chart/#/gallery/vegalite>
(swap `/vegalite` for `/echarts` or `/chartjs` to view the other backends).
flint-chart itself is a Microsoft Research + IDEAS Lab (Renmin University)
project — canonical docs:
<https://microsoft.github.io/flint-chart/#/documentation/getting-started>
(getting started, API reference, architecture, chart-template extension),
<https://microsoft.github.io/flint-chart/#/mcp> (MCP server deployment + full
CLI), and <https://microsoft.github.io/flint-chart/> (project home + live
editor).

## Step 0 — pick the chart (when the user hasn't said which one)

**Skip this step** if the user already named the chart type (e.g. "scatter of
weight vs mpg"). Jump to Step 1 and author the spec. Otherwise, work down this
list before choosing a `chartType`.

### 0.1 One-sentence message — the Big Idea

Before choosing a chart, establish the message it should carry. **Load the
`chart-big-idea` skill and run it now** — look in
`.github/skills/local/chart-big-idea/SKILL.md` first (heir-installed), then
`.github/skills/chart-big-idea/SKILL.md` (baseline).

It does four things this step cannot do inline:

- **Reads the surrounding context first** — the prose next to the insertion
  point, the ticket, the section heading, prior captions — so you do not ask the
  user to re-articulate a claim they already wrote.
- **Questions the intent** — whether the chart should exist at all, and whether
  the stated purpose is the real one. If the intended message and the data
  disagree, that surfaces here rather than after rendering.
- **Elicits the Big Idea** with a three-question ladder, one question at a time,
  when it is not written down anywhere.
- **Asks the TRADITIONAL vs INNOVATIVE style stance**, which changes the
  chartType you pick in §0.2.

The output is a compact Chart Brief. Treat it as the constraint on everything
below: §0.2 selection, §0.4 coverage, and the spec you author in Steps 1-3.

**If that skill is not available**, do the compact version inline
(Knaflic — _Storytelling with Data_):

- What is your unique point of view?
- What is at stake?
- Express it as a complete sentence, not a phrase.

If you cannot write the sentence, ask the user for context before drawing.
"Show sales" is a phrase; "Q4 sales dropped 18% in APAC — that's where our
attention should go this quarter" is a sentence. The sentence shape drives the
chart choice.

### 0.2 Question → family → chart

> **Deeper reference**: the [`chart-vocabulary`](../chart-vocabulary/SKILL.md) skill carries the full 7-goal × ~30-chart catalog, CSAR evaluation loop, override decision table, and 5-visual rule. Reach for it when the 7 rows below aren't enough, when evaluating an AI-suggested chart, or when the artifact will be hand-authored (not rendered via Flint).

| Analytical question            | Family       | Primary chart                                                                                                     | Alternates                                                                                                                                                                                                                                                                               |
| ------------------------------ | ------------ | ----------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rank or compare categories?    | Comparison   | `Bar Chart` (2-15 items; horizontal orientation for long labels)                                                  | `Grouped Bar Chart` (2-4 series), `Stacked Bar Chart` (composition + total; use `stackMode: normalize` for 100% stacked), `Slope Chart` (before/after 2 periods), `Bar Chart` with `row`/`column` facet (many items, aka Small Multiples), `Waterfall Chart` (sequential adds/subtracts) |
| Change over continuous time?   | Trend        | `Line Chart`                                                                                                      | `Area Chart` (volume emphasis), `Bar Chart` + `Line Chart` combo via multi-encoding `y: ["bars", "line"]` (dual metric with different scales), `Sparkline` (in-table trend)                                                                                                              |
| How are values distributed?    | Distribution | `Histogram` (one variable)                                                                                        | `Boxplot` (compare groups + stats), `Violin Plot` (compare + shape, Vega-Lite), `Strip Plot` (every point matters), `Density Plot` (smooth shape), `ECDF Plot` (cumulative)                                                                                                              |
| Correlation between variables? | Relationship | `Scatter Plot`                                                                                                    | `Scatter Plot` with `size` channel (3 vars, aka Bubble), `Regression` (with fit line), `Connected Scatter Plot` (trajectory over time), `Parallel Coordinates` (many vars, ECharts)                                                                                                      |
| Part of a whole?               | Proportion   | `Bar Chart` (most accurate) or `Stacked Bar Chart` with `stackMode: normalize`                                    | `Pie Chart` (**only** if one slice dominates ≥60% OR comparing to 50%), donut (use the center for a KPI) — `Donut Chart` on Vega-Lite, `Doughnut Chart` on Chart.js, `Pie Chart` + `innerRadius` on ECharts, `Treemap` (many/hierarchy, ECharts), `Sunburst` (interactive hierarchy, ECharts), `Funnel` (sequential stages, ECharts)                       |
| Flow between stages?           | Flow         | `Sankey` (linear flow, ECharts)                                                                                   | `Streamgraph` (aesthetic, precision sacrificed), `Heatmap` (matrix pattern), `Chord`-like flows → use `Sankey` instead                                                                                                                                                                   |
| Progress toward a target?      | KPI          | `Bullet Chart` (Few's superior alternative to gauges: actual + target + qualitative ranges in one horizontal bar) | `KPI Card` (single number with delta), `Sparkline` (in-table trend), `Gauge` (ECharts — reserve for high-visibility single-KPI tiles only)                                                                                                                                               |

### 0.3 Anti-patterns — don't recommend

- **Pie with >5 slices** — humans can't compare angles; use `Bar Chart` or `Stacked Bar Chart` with `stackMode: normalize`
- **Pie without a dominant slice** — if no category is ≥60% or the story isn't "X vs the rest", use a `Bar Chart`
- **Word cloud for real analysis** — position and word length distort; use `Bar Chart` of top-N terms (not in Flint; export to another tool)
- **Dual-axis combo without justification** — dual axes mislead by aligning unrelated scales; consider two separate charts
- **Truncated Y-axis on bars** — exaggerates differences; always start `Bar Chart` at zero (Flint does this by default; don't override)
- **Streamgraph when precise values matter** — the flowing baseline sacrifices readability; use `Area Chart` instead
- **Gauge over Bullet** — `Bullet Chart` packs actual + target + qualitative bands in less space with more precision
- **More than 5 series on a Line Chart** — becomes a spaghetti chart; use `row`/`column` facet (Small Multiples) or highlight one series and gray out the rest

### 0.4 Flint coverage — substitutes when the ideal chart isn't native

Some charts from wider visualization literature aren't in Flint's registry.
Recommend the substitute, not the missing chart:

| Ideal chart                                                             | Flint substitute                                               | How                                                                                     |
| ----------------------------------------------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Waffle Chart (10×10 grid %)                                             | `Bar Chart` or `Stacked Bar Chart` with `stackMode: normalize` | Labeled percentage bar communicates the same "N out of 100"                             |
| Chord Diagram (circular flows)                                          | `Sankey` (ECharts backend)                                     | Linear flow is easier to read anyway                                                    |
| Pareto Chart (bars + cumulative %)                                      | `Bar Chart` + `Line Chart` via multi-encoding                  | Sort bars descending, overlay cumulative-% line                                         |
| Beeswarm Plot (every point)                                             | `Strip Plot` with `stepWidth`, `pointSize`, `opacity`          | Jittered points instead of packed; same "every dot is real" story                       |
| Ridgeline Plot (many densities)                                         | `Violin Plot` with `row` facet                                 | Density curves stacked per group                                                        |
| Small Multiples                                                         | any chart with `row` or `column` encoding                      | Native facet support                                                                    |
| Word Cloud / Sentiment / NPS Gauge / Likert / Mind Map / Hierarchy Tree | Not in Flint's scope                                           | Export prepared data to Power BI / Tableau / dedicated tool                             |
| Control Chart / Run Chart / Pareto / Process Capability (SPC)           | Not in Flint's scope                                           | Use a dedicated SPC / Six Sigma tool; Flint isn't built for statistical process control |
| Decomposition Tree / Key Influencers / Smart Narrative (AI-Powered)     | Not in Flint's scope                                           | These are Power BI features; Flint is a chart compiler, not an analytics engine         |
| Table / Matrix (precise value lookup)                                   | Use a data table (not Flint)                                   | Stephen Few's rule — tables for lookup, graphs for pattern                              |

### 0.5 When to fetch a deep reference

Four reference layers, ordered by cost. Fetch the cheapest one that answers the question.

**Chart selection — "which chart for which analytical question?"**

Fetch [The Defensible Decision — Complete Chart Gallery](https://www.thedefensibledecision.com/gallery/chart-gallery.html) when:

- The user asks about a chart not in §0.2 or §0.4
- The user asks "what other charts could work here?"
- The user needs per-chart design tips (axis handling, color, labeling, accessibility)
- The compact table above is ambiguous for the case at hand

The gallery has 48 charts across 10 families with per-chart 💡 tips, distilled from Knaflic / Kirk / Few / Wexler.

**Chart capability — runtime (fastest, always matches the pinned server version)**

Two runtime paths that need no fetch and always reflect the actual server the user has installed:

- **`list_chart_types` MCP tool** — call with `{ backend: 'vegalite' | 'echarts' | 'chartjs' }` to get the current server's chart-type catalog and encoding channels. Zero-fetch; matches whatever `flint-chart-mcp` version is pinned.
- **`flint://chart-types` MCP resource** — a browsable version of the same catalog, exposed as an MCP resource for hosts that surface resources in their UI (e.g., Claude Desktop). Same data, host-native display.

Prefer these over external references when the question is "does the server I'm actually talking to render `<chartType>` on `<backend>`?" They cost nothing and cannot go stale.

> **0.4.1 note.** The underlying `flint-chart` library ships **backend-neutral chart-type recommendation** and **chart-type transformation** APIs (public since 0.3.0), but these are NOT yet exposed as distinct MCP tools — they surface only through the interactive `create_chart_view` MCP App UI. On hosts that render the MCP App (Claude Desktop today; VS Code Copilot expected to follow), the user can switch between compatible chart types in the rendered view without rewriting the spec (e.g., dense Line Chart → compact Sparkline rows; the data roles are preserved). For headless workflows, keep using §0.2 and the `list_chart_types` catalog.

**Chart capability — gallery (canonical live examples)**

Fetch the canonical [Flint gallery](https://microsoft.github.io/flint-chart/#/gallery/vegalite) (maintained by the microsoft/flint-chart team; always tracks the current release) when:

- You need to confirm Flint actually renders a specific `chartType` on a specific backend. Swap the trailing `/vegalite` → `/echarts` or `/chartjs` to view the same catalog for other backends.
- The user is deciding between Vega-Lite vs ECharts vs Chart.js and wants to see the same chart family rendered natively on each backend.
- You need a live example of a chart variant (e.g. a _faceted_ boxplot, a _dodge = local_ grouped bar, a _sparse_ streamgraph) — the gallery shows multiple named variants per `chartType`.
- You want the canonical semantic grouping (Bar & Column / Line & Area / Scatter & Points / Distributions / Circular & Radial / Tables & Multi-Dimensional / Maps) that Flint itself uses to organize its chart registry.

This is the authoritative reference for **what Flint actually does**; §0.2–0.4 above is the compact map, but the gallery is the source of truth for edge cases and backend-specific behavior.

**Chart capability — deep reference (per-backend catalogs + semantic types + API)**

When the gallery is ambiguous or you need to compare all supported charts side-by-side in source form, fetch the upstream markdown at the `0.4.0` tag:

- [`docs/reference-vegalite.md`](https://github.com/microsoft/flint-chart/blob/0.4.0/docs/reference-vegalite.md) — all 35 Vega-Lite chart types with encoding channels and the per-chart `chartProperties` matrix (control type, domain, default, availability)
- [`docs/reference-echarts.md`](https://github.com/microsoft/flint-chart/blob/0.4.0/docs/reference-echarts.md) — the 37 ECharts chart types
- [`docs/reference-chartjs.md`](https://github.com/microsoft/flint-chart/blob/0.4.0/docs/reference-chartjs.md) — the 21 Chart.js chart types
- [`docs/design-semantics.md`](https://github.com/microsoft/flint-chart/blob/0.4.0/docs/design-semantics.md) — the semantic type system (46 registered types across 6 families) that drives Flint's automatic layout; reach for this when Step 3 needs a value the inline list does not cover
- [`docs/api-reference.md`](https://github.com/microsoft/flint-chart/blob/0.4.0/docs/api-reference.md) — canonical `ChartAssemblyInput` structure and every top-level field
- [`docs/overview.md`](https://github.com/microsoft/flint-chart/blob/0.4.0/docs/overview.md) — high-level tour of the compilation pipeline; useful when explaining what Flint does to a new user
- [`docs/README.md`](https://github.com/microsoft/flint-chart/blob/0.4.0/docs/README.md) — the docs index; also documents the abstract channel vocabulary and the two-stage compiler

> **Why `0.4.0` and not `0.4.1`.** The `flint-chart` library repository tags releases independently of the `flint-chart-mcp` npm package. Its tags are `0.1.1`, `0.2.1`, `0.3.0`, `0.4.0` — **there is no `0.4.1` tag**, so `/blob/0.4.1/` URLs 404. The `0.4.0` generated references report 35 Vega-Lite / 37 ECharts / 21 Chart.js chart types, which matches the pinned 0.4.1 server's `list_chart_types` output exactly, so they are the accurate reference for what this plugin runs.

> **The library has more backends than the MCP server exposes.** The upstream docs also ship `reference-plotly.md` (38 chart types) and `reference-excel.md` (18 templates). Neither is reachable through this MCP server: `list_chart_types` accepts only `vegalite`, `echarts`, and `chartjs`, and rejects `plotly` or `excel` with an enum validation error (verified against 0.4.1). Treat Plotly/Excel material in the upstream docs as out of scope for anything you author here.

**Rule of thumb**: Defensible Decision answers "should I use a bar or a boxplot?"; `list_chart_types` and the Flint gallery answer "will Flint's `Bar Chart` on ECharts backend do what I need?"; the deep reference (`docs/reference-*.md`) answers "what exact channels and properties does that combination support?".

### 0.6 Design principles (invoke, don't substitute for reading)

Short-form pointers to the underlying literature. Invoke these when justifying
a choice; read the books themselves for depth.

- **Trustworthy · Accessible · Elegant** (Kirk) — check the chart against all three before shipping
- **Tables for lookup, graphs for pattern** (Few) — if the user wants exact values, a data table beats any chart; use `Bar Table` (Flint) only when you want compact bars with labels
- **Explanatory vs exploratory** (Knaflic) — for stakeholder communication, show the pearl, not the oyster bed; strip clutter aggressively
- **Bullet > Gauge** (Few) — always prefer `Bullet Chart` for KPI-vs-target; reserve `Gauge` for large single-KPI tiles
- **Gestalt** (Knaflic Ch. 3) — group with proximity, distinguish with color/shape, connect with lines, enclose with backgrounds
- **Dashboard = one screen, no scrolling, reduce to essence** (Few — _Information Dashboard Design_) — if it doesn't fit, cut, don't scroll

---

## Step 1 — pick `chartType`

Use one of the registered names **exactly**. Vega-Lite is the default and
broadest backend; the table below lists each Vega-Lite chart type, the
channels it accepts, and its tuning properties (see "Chart-level
properties"). Required channels are noted.

| chartType                  | Channels                                              | Notes / required                                                                                                                                                              |
| -------------------------- | ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `"Scatter Plot"`           | x, y, color, size, opacity, column, row               | x + y required                                                                                                                                                                |
| `"Regression"`             | x, y, size, color, column, row                        | scatter + fit line; props `regressionMethod`, `polyOrder`                                                                                                                     |
| `"Connected Scatter Plot"` | x, y, order, color, detail, column, row               | x + y required; `order` = connection sequence (time/index), so the line traces a trajectory and may self-cross                                                                |
| `"Ranged Dot Plot"`        | x, y, color                                           | dumbbell of two x per category                                                                                                                                                |
| `"Strip Plot"`             | x, y, color, size, column, row                        | jittered points; props `stepWidth`, `pointSize`, `opacity`                                                                                                                    |
| `"Bar Chart"`              | x, y, color, opacity, column, row                     | one discrete + one measure; prop `cornerRadius`                                                                                                                               |
| `"Grouped Bar Chart"`      | x, y, group, column, row                              | `group` = the clustering category; prop `dodge`                                                                                                                               |
| `"Stacked Bar Chart"`      | x, y, color, column, row                              | prop `stackMode`                                                                                                                                                              |
| `"Pyramid Chart"`          | x, y, color                                           | diverging horizontal bars                                                                                                                                                     |
| `"Lollipop Chart"`         | x, y, color, column, row                              | prop `dotSize`                                                                                                                                                                |
| `"Waterfall Chart"`        | x, y, color, column, row                              | `color` = Type column, values `start`/`delta`/`end` only; omit it for auto sign coloring; props `cornerRadius`, `totals`                                                      |
| `"Gantt Chart"`            | y, x, x2, color, detail, column, row                  | x = start, x2 = end                                                                                                                                                           |
| `"Bullet Chart"`           | y, x, goal, color, column, row                        | `goal` required (target)                                                                                                                                                      |
| `"Histogram"`              | x, color, column, row                                 | x = measure to bin; prop `binCount`                                                                                                                                           |
| `"Boxplot"`                | x, y, color, opacity, column, row                     | category + measure; props `whiskerMethod`, `showOutliers`, `dodge`                                                                                                            |
| `"ECDF Plot"`              | x, color, detail, column, row                         | x = measure; cumulative distribution (step line); prop `showPoints`                                                                                                           |
| `"Heatmap"`                | x, y, color, column, row                              | color = the measure                                                                                                                                                           |
| `"Line Chart"`             | x, y, color, strokeDash, detail, opacity, column, row | props `interpolate`, `showPoints`                                                                                                                                             |
| `"Sparkline"`              | x, y, color, detail, row, column                      | x + y required; small-multiple mini trend lines, one per series (series from `color` or `detail`); props `interpolate`, `baseline`, `trendWidth`                              |
| `"Bump Chart"`             | x, y, color, detail, column, row                      | rank-over-time lines                                                                                                                                                          |
| `"Slope Chart"`            | x, y, color, detail, column, row                      | two-period value change; straight segments + end points, one line per category                                                                                                |
| `"Area Chart"`             | x, y, color, opacity, column, row                     | props `interpolate`, `opacity`, `stackMode`                                                                                                                                   |
| `"Range Area Chart"`       | x, y, y2, color, column, row                          | x + y + y2 required; translucent band from `y` (low) to `y2` (high), value axis fits the band (not zero)                                                                      |
| `"Violin Plot"`            | x, y, color, row                                      | x (category) + y (measure) required; mirrored KDE density per category, prop `bandwidth`; **Vega-Lite only**; a genuine `color` subgroup splits two groups or grids 3+ groups |
| `"Streamgraph"`            | x, y, color, column, row                              | center-stacked areas                                                                                                                                                          |
| `"Density Plot"`           | x, color, column, row                                 | prop `bandwidth`                                                                                                                                                              |
| `"Pie Chart"`              | size, color, column, row                              | `size` = slice value (→ angle), `color` = category; props `innerRadius`, `sortSlices`                                                                                         |
| `"Donut Chart"`            | size, color, column, row                              | same channels as Pie; **Vega-Lite only** (Chart.js spells it `"Doughnut Chart"`; ECharts has neither); `innerRadius` defaults to **0**, so set it or you get a pie                |
| `"Rose Chart"`             | x, y, color, column, row                              | polar bars; props `alignment`, `padAngle`, `sortSlices`                                                                                                                       |
| `"Radar Chart"`            | x, y, color, column, row                              | props `filled`, `fillOpacity`, `strokeWidth`                                                                                                                                  |
| `"Candlestick Chart"`      | x, open, high, low, close, column, row                | OHLC all required                                                                                                                                                             |
| `"Bar Table"`              | y, x, color, column, row                              | compact bars + value labels                                                                                                                                                   |
| `"KPI Card"`               | metric, value, goal                                   | big-number tile; prop `behindThreshold`                                                                                                                                       |
| `"Map"`                    | longitude, latitude, color, size, opacity             | bubble map; props `region`, `projection`                                                                                                                                      |
| `"Choropleth"`             | id, color, detail                                     | `id` = geographic key                                                                                                                                                         |

**Donut chart — the type name differs per backend.** There is no single donut
type that works everywhere; pick by backend:

| Backend | Use | Hole behavior |
| --- | --- | --- |
| Vega-Lite | `"Donut Chart"` (added in 0.4.1) | `innerRadius` defaults to **0** — without it the compiled `arc` mark has no hole and looks like a pie. Always set `chartProperties.innerRadius`. |
| Chart.js | `"Doughnut Chart"` (note the spelling) | `innerRadius` defaults to **55**, so it is a donut out of the box |
| ECharts | `"Pie Chart"` + `chartProperties.innerRadius > 0` | no donut type is registered; the hole compiles to a `radius` range |

`"Pie Chart"` with `innerRadius` remains valid on all three backends, so it is
the safe choice when the backend is not yet decided.

**Choosing a bar chart (most common mix-up).** All three take one discrete
category on `x` (or `y`) plus one measure. They differ in how a **second**
category is shown — and each reads that second category from a **different
channel**:

- `"Bar Chart"` — use for a single series. When multiple rows share an `x`, a
  second category on `color` produces stacked segments. For side-by-side bars,
  use `"Grouped Bar Chart"` with the second category on `group`.
- `"Stacked Bar Chart"` — second category on `color`, drawn as **stacked**
  segments within each bar (totals matter). Tune with `stackMode`
  (`stacked` / `normalize` / `layered`).
- `"Grouped Bar Chart"` — second category on the **`group`** channel, drawn as
  **side-by-side (dodged)** bars within each `x` cluster (compare values
  directly). Put the clustering category on `group`, _not_ `color`.

Rule of thumb: comparing parts-to-whole → Stacked; comparing values
side-by-side → Grouped (use `group`); single series → Bar.

**Waterfall color is a special "Type" column, not a free category.** On a
`"Waterfall Chart"` the `color` channel is reserved for a _type_ field whose
values are literally `start`, `delta`, and `end` — it drives which bars anchor
to zero, not an arbitrary grouping. Do **not** bind `color` to an
`Increase`/`Decrease` (or up/down, gain/loss) category: the up/down direction is
already derived from the **sign** of the `y` value and colored automatically
(green up / red down). For the common case, **omit `color` entirely** and let
Flint infer the start/delta/end and per-bar sign coloring. To force which bars
are anchored totals, use the `totals` property (`first`/`last`/`both`), not a
color field. Only bind `color` when you genuinely have a `start`/`delta`/`end`
type column.

**Backend coverage.** Vega-Lite supports all of the above. Other backends
support a subset (verify if targeting a non-VL backend):

- **ECharts** adds: `"Calendar Heatmap"`, `"Gauge"`,
  `"Funnel"`, `"Treemap"`, `"Sunburst"`, `"Sankey"`,
  `"Parallel Coordinates"`, `"Graph"`, `"Tree"`.
- **Chart.js** supports these 21: Scatter Plot, Connected Scatter Plot, Bubble
  Chart, Strip Plot, Bar Chart, Grouped Bar Chart, Stacked Bar Chart, Combo
  Chart, Histogram, Waterfall Chart, Gantt Chart, Line Chart, Bump Chart, Slope
  Chart, Area Chart, Range Area Chart, ECDF Plot, Pie Chart, Doughnut Chart,
  Radar Chart, Rose Chart.

You do not need to call the library or inspect its source to author the
input — pick from this table.

## Step 2 — map fields to channels

Each channel maps to an **encoding object** `{ field, ... }` (or a bare
string shorthand, expanded to `{ field: "<string>" }`):

```json
"encodings": {
  "x": { "field": "weight" },
  "y": "mpg",
  "color": { "field": "origin" }
}
```

**Encoding object fields** (all optional except `field`):

| Field       | Values                                           | Purpose                                             |
| ----------- | ------------------------------------------------ | --------------------------------------------------- |
| `field`     | column name                                      | Bind the channel to a data column                   |
| `type`      | `quantitative`, `nominal`, `ordinal`, `temporal` | Override the inferred encoding type (rarely needed) |
| `aggregate` | `count`, `sum`, `average`, `mean`                | Force an aggregation on a measure channel           |
| `sortOrder` | `ascending`, `descending`                        | Sort direction for a discrete/sorted axis           |
| `sortBy`    | channel name (e.g. `"y"`) or field               | Sort a category axis by another channel's measure   |
| `scheme`    | Vega scheme name (e.g. `viridis`, `redblue`)     | Color scheme for the `color` channel                |

You usually don't need `type`, `aggregate`, or `sortOrder` — they're
inferred from the semantic type. Set them only with specific intent.

**Multi-series (wide → long).** To plot several measure columns as series,
pass an **array** on `x` or `y` (only those two channels). The library
folds them into long form and synthesizes a series/legend field:

```json
"encodings": { "x": { "field": "month" }, "y": ["sales", "profit"] }
```

All array fields must be quantitative, and you cannot also bind `color`
when using the array form (the fold owns the color/legend). This is the
**only** built-in reshape — there is no `transforms`/`fold` property. For any
other shape (long↔wide, an aggregate the encodings can't express, a derived
column, a pivot, a join), reshape the data first with a host tool — pandas/polars,
Arquero/`Array.map`/SQL, or a data/MCP tool — and pass the result as
`data.values`. If you have no way to transform, surface the gap to the developer
rather than inventing a transform property that does not exist.

## Step 3 — annotate with semantic types

**This is the most important step.** Semantic types drive all downstream
decisions — formatting, zero baseline, color scheme, scale direction, and
more. Pick the most specific type for each field. Full registered set:

| Family                     | Semantic types                                                                                      |
| -------------------------- | --------------------------------------------------------------------------------------------------- |
| Temporal (point)           | `DateTime`, `Date`, `Time`, `Timestamp`                                                             |
| Temporal (granule)         | `Year`, `Quarter`, `Month`, `Week`, `Day`, `Hour`, `YearMonth`, `YearQuarter`, `YearWeek`, `Decade` |
| Temporal (span)            | `Duration`                                                                                          |
| Measure (amount)           | `Amount`, `Price`, `Quantity`, `Count`, `Number`                                                    |
| Measure (proportion)       | `Percentage`                                                                                        |
| Measure (signed/diverging) | `Profit`, `PercentageChange`, `Sentiment`, `Correlation`                                            |
| Measure (physical)         | `Temperature`                                                                                       |
| Discrete / rank            | `Rank`, `Score`, `ID`                                                                               |
| Geographic (coord)         | `Latitude`, `Longitude`                                                                             |
| Geographic (place)         | `Country`, `State`, `City`, `Region`, `Address`, `ZipCode`                                          |
| Categorical                | `Category`, `Name`, `Status`, `Boolean`, `Direction`, `Range`                                       |
| Fallback                   | `Unknown`                                                                                           |

What choosing well gets you (automatically):

- `Price` / `Amount` → currency formatting, zero baseline, sequential color
- `Temperature` → diverging color scheme, no forced zero baseline
- `Correlation` → fixed `[-1, 1]` diverging domain
- `Rank` → reversed axis (1 on top), discrete color
- `Date` / `DateTime` → temporal axis with auto-granularity formatting
- `Percentage` → percent formatting, 0–100 domain awareness

If you don't know, use `Quantity` for numbers, `Category` for strings,
`Date`/`DateTime` for date-shaped values. Do **not** invent type names.

## Chart-level properties (`chartProperties`)

`chartProperties` is an optional per-chart tuning map. Set a property only
when the user asks for that behavior — defaults are sensible. These are
**design choices**, not styling overrides (colors/fonts/ticks are still
derived). Values are clamped to the ranges shown.

| Chart type              | Property           | Type / range (default)                                                                                                 | Effect                                                                                                                         |
| ----------------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Bar Chart               | `cornerRadius`     | 0–15 (0)                                                                                                               | Round bar corners (px)                                                                                                         |
| Area / Stacked Bar      | `stackMode`        | `stacked` \| `normalize` \| `center` \| `layered` (unset)                                                              | Stacking behavior; `normalize` = 100%, `center` = streamgraph                                                                  |
| Grouped Bar / Boxplot   | `dodge`            | `auto` \| `local` \| `global` (`auto`)                                                                                 | `local` compacts sparse groups per category; `global` preserves aligned group lanes; leave `auto` unless the user requests one |
| Line / Area / Sparkline | `interpolate`      | `linear` \| `monotone` \| `step` \| `step-before` \| `step-after` \| `basis` \| `cardinal` \| `catmull-rom` (`linear`) | Curve shape                                                                                                                    |
| Line / ECDF Plot        | `showPoints`       | boolean (false)                                                                                                        | Draw point markers on the line                                                                                                 |
| Sparkline               | `baseline`         | `mean` \| `zero` \| `median` \| `none` (`mean`)                                                                        | Reference line per spark row                                                                                                   |
| Sparkline               | `trendWidth`       | 80–600 (240)                                                                                                           | Mini line-plot width (px)                                                                                                      |
| Boxplot                 | `whiskerMethod`    | `iqr` \| `minmax` (`iqr`)                                                                                              | Whisker rule (Tukey 1.5×IQR vs min–max)                                                                                        |
| Boxplot                 | `showOutliers`     | boolean (true)                                                                                                         | Show outlier points (Tukey only)                                                                                               |
| Area                    | `opacity`          | 0.1–1 (0.7)                                                                                                            | Fill opacity                                                                                                                   |
| Scatter                 | `opacity`          | 0.1–1 (1)                                                                                                              | Point opacity                                                                                                                  |
| Strip Plot              | `stepWidth`        | 10–100 (20)                                                                                                            | Jitter spread                                                                                                                  |
| Strip Plot              | `pointSize`        | 0–150 (0=auto)                                                                                                         | Point size                                                                                                                     |
| Strip Plot              | `opacity`          | 0–1 (0=auto)                                                                                                           | Point opacity                                                                                                                  |
| Histogram               | `binCount`         | 5–50 (Auto)                                                                                                           | Maximum bin cap; Auto lets the backend choose                                                                                  |
| Density Plot            | `bandwidth`        | 0.05–2 (0=auto)                                                                                                        | Kernel bandwidth                                                                                                               |
| Pie Chart               | `innerRadius`      | 0–100 (0)                                                                                                              | Donut hole size (>0 → donut)                                                                                                   |
| Donut Chart             | `innerRadius`      | 0–100 (0)                                                                                                              | Hole size on the Vega-Lite donut type; **defaults to 0**, so set it explicitly                                                  |
| Doughnut Chart          | `innerRadius`      | 20–80 (55)                                                                                                             | Hole size on the Chart.js doughnut type; already a donut by default                                                            |
| Pie / Rose              | `sortSlices`       | `none` \| `descending` \| `ascending` (`none`)                                                                         | Order wedges and their legend by slice value                                                                                   |
| Rose Chart              | `alignment`        | `left` \| `center` (`left`)                                                                                            | Wedge alignment                                                                                                                |
| Rose Chart              | `padAngle`         | 0–0.1 (0)                                                                                                              | Gap between slices                                                                                                             |
| Lollipop                | `dotSize`          | 20–300 (80)                                                                                                            | Circle size (px)                                                                                                               |
| Waterfall               | `cornerRadius`     | 0–8 (0)                                                                                                                | Round bar corners                                                                                                              |
| Waterfall               | `totals`           | `auto` \| `none` \| `first` \| `last` \| `both` (`auto`)                                                               | Which bars anchor to zero as totals (only when no Type column)                                                                 |
| Waterfall               | `showTextLabels`   | boolean (false)                                                                                                        | Render value labels on bars                                                                                                    |
| Regression              | `regressionMethod` | `linear` \| `log` \| `exp` \| `pow` \| `quad` \| `poly` (`linear`)                                                     | Fit method                                                                                                                     |
| Regression              | `polyOrder`        | 2–10 (3)                                                                                                               | Polynomial order (when `poly`)                                                                                                 |
| Radar                   | `filled`           | boolean (true)                                                                                                         | Fill the polygon                                                                                                               |
| Radar                   | `fillOpacity`      | 0–0.5 (0.15)                                                                                                           | Polygon fill opacity                                                                                                           |
| Radar                   | `strokeWidth`      | 0.5–4 (1.5)                                                                                                            | Line width                                                                                                                     |
| KPI Card                | `behindThreshold`  | 0–1 (0.5)                                                                                                              | Value/goal ratio cutoff for color                                                                                              |
| Map                     | `region`           | `us` \| `world` \| `auto` (`auto`)                                                                                     | Geographic scope                                                                                                               |
| Map                     | `projection`       | `mercator` \| `equalEarth` \| `orthographic` \| `stereographic` \| `conic` \| `mollweide`                              | Map projection                                                                                                                 |

**Cross-cutting properties** (apply to position/faceted charts when
relevant; set only to force non-default behavior):

- `independentYAxis` (boolean) — faceted charts: give each panel its own
  y-scale. **Not for Sparkline** — 0.3.0 removed this for Sparkline (rows
  always self-scale now); it still applies to other faceted charts.
- `logScale_x` / `logScale_y` (boolean) — force a logarithmic axis.
- `includeZero_x` / `includeZero_y` (boolean) — force the axis to include 0.
- `xAxisType` / `yAxisType` (`temporal` | `nominal`) — force a temporal
  field to render as discrete bands (or vice-versa).

## Parameter overrides — when to reach for them

Overrides exist, but prefer letting semantic types drive decisions. Reach
for an override only when the user's intent genuinely conflicts with the
default:

- **Force an aggregation:** `encodings.y = { field: "sales", aggregate: "sum" }`.
- **Sort a category axis by its measure:** `encodings.x = { field: "name", sortBy: "y", sortOrder: "descending" }`.
- **Pick a color scheme:** `encodings.color = { field: "region", scheme: "tableau10" }`.
- **Override an inferred type:** `encodings.x = { field: "year", type: "ordinal" }` (e.g. treat a year as discrete bands).
- **Resize the chart:** Flint sizes from two numbers — `baseSize` (the _target_
  it aims for, default 400×320) and `canvasSize` (a _hard ceiling_ it may never
  exceed). With dense data the chart stretches from base toward the ceiling.
  - Want a comfortable size that may grow for dense data → set `chart_spec.baseSize = { width, height }`.
  - Want a fixed slot it must fit inside → set `chart_spec.canvasSize = { width, height }` alone; the chart fills it and shrinks to fit, never overflowing. _What you ask for is what you get._
  - Both → aims for `baseSize`, grows toward `canvasSize`, never beyond.
- **Force log / zero baseline:** the `logScale_*` / `includeZero_*` chart
  properties above.

Global layout tuning lives in the top-level `options` object (e.g.
`addTooltips`, band padding, facet sizing). It is rarely needed for
authoring — omit it unless asked.

## Worked examples

In each example `data` is a placeholder — the host binds real rows or a
URL. You author only `chart_spec` and `semantic_types`.

### Scatter plot

User: "Plot car weight vs fuel economy, colored by origin."

```json
{
  "data": { "values": [] },
  "semantic_types": {
    "weight": "Quantity",
    "mpg": "Quantity",
    "origin": "Country"
  },
  "chart_spec": {
    "chartType": "Scatter Plot",
    "encodings": {
      "x": { "field": "weight" },
      "y": { "field": "mpg" },
      "color": { "field": "origin" }
    },
    "baseSize": { "width": 400, "height": 300 }
  }
}
```

### Revenue bar chart with facets, sorted by value

User: "Show revenue by product line, biggest first, one panel per region."

```json
{
  "data": { "values": [] },
  "semantic_types": {
    "product_line": "Category",
    "revenue": "Amount",
    "region": "Region"
  },
  "chart_spec": {
    "chartType": "Bar Chart",
    "encodings": {
      "x": {
        "field": "product_line",
        "sortBy": "y",
        "sortOrder": "descending"
      },
      "y": { "field": "revenue" },
      "column": { "field": "region" }
    }
  }
}
```

### Time series, multiple series (wide → long via array)

User: "Line chart of monthly sales and profit."

```json
{
  "data": { "values": [] },
  "semantic_types": {
    "month": "YearMonth",
    "sales": "Amount",
    "profit": "Profit"
  },
  "chart_spec": {
    "chartType": "Line Chart",
    "encodings": {
      "x": { "field": "month" },
      "y": ["sales", "profit"]
    },
    "chartProperties": { "interpolate": "monotone", "showPoints": true }
  }
}
```

### Donut chart, value on `size`

User: "Show market share by vendor as a donut."

Pie/donut maps the slice value to `size` (rendered as angle) and the
category to `color`. Data is already long (one row per vendor).

On **Vega-Lite**, use the first-class `"Donut Chart"` type. `innerRadius`
defaults to 0, so set it — without it the chart compiles to a plain `arc` mark
with no hole:

```json
{
  "data": { "values": [] },
  "semantic_types": {
    "vendor": "Category",
    "share": "Percentage"
  },
  "chart_spec": {
    "chartType": "Donut Chart",
    "encodings": {
      "size": { "field": "share" },
      "color": { "field": "vendor" }
    },
    "chartProperties": { "innerRadius": 60 }
  }
}
```

On **ECharts**, no donut type is registered — use `"Pie Chart"` with the same
`innerRadius`. On **Chart.js**, use `"Doughnut Chart"` (that spelling), which
already has a hole by default:

```json
{
  "chart_spec": {
    "chartType": "Doughnut Chart",
    "encodings": {
      "size": { "field": "share" },
      "color": { "field": "vendor" }
    }
  }
}
```

### Bullet chart (KPI vs target)

User: "Show each rep's sales against their quota."

```json
{
  "data": { "values": [] },
  "semantic_types": {
    "rep": "Name",
    "sales": "Amount",
    "quota": "Amount"
  },
  "chart_spec": {
    "chartType": "Bullet Chart",
    "encodings": {
      "y": { "field": "rep" },
      "x": { "field": "sales" },
      "goal": { "field": "quota" }
    }
  }
}
```

## What you should NOT do

- **Don't re-emit the data.** Reference columns by name; let the host bind
  `data` (url, variable, or small literal). Never paste large datasets.
- **Don't write backend specs directly** — write the `ChartAssemblyInput`,
  then call the assembler. That's the whole point.
- **Don't invent transforms.** The only built-in reshape is the array form
  on `x`/`y`. If the data shape is wrong for the chart, say so and ask the
  host to reshape it.
- **Don't invent field names.** Reference only columns that exist, spelled
  exactly. If the data is the wrong shape for the chart, reshape it upstream
  rather than guessing column names that aren't there.
- **Don't set `type`/`aggregate`/`sortOrder`** unless intent conflicts
  with the default.
- **Don't pass colors, font sizes, axis tick counts** — the compiler
  derives these. Users fine-tune the _output_ spec.
- **Don't invent semantic type names.** If none fit, use the family
  default (`Quantity`, `Category`, `Date`).
- **Don't call the library to discover channels/types** — this document is
  the authoring reference.

## Validation checklist

Before returning, verify:

1. `chartType` is an exact registered name supported by the target backend.
2. Every `field` referenced in `encodings` is a real column name.
3. Every encoded field has an entry in `semantic_types` (specific type).
4. Required channels for the chart type are present (e.g. Bullet→`goal`,
   Candlestick→`open/high/low/close`, Pie→`size`+`color`).
5. Any `chartProperties` keys are valid for that chart type and in range.
6. You did **not** inline large data or hand-tune derived styling.
7. The data carries no embedded total/subtotal level (e.g. an `all` / `total`
   row) mixed with its components on a stacked, grouped, or colored channel.

## Would Revise If

Revise this skill by 2026-10-22 (90 days) or sooner if any of the following fires:

- [_The Defensible Decision_ chart gallery](https://www.thedefensibledecision.com/gallery/chart-gallery.html) 404s or restructures such that the §0.5 deep-reference URLs no longer resolve — refresh the escalation targets or fold the needed tips into §0 directly.
- Any of the §0.5 upstream deep-reference URLs (`docs/reference-vegalite.md`, `docs/reference-echarts.md`, `docs/reference-chartjs.md`, `docs/design-semantics.md`, `docs/api-reference.md`, `docs/overview.md`, `docs/README.md` at the `0.4.0` tag) 404 or move — refresh the URLs to the newest tag that exists (check `https://api.github.com/repos/microsoft/flint-chart/tags`; the library tags independently of the MCP package, so a matching tag may not exist).
- `flint-chart-mcp` ships a breaking change (chart-type rename, `ChartAssemblyInput` shape change, tool signature change) that this skill doesn't account for — sync §0.4 (Flint coverage) and the worked examples to the new version.
- Any recommendation in §0.2 (question → family → chartType) is refuted by a source we trust (a case study, a Knaflic/Kirk/Few/Wexler update, or field feedback from ≥2 heir workspaces) — retire or rework that row.
- The plugin gets ≥3 heir installs and none of them exercise §0.5 (deep-reference escalation) — that signals the compact table alone is sufficient and §0.5 is decorative; prune it.
- The upstream fork base ([`microsoft/flint-chart/agent-skills/flint-chart-author/SKILL.md`](https://github.com/microsoft/flint-chart/blob/main/agent-skills/flint-chart-author/SKILL.md)) publishes a materially revised body — decide whether to rebase §1-N onto the new upstream or hold on the current fork point. **Do not rebase blindly.** As of 2026-08-05 upstream's skill is itself behind its own generated references: it still teaches "Donut chart: use `Pie Chart` with `innerRadius`" and never names the `Donut Chart` type that `reference-vegalite.md` documents. A straight rebase would regress the backend-specific donut guidance and the corrected `binCount` / `polyOrder` ranges in §Chart-level properties. Diff against the generated `reference-*.md` files, not against upstream's skill.
- **Upstream absorbs chart selection itself.** `flint-chart` 0.3.0 shipped backend-neutral chart-type recommendations and transformations — the capability §0 exists to provide. The pin moved to `0.4.1` on 2026-08-05 after a handshake + catalog + 6-spec compatibility re-test; those recommendations are still reachable only through the `create_chart_view` MCP App UI, not as distinct MCP tools, so §0 stands. If they become tool-reachable and match or beat §0.2 on the same question, §0 is redundant: call the upstream recommender and keep only the framing this plugin adds on top.
- **The backend list changes.** §0.4 and the worked examples assume Vega-Lite / ECharts / Chart.js. The `flint-chart` library carries Plotly (38 chart types, including Funnel, Gauge, and Density Contour) and Excel (18 native Office.js templates), but as of the pinned `0.4.1` server neither is reachable: `list_chart_types` rejects `plotly` and `excel` with an enum validation error. If a future server accepts either, the coverage rules and the "Flint can't express this" escape hatch both need reworking — re-check whenever `list_chart_types` accepts a backend this skill does not name.
