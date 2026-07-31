---
name: figure-generator
description: "Ship deterministic hand-authored SVG generators for print-quality figures backed by real published datasets. Ships the .mjs generator pattern reading from data/<slug>.json, the data-sha256 audit hash embed for provenance, the dataset-first rule with contract tests pinning headline numbers, the dataset-inversion procedure for reverse-engineering data from an approved sample SVG, the fix-in-generator-never-in-SVG rule, and the figure-count hoist to one JSON. Use when authoring reproducible book or report figures, when a figure's numbers might drift silently, or when reverse-engineering data from a graphic whose dataset is missing."
lastReviewed: 2026-07-29
---

# Figure generator discipline

Deterministic figure production for books, reports, and any artifact where a figure's numbers have to survive re-generation and stay auditable. Distilled from a shipped book — Fabio Correa's *The Defensible Decision*, 53 figures across 14 chapters, every generator hand-authored, every dataset published — via Alex_DDA's `dd-book-illustrator` skill.

The engineering side of the illustration workflow. [`print-svg-style-guide`](../print-svg-style-guide/SKILL.md) governs how figures LOOK; this skill governs how they get MADE, VERSIONED, and AUDITED.

## When to invoke

- Authoring a new figure for a book, report, or exec-facing document whose numbers should stay traceable
- Re-authoring an existing figure whose data has drifted or whose script is missing
- Reverse-engineering the underlying dataset from an approved sample SVG
- Setting up a contract test for a new figure's headline numbers
- Diagnosing why a figure's numbers do not match the surrounding prose

## The generator pattern

Every shipped figure is emitted by a deterministic `.mjs` script that:

