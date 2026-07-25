# flint-chart-plugin

**Pick the right chart for your data, then render it locally — Vega-Lite / ECharts / Chart.js.**

An [Alex — ACT Edition](https://github.com/fabioc-aloha/Alex_ACT_Edition) plugin that pairs a **chart-framing skill**, a **chart-selection + spec-authoring skill**, and a **local MCP server** (upstream [`flint-chart-mcp`](https://www.npmjs.com/package/flint-chart-mcp) from [microsoft/flint-chart](https://github.com/microsoft/flint-chart)) so the agent can go from _"chart this"_ to a rendered image without your data ever leaving the machine.

## What it does

Three capabilities in one plugin:

1. **Chart framing.** Before picking a chart type, the `chart-big-idea` skill distills the one-sentence Big Idea, story arc, audience, and TRADITIONAL vs INNOVATIVE style stance into a compact Chart Brief. It reads the surrounding docs / prose / ticket for an existing Big Idea first (so it doesn't ask you to re-articulate what you already wrote); if none is found, a 3-question elicitation ladder helps you get to one.
2. **Chart selection.** When you ask _"which chart should I use?"_, the `flint-chart` skill walks a compact question → family → chartType framework (Comparison / Trend / Distribution / Relationship / Proportion / Flow / KPI) distilled from Knaflic, Kirk, Few, and Wexler — constrained by the Brief. For deep per-chart design tips, it escalates to [_The Defensible Decision_ gallery](https://www.thedefensibledecision.com/gallery/chart-gallery.html) on demand.
3. **Chart rendering.** When you're ready to draw, the skill authors a compact `ChartAssemblyInput` and the bundled MCP server renders it locally (PNG / SVG) or opens an interactive chart panel via `create_chart_view`. No data leaves the machine.

### Demo — the heart chart, with meaning

> **Big Idea** — _Love's iconic silhouette **is** the four-archetype map of love: the heart's two upper lobes sit in the high-passion quadrants (infatuation left, consummate right), and its two lower sides sit in the low-passion quadrants (indifference left, companionate right)._

That one sentence — the load-bearing output of the [`chart-big-idea`](.github/skills/chart-big-idea/SKILL.md) skill — is what makes this a chart _with meaning_ instead of _decoration_. Everything downstream is a direct consequence of it: the story arc (Relationship with quadrant annotation), the audience read (Read / General / Persuasive), the TRADITIONAL-vs-INNOVATIVE stance (INNOVATIVE, because the heart-as-mnemonic argument is irreducibly geometric), the chartType (layered `scatter_plot`), the 12-layer composition (shaded quadrants → midpoint rules → parametric heart curve → archetype dots → axis subtitles), and the archetype placement (each of the heart's four lobes lands in its matching semantic quadrant).

<p align="center">
  <img src="https://raw.githubusercontent.com/fabioc-aloha/flint-chart-plugin/main/assets/heart-chart.svg" alt="A heart-shaped curve traced onto an Intimacy × Passion plane, rendered as a layered Vega-Lite chart via the flint-chart MCP server. The x-axis is Intimacy (subtitle: trust, vulnerability, shared meaning), the y-axis is Passion (subtitle: desire, chemistry, excitement). Both axes run from low to high. Dashed lines partition the plot into four quadrants labelled INFATUATION (top left), CONSUMMATE LOVE (top right, on a warm cream background), INDIFFERENCE (bottom left, on a cool grey background), and FRIENDSHIP (bottom right). A red heart curve fills the plane; four bold dots sit at the heart's lobes, each labelled with an archetype that matches its semantic quadrant." width="480" />
</p>

**Skill-to-chart flow** — what the `chart-big-idea` skill did before the first line of the Vega-Lite spec was authored:

1. **Step 0 — read context.** The Big Idea was distilled from a written essay on the orthogonality of intimacy and passion, not asked cold from the user.
2. **Step 1 — draft the sentence.** Subject (heart silhouette) + verb (_is_) + implication (the four-archetype map). No 3-question elicitation ladder needed because Step 0 surfaced enough.
3. **Steps 2–4 — story arc + audience + style stance.** Relationship-with-annotation, general-audience read, INNOVATIVE (justified because the argument itself is 2D-geometric).
4. **Step 5 — emit the Chart Brief.** The brief is what `/render-chart` then handed to the [`flint-chart`](.github/skills/flint-chart/SKILL.md) skill for chartType selection and rendering.

The rendered demo ships in [`demos/heart-with-axes/`](demos/heart-with-axes/) — an interactive `report.html` you can open in any browser, plus a folder README with the Chart Brief and layer breakdown. Design decisions and the plugin's own genesis live in [`docs/`](docs/).

## Architecture — two skills, one prompt

```text
/render-chart <request>
      │
      ├─▶ chart-big-idea skill  ─────────────▶  Chart Brief
      │     Step 0: read surrounding context
      │     Step 1: Big Idea (or 3-Q ladder)
      │     Step 2: story arc
      │     Step 3: audience + stakes
      │     Step 4: TRADITIONAL vs INNOVATIVE (asks the user)
      │     Step 5: emit Chart Brief
      │
      └─▶ flint-chart skill  ────────────────▶  rendered chart
            §0.2 selection (constrained by Brief)
            §0.4 Flint-coverage check
            Steps 1-N: author ChartAssemblyInput
            MCP call: create_chart_view / render_chart
```

The Brief locks the framing; the selection skill handles the mechanical chartType lookup and MCP dispatch. Either skill can be invoked standalone if you already have the other half of the picture.

## What ships

| File                                     | Role                                                                                    |
| ---------------------------------------- | --------------------------------------------------------------------------------------- |
| `.github/skills/chart-big-idea/SKILL.md` | Framing skill — Big Idea, story arc, audience, style stance, Chart Brief output         |
| `.github/skills/flint-chart/SKILL.md`    | Selection + spec-authoring skill (§0 chart selection + Steps 1-N `ChartAssemblyInput`)  |
| `.github/prompts/render-chart.prompt.md` | `/render-chart <request>` slash-command entry point (loads both skills in order)        |
| `mcp.json`                               | MCP server registration fragment — merges into your workspace-root `.mcp.json`          |
| `manifest.json`                          | Plugin manifest — declares all shipping assets, install paths, prerequisites            |
| `README.md`                              | This file                                                                               |
| `LICENSE`                                | MIT (dual-copyright: Fabio Correa for plugin work + Microsoft for the flint-chart body) |

## Prerequisites

- **Node.js ≥ 22** on your machine (required for `npx flint-chart-mcp`)
- **MCP-capable host** — VS Code Copilot (1.118+), Claude Desktop, Cursor, or any MCP stdio client
- **Alex — ACT Edition ≥ 3.x** with `.github/skills/local/` and `.github/prompts/local/` registered (default; older heirs see [`mall-installation.instructions.md`](https://github.com/fabioc-aloha/Alex_ACT_Edition/blob/main/.github/instructions/mall-installation.instructions.md) for the manual settings fallback)

## Install

### Option A — via Alex Mall (once landed)

```text
/mall-install flint-chart-plugin
```

### Option B — manual (works today)

```bash
# From your Alex ACT Edition workspace root:
git clone https://github.com/fabioc-aloha/flint-chart-plugin.git /tmp/flint-chart-plugin

# Copy the two skills into your heir-local skill folder
mkdir -p .github/skills/local
cp -r /tmp/flint-chart-plugin/.github/skills/chart-big-idea .github/skills/local/
cp -r /tmp/flint-chart-plugin/.github/skills/flint-chart .github/skills/local/

# Copy the prompt into your heir-local prompt folder
mkdir -p .github/prompts/local
cp /tmp/flint-chart-plugin/.github/prompts/render-chart.prompt.md .github/prompts/local/

# Merge the MCP sidecar into your workspace-root .mcp.json (create if absent)
cat /tmp/flint-chart-plugin/mcp.json  # inspect first
# then merge the "flint" entry under "servers" in your workspace .mcp.json

# Reload VS Code. The MCP server (`flint`) will spawn via `npx` on the first
# tool call (~1-2s cold start; cached thereafter).
```

For deep MCP config (HTTP transport, allowed hosts, deployment, full CLI reference), see the canonical [Flint MCP doc](https://microsoft.github.io/flint-chart/#/mcp).

## Usage patterns

### Ambient (most common)

```text
User: I have monthly sales for 12 regions. Best way to compare them side by side?
Agent: [loads chart-big-idea → Step 0 finds no doc context → asks "what surprised you?" →
        drafts Chart Brief (Big Idea + Comparison arc + TRADITIONAL stance) →
        loads flint-chart → §0.2 recommends Small Multiples with row facet
        (12 > Grouped Bar's 4-series ceiling) → §0.4 confirms Flint coverage →
        asks for the CSV → authors spec → calls create_chart_view]
```

### Explicit slash command

```text
User: /render-chart render a scatter of weight vs mpg colored by origin
Agent: [Big Idea preflight → authors ChartAssemblyInput → calls create_chart_view]
```

### Validation only

```text
User: I hand-wrote this Flint spec — check it: {...}
Agent: [calls validate_chart → returns valid | warnings | computed size]
```

### Backend compilation for embedding

```text
User: Give me the Vega-Lite JSON so I can embed it in our React app
Agent: [calls compile_chart with backend: 'vegalite' → returns native spec, no PNG]
```

### Capability discovery

```text
User: What chart types can Flint make for ECharts?
Agent: [calls list_chart_types with backend: 'echarts' → returns full catalog]
```

## Configuration

The bundled `mcp.json` fragment is minimal:

```jsonc
{
  "servers": {
    "flint": {
      "command": "npx",
      "args": ["-y", "flint-chart-mcp@^0.2.2"],
    },
  },
}
```

### Common variations

**Hardened deployment** (reject local `data.url` file references; accept only inline `data.values`):

```jsonc
{
  "servers": {
    "flint": {
      "command": "npx",
      "args": ["-y", "flint-chart-mcp@^0.2.2", "--disable-file-reference"],
    },
  },
}
```

**Restrict backends** (e.g., Vega-Lite + ECharts only, no Chart.js):

```jsonc
{
  "servers": {
    "flint": {
      "command": "npx",
      "args": [
        "-y",
        "flint-chart-mcp@^0.2.2",
        "--backends",
        "vegalite,echarts",
      ],
    },
  },
}
```

**Air-gapped / corporate npm firewall** — install once when online, then run without npx download:

```bash
npm install -g flint-chart-mcp@0.2.2
```

Then update the fragment:

```jsonc
{ "servers": { "flint": { "command": "flint-chart-mcp", "args": [] } } }
```

**Pinned version** — replace `^0.2.2` with an exact version (`0.2.2`) to lock out even patch updates. Bump to `^0.3.0` when it publishes to npm (as of 2026-07-24, npm `latest` is 0.2.2).

**Naming conflict** — if you already have a `flint` server registered, rename this one to `flint-chart` in your merged `.mcp.json`. The skill and prompt reference the server by tool inventory, not by name.

## What the plugin does NOT do

- Author or render charts outside Flint's supported chart types (Beeswarm, Chord Diagram, Waffle Chart, Word Cloud, SPC charts, AI-Powered analytics — see the skill's §0.4 Flint coverage table for substitutions)
- Transform / aggregate / filter data — do that with your data tool first, then hand Flint the prepared rows
- Handle Power BI, Tableau, or other BI tools — Flint targets Vega-Lite, ECharts, and Chart.js only
- Ship the MCP server code — it downloads from npm on demand (bundling would be 80-120 MB per plugin across 6 OS/arch native-binary variants)

## Publishing to the Mall

This repo is the source-of-truth. The [Alex ACT Plugin Mall](https://github.com/fabioc-aloha/Alex_Skill_Mall) vendors a specific version at `plugins/data-analytics/flint-chart-plugin/`. To publish a new version — or refresh the Mall's vendored README after upstream doc edits — follow the step-by-step runbook in **[`docs/publishing-to-mall.md`](docs/publishing-to-mall.md)**.

Short version: vendor the four installable payload files (2 skills + 1 prompt + `mcp.json`) byte-for-byte into the Mall's plugin folder, copy the README with image `src` rewritten to absolute `raw.githubusercontent.com` URLs, update the Mall's `plugin.json` version, append a curation-log entry, rebase on the Mall's `main`, commit with a severity tag, push. The runbook has the exact commands and a verification checklist.

## Contributing

Issues and PRs welcome. See [`.github/copilot-instructions.md`](.github/copilot-instructions.md) for the repo's conventions (commit-message severity tags, frontmatter rules, lint discipline, falsifiability) — those instructions load automatically for AI agents but are also useful for human contributors.

This repo pairs with:

- Upstream flint-chart (Microsoft): <https://github.com/microsoft/flint-chart>
- Alex ACT Edition (host framework): <https://github.com/fabioc-aloha/Alex_ACT_Edition>
- Alex ACT Plugin Mall (distribution): <https://github.com/fabioc-aloha/Alex_Skill_Mall>

## Attribution

**Chart-selection framework** distilled from standard visualization literature:

- Cole Nussbaumer Knaflic — _Storytelling with Data_ (message-first framing, explanatory vs exploratory, 6 lessons)
- Andy Kirk — _Data Visualisation_ (trustworthy · accessible · elegant)
- Stephen Few — _Show Me the Numbers_, _Information Dashboard Design_ (tables vs graphs, bullet > gauge)
- Wexler / Shaffer / Cotgreave — _Big Book of Dashboards_ (28 case studies)

For per-chart design tips and the full 48-chart catalog, see [_The Defensible Decision_ chart gallery](https://www.thedefensibledecision.com/gallery/chart-gallery.html) — the skill fetches from there on demand when the question is **which chart** to pick.

For live examples of every Flint `chartType` across all backends, organized by semantic category (Bar & Column / Line & Area / Scatter & Points / Distributions / Circular & Radial / Tables & Multi-Dimensional / Maps), see the canonical [Flint gallery](https://microsoft.github.io/flint-chart/#/gallery/vegalite) (swap `/vegalite` for `/echarts` or `/chartjs` to view the other backends) — the skill fetches from there when the question is **what will Flint render**.

**flint-chart** is a [Microsoft Research](https://www.microsoft.com/en-us/research/) + [IDEAS Lab (Renmin University)](https://ideas-lab.net/) project. Canonical docs: [getting started](https://microsoft.github.io/flint-chart/#/documentation/getting-started) (concepts, API reference, architecture, chart-template extension), [MCP server](https://microsoft.github.io/flint-chart/#/mcp) (deployment + full CLI), [project home](https://microsoft.github.io/flint-chart/) (live editor + release notes).

**flint-chart-mcp** is published by Microsoft Corporation to npm at [`flint-chart-mcp`](https://www.npmjs.com/package/flint-chart-mcp) (MIT license).

**The `flint-chart` skill body** in this repo is forked from [`microsoft/flint-chart/agent-skills/flint-chart-author/SKILL.md`](https://github.com/microsoft/flint-chart/blob/main/agent-skills/flint-chart-author/SKILL.md) (MIT-licensed), with a prepended §0 Chart Selection section added by this plugin.

**The `chart-big-idea` skill and the `/render-chart` prompt** are new work in this repo.

## License

MIT (dual-copyright — see [`LICENSE`](LICENSE)).
