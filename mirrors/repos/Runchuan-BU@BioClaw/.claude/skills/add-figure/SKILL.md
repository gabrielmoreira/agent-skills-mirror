---
name: add-figure
description: Add a Python-only figure reference skill to a BioClaw installation. Use when the user wants publication-quality plotting guidance inside agent containers without adding source-code features. Creates `container/skills/figure/` with a Python-only `SKILL.md` and a root-level `seaborn_reference.md`.
disable-model-invocation: true
---

# Add Figure Skill

This skill adds a new runtime skill at `container/skills/figure/` for publication-quality plotting inside BioClaw containers.

## What This Adds

- A new container runtime skill: `container/skills/figure/SKILL.md`
- A flattened seaborn reference: `container/skills/figure/seaborn_reference.md`
- Python-only plotting guidance for `matplotlib`, `seaborn`, `scanpy`, and related Python tools
- Journal palette constants translated to Python hex lists and dicts

## What This Must Not Change

- Do not modify any source files in `src/`, `container/agent-runner/`, or other app code
- Do not modify `Dockerfile`
- Do not modify sync logic in `src/container-runner.ts`
- Do not add any R dependency or R code examples

The feature is entirely delivered as a skill, not as application code.

## Why This Shape

BioClaw already syncs `container/skills/<skill>/` into `/home/node/.claude/skills/<skill>/` inside the container.

The sync only copies one directory level, so any reference material needed at runtime must live directly under `container/skills/figure/`, not under nested `references/`.

## Implementation Steps

Run all steps directly. Only pause if the repo already contains a user-modified `container/skills/figure/` and you need conflict resolution.

### 1. Verify Current State

Check:

```bash
pwd
ls -la container/skills
test -e container/skills/figure && echo "figure skill already exists" || echo "no figure skill yet"
```

If `container/skills/figure/` already exists, inspect it before changing anything.

### 2. Create `container/skills/figure/`

Create:

```text
container/skills/figure/
├── SKILL.md
└── seaborn_reference.md
```

Do not add nested directories.

### 3. Write `container/skills/figure/SKILL.md`

Create a Python-only runtime skill with frontmatter like:

```yaml
---
name: figure
description: Python-only reference for publication-quality academic figures inside BioClaw containers. Covers matplotlib, seaborn, scanpy-style workflows, journal palette constants, bioinformatics plot standards, anti-patterns, and a pre-flight quality checklist.
---
```

The file must include all of the following sections.

#### Required Section: Purpose and Rules

State clearly:

- Python only
- Save outputs to `/workspace/group/`
- Prefer `.pdf` or `.svg` for final figures
- Use `.png` only when raster is necessary, at `dpi >= 300`
- Root-level seaborn reference lives at `/home/node/.claude/skills/figure/seaborn_reference.md`

#### Required Section: Tool Routing

Include a short table routing these tasks to Python tools:

- General plots -> `seaborn` + `matplotlib`
- Annotation-heavy custom figures -> `matplotlib`
- Single-cell embeddings -> `scanpy`
- Clustered heatmaps -> `seaborn.clustermap`
- Set intersections -> `upsetplot`
- Survival curves -> `lifelines` + `matplotlib`
- Enrichment bubble plots -> `seaborn.scatterplot`

#### Required Section: Chart Type Selection

Include a Python-only chart selection table for:

- Histogram / density / violin
- Group comparison
- Scatter / hexbin
- Line / area
- Heatmap / clustered heatmap
- Volcano plot
- UMAP / t-SNE
- Relative composition
- Alpha diversity
- Beta diversity / ordination
- Enrichment bubble plot
- Kaplan-Meier curve
- Multi-panel layout

Every row must reference Python functions only.

#### Required Section: Publication-Quality Defaults

Include a code block defining:

- `BIO_STYLE`
- `SAVEFIG_KWARGS`
- `finish_axis(ax)`

The style must:

- Use sans-serif fonts with Arial/Helvetica fallbacks
- Remove top and right spines
- Set figure and save DPI to 300
- Set `savefig.bbox` to `tight`
- Keep visible text at publication-safe sizes
- Preserve editable SVG text with `svg.fonttype = "none"`

#### Required Section: Universal Standards

Document:

- Vector first
- Raster at 300+ DPI
- No on-image title
- Labeled axes with units
- Legend placement
- Panel labels for multi-panel figures
- Tight margins
- Minimum text size

#### Required Section: Color Standards

Include:

- Discrete palette usage guidance
- Continuous palette usage guidance
- Colorblind and consistency rules
- Explicit ban on `jet` and `rainbow`

#### Required Code Block: Python Palette Constants

Define a `JOURNAL_PALETTES` dict containing these keys:

- `NPG`
- `Lancet`
- `AAAS`
- `JCO`
- `NEJM`
- `D3_CATEGORY10`
- `D3_CATEGORY20`

Define a `MATERIAL_PALETTES` dict containing named color families such as:

- `red`
- `pink`
- `purple`
- `deep_purple`
- `indigo`
- `blue`
- `light_blue`
- `cyan`
- `teal`
- `green`
- `light_green`
- `lime`
- `yellow`
- `amber`
- `orange`
- `deep_orange`
- `brown`
- `gray`
- `blue_gray`

Also define:

```python
def apply_palette(name, n=None):
    colors = JOURNAL_PALETTES[name]
    return colors if n is None else colors[:n]
```

Use these exact journal palette hex values:

