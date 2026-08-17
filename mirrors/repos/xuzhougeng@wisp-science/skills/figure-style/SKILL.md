---
name: figure-style
description: "Correctness and legibility checklist for publication figures, plus a matplotlib sidecar. Load before plotting anything and call `apply_figure_style()` (role-mapped font ladder, outward ticks, frameless legends, 300-dpi saves, CJK-safe fonts). Covers data fidelity, label budgets, axis/colour/type rules, chart choice by data shape, composition, and a mandatory render-then-inspect QA pass (bbox collisions + per-panel visual crops). Helpers: focal_palette, bar_with_points, strip_with_median, end_of_line_labels, panel_letter, set_frame, panel_crops. Multi-panel assembly lives in figure-composer; whole-paper figure ordering in paper-narrative."
license: Apache-2.0
---

# Figure correctness checklist

This skill makes one plot trustworthy and readable. It deliberately has no
house aesthetic — frame, font family, and sizes are all parameters of
`apply_figure_style()`, which must run before the first plotting call.
Multi-panel assembly is `figure-composer`'s job; deciding what each figure in
a paper should argue is `paper-narrative`'s.

Two tiers of rule live below. **Hard rules** — everything under *Tell the
truth*, *Never do*, and *Prove the render*, plus any rule stating a
perceptual or factual invariant (semantic-zero centring, colour-vision
safety, leader-line anchoring) — apply to every plot with no override.
Everything else is a default: deviate when you have a deliberate reason, not
by accident.

## Tell the truth about the data

- **Excluded means excluded.** A row the source data marks excluded either
  disappears from the plot or appears as a clearly distinct open/hatched
  marker named in the key — and it never contaminates a summary statistic
  drawn next to included rows.
- **Peers must be comparable.** Arms measured under different N, budget,
  initialisation, or protocol don't sit side by side as if equivalent. Facet
  them apart or mark the label, and state the difference once in the caption.
- **The figure can't contradict itself.** Before saving, trace every
  categorical label, threshold, and title back to the rule that defines it
  and check each plotted row satisfies it. A row that contradicts its label
  means the figure is wrong.
