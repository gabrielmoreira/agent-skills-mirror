# STRM Mapping — Gemini CLI Context

This file configures Gemini CLI for NIST IR 8477 Set-Theory Relationship Mapping (STRM) work
in this repository. It is loaded automatically when you run `gemini` from the repo root.

---

## Purpose of This Repository

This repository produces **Set-Theory Relationship Mapping (STRM)** CSV files between any two
cybersecurity frameworks, control catalogs, or regulatory requirements, following the NIST IR 8477
methodology. You are acting as a GRC mapping analyst whose output is structured CSV files.

---

## When to Perform STRM Mapping

Activate the STRM workflow whenever the user asks to:

- Map, crosswalk, align, or compare any two frameworks, catalogs, or control sets
- Create a STRM CSV output file between any two documents
- Perform a gap analysis between any source and target document
- Extend or verify an existing STRM mapping file

---

## Working Directory

All work **must** be performed inside `working-directory/` at the repository root.
Open Gemini CLI from the repository root so relative paths resolve correctly.

- Read input files from `working-directory/`, `knowledge/`, or `examples/`
- Write all in-progress and output files to `working-directory/`
- Never write output to the repo root or any other location

---

## Saving Completed Mappings

When a mapping is fully complete, create a dated artifact folder:

```
working-directory/mapping-artifacts/YYYY-MM-DD_<FocalFramework>-to-<TargetFramework>/
```

Place the completed CSV inside the dated folder.

---

## Runtime Parameters

Before beginning any work, confirm both parameters with the user if not already specified:

| Parameter | Description | Example |
|---|---|---|
| **Source (Focal) Document** | The framework being mapped FROM | `FFIEC CAT`, `ISO/IEC 27001:2022` |
| **Target (Reference) Document** | The framework being mapped TO | `CIS Controls v8`, `NIST CSF 2.0` |

---

## Step-by-Step Workflow

### 1. Gather Source Files

Read before generating output:

```
knowledge/ir8477-strm-reference.md                                 ← STRM methodology rules
working-directory/<source-document>.csv/.pdf/.md/.json/.yml/.toml  ← Focal document
working-directory/<target-document>.csv/.pdf/.md/.json/.yml/.toml  ← Reference document
```

Search order: `working-directory/` → repo root → `knowledge/`

Check for a prior STRM file for this source→target pair before starting.

### 2. Identify FDE and RDE

- **FDE** (Focal Document Element) = a single control from the **source** document
- **RDE** (Reference Document Element) = a single control from the **target** document

For each document determine: full name, URL/citation, control ID format, maturity tiers.

### 3. Assign STRM Attributes per Mapping Row

| Attribute | Allowed Values | Scoring Rule |
|---|---|---|
| `Confidence Levels` | `high`, `medium`, `low` | high=+0, medium=−1, low=−2 |
| `NIST IR-8477 Rational` | `semantic`, `functional`, `syntactic` | syntactic=−1, others=+0 |
| `STRM Relationship` | `equal`, `subset_of`, `superset_of`, `intersects_with`, `not_related` | equal=10, subset/superset=7, intersects=4, not_related=0 |
| `Strength of Relationship` | Integer 1–10 | base + confidence adj + rationale adj, clamped to [1,10] |
| `STRM Rationale` | Free text | Explain both FDE and RDE, then why the relationship holds |
| `Notes` | Free text | Flag scope differences, partial overlaps, or gaps |

#### Strength Score Formula

```
strength = base_score + confidence_adj + rationale_adj
base_score  : equal=10  subset_of=7  superset_of=7  intersects_with=4  not_related=0
confidence  : high=0    medium=-1    low=-2
rationale   : syntactic=-1   semantic=0   functional=0
result      : clamp(strength, 1, 10)
```

#### Calibration Defaults

| Attribute | Default | Override Condition |
|---|---|---|
| `Confidence Levels` | `high` | `medium` when interpretation/jurisdictional ambiguity; `low` when significant inference required |
| `NIST IR-8477 Rational` | `semantic` | `functional` when same outcome via different mechanisms; `syntactic` only when wording similarity is the primary justification |

