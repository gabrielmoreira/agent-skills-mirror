# GitHub Copilot Instructions — STRM Mapping Repository

This repository produces **Set-Theory Relationship Mapping (STRM)** CSV files between
cybersecurity frameworks, control catalogs, and regulatory requirements, based on
[NIST IR 8477](https://nvlpubs.nist.gov/nistpubs/ir/2023/NIST.IR.8477.pdf).

When assisting in this repository, Copilot should act as a GRC mapping analyst and
apply the following rules to all suggestions and completions.

---

## Core Concepts

- **FDE** (Focal Document Element): one control from the **source** framework
- **RDE** (Reference Document Element): one control from the **target** framework
- **STRM Relationship**: the set-theory relationship between FDE and RDE —
  `equal`, `subset_of`, `superset_of`, `intersects_with`, or `not_related`
- **Strength of Relationship**: integer 1–10 computed via formula (see below)

---

## Output Files

All output CSV files must follow this 12-column structure:

```
Row 1: FDE#,FDE Name,Focal Document Element (FDE),Confidence Levels,NIST IR-8477 Rational,STRM Rationale,STRM Relationship,Strength of Relationship,<Target> Requirement Title,Target ID #,<Target> Requirement Description,Notes
Row 2+: <data rows>
```

### File Naming Convention

```
Set Theory Relationship Mapping (STRM)_ [(<Focal>-to-<Bridge>)-to-<Target>] - <Focal> to <Target>.csv
```

For direct mappings (no bridge), repeat the focal name in both slots.

---

## Strength Score Formula

```
base:       equal=10  subset_of=7  superset_of=7  intersects_with=4  not_related=0
confidence: high=0    medium=-1    low=-2
rationale:  syntactic=-1   semantic=0   functional=0
result:     clamp(base + confidence + rationale, 1, 10)
```

Confidence defaults to `high`. Use `medium` when ambiguity exists; `low` when significant inference is required.
Rationale defaults to `semantic`. Use `functional` when same outcome via different mechanisms.

---

## Rationale Writing Pattern

```
<Source> <FDE#> requires <X>. <Target> <RDE#> requires <Y>. Both <shared objective>.
```

For `intersects_with`, append: "Both address <overlap>. <Source> additionally covers <A>; <Target> additionally covers <B>."

---

## File Locations

| Purpose | Location |
|---|---|
| Input framework files | `working-directory/` |
| In-progress CSV output | `working-directory/` |
| Completed artifacts | `working-directory/mapping-artifacts/YYYY-MM-DD_<Focal>-to-<Target>/` |
| Blank template | `TEMPLATE_Set Theory Relationship Mapping (STRM).csv` |
| Methodology reference | `knowledge/ir8477-strm-reference.md` |
| Worked examples | `examples/` |
| Risk catalog (opt-in) | `knowledge/library/risks.json` |
| Threat catalog (opt-in) | `knowledge/library/threats.json` |

Never write output to the repository root.

---

## Transitivity Rules

When deriving A→C from A→B and B→C:

| A→B | B→C | A→C |
|---|---|---|
| equal | equal | equal |
| equal | X | X |
| X | equal | X |
| subset_of | subset_of | subset_of |
| superset_of | superset_of | superset_of |
| not_related | anything | not_related |
| intersects_with | anything | indeterminate |

---

## Quality Rules

- Never leave the Rationale column empty.
- Always compute Strength via formula; never assign arbitrarily.
- One FDE can produce multiple rows (one row per matching target control).
- Never invent target control IDs — use only IDs from the actual target document.
- Columns I and K use target-adapted names: replace `<Target>` with the actual target document name (e.g., `ISO 27001 Requirement Title`, `ISO 27001 Requirement Description`).
- Risk and threat files (`risks.json`, `threats.json`) are opt-in — load only when explicitly requested.