```python
JOURNAL_PALETTES = {
    "NPG": [
        "#E64B35", "#4DBBD5", "#00A087", "#3C5488", "#F39B7F",
        "#8491B4", "#91D1C2", "#DC0000", "#7E6148", "#B09C85",
    ],
    "Lancet": [
        "#00468B", "#ED0000", "#42B540", "#0099B4",
        "#925E9F", "#FDAF91", "#AD002A", "#ADB6B6",
    ],
    "AAAS": [
        "#3B4992", "#EE0000", "#008B45", "#631879", "#008280",
        "#BB0021", "#5F559B", "#A20056", "#808180", "#1B1919",
    ],
    "JCO": [
        "#0073C2", "#EFC000", "#868686", "#CD534C", "#7AA6DC",
        "#003C67", "#8F7700", "#3B3B3B", "#A73030", "#4A6990",
    ],
    "NEJM": [
        "#BC3C29", "#0072B5", "#E18727", "#20854E",
        "#7876B1", "#6F99AD", "#FFDC91", "#EE4C97",
    ],
    "D3_CATEGORY10": [
        "#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD",
        "#8C564B", "#E377C2", "#7F7F7F", "#BCBD22", "#17BECF",
    ],
    "D3_CATEGORY20": [
        "#1F77B4", "#AEC7E8", "#FF7F0E", "#FFBB78", "#2CA02C",
        "#98DF8A", "#D62728", "#FF9896", "#9467BD", "#C5B0D5",
        "#8C564B", "#C49C94", "#E377C2", "#F7B6D2", "#7F7F7F",
        "#C7C7C7", "#BCBD22", "#DBDB8D", "#17BECF", "#9EDAE5",
    ],
}
```

Translate the Material palette into Python hex lists under `MATERIAL_PALETTES`. Keep it as a dict of family name -> 10-step tonal list.

#### Required Section: Bioinformatics-Specific Plot Standards

Include Python examples and standards for:

- UMAP / t-SNE
- Heatmap
- Volcano plot
- Relative composition bar plot
- Alpha diversity
- Beta diversity / ordination
- Enrichment bubble plot
- Survival curve

The examples must use Python syntax only.

The section must explicitly require:

- UMAP/t-SNE axes without ticks
- Heatmaps with visible color bars
- Volcano plots with cutoff lines at `abs(log2FC) >= 1` and `padj <= 0.05`
- Relative abundance y-axis constrained appropriately
- Alpha diversity shown with both summary and individual points
- PCoA axes labeled with explained variance when available
- Survival plots labeled with time unit

#### Required Section: Quality Checklist

Include a pre-flight checklist covering:

- Output format / DPI
- Axis labels and units
- No in-figure title
- Legend placement
- Panel labels
- Color consistency
- Colorblind-safe interpretation
- Statistical annotation correctness
- Minimum font size
- No chartjunk

#### Required Section: Anti-Patterns

Include a table forbidding at least:

- Default unstyled plots
- Too many cluster colors in one panel
- UMAP/t-SNE with ticks
- Heatmap without labeled color bar
- Volcano plot without thresholds
- Bar plots that hide variability
- Overlapping labels

#### Required Section: Working Rules

End with rules such as:

- Prefer reusable plotting code over one-off snippets
- Keep filenames stable and descriptive
- Keep figure code reproducible in the workspace
- Fall back to plain `matplotlib` if a preferred library is unavailable

### 4. Write `container/skills/figure/seaborn_reference.md`

Create a root-level seaborn reference file for shallow-copy sync. It should be concise but directly usable.

It must include:

- Title: `# Seaborn API Reference`
- Source note pointing to https://seaborn.pydata.org/
- Objects interface example using `seaborn.objects as so`
- Short tables for marks and stats
- Sections for:
  - Relational plots
  - Distribution plots
  - Categorical plots
  - Regression plots
  - Matrix plots
  - Multi-plot grids
  - Style and context
- A final `## Common Patterns for Bio` section with examples for:
  - Volcano plot
  - Expression heatmap with clustering
  - Violin + strip
  - UMAP embedding

Keep the file at the skill root. Do not place it under `references/`.

### 5. Explicit Removals and Exclusions

The generated `container/skills/figure/SKILL.md` must not contain:

- `AutoFigure-Edit`
- `ggplot2`
- `ComplexHeatmap`
- `clusterProfiler`
- `BioCircos`
- `circlize`
- `R Graph Gallery`
- `r4ds`
- Any `geom_` examples
- Any R code fences

This skill is intentionally Python-only because the BioClaw container does not include R.

### 6. Validation

Run:

```bash
ls -la container/skills/figure

rg -n "AutoFigure|ggplot2|ComplexHeatmap|clusterProfiler|BioCircos|circlize|R Graph Gallery|r4ds|geom_" \
  container/skills/figure

rg -n "JOURNAL_PALETTES|MATERIAL_PALETTES|NPG|Lancet|AAAS|JCO|NEJM|D3_CATEGORY10|D3_CATEGORY20" \
  container/skills/figure/SKILL.md
```

If Docker is available, also verify in-container readability:

```bash
docker run --rm --entrypoint sh \
  -v "$PWD/container/skills/figure:/home/node/.claude/skills/figure:ro" \
  bioclaw-agent:latest \
  -lc 'ls -1 /home/node/.claude/skills/figure && sed -n "1,10p" /home/node/.claude/skills/figure/SKILL.md'
```

### 7. Final Output to the User

Report:

- Which files were created
- That no source files were modified
- That the skill is Python-only
- Validation results

If preparing for a PR, remind the user that the PR should only include the new contributed skill under `.claude/skills/add-figure/` when contributing back to the BioClaw repo.
