# alex-act-illustrator-plugin

**Visual-authoring bundle for AI agents. Charts, print-quality SVG figures, AI-generated imagery, and a browsable HTML shell — one plugin.**

An [Alex ACT constellation](https://github.com/fabioc-aloha/Alex_ACT_Steward) plugin maintained by Alex_ACT_Steward. Source of truth: [`Alex_ACT_Illustrator_Plugin`](https://github.com/fabioc-aloha/Alex_ACT_Illustrator_Plugin).

## What ships (8 skills + 1 prompt + 3 MCP servers)

Four feature areas, unified by a shared framing gate (`chart-big-idea` Step 0.5 — *does this artifact belong on paper / in this doc at all?*) and a shared verification pass (`render-verify` Prose-coupling — *did the render actually say what it was meant to say?*).

### Feature 1 — Flint (statistical chart authoring)

| Skill | Role |
|---|---|
| `chart-big-idea` | Framing — distill the one-sentence Big Idea + story arc + audience + TRADITIONAL vs INNOVATIVE stance BEFORE picking a chart type |
| `chart-vocabulary` | Selection reference — 7-goal catalog (comparison / trend / distribution / relationship / proportion / flow / deviation), CSAR evaluation loop, 5-visual dashboard rule, gallery pointers |
| `flint-chart` | Selection + rendering — compact question → family → chartType framework distilled from Knaflic / Kirk / Few / Wexler; authors ChartAssemblyInput and renders via the flint-chart-mcp server (Vega-Lite / ECharts / Chart.js) locally |
| `render-verify` | Verification — open the rendered artifact, read its console errors, walk failure catalogs (empty binding / collapsed scale / merged color scale / etc.), Prose-coupling check against the Big Idea |

Prompt: `/render-chart` chains the four skills end-to-end.

### Feature 2 — Print figures (hand-authored print-quality SVG for books + reports)

| Skill | Role |
|---|---|
| `print-svg-style-guide` | Canvas + typography grammar (viewBox math, print-legibility floor, Tailwind semantic palette, four composition idioms: BEFORE/AFTER paired panels with badges, numbered critique callouts, family-band abstracts, 5-Visual Rule dashboards) |
| `figure-generator` | Deterministic `.mjs` generator pattern reading from `data/<slug>.json` with `data-sha256` audit hash, dataset-first + contract tests, dataset-inversion procedure, fix-in-generator-never-in-SVG rule |

Book-tested across 53 shipped figures in *The Defensible Decision* (Fabio Correa).

### Feature 3 — Replicate (AI image generation)

| Skill | Role |
|---|---|
| `replicate-imagery` | Thin routing skill — when to reach for Replicate (FLUX, Ideogram, Recraft, SDXL, Imagen) vs Flint (data charts) vs Mermaid (technical diagrams) vs svg-banner (brand banners); brand alignment via `brand-palette.json`; composes with Replicate's upstream agent skills (prompt-images, find-models, run-models, compare-models, prompt-videos) installable via `npx skills add replicate/skills` |

Opt-in via `REPLICATE_API_TOKEN` — users who never generate AI imagery pay no cost.

### Feature 4 — Shell (browsable HTML surface for galleries + catalogs + reports)

| Skill | Role |
|---|---|
| `docs-shell` | The single-page HTML shell (`index.html` + `manifest.json` at repo root) that renders concatenated markdown as browsable, GitHub-styled documentation with a two-line topnav, per-doc emoji icons, sticky page header, and sidebar TOC. Ships a starter bundle (`starter/index.html`, `starter/manifest.json`, `starter/about.md`). |

## MCP servers

| Server | Required? | Purpose |
|---|---|---|
| `flint` | ✅ Yes | `flint-chart-mcp` — renders ChartAssemblyInput (Vega-Lite / ECharts / Chart.js) locally |
| `replicate` | Optional | `replicate-mcp` — HTTP-API bridge to Replicate. Only needed for `replicate-imagery`. Auth via `REPLICATE_API_TOKEN` env var |
| `playwright` | Optional | `@playwright/mcp` — satisfies `render-verify`'s browser capability on hosts with no built-in browser (chiefly GitHub Copilot CLI). VS Code Copilot heirs omit it |

## Supersedes (Mall history)

This plugin renamed from `flint-chart-plugin` (v0.5.1, 3 skills) on 2026-07-29 and expanded to 8 skills covering the broader visual-authoring surface. Per Mall commit `e739dd6`, its capability now supersedes four previously-published Mall plugins that were removed:

- `data-analytics/visual-vocabulary/` — absorbed as this plugin's `chart-vocabulary` skill (literal adaptation from Alex_ACT_Visual_Storytelling v1.2.0)
- `data-analytics/data-visualization/` — subsumed by `chart-big-idea` + `chart-vocabulary` + `flint-chart §0.2`
- `media-graphics/svg-dashboard-composition/` — subsumed by `print-svg-style-guide` + `figure-generator` (with print-legibility floor math + `data-sha256` provenance)
- `image-generation/imagen/` — Google Vertex direct; this plugin's `replicate-imagery` routes to Imagen 4 via Replicate

## Prerequisites

- **Node.js ≥ 22** — for the `flint-chart-mcp` server
- **`REPLICATE_API_TOKEN`** — optional; only needed for the `replicate-imagery` skill (get one at <https://replicate.com/account/api-tokens>)
- **Installed browser** — optional; only needed if using the `playwright` MCP server (Edge / Chrome / Firefox / WebKit)

## License

MIT (per upstream `Alex_ACT_Illustrator_Plugin/LICENSE`).

## Repo + docs

- Source: <https://github.com/fabioc-aloha/Alex_ACT_Illustrator_Plugin>
- Publisher notes + roadmap: `illustrator/plan.md` in [Alex_ACT_Steward](https://github.com/fabioc-aloha/Alex_ACT_Steward)
