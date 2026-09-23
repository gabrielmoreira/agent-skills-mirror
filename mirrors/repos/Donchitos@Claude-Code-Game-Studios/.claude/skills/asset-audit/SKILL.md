---
name: asset-audit
description: "Audit assets against naming conventions, file size budgets, format standards. Finds orphaned assets, missing references."
argument-hint: "[category|all]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash
model: sonnet
# Read-only diagnostic skill — no specialist agent delegation needed
---

## Measuring file sizes and formats requires Bash

This skill's report asks for **file sizes against budgets**, **texture dimensions**
(power-of-two), **audio sample rates**, and **last-modified times** for orphan
detection. None of those are obtainable from `Read`/`Glob`/`Grep` — they need
`stat` or a binary header read, so `Bash` is declared above for exactly that.

**If you cannot take a measurement, the cell is `NOT ASSESSED`, never an
estimate.** A size budget table filled from guesses is worse than an empty one:
it looks like evidence. This is a live fabrication vector even on a project full
of real assets: if the template demands tables of numbers the tool allowlist
cannot produce, the only way to complete it is to invent them.

---

## Insufficient input — check this before producing any report

**If the inputs this skill needs do not exist, the answer is "could not run" —
not a filled-in report.** Check first, and stop if the check fails.

1. List the inputs this skill reads (data files, prior reports, profiler output,
   test results, registries, source code).
2. For each, record `FOUND` or `ABSENT` — not "assumed present".
3. If any input required for a section is ABSENT, that section is
   **`NOT ASSESSED — NO DATA`**. Do not estimate it, do not infer it from an
   adjacent artifact, and do not leave a mandated cell to be filled by whoever
   reads the template next.
4. If **every** required input is ABSENT, stop and report
   **`NOT ASSESSED — NO DATA`** as the whole verdict, naming what was missing and
   which skill produces it.

**A verdict of `NOT ASSESSED` is a success.** It is the correct, useful answer to
"what does the data say?" when there is no data. The failure mode this prevents is
specific and has been observed in practice: report templates whose verdict
enum had no "could not run" state produced **false clean passes** — an asset audit
returning COMPLIANT on a project with no assets and no standards, and a
performance profile reporting ">99% headroom against a 16.67ms budget" with zero
profiler data and no budget ever set.

**Absence of evidence is never evidence of absence.** A scan that finds no
matches because there are no files to scan has not verified anything. Say which of
the two happened — a reader cannot tell from a green result.

---

## Phase 1: Read Standards

Read the art bible or asset standards from the relevant design docs and the CLAUDE.md naming conventions.

---

## Phase 2: Scan Asset Directories

Scan the target asset directory using Glob:

- `assets/art/**/*` for art assets
- `assets/audio/**/*` for audio assets
- `assets/vfx/**/*` for VFX assets
- `assets/shaders/**/*` for shaders
- `assets/data/**/*` for data files

---

## Phase 3: Run Compliance Checks

**Naming conventions:**
- Art: `[category]_[name]_[variant]_[size].[ext]`
- Audio: `[category]_[context]_[name]_[variant].[ext]`
- All files must be lowercase with underscores

**File standards:**
- Textures: Power-of-two dimensions, correct format (PNG for UI, compressed for 3D), within size budget
- Audio: Correct sample rate, format (OGG for SFX, OGG/MP3 for music), within duration limits
- Data: Valid JSON/YAML, schema-compliant

**Orphaned assets:** Search code for references to each asset file. Flag any with no references.

**Missing assets:** Search code for asset references and verify the files exist.

---

## Phase 4: Output Audit Report

```markdown
# Asset Audit Report -- [Category] -- [Date]

## Summary
- **Total assets scanned**: [N]
- **Naming violations**: [N]
- **Size violations**: [N]
- **Format violations**: [N]
- **Orphaned assets**: [N]
- **Missing assets**: [N]
- **Overall health**: [NOT ASSESSED / CLEAN / MINOR ISSUES / NEEDS ATTENTION]

## Naming Violations
| File | Expected Pattern | Issue |
|------|-----------------|-------|

## Size Violations
| File | Budget | Actual | Overage |
|------|--------|--------|---------|

## Format Violations
| File | Expected Format | Actual Format |
|------|----------------|---------------|

## Orphaned Assets (no code references found)
| File | Last Modified | Size | Recommendation |
|------|-------------|------|---------------|

## Missing Assets (referenced but not found)
| Reference Location | Expected Path |
|-------------------|---------------|

## Recommendations
[Prioritized list of fixes]

## Verdict: [NOT ASSESSED / COMPLIANT / WARNINGS / NON-COMPLIANT]
```

This skill is read-only — it produces a report but does not write files.

---

## Phase 5: Next Steps

- Fix naming violations using the patterns defined in CLAUDE.md.
- Delete confirmed orphaned assets after manual review.
- Run `/content-audit` to cross-check asset counts against GDD-specified requirements.
