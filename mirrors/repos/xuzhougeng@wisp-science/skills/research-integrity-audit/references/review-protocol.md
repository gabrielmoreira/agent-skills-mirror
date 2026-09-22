# Review protocol

## Why the manifest is the critical step

The unit of comparison must match the experimental unit. Whole composite
figures dilute local reuse, while overlapping crops of the same source create
trivial self-matches. Automatic whitespace or connected-component splitting
cannot reliably distinguish a panel, its label, an inset, and a grid cell.

For each source, record:

- figure/panel/row/column or experimental-condition label;
- exact `[x0, y0, x1, y1]` box in source pixels;
- modality (`kind`);
- `derivation_group` for expected same-source relationships;
- whether the crop is in scope for comparison.

Keep a context crop for reporting and, where labels or borders dominate, add a
tight data-only crop as a separate panel. Do not let both overlap and enter the
same all-pairs pass unless their relationship is explicitly being tested.

## Candidate metrics

Metrics are deliberately not universal verdict thresholds.

- Exact normalized-pixel SHA-256 catches literal copies.
- aHash/dHash/pHash catch close full-frame copies but are weak for partial
  crops and can over-rank sparse charts.
- Global NCC is useful after accurate cropping and simple intensity changes;
  it falls sharply under different crops or local edits.
- SIFT matches survive scale, rotation, crop, contrast, and recompression.
  RANSAC tests whether the correspondences share one geometric transform.
- Inlier ratio measures consistency; inlier count measures evidence volume;
  spatial coverage measures whether evidence spans the data rather than one
  label, rim, or scale bar.
- Registered NCC and red/green overlays are meaningful only inside the valid
  overlap after a credible transform.

As a review queue, `inliers >= 8` is a useful broad starting point. Fewer
inliers can still matter in a tiny or low-texture panel; many inliers can still
be false when they come from regular text, axes, grids, or shared borders.
Always inspect distribution and controls.

## False-positive patterns

- same plot template, axes, tick labels, legends, or repeated condition text;
- two crops that overlap inside one source image;
- membrane/array grids with regular repeated dots;
- plate/dish rims, identical holders, slide edges, or scanner borders;
- scale bars, arrows, panel labels, or annotations;
- repeated tissue architecture without matching local landmarks;
- expected raw-channel/merge relationships;
- overview and declared magnified inset;
- the same animal in a declared longitudinal imaging series.

Mask or recrop these structures, then repeat the feature match. Genuine reuse
usually retains distributed random landmarks after the confounder is removed.

## Modality-specific review

### Microscopy and histology

Compare nuclei, cell boundaries, vessels, tears, folds, staining speckles, and
background debris. Check rotations and flips. A shared DAPI field across two
channels may be expected; the same field across unrelated conditions is not.
Adjacent serial sections can be similar but should not align at pixel-level
random detail.

### Western blots and gels

Review the uncropped blot first. Then split by protein row and lane when the
scientific question is lane reuse. Compare band outline, local background,
speckles, edge halos, and neighboring-lane leakage. A single similarly shaped
band is weak evidence without background correspondence. Stretching or
contrast inversion must not erase provenance context.

### Plates, colonies, wounds, and gross specimens

Ignore repeated rims, holders, rulers, and printed labels. Crop or mask the
interior and compare irregular stain islands, scratches, bubbles, reflections,
notches, wound contour, hair/marker positions, and background debris. Run
negative controls against other same-modality panels.

### IVIS and longitudinal imaging

Separate the anatomical photograph from the signal overlay when possible. The
same animal and pose over time may be a legitimate repeated acquisition; the
signal layer must still match the stated time point. Record this as an expected
longitudinal relationship rather than silently excluding it.

### Charts and schematics

Do not treat repeated layout as image duplication. Compare underlying values or
source data if the concern is duplicated data. Schematics are quality-reviewed
for relevance and attribution, not passed through photo-forensics thresholds.

## Evidence standard

For each unresolved or positive pair retain:

1. labeled side-by-side full panels;
2. tight data-only crops;
3. inlier match visualization with distribution visible;
4. registered red/green overlay and/or difference image;
5. transform, inlier count/ratio, coverage, overlap, and registered NCC;
6. at least one suitable negative control;
7. source path/page, bounding box, and experimental labels.

Verdicts:

- **Confirmed duplicate**: distributed random details and registration agree;
  no legitimate derivation explains the relationship.
- **High-confidence concern**: strong evidence, but resolution, annotation, or
  experimental context prevents confirmation.
- **Needs raw data**: suggestive localized match or ambiguous expected
  derivative; request uncropped originals and metadata.
- **Expected derivative/longitudinal view**: relationship is real and explained
  by the figure design or acquisition protocol.
- **Excluded false positive**: the signal is attributable to layout, labels,
  borders, overlap, or noncorresponding data detail.

Avoid words such as fraud, fabrication, or misconduct unless an authoritative
source has already established that conclusion and it is directly relevant.
