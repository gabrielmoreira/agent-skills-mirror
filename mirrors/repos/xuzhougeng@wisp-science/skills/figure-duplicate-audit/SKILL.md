---
name: figure-duplicate-audit
description: "Audit scientific figures for duplicated, reused, transformed, or uninformative image panels. Use for \u56fe\u7247\u67e5\u91cd, \u8bba\u6587\u56fe\u50cf\u91cd\u590d, PDF figure \u5ba1\u6838, when the user attaches a PDF, asks to review selected PDF pages, or tags a directory containing manuscript input images. For PDFs, extract large embedded figure images before splitting them into panels; for directories, preserve originals and split every composite image directly. Produces a reviewed panel manifest, all-pairs candidate table, visual evidence, coverage accounting, and a cautious integrity report."
compatibility: Requires Python 3.10+, Pillow, NumPy, pypdf, and pypdfium2. OpenCV with SIFT support is required for the full feature-matching pass.
---

# Figure duplicate audit

Audit at the smallest meaningful experimental-image unit. Hashes and feature
matches find candidates; they do not establish misconduct or even duplication
on their own.

## Inputs and workspace

Accept either one PDF or one directory of manuscript images. Resolve tagged or
attached paths before running anything. Ask for a page range only when the user
did not specify one and scanning the whole PDF would materially change scope.

Create a new analysis directory such as `analysis/figure-audit-YYYYMMDD-HHMM`.
Never modify source images, overwrite a prior audit, or silently omit an
unreadable file.

Locate this skill's `scripts/audit_figures.py` from the resource paths returned
by `use_skill`. If imports fail, load `local-env-setup`, create a project-local
environment, and install the packages named in `compatibility`. Do not continue
with the hash-only fallback when the user requested a strict or exhaustive
review.

## 1. Prepare sources

For a PDF:

```text
python audit_figures.py prepare --input PAPER.pdf --output AUDIT_DIR --pages "1-40,49-54"
```

The script extracts qualifying embedded raster images first. It renders a page
only when no large embedded image is available and the page looks like a figure
page, or when `--render-fallback all` is explicitly used. Review
`sources.json`, `skipped.json`, and `sources-contact-sheet.png`; confirm that
every requested figure is represented. A page render still contains captions
and page furniture, so crop the figure before panel splitting.

For a directory:

```text
python audit_figures.py prepare --input FIGURE_DIR --output AUDIT_DIR
```

The script recursively inventories supported images, normalizes EXIF
orientation into audit copies, and records hashes and original paths. It does
not alter the directory.

## 2. Verify panel boundaries

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
python audit_figures.py materialize --workspace AUDIT_DIR
```

Inspect `panels-contact-sheet.png` immediately. Fix bad crops and rerun. Do not
scan until `manifest-warnings.json` has no unexplained out-of-bounds,
duplicate-ID, or overlapping-box warning. Preserve parent/context crops when a
tighter data-only crop is needed for matching.

## 3. Run all-pairs screening

```text
python audit_figures.py scan --workspace AUDIT_DIR --features required
```

The scan combines exact pixel hashes, perceptual hashes, normalized
correlation, and SIFT + RANSAC geometry. It writes `candidates.csv`,
`candidates.json`, `quality-flags.csv`, and `scan-summary.json`. Review every
candidate, not only the first page of the table. Re-scan after any crop change.

Automatic scores are triage signals. Repeated labels, axes, membrane grids,
plate rims, scale bars, and regular tissue texture often produce false
matches. Conversely, different crops, contrast changes, rotation, mirroring,
or recompression can hide a duplicate from hashes and global correlation.

## 4. Confirm or exclude candidates

Generate evidence for selected pairs or the highest-ranked unresolved pairs:

```text
python audit_figures.py evidence --workspace AUDIT_DIR --pair PANEL_A,PANEL_B
python audit_figures.py evidence --workspace AUDIT_DIR --top 20
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

## 5. Review uninformative images

Treat automated quality flags as prompts. Mark a panel uninformative only for a
specific reason such as blank/placeholder content, corruption, unreadably low
resolution, a caption mismatch, or unrelated residual artwork. A negative
result, schematic, control, or visually sparse field is not "useless" merely
because it contains little signal.

## 6. Report

The final report must include:

1. exact input, page scope, figure/source count, and unreadable or skipped files;
2. number of reviewed sources, panels, and all-pairs comparisons;
3. methods and whether the SIFT pass actually ran;
4. a table of `confirmed duplicate`, `high-confidence concern`, `needs raw
   data`, `expected derivative/longitudinal view`, and `excluded false positive`;
5. panel IDs, source/page, bounding boxes, metrics, and evidence paths for every
   reported concern;
6. separately listed quality/uninformative findings;
7. limitations, especially uncertain panel boundaries or unsplit lanes.

Use neutral language: the audit identifies image reuse or similarity, not
intent. Do not claim the review is exhaustive unless coverage accounting shows
that every in-scope source and experimental-image unit was inspected.
