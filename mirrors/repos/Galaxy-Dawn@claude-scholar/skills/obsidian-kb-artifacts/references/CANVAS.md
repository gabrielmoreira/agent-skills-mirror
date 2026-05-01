# CANVAS

Canvas files are optional derived artifacts stored under `Maps/`. They are not the source of truth.

## Placement and scope

- Default path: `Maps/*.canvas`
- Default auto-maintained canvas: `Maps/literature.canvas`
- Other canvases are explicit-only unless a workflow clearly requires them
- Keep canvas references project-local unless the user explicitly asks for cross-project mapping

## Core JSON structure

Use the standard JSON Canvas shape:

```json
{
  "nodes": [],
  "edges": []
}
```

Each node needs a stable `id`, coordinates (`x`, `y`), and size (`width`, `height`).
Each edge needs `id`, `fromNode`, and `toNode`.

## Recommended node types

- `file` node: canonical note under `Sources/*`, `Knowledge/*`, `Experiments/*`, `Results/*`, `Writing/*`
- `text` node: short synthesis, legend, gap summary, or section heading
- `link` node: external URL when the relationship should stay outside the vault
- `group` node: visual cluster for a topic, method family, dataset family, or review bucket

Avoid treating free-form text nodes as a second knowledge store. Durable content belongs in markdown notes first.

## File-node conventions

Use `file` nodes for canonical notes that already exist on disk.

- paper/source note -> point to `Sources/Papers/*` or other `Sources/*`
- synthesis note -> point to `Knowledge/*`
- experiment note -> point to `Experiments/*`
- stable result/report -> point to `Results/*` or `Results/Reports/*`

File nodes should reference existing files only. If the note does not exist yet, create the note first or use a temporary `text` node that clearly indicates draft intent.

## Edge conventions

Use edges to express relationship semantics, not decoration.

- method extends method
- paper uses dataset
- result supports claim
- gap motivates experiment
- report summarizes experiment

When labels are supported in the producing workflow, keep them short and explicit:
- `uses`
- `extends`
- `compares`
- `supports`
- `contradicts`
- `motivates`
- `summarizes`

Do not draw unlabeled dense meshes when a few explicit edges communicate the structure better.

## Group and color conventions

Use groups to organize major clusters such as:
- `Methods`
- `Datasets`
- `Claims`
- `Gaps`
- `Experiments`
- `Results`

Use color sparingly and consistently. Color is a navigation aid, not a semantic database.

Suggested pattern:
- one group color per cluster family
- neutral text nodes for summaries
- do not encode critical meaning only through color

## Layout conventions

- Keep 50–100 px spacing between unrelated nodes
- Align related file nodes in rows or columns
- Put source papers on one side, synthesis notes in the middle, and gaps / experiments / results downstream
- Avoid overlapping groups
- Prefer a stable, readable layout over a compact but fragile layout

## Recommended `Maps/literature.canvas` structure

For literature workflow, prefer this shape:

1. `Sources/Papers/*` file nodes for the key papers
2. `Knowledge/*` file nodes for:
   - `Literature Overview`
   - `Method Taxonomy`
   - `Research Gaps`
3. `text` nodes for short bridge summaries where needed
4. groups for `Methods`, `Datasets`, `Gaps`, and `Results`
5. edges showing:
   - paper -> method family
   - paper -> dataset
   - paper -> gap or limitation
   - gap -> experiment direction

This keeps the canvas derived from canonical notes instead of replacing them.

## Validation checklist

Before treating a canvas as valid, check:

- every `file` node target exists
- every edge endpoint points to an existing node id
- node ids are unique
- groups do not reference missing child nodes
- archived notes are either intentionally preserved or relinked; no silent dangling references
- the canvas adds navigation value instead of duplicating a markdown table

## What not to put in Canvas

- raw source-of-truth metadata that belongs in `_system/registry.md`
- long-form synthesis that belongs in `Knowledge/*`
- unstable scratch thinking that should remain in `Daily/*`
- auto-generated project-wide mega-graphs by default

Generate or update a canvas only when the user explicitly asks for it, or when `Maps/literature.canvas` is part of the literature workflow.