#### Observed Distribution (calibration reference)

| Relationship | Approx % | Rationale | Approx % |
|---|---|---|---|
| `equal` | 43% | `semantic` | 63% |
| `intersects_with` | 39% | `functional` | 37% |
| `subset_of` | 17% | `syntactic` | <1% |
| `superset_of` | 1% | | |

### 4. Write the Output CSV

#### File Naming Convention

```
Set Theory Relationship Mapping (STRM)_ [(<Focal>-to-<Bridge>)-to-<Target>] - <Focal> to <Target>.csv
```

For direct mappings, repeat the focal name as bridge: `(NIST_CSF-to-NIST_CSF)`.

#### CSV Structure (12 columns)

```
Row 1: FDE#,FDE Name,Focal Document Element (FDE),Confidence Levels,NIST IR-8477 Rational,STRM Rationale,STRM Relationship,Strength of Relationship,<Target> Requirement Title,Target ID #,<Target> Requirement Description,Notes
Row 2+: <data rows>
```

### 5. Rationale Writing Pattern

```
<Source> <FDE#> requires <what FDE requires>. <Target> <Target ID#> requires <what RDE requires>. Both <shared objective>.
```

For `intersects_with`: append "Both address <overlap>. <Source> additionally covers <FDE scope>; <Target> additionally covers <RDE scope>."

---

## Transitivity Rules

| A→B | B→C | Derived A→C |
|---|---|---|
| equal | equal | equal |
| equal | X | X |
| X | equal | X |
| subset_of | subset_of | subset_of |
| superset_of | superset_of | superset_of |
| not_related | anything | not_related |
| anything | not_related | not_related |
| intersects_with | anything | indeterminate — flag for manual review |

---

## Inverse Relationships

| Forward | Inverse |
|---|---|
| equal | equal |
| subset_of | superset_of |
| superset_of | subset_of |
| intersects_with | intersects_with |
| not_related | not_related |

---

## Quality Rules

1. **Never leave Rationale empty** — every row needs a narrative.
2. **Strength score must match the formula** — compute explicitly, do not guess.
3. **One FDE can map to multiple target controls** — one row per target control.
4. **`not_related` is rare** — only when there is genuinely zero overlap.
5. **Do not invent target control IDs** — every Target ID# must come from the actual document.
6. **Confidence defaults to `high`** — lower only when ambiguity or inference is required.
7. **Focus on Baseline maturity first** — prioritize baseline/foundational controls.
8. **Adapt column header labels** — replace `<Target>` placeholder with actual target name.

---

## Optional: Risk and Threat-Enriched Mappings

> Use these files **only** when the user explicitly requests risk or threat data.

| File | Contents |
|---|---|
| `knowledge/library/risks.json` | SCF 2025.4 risk catalog |
| `knowledge/library/threats.json` | Threat catalog |

Relationship chain: **Threat → Risk → Control**

Activate when user says: "include risk data", "add threat context", "risk-to-control mapping",
"threat-to-risk", "threat-to-control", "use the risk library".

---

## Template Reference

Generate a new mapping CSV with:
```bash
node scripts/bin/strm-init-mapping.mjs --focal "<Focal>" --target "<Target>" [--bridge "<Bridge>"] [--working-dir working-directory]
```

The script creates the artifact folder and writes a CSV with the canonical single header row.

Do not modify the blank template:
```
TEMPLATE_Set Theory Relationship Mapping (STRM).csv
```

Use the template only as a schema/reference baseline.

---

## Key Resources

| Resource | Purpose |
|---|---|
| `knowledge/ir8477-strm-reference.md` | Full NIST IR 8477 methodology reference |
| `examples/example-control-to-control.md` | ISO 27001 → SOC 2 worked example |
| `examples/example-framework-to-control.md` | Framework-to-control example |
| `examples/example-framework-to-regulation.md` | Framework-to-regulation example |
| `knowledge/library/risks.json` | SCF 2025.4 risk catalog (opt-in only) |
| `knowledge/library/threats.json` | Threat catalog (opt-in only) |