- **A sentence-title is a claim — test it.** Check the claim against every
  category on the axis. One counterexample means qualifying ("on 3 of 4
  pairs") or demoting the title to a description.
- **State n and what's held fixed.** Any summary mark comes with `n` and the
  unit of replication; any small-multiple that fixes a variable names the
  fixed value — in-panel, or in the caption when the label budget is tight.
- **Context structure comes from references.** A tree, ordering, or topology
  drawn as background (scale bar, category strip) uses an established
  reference. Infer it from the plotted data only when the structure is
  itself the finding.
- **One claim, one number.** Each quantitative claim (accuracy, runtime,
  count) has a single canonical value reused identically in every panel,
  caption, and the abstract — with a definition of what it measures.

## Say less, and say it in the right place

The panel shows the pattern; the caption carries the context. Design for a
general scientific reader, not for yourself.

- **Floor.** Every visually distinct mark must be identifiable from the
  figure alone. Deleting a label may only ever leave the reader asking "why
  is that there?" — never "what is that?". Comparators are named for what
  they are ("no joint training", "prior method"), not a role word
  ("baseline"). Gloss any term a general scientist can't parse.
- **Ceiling.** Per panel: title, axis labels, ticks, series identity
  (labelled once per row of small multiples), and at most 2–3 narrative
  annotations. More than ~6 strings beyond axes/ticks means over budget.
  Identity labels are floor, not budget.
- **Caption material:** n=, held-fixed values, abbreviation expansions,
  exclusion rationale, non-comparability footnotes, methods caveats.
- **Titles state takeaways.** "Robust to gene dropout" works; "Fewer genes"
  doesn't — read it aloud and if a listener would ask "fewer genes *what*?",
  rewrite. A row of small multiples varying one thing gets one row header,
  not per-panel titles.
- **Numbers on marks: headline only.** Print the one value a reader would
  quote; the axis serves the rest.
- **Tie-break: delete and re-read.** If the message survives without the
  label, the label stays gone.

## Axes and scales

- Limits clear the data by at least a marker radius on every side —
  `ax.margins(0.04)` — and no mark or text touches a spine.
- Data using under 40% of an axis calls for a break or a data-floor start
  with an explicit non-zero tick. Nothing may be drawn inside a break gap:
  the gap has no coordinates.
- Log ticks read as `10²`/`1k/10k/100k`, never raw exponents. Filled bars on
  a log value axis are banned outright — bar length would encode the ratio
  to an arbitrary floor. Points with a median tick replace them.
- In a row/column of small multiples, tick *labels* appear once (leftmost or
  bottommost); interior panels keep tick marks only. Panels sharing y and
  differing only in x abut (`wspace≤0.06`) under one row header.
- A panel's data envelope fills ≥75% of its rectangle; dead bands mean
  reshaping the grid, not padding the panel.
- When better-is-up/down isn't obvious from the axis label, put an upright
  "higher = better" cue in the margin — once per row, never per panel, never
  caption-only, and never rotated with rotated text (`goodness_arrow`).
- The full-width figure must fit the venue's double-column width at 300 dpi,
  and adding a schematic or label never squeezes the data panels narrower.

## Colour

- **A colour is a binding.** Once an entity gets a colour, every mark for
  that entity — line, fill, marker, text, heatmap row — reuses it exactly.
  Colour is the cross-reference; nobody should read a legend twice.
- **Few hues, one dominant.** Use the minimum hue count. A focal series is
  saturated and heavy; comparators desaturate and thin (`focal_palette`).
  The focal hue may not collide with any categorical palette in the same
  figure, and the focal series must stay identifiable even at zero width or
  full overlap — outline, marker, or tinted band.
- **Nested categories:** outer level chooses the hue family, inner level
  samples within it.
- **Continuous data:** perceptually uniform sequential map; single-hue ramp
  for rank/size; diverging map for signed values, centred on the *semantic*
  zero (0, 1.0, median) — never the data midpoint.
- **Colour-vision safety.** No red/green binary. Every binary pair survives
  a deuteranopia simulation. One alarm hue is reserved for
  error/anomaly/perturbation and never doubles as a series colour.
- **Two palettes ⇒ two legends,** each adjacent to the first panel using its
  palette.

## Type

- Panel titles are plain-language sentences, regular weight, left-aligned;
  metric names live on the axis.
- **Three sizes, mapped to roles**: base for titles/axis labels/series
  identity, one step down for legends/annotations, one more for ticks
  (`apply_figure_style(sizes=(8,7,6))`). Panel letters alone break the rule
  (bold, larger). A label that doesn't fit gets a layout fix or a shorter
  string, never a fourth size.
- Species, genes, and variables that convention italicises are italicised;
  abbreviations inherit the style and expand once on first use.
- Large numbers wear magnitude suffixes — `4.2B`, `120 kb` — not comma
  grouping.
- On-mark values: ≤2 significant figures, unless rounding would collapse two
  distinct rows, in which case show the separating digit. Text on a fill
  needs 4.5:1 contrast or it moves outside the mark.
- No codebase identifiers as labels: readable name first, code in
  parentheses or the caption.
- Panel letters: bold, top-left, outside the axes box; case per venue
  (`panel_letter(ax, 'a', case=...)`).

## Match the chart to the data

- **Category × number:** show the distribution. Small n → jittered strip
  with median tick (`strip_with_median`); large n → box/violin; mean-as-
  message → bar with raw points *or* interval (`bar_with_points`), not both.
  `errorbar='ci95'` is the t-interval, valid at small n. A missing category
  is marked `n.d.`/`—`/hatched ghost — an empty slot reads as zero — and a
  true zero gets a visible stub.
- **One observation per category:** lollipop (dot plus thin stem to the
  semantic zero), value beside the dot.
- **Series over a continuum:** mean line with markers, raw runs as thin
  translucent traces behind it, series named by text at the line's right end
  (`end_of_line_labels`) rather than a legend box. Per-bin summary glyphs
  are unmistakable-for-raw, identical across series, and drawn under the raw
  points.
- **Overlapping distributions:** stacked panels with shared x, or a
  ridgeline; overlay only when separation is obvious.
- **Matrices:** under ~200 cells, print every value; state the threshold in
  the colourbar label.
- **Embedding scatters** (UMAP/t-SNE/PCA): no ticks or tick labels, a corner
  arrow pair for axes, clusters labelled by thin leaders into whitespace.
- **Prediction vs. observation:** adjacent tracks, identical x and colours,
  alignment carries the comparison; target regions as translucent spans in
  the legend.
- **Insets** connect visibly to their source region: box plus connectors, or
  a wedge.
- **Named-point scatters** direct-label at least max, min, and every flagged
  point via thin leaders — and after rendering, confirm each leader ends
  within a marker radius of its row.

## Composition

- Show what is being measured before the result — plain title, labelled
  schematic, or panel order — and any schematic reuses the exact words and
  glyphs of the data panels.
- A multi-panel figure exists to make one sentence true. Panels that neither
  state, support, nor bound that sentence move to the supplement.
- Legends are frameless, sit in natural whitespace or become direct labels,
  read swatch-first left-aligned, and resolve every distinct glyph.
- Grouped small multiples take one spanning header per group, not repeated
  titles.
- Across a paper, Figure 1 renders the pitch as data (scope, not
  architecture); later figures carry mechanism, evidence, robustness,
  application. Panels are judged against the paper's pitch and move between
  figures when the story requires (`paper-narrative` runs that review).
- Between revision rounds, a passing panel is left alone — decorating a
  clean panel is a regression.

## Never do

Each of these is a correctness failure:

- red vs. green as an opposing pair;
- filled bars on a log value axis;
- a diverging map centred on the data midpoint, or a colourbar whose ticks
  skip the semantic centre;
- an axis title that repeats the tick labels;
- direction-of-goodness explained only in the caption;
- a "reference" line at a value that is one of the plotted points;
- an excluded row inside a plotted summary;
- a leader line whose nearest mark is not its target.

## Prove the render

Run both checks after `fig.savefig(...)` and before presenting the file.

**1. Collision scan.** Assert no visible text box overlaps another or a
spine (a tick label touching its own spine doesn't count), and every text
box sits inside `fig.bbox`:

```python
rend = fig.canvas.get_renderer()
labels = [(t, t.get_window_extent(rend)) for t in fig.findobj(mpl.text.Text)
          if t.get_text().strip() and t.get_visible()]
frames = [(s, s.get_window_extent(rend)) for ax in fig.axes
          for s in ax.spines.values() if s.get_visible()]
own_ticks = {ax: set(ax.get_xticklabels(which='both') + ax.get_yticklabels(which='both'))
             for ax in fig.axes}
hits  = [(a, b) for i, (a, ba) in enumerate(labels)
         for b, bb in labels[i+1:] if ba.overlaps(bb)]
hits += [(t, s) for t, bt in labels for s, bs in frames
         if bt.overlaps(bs) and t not in own_ticks[s.axes]]
assert not hits
```

Move, shorten, or stagger until the scan is clean, re-saving each time.

**2. Visual pass.** Geometry can't see a low-contrast label, crossing
leaders, or two confusable series colours. Crop each panel to its own file
and inspect every crop with Wisp's `view_image` tool:

```python
from PIL import Image

fig.savefig("figure.png")
for letter, box in panel_crops(fig).items():
    Image.open("figure.png").crop(box).save(f"figure-{letter}.png")
```

Leave Python, then `view_image` each crop asking: every glyph legible
against its background? smallest element still has a stroke or stub? leaders
uncrossed? any two series colours confusable? legend beside what it keys?
A visual defect that passed the collision scan is still a defect.

**3. R output.** Prefer explicit `ggsave(filename, plot = p, dpi = 300,
bg = "white", ...)` over the active device; for base graphics open
`png(..., bg = "white", res = 300)`, draw, and always `dev.off()`. Then
assert the file exists and is non-empty and inspect it — a "successful" R
call with a missing, zero-byte, or blank file is a failed render.

---
*Defaults when unsure: fewer hues, direct labels over legends, raw data over
summaries, and name the measurement before showing its result.*
