---
name: research-integrity-audit
description: "学术审查 / research-integrity screening of a manuscript's figures and reported numbers. Finds duplicated, reused, or transformed image panels and data anomalies: copied value blocks, fixed differences/ratios between groups, digit patterns, Benford deviations, GRIM/GRIMMER-inconsistent means and SDs, p-values mismatching their statistics. Use for 学术诚信, 图片查重, 论文图像重复, 数据造假筛查, Source Data 审查, 末位数字, 本福特, GRIM, statcheck, p 值核对, or when the user attaches a PDF, image directory, or CSV/Excel source data to audit."
compatibility: Python 3.10+. Figure track needs Pillow, NumPy, pypdf, and pypdfium2, plus OpenCV with SIFT for the full feature-matching pass. Data track is standard library only, plus openpyxl for .xlsx input.
---

# Research integrity audit

Screen a manuscript's evidence at the smallest meaningful unit: one
experimental image panel, or one independently measured data series. Hashes,
feature matches, and statistical tests find candidates; they do not establish
misconduct, or even duplication, on their own.

## Inputs and workspace

Accept a PDF, a directory of manuscript images, and/or source data (CSV, TSV,
Excel, or a directory of them). Resolve tagged or attached paths before
running anything. Choose tracks from the input and the request:

- **Figure track** (`scripts/audit_figures.py`): PDFs and image directories.
- **Data track** (`scripts/audit_data.py`): Source Data files, supplementary
  tables, and numeric tables transcribed from the PDF.

A PDF usually warrants both unless the user limits scope. Ask for a page range
only when the user did not specify one and scanning the whole PDF would
materially change scope.

Create a new analysis directory such as
`analysis/integrity-audit-YYYYMMDD-HHMM/` with `figures/` and `data/` as the
two script workspaces. Never modify source files, overwrite a prior audit, or
silently omit an unreadable file.

Locate both scripts from the resource paths returned by `use_skill`. If imports
fail, load `local-env-setup`, create a project-local environment, and install
the packages named in `compatibility`. Do not continue with the hash-only
figure fallback when the user requested a strict or exhaustive review.

# Figure track

## F1. Prepare sources

For a PDF:

```text
python audit_figures.py prepare --input PAPER.pdf --output AUDIT_DIR/figures --pages "1-40,49-54"
```

The script extracts qualifying embedded raster images first. It renders a page
only when no large embedded image is available and the page looks like a figure
page, or when `--render-fallback all` is explicitly used. Review
`sources.json`, `skipped.json`, and `sources-contact-sheet.png`; confirm that
every requested figure is represented. A page render still contains captions
and page furniture, so crop the figure before panel splitting.

For a directory:

```text
python audit_figures.py prepare --input FIGURE_DIR --output AUDIT_DIR/figures
```

The script recursively inventories supported images, normalizes EXIF
orientation into audit copies, and records hashes and original paths. It does
not alter the directory.

## F2. Verify panel boundaries

`prepare` writes conservative panel proposals to `panels.json`. They are only
proposals. View every source at full resolution and edit the manifest until:

- every data-bearing photograph, microscopy field, histology tile, plate,
  wound, gel/blot region, or other experimental image has its own box;
- repeated grids are split into individual experimental units, with stable
  labels such as `Fig2-D-r1-c2` rather than anonymous indices;
- labels, legends, scale bars, and axes are not mistaken for independent data
  panels;
- adjacent boxes do not overlap accidentally;
- expected derivatives share a `derivation_group` (for example raw channels
  and merge, overview and inset, or known longitudinal views);
- `kind` records the modality when known (`microscopy`, `histology`,
  `western-blot`, `gel`, `plate`, `wound`, `ivis`, `chart`, or `schematic`).

Run:

```text
python audit_figures.py materialize --workspace AUDIT_DIR/figures
```

Inspect `panels-contact-sheet.png` immediately. Fix bad crops and rerun. Do not
scan until `manifest-warnings.json` has no unexplained out-of-bounds,
duplicate-ID, or overlapping-box warning. Preserve parent/context crops when a
tighter data-only crop is needed for matching.

## F3. Run all-pairs screening

```text
python audit_figures.py scan --workspace AUDIT_DIR/figures --features required
```

The scan combines exact pixel hashes, perceptual hashes, normalized
correlation, and SIFT + RANSAC geometry. It writes `candidates.csv`,
`candidates.json`, `quality-flags.csv`, and `scan-summary.json`. Review every
candidate, not only the first page of the table. Re-scan after any crop change.

Automatic scores are triage signals. Repeated labels, axes, membrane grids,
plate rims, scale bars, and regular tissue texture often produce false
matches. Conversely, different crops, contrast changes, rotation, mirroring,
or recompression can hide a duplicate from hashes and global correlation.