1. Reads from `data/<slug>.json` — never inlines the numbers
2. Computes a SHA-256 hash of the source data
3. Embeds the hash in the SVG as an XML comment (`<!-- data-sha256: ... -->`)
4. Emits to `assets/figures/<NN>-<slug>.svg` (or the project's chosen path)

Skeleton:

```javascript
// scripts/generate-<slug>.mjs
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";

const DATA_PATH = "data/<slug>.json";
const OUT_PATH = "assets/figures/<NN>-<slug>.svg";

const raw = readFileSync(DATA_PATH, "utf8");
const data = JSON.parse(raw);
const dataHash = createHash("sha256").update(raw).digest("hex");

// ... layout math using data ...

const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 480" font-family="Inter, system-ui, sans-serif">
  <!-- data-sha256: ${dataHash} -->
  <title>${title}</title>
  <!-- ... marks, labels, axes ... -->
</svg>`;

writeFileSync(OUT_PATH, svg);
console.log(`Wrote ${OUT_PATH} (data-sha256: ${dataHash.slice(0, 12)}...)`);
```

### Why hand-authored and not a rendering library

- **Layout math is exact.** Statistical-chart libraries (Vega-Lite, ECharts, Chart.js via the `flint-chart` MCP server) own final geometry — they stretch within a `baseSize` ceiling and return their own `computedSize`. Print-legibility gates and bounds gates need the generator to own layout, not the renderer.
- **Regen is byte-stable.** Given the same dataset, a hand-authored generator produces byte-identical output. That is what makes `data-sha256` a useful audit hash.
- **Debugging is easier.** When a figure looks wrong, `console.log()` inside the generator shows exactly the numbers it saw. A renderer failure hides behind opaque layout errors.

`flint-chart` still has a role — as an EXPLORATION tool during the design pass (Step 5a of the [chart-big-idea → flint-chart → hand-author] pipeline). Flint helps pick a chart family faster than reasoning from scratch. The shipped artifact, though, is always a hand-authored generator when the target is print.

## Dataset-first rule

Every figure must be backed by a REAL, PUBLISHED dataset. Never inline composite numbers. The rule holds for character-anchored figures and generic figures alike; the reader must be able to reproduce the scenario.

The publication set for each dataset:

- `data/<slug>.json` (source of truth)
- `data/<slug>.csv` (human-readable copy for readers who prefer tables)
- `data/<slug>.md` (README describing schema, provenance, units)
- `data/<slug>.schema.json` (JSON Schema so downstream consumers can validate)

For a companion-site workflow (static-site publication):

- Publish to `datasets/<slug>/` on the site (schema page + CSV + JSON + README)
- Publication is a PREREQUISITE for shipping the figure, not a follow-up

**Naming convention**: `<slug>` describes the figure content, not the character or the chapter. `q3-region-revenue` is right; `chapter-5-figure-4` is not. Readers look up datasets by concept, not by figure number, so the concept has to be in the name.

## Contract tests (pin the headline numbers)

For every figure, write a contract test that pins the values the surrounding prose cites. Runs via Node's built-in test runner.

Skeleton:

```javascript
// scripts/<slug>-contract.test.mjs
import { readFileSync } from "node:fs";
import { test } from "node:test";
import assert from "node:assert/strict";

const data = JSON.parse(readFileSync("data/<slug>.json", "utf8"));

test("Q4 aggregate matches the chapter total", () => {
  const q4Total = data.regions.reduce((s, r) => s + r.q4, 0);
  assert.equal(q4Total, 28400000); // "$28.4M quarter" in chapter prose
});

test("EMEA variance matches the prose claim", () => {
  const emea = data.regions.find(r => r.name === "EMEA");
  const variance = emea.actual - emea.plan;
  assert.equal(variance, 1700000); // "$1.7M variance" in chapter prose
});

test("Cohort 6 gain is 2.18x Cohort 1", () => {
  const c1 = data.cohorts[0].gain;
  const c6 = data.cohorts[5].gain;
  assert.equal(Math.round((c6 / c1) * 100) / 100, 2.18); // ordinal claim in prose
});
```

Run: `node --test scripts/<slug>-contract.test.mjs`

### What to pin

- **Aggregate totals** cited in prose (`$28.4M quarter`)
- **Per-segment values** the prose names (`$1.7M variance in EMEA`)
- **Ordinal claims** (`2.18× larger`, `third-lowest`, `only region falling`)

### What NOT to pin

- The full dataset shape (schema tests belong in a separate `<slug>.schema.test.mjs`)
- Numbers that appear ONLY in the figure and never in prose (over-constrained; makes future dataset edits noisy)

### Register the test

Many projects use an explicit test list (e.g., `dd:contract` in the DDA workflow). Dropping a new `<slug>-contract.test.mjs` into `scripts/` does nothing if the harness enumerates its tests explicitly. Add the test to whatever list the project maintains. **The tell is the test count**: if it did not rise by the number of tests you wrote, you are not wired in.

Typical `package.json` edit:

```json
{
  "scripts": {
    "dd:<slug>": "node scripts/generate-<slug>.mjs && node --test scripts/<slug>-contract.test.mjs",
    "dd:contract": "node --test scripts/<slug1>-contract.test.mjs scripts/<slug2>-contract.test.mjs ..."
  }
}
```

Both edits ship together — the per-figure script and the aggregate list.

## Fix in the generator, never in the SVG

Manual SVG edits get clobbered on the next regen. The rule is absolute:

| Symptom                                        | Fix in                                                                                                   |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Number wrong in the SVG                        | The generator's layout math, or the dataset                                                              |
| Text truncated                                 | The generator's layout — see `print-svg-style-guide` § "when text won't fit" (cut / reflow / abbreviate / grow) |
| Color miscoded                                | The generator's palette lookup, not the SVG's `fill` attribute                                           |
| XML-invalid comment (`--` inside, bare `&`)    | The generator's comment emission — see `render-verify` § SVG XML invalid                                 |
| Regenerating clobbers your patch               | That is the rule working, not a bug                                                                      |

The one legitimate exception: a one-off, throwaway figure that will never regenerate. If you are SURE, hand-edit the SVG. But then treat that SVG as the source of truth and delete the generator, so the next contributor is not misled.

## Dataset inversion (reverse-engineer the data from an approved sample SVG)

Sometimes an approved sample SVG exists but its underlying dataset is missing. Do not reconstruct the data from prose descriptions — prose fabricates. Invert the sample.

### Procedure

1. **Extract axis tick coordinates and their labeled values** from the sample.

   ```powershell
   Select-String -Path <sample>.svg -Pattern '<text|<line' | Select-Object -First 40
   ```

   Look for `<text>` elements near axis lines with numeric content; those are tick labels. Match each label to the `<line>` coordinate it labels.

2. **Solve two ticks for the linear scale**:

   ```text
   pxPerUnit = (y1 - y2) / (v2 - v1)
   ```

   where `y1, y2` are pixel Y coordinates of two ticks and `v1, v2` are their labeled values. Example from a shipped case: Fig 6.6 solved to `2.25 px per point`.

3. **Invert every data-point coordinate through the scale**.

   ```javascript
   const dataValue = (yAxisBase - pointY) / pxPerUnit + valueBase;
   ```

   Round to the domain's natural precision (integer, one decimal, etc.).

4. **The test that the derivation is faithful**: every derived value resolves to an EXACT value on the natural grid. Fig 6.6's 24 data points all landed on integers — no fractional pixels, no rounding fudge. If they do not, either the scale is wrong or the sample is drawing something other than the dataset you think it is.

5. **Feed the derived values into the generator and verify byte-identity**. The output polylines should be byte-identical to the sample. That is the strongest evidence the dataset faithfully encodes the approved design.

### Why inversion beats prose reconstruction

Prose fabricates. In a real case, prose said *"EMEA is the only region falling"* — the sample proved three regions decline and the two lines diverge (gaps 10 → 15 → 20 → 30). A generator authored from the prose would have shipped one wrong region trajectory. The sample doesn't lie, and the byte-identity check is the strongest possible verification.

## Figure-count hoist (one JSON, not scattered constants)

When a project runs multiple gates that all depend on "how many figures are expected," hoist the count into one JSON file. Every gate reads from it. Adding a figure touches ONE file.

```json
{ "expectedFigures": 62, "expectedPages": 439 }
```

Consumers read the same file:

- `check-placeholders.cjs` — counts `![...]()` declarations in chapter markdown
- `build-pdf.js` — counts figures embedded as data-URIs during the build
- `check-rendered-figures.cjs` — counts `/Image` XObjects in the built PDF
- `check-placeholders.test.cjs` — the contract test for the above

JSON, not a `.js` module, is deliberate: if the root `package.json` declares `"type": "module"`, the `.js` build script is ESM and cannot `require()`, while the gate scripts are `.cjs`. JSON is the only format both read without a bridge (CJS `require`, ESM `readFileSync` + `JSON.parse`).

Before hoisting, the figure count typically lives scattered across three or four files. Three of the four go silently stale on the next figure. Bump one number, hope the rest catch up, discover in a slow build that one did not. Hoist eliminates the class of drift.

### Page count: measure, do not predict

`expectedPages` must be read off the PDF-build output, never assumed. A figure does not reliably add a page. In the DDA workflow, Fig 5.4 added a page; Fig 6.6 did not (439 → 439). Set the value AFTER the build, not before.

## Anti-patterns

| Don't                                                       | Do                                                                                                             |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Inline numbers in the generator (`const q3Total = 28400000`) | Read from `data/<slug>.json` and hash the raw text into the SVG                                                |
| Ship a figure without a contract test                       | Numeric truth is the argument's substrate; drift without a test is silent                                      |
| Hand-edit the emitted SVG to fix a defect                   | Grep `scripts/generate-*` for the filename first — fix the generator, then re-run it                           |
| Reconstruct a dataset from prose descriptions                | Prose fabricates. Invert the sample instead                                                                    |
| Bump the figure count without hoisting                       | Every gate that reads a figure count separately is a future stale-count bug                                    |
| Predict `expectedPages` from figure count                    | Measure it off the built PDF                                                                                   |
| Skip test-registration ("the test file exists, it must run") | Explicit test lists silently skip unregistered files. The tell is the test count did not rise                  |
| Ship a figure whose SVG passes every gate but is XML-invalid | See [`render-verify`](../render-verify/SKILL.md) § SVG XML invalid. Inline HTML is lenient; `<img>` is strict  |

## Related skills

- [`print-svg-style-guide`](../print-svg-style-guide/SKILL.md) — how figures LOOK. Governs the SVG this skill emits.
- [`chart-big-idea`](../chart-big-idea/SKILL.md) — Step 0.5 (earn-a-figure) and Step 4.5 (focus discipline) run BEFORE this skill fires. Decides whether the figure should exist.
- [`flint-chart`](../flint-chart/SKILL.md) — exploration tool during figure design. Not the shipping path for print-quality figures.
- [`render-verify`](../render-verify/SKILL.md) — post-render check. § SVG XML invalid and § Prose-coupling check fire on the artifacts this skill produces.

## Would revise if

- ≥2 figures generated through this skill's discipline ship with drift a contract test should have caught within a quarter
- Dataset inversion procedure fails on ≥1 real sample where the derivation was correct but the byte-identity check failed
- Figure-count hoist is skipped ≥3 times in favor of scattered constants (rule is not landing)
- The generator-vs-SVG-patch rule is violated ≥2 times where the manual patch survived because "the generator will never re-run" (rule too soft)

Track outcomes at [`operations/ledgers/curation-log.md`](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/operations/ledgers/curation-log.md) in Alex_ACT_Steward.

Adapted from *The Defensible Decision* (Fabio Correa) via the `dd-book-illustrator` skill in Alex_DDA. The generator pattern, contract-test discipline, and dataset-inversion procedure are book-tested across 53 shipped figures.
