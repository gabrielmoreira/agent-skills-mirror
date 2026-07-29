# flint-chart-plugin

**Pick the right chart for your data, then render it locally — Vega-Lite / ECharts / Chart.js.**

An [Alex — ACT Edition](https://github.com/fabioc-aloha/Alex_ACT_Edition) plugin that pairs a **chart-framing skill**, a **chart-selection + spec-authoring skill**, and a **local MCP server** (upstream [`flint-chart-mcp`](https://www.npmjs.com/package/flint-chart-mcp) from [microsoft/flint-chart](https://github.com/microsoft/flint-chart)) so the agent can go from _"chart this"_ to a rendered image without your data ever leaving the machine.

## What it does

Four capabilities in one plugin:

1. **Chart framing.** Before picking a chart type, the `chart-big-idea` skill distills the one-sentence Big Idea, story arc, audience, and TRADITIONAL vs INNOVATIVE style stance into a compact Chart Brief. It reads the surrounding docs / prose / ticket for an existing Big Idea first (so it doesn't ask you to re-articulate what you already wrote); if none is found, a 3-question elicitation ladder helps you get to one.
2. **Chart selection.** When you ask _"which chart should I use?"_, the `flint-chart` skill walks a compact question → family → chartType framework (Comparison / Trend / Distribution / Relationship / Proportion / Flow / KPI) distilled from Knaflic, Kirk, Few, and Wexler — constrained by the Brief. For deep per-chart design tips, it escalates to [_The Defensible Decision_ gallery](https://www.thedefensibledecision.com/gallery/chart-gallery.html) on demand.
3. **Chart rendering.** When you're ready to draw, the skill authors a compact `ChartAssemblyInput` and the bundled MCP server renders it locally (PNG / SVG) or opens an interactive chart panel via `create_chart_view`. No data leaves the machine.
4. **Render verification.** After rendering, the `render-verify` skill opens the result, reads its console errors, and walks a failure catalog — empty binding, collapsed scale, merged color scale, undefined category, double-scaled units. A chart with any of those renders as a **valid image that tells the wrong story**, and `validate_chart` cannot catch it. Only looking does. The skill is not chart-only: a second catalog covers any rendered artifact — 404'd images, clipped text, missing fonts, layout collapse, surviving placeholders.

### Demo — the heart chart, with meaning

> **Big Idea** — _Love's iconic silhouette **is** the four-archetype map of love: the heart's two upper lobes sit in the high-passion quadrants (infatuation left, consummate right), and its two lower sides sit in the low-passion quadrants (indifference left, companionate right)._

That one sentence — the load-bearing output of the [`chart-big-idea`](https://github.com/fabioc-aloha/flint-chart-plugin/blob/main/.github/skills/chart-big-idea/SKILL.md) skill — is what makes this a chart _with meaning_ instead of _decoration_. Everything downstream is a direct consequence of it: the story arc (Relationship with quadrant annotation), the audience read (Read / General / Persuasive), the TRADITIONAL-vs-INNOVATIVE stance (INNOVATIVE, because the heart-as-mnemonic argument is irreducibly geometric), the chartType (layered `scatter_plot`), the 12-layer composition (shaded quadrants → midpoint rules → parametric heart curve → archetype dots → axis subtitles), and the archetype placement (each of the heart's four lobes lands in its matching semantic quadrant).

<p align="center">
  <img src="https://raw.githubusercontent.com/fabioc-aloha/flint-chart-plugin/main/assets/heart-chart.svg" alt="A heart-shaped curve traced onto an Intimacy × Passion plane, rendered as a layered Vega-Lite chart via the flint-chart MCP server. The x-axis is Intimacy (subtitle: trust, vulnerability, shared meaning), the y-axis is Passion (subtitle: desire, chemistry, excitement). Both axes run from low to high. Dashed lines partition the plot into four quadrants labeled INFATUATION (top left), CONSUMMATE LOVE (top right, on a warm cream background), INDIFFERENCE (bottom left, on a cool gray background), and FRIENDSHIP (bottom right). A red heart curve fills the plane; four bold dots sit at the heart's lobes, each labeled with an archetype that matches its semantic quadrant." width="480" />
</p>

**Skill-to-chart flow** — what the `chart-big-idea` skill did before the first line of the Vega-Lite spec was authored:

1. **Step 0 — read context.** The Big Idea was distilled from a written essay on the orthogonality of intimacy and passion, not asked cold from the user.
2. **Step 1 — draft the sentence.** Subject (heart silhouette) + verb (_is_) + implication (the four-archetype map). No 3-question elicitation ladder needed because Step 0 surfaced enough.
3. **Steps 2–4 — story arc + audience + style stance.** Relationship-with-annotation, general-audience read, INNOVATIVE (justified because the argument itself is 2D-geometric).
4. **Step 5 — emit the Chart Brief.** The brief is what `/render-chart` then handed to the [`flint-chart`](https://github.com/fabioc-aloha/flint-chart-plugin/blob/main/.github/skills/flint-chart/SKILL.md) skill for chartType selection and rendering.

The rendered demo ships in [`demos/heart-with-axes/`](https://github.com/fabioc-aloha/flint-chart-plugin/tree/main/demos/heart-with-axes/) — an interactive `report.html` you can open in any browser, plus a folder README with the Chart Brief and layer breakdown. Design decisions and the plugin's own genesis live in [`docs/`](https://github.com/fabioc-aloha/flint-chart-plugin/tree/main/docs/).

## Architecture — three skills, one prompt

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
      ├─▶ flint-chart skill  ────────────────▶  rendered chart
      │     §0.2 selection (constrained by Brief)
      │     §0.4 Flint-coverage check
      │     Steps 1-N: author ChartAssemblyInput
      │     MCP call: create_chart_view / render_chart
      │
      └─▶ render-verify skill  ──────────────▶  verified artifact
            open the artifact (host browser or playwright MCP)
            read console errors BEFORE judging the picture
            walk the failure catalogs
            check the picture against the Big Idea
```

The Brief locks the framing; the selection skill handles the mechanical chartType lookup and MCP dispatch; the verification skill closes the loop that the selection skill deliberately opens (a post-Flint Vega-Lite edit can no longer be validated by the server). Any skill can be invoked standalone if you already have the other parts of the picture.

## What ships

| File                                     | Role                                                                                    |
| ---------------------------------------- | --------------------------------------------------------------------------------------- |
| `.github/skills/chart-big-idea/SKILL.md` | Framing skill — Big Idea, story arc, audience, style stance, Chart Brief output         |
| `.github/skills/flint-chart/SKILL.md`    | Selection + spec-authoring skill (§0 chart selection + Steps 1-N `ChartAssemblyInput`)  |
| `.github/skills/render-verify/SKILL.md`  | Verification skill — failure catalogs, host-capability table, Playwright setup          |
| `.github/prompts/render-chart.prompt.md` | `/render-chart <request>` slash-command entry point (loads all three skills in order)   |
| `.vscode/mcp.json`                       | MCP server registration — `flint` (required) + `playwright` (optional; see Install)     |
| `.vscode/settings.json`                  | Registers the `local/` skill + prompt discovery roots                                   |
| `manifest.json`                          | Plugin manifest — declares all shipping assets, install paths, prerequisites            |
| `README.md`                              | This file                                                                               |
| `LICENSE`                                | MIT (dual-copyright: Fabio Correa for plugin work + Microsoft for the flint-chart body) |

## Prerequisites

- **Node.js ≥ 22** on your machine (required for `npx flint-chart-mcp`)
- **MCP-capable host.** Actively supported and verified: **VS Code Copilot**
  (1.118+), **GitHub Copilot CLI**, and the **GitHub Copilot app**. Other MCP
  stdio clients (Claude Desktop, Cursor, …) should work and their config paths
  are listed below as a courtesy, but they are not verified against each release.
- **Alex — ACT Edition ≥ 3.x** with `.github/skills/local/` and `.github/prompts/local/` registered (default; older heirs see [`mall-installation.instructions.md`](https://github.com/fabioc-aloha/Alex_ACT_Edition/blob/main/.github/instructions/mall-installation.instructions.md) for the manual settings fallback)
- **An installed browser** — _only_ if you enable the optional `playwright` server. Edge, Chrome, Firefox, or WebKit. Nothing is bundled; see [Registering the MCP servers](#registering-the-mcp-servers). Not needed on hosts with built-in browser tools (e.g. VS Code Copilot).

## Install

### Option A — via Alex Mall (once landed)

```text
/mall-install flint-chart-plugin
```

### Option B — manual (works today)

```bash
# From your Alex ACT Edition workspace root:
git clone https://github.com/fabioc-aloha/flint-chart-plugin.git /tmp/flint-chart-plugin

# Copy the three skills into your heir-local skill folder
mkdir -p .github/skills/local
cp -r /tmp/flint-chart-plugin/.github/skills/chart-big-idea .github/skills/local/
cp -r /tmp/flint-chart-plugin/.github/skills/flint-chart .github/skills/local/
cp -r /tmp/flint-chart-plugin/.github/skills/render-verify .github/skills/local/

# Copy the prompt into your heir-local prompt folder
mkdir -p .github/prompts/local
cp /tmp/flint-chart-plugin/.github/prompts/render-chart.prompt.md .github/prompts/local/

# Then: register the local/ roots, and merge the MCP server entry (both below).
```

#### PowerShell (Windows)

```powershell
# From your Alex ACT Edition workspace root:
git clone https://github.com/fabioc-aloha/flint-chart-plugin.git $env:TEMP\flint-chart-plugin
$src = "$env:TEMP\flint-chart-plugin"

# Copy the three skills into your heir-local skill folder
New-Item -ItemType Directory -Force -Path .github\skills\local | Out-Null
Copy-Item "$src\.github\skills\chart-big-idea" -Destination .github\skills\local\ -Recurse -Force
Copy-Item "$src\.github\skills\flint-chart"    -Destination .github\skills\local\ -Recurse -Force
Copy-Item "$src\.github\skills\render-verify"  -Destination .github\skills\local\ -Recurse -Force

# Copy the prompt into your heir-local prompt folder
New-Item -ItemType Directory -Force -Path .github\prompts\local | Out-Null
Copy-Item "$src\.github\prompts\render-chart.prompt.md" -Destination .github\prompts\local\ -Force

# Then: register the local/ roots, and merge the MCP server entry (both below).
```

### Registering the MCP servers

Inspect [`.vscode/mcp.json`](https://github.com/fabioc-aloha/flint-chart-plugin/blob/main/.vscode/mcp.json) first, then **merge** its entries
into your host's config. Merge, don't overwrite — if the file already exists it
almost certainly holds other servers you'd destroy.

| Server       | Required? | Role                                                        |
| ------------ | --------- | ----------------------------------------------------------- |
| `flint`      | Yes       | Renders the chart                                           |
| `playwright` | **No**    | Verification browser — needed on Copilot CLI, not VS Code   |

| Host                         | Config path                       | Top-level key |
| ---------------------------- | --------------------------------- | ------------- |
| VS Code (workspace)          | `.vscode/mcp.json`                | `servers`     |
| Claude Code / Claude Desktop | `.mcp.json` (workspace root)      | `servers`     |
| Cursor                       | `.cursor/mcp.json`                | `servers`     |
| GitHub Copilot CLI           | `~/.copilot/mcp-config.json`      | `mcpServers`  |

Then reload VS Code. Each server spawns via `npx` on the first tool call (~1-2s
cold start; cached thereafter).

#### The optional `playwright` server — omit it on VS Code

The `render-verify` skill names a **capability** (open a page, read its console,
screenshot it), not a product. VS Code Copilot already has built-in browser
tools that satisfy it — they open `file://` with no flags and no browser
download. **On VS Code, drop the `playwright` entry.**

Add it when your host has no browser capability of its own. **GitHub Copilot CLI
is the main case** — it is a terminal agent with no browser, so this server is
the only way it can verify a render rather than assume one.

If you do enable it, three measured facts matter:

- **No bundled browser.** Playwright drives an _installed_ one by channel. The
  shipped config uses `--browser msedge`, because Edge ships with Windows and
  the upstream default (`chrome`) is frequently absent there. Where Edge is not
  installed — typically Linux — switch to `chrome`, `firefox`, or `webkit`, or
  run `npx playwright install <channel>`.
- **`file://` is blocked by default**, which is why the shipped entry carries
  `--allow-unrestricted-file-access`. Without that flag every local render
  silently fails to load.
- **It writes `.playwright-mcp/` into your working directory.** Gitignore it —
  this repo does. Also never pass a bare `filename` to a screenshot call, or the
  image lands in your repo root instead of the ignored folder.

> [!WARNING]
> `--allow-unrestricted-file-access` lets the browser read any file you can read.
> That is a reasonable trade for verifying local artifacts you just produced. It
> is **not** safe combined with browsing untrusted web pages, where a hostile
> page may try to drive the agent into reading and exfiltrating local files. Keep
> this server scoped to local verification; use a separate config without the
> flag for general browsing.

Both servers share the same path traps:

> [!IMPORTANT]
> **VS Code reads `.vscode/mcp.json`, not a workspace-root `.mcp.json`.** Root
> `.mcp.json` is the Claude Code convention. The `servers` schema is identical
> in both, which is exactly why the wrong path looks like it should work — and
> VS Code shows no error, because it isn't parsing a broken file, it's reading
> no file at all.

The CLI is a step worse again:

> [!WARNING]
> **GitHub Copilot CLI fails harder: wrong path _and_ wrong schema.** Its config
> lives at `~/.copilot/mcp-config.json` (or `$COPILOT_HOME/mcp-config.json`) and
> the top-level key is **`mcpServers`**, not `servers`. Pasting the `servers`
> block there produces the same silent nothing. Easiest route is to let the CLI
> write the file for you: run `/mcp add` inside a session rather than editing
> the JSON by hand.

### Registering the `local/` roots

VS Code discovers skills in `.github/skills/` and prompts in `.github/prompts/`.
It does **not** search their subfolders, so a plugin installed under `local/`
loads nothing — again with no error. On an Alex ACT Edition heir these roots are
already registered; on a plain VS Code workspace, add them to
`.vscode/settings.json`:

```jsonc
{
  "chat.agentSkillsLocations": { ".github/skills/local": true },
  "chat.promptFilesLocations": { ".github/prompts/local": true }
}
```

Keep these **additive** — don't disable the defaults. Your own skills and prompts
stay in the default roots; installed plugins live under `local/`, and the two
sets coexist. (Each skill's `name` must match its parent directory name, which
all three of this plugin's skills satisfy.)

This repo dogfoods the same wiring — see [`.vscode/settings.json`](https://github.com/fabioc-aloha/flint-chart-plugin/blob/main/.vscode/settings.json)
and [`.vscode/mcp.json`](https://github.com/fabioc-aloha/flint-chart-plugin/blob/main/.vscode/mcp.json).

### If the tools still don't appear

If the `flint` tools are missing after a reload:

1. **Approve the server.** `Ctrl+Shift+P` → **MCP: List Servers** → `flint` → **Start**. VS Code will not launch a local stdio server until you approve it.
2. **Read the server output.** Same menu → **Show Output**. Startup crashes surface there and nowhere else.
3. **Restart the chat session.** A window reload is not always enough — the agent's tool inventory can stay stale until the session restarts.

### Verify your install

Four checks, in this order. Each isolates a different half of the system, so the
first one that fails tells you where the fault is.

1. **Server.** From a clone of this repo, run the bundled checker — no agent, no
   host, and no MCP client needed:

   ```bash
   node scripts/verify-install.mjs
   ```

   It reads the pin from [`.vscode/mcp.json`](https://github.com/fabioc-aloha/flint-chart-plugin/blob/main/.vscode/mcp.json) so it verifies
   the version your config actually requests, handshakes over stdio, and asserts
   all five tools are advertised. Exit 0 means the server is healthy and any
   remaining fault is on the client side — config path, trust, or a stale
   session. This is the one check that must not depend on your agent, since your
   agent may be the thing that's broken.

   Two optional flags, useful when changing the pin: `--catalog` lists the
   backends and per-backend chart-type counts, and `--compat` validates the
   chart-property patterns this plugin documents. Both report version-dependent
   facts that the docs would otherwise assert blindly.

   Installed from the Alex Mall instead? That vendors only the skills, the
   prompt, and `mcp.json` — no `scripts/`. Either clone this repo to run the
   checker, or ask your agent to probe `npx -y flint-chart-mcp` over stdio with
   an `initialize` handshake followed by `tools/list`; a `serverInfo` block plus
   a `tools` array means the same thing.
2. **Client.** Ask the agent whether it can see `render_chart`, `compile_chart`,
   `validate_chart`, `list_chart_types`, and `create_chart_view`. All five, or
   your host isn't reading the config you edited.
3. **Skills and prompt.** Type `/` in chat. `chart-big-idea`, `flint-chart`,
   `render-verify`, and `render-chart` should all appear. If the MCP tools work
   but these don't, the discovery roots above are missing.
4. **Render.** Ask for any chart. `list_chart_types` should return 34 Vega-Lite
   chart types, and a render should produce an image.

This repo runs the same four checks against its own [`.vscode/`](https://github.com/fabioc-aloha/flint-chart-plugin/tree/main/.vscode/) config —
last verified 2026-07-25 against `flint-chart-mcp` 0.2.2 (MCP protocol
`2024-11-05`).

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

**Pinned version** — the pin is `^0.2.2` **by decision, not by lag**. Caret on a `0.x` version means `>=0.2.2 <0.3.0`, so 0.3.x and 0.4.x are never picked up automatically. Public npm `latest` is already 0.4.0, but it is unreachable from Microsoft corporate machines (their npm mirror stops at 0.2.2), and most heirs of this plugin are corpnet repos — so bumping would break more adopters than it helps. See the Unreleased section of [`CHANGELOG.md`](https://github.com/fabioc-aloha/flint-chart-plugin/blob/main/CHANGELOG.md) for the full rationale and the conditions that would change it. If you check versions yourself, run `npm config get registry` first: a corporate mirror can report a stale `latest` that is not the public one.

**Naming conflict** — if you already have a `flint` server registered, rename this one to `flint-chart` in your merged config. The skill and prompt reference the server by tool inventory, not by name.

## What the plugin does NOT do

- Author or render charts outside Flint's supported chart types (Beeswarm, Chord Diagram, Waffle Chart, Word Cloud, SPC charts, AI-Powered analytics — see the skill's §0.4 Flint coverage table for substitutions)
- Transform / aggregate / filter data — do that with your data tool first, then hand Flint the prepared rows
- Handle Power BI, Tableau, or other BI tools — Flint targets Vega-Lite, ECharts, and Chart.js only
- Ship the MCP server code — it downloads from npm on demand (bundling would be 80-120 MB per plugin across 6 OS/arch native-binary variants)

## Publishing to the Mall

This repo is the source-of-truth. The [Alex ACT Plugin Mall](https://github.com/fabioc-aloha/Alex_Skill_Mall) vendors a specific version at `plugins/data-analytics/flint-chart-plugin/`. To publish a new version — or refresh the Mall's vendored README after upstream doc edits — follow the step-by-step runbook in **[`docs/publishing-to-mall.md`](https://github.com/fabioc-aloha/flint-chart-plugin/blob/main/docs/publishing-to-mall.md)**.

Short version: vendor the five installable payload files (3 skills + 1 prompt + `mcp.json`) byte-for-byte into the Mall's plugin folder, copy the README with image `src` rewritten to absolute `raw.githubusercontent.com` URLs, update the Mall's `plugin.json` version, append a curation-log entry, rebase on the Mall's `main`, commit with a severity tag, push. The runbook has the exact commands and a verification checklist.

## Contributing

Issues and PRs welcome. See [`.github/copilot-instructions.md`](https://github.com/fabioc-aloha/flint-chart-plugin/blob/main/.github/copilot-instructions.md) for the repo's conventions (commit-message severity tags, frontmatter rules, lint discipline, falsifiability) — those instructions load automatically for AI agents but are also useful for human contributors.

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

MIT (dual-copyright — see [`LICENSE`](https://github.com/fabioc-aloha/flint-chart-plugin/blob/main/LICENSE)).