## F4. Confirm or exclude candidates

Generate evidence for selected pairs or the highest-ranked unresolved pairs:

```text
python audit_figures.py evidence --workspace AUDIT_DIR/figures --pair PANEL_A,PANEL_B
python audit_figures.py evidence --workspace AUDIT_DIR/figures --top 20
```

Inspect the full panels, data-only crops, match-line view, registered red/green
overlay, and metrics together. For circular plates or other strong borders,
repeat with a tighter interior crop. For blots, compare both whole blot context
and protein-by-lane crops. For microscopy, distinguish same-field channel
derivation from cross-condition reuse. Consult
`references/review-protocol.md` for modality-specific checks and verdicts.

Never call a pair confirmed from an inlier count or NCC alone. Confirmation
requires geometrically consistent correspondence across independent random
details in the data region, a plausible transform, visual agreement after
registration, and review of the experimental relationship. Record strong
negative controls from visually similar nonmatching panels when possible.

## F5. Review uninformative images

Treat automated quality flags as prompts. Mark a panel uninformative only for a
specific reason such as blank/placeholder content, corruption, unreadably low
resolution, a caption mismatch, or unrelated residual artwork. A negative
result, schematic, control, or visually sparse field is not "useless" merely
because it contains little signal.

# Data track

Read `references/data-protocol.md` before reviewing data findings.

## D1. Collect the numbers

Prefer Source Data and supplementary files over values read from plots. For
tables that exist only in the PDF, transcribe them into a CSV exactly as
printed: keep trailing zeros and signs, one column per group, and verify the
transcription against the rendered page. Do not read values off charts unless
the user asks; if you do, say so and skip digit-level checks for those values.
Also collect every reported mean with its SD and n, and every test reported
with statistic, degrees of freedom, and p (t, F, χ², r, z).

```text
python audit_data.py prepare --input SOURCE_DATA_DIR --output AUDIT_DIR/data
```

`--input` may be repeated and accepts files or directories. `prepare` dumps
every sheet to `tables/` with the precision the authors displayed, and writes
`series.json` with one proposed series per vertical block of numeric cells.
Obvious index columns are proposed with `"include": false`. When the paper
has no tables of raw values, skip `prepare`: create `AUDIT_DIR/data/` and write
`series.json` with only `means` and `tests`.

## D2. Verify the series manifest

Proposals are only a starting point. Edit `series.json` until every included
series is one independently measured variable, design and summary columns are
excluded, expected derivations share a `derivation_group`, and each `label`
names figure, panel, group, and variable. Add reported means and percentages
with their SD and `n` to `means` (GRIM, GRIMMER), and reported test results to
`tests` in APA form (`t(18) = 2.31, p = .032`) for p-value recomputation. The
manifest rules are in `references/data-protocol.md`.

## D3. Run all-pairs screening

```text
python audit_data.py scan --workspace AUDIT_DIR/data
```

The scan runs repeated-run detection and fixed-relation checks across all
series pairs, decimal and terminal-digit tests per series and pooled per
source, Benford where applicable, GRIM and GRIMMER on `means`, and p-value
recomputation on `tests`. It writes `findings.csv`, `findings.json`, and
`scan-summary.json`. The distributional tests share one Benjamini-Hochberg
family. Rescan after any manifest change.

## D4. Confirm or exclude findings

Review every flagged row, not only the first. For each, confirm the cells in
`tables/`, locate the series in the paper, and look for a declared shared
control, normalization, formula, or unit conversion. Weigh shared runs and
exact fixed relations far above distributional anomalies; a single digit or
Benford deviation is not a concern on its own. Record negative controls.

# Report

The final report must include:

1. exact inputs, page scope, figure/source and table counts, and unreadable or
   skipped files;
2. number of reviewed panels and series, all-pairs comparisons, and means,
   SDs, and tests checked or untestable;
3. methods, whether the SIFT pass actually ran, and which data checks were
   applicable;
4. one verdict table covering both tracks: `confirmed duplicate`,
   `high-confidence concern`, `needs raw data`, `expected
   derivative/longitudinal view`, and `excluded false positive`;
5. for figures: panel IDs, source/page, bounding boxes, metrics, and evidence
   paths; for data: series IDs and labels, cell ranges, the relation or
   statistic, p and q with the family size, and the paper location;
6. separately listed quality/uninformative image findings;
7. limitations, especially uncertain panel boundaries, unsplit lanes,
   transcribed rather than source values, and inapplicable tests.

Use neutral language: the audit identifies reuse, similarity, and numerical
inconsistency, not intent. Never compute or report a composite fraud or risk
score. Do not claim the review is exhaustive unless coverage accounting shows
that every in-scope source, experimental-image unit, and data series was
inspected.
