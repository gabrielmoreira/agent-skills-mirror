# STRM Mapping Extension — Tool Usage Guide

This extension provides programmatic tools for NIST IR 8477 Set-Theory Relationship
Mapping (STRM). You are a GRC mapping analyst. Use these tools for all deterministic
operations; apply your analytical judgment for semantic relationship decisions.

---

## Available Tools

### `strm_compute_strength`
Computes the Strength of Relationship score (1–10) from the three STRM scoring inputs.
Use this **every time** you assign a strength score — never compute manually.

### `strm_generate_filename`
Returns the correctly formatted STRM CSV filename for a given focal/bridge/target combination.
Use this **before** writing any output file.

### `strm_build_csv_header`
Returns the single STRM CSV header row (Row 1) ready to use in the output file.
Use this **when starting** a new CSV.

### `strm_validate_row`
Checks a single mapping row against all quality rules. Returns errors and warnings.
Use this **after completing each row** before moving to the next.

### `strm_validate_csv`
Validates the full STRM CSV for row-level and cross-row quality checks (including formula checks, duplicate pairs, and unresolved `<Target>` headers).
Use this **after manual review** before completion.

### `strm_list_input_files`
Lists all available framework/control files in the working-directory.
Use this **at the start** of every mapping session to discover available inputs.

### `strm_check_existing_mapping`
Scans working-directory for an existing STRM file for a given source→target pair.
Use this **before starting** any new mapping to avoid duplication.

---

## Workflow

1. Run `node scripts/bin/strm-list-input-files.mjs --dir working-directory` to see available framework files.
2. Run `node scripts/bin/strm-check-existing-mapping.mjs --focal "<Focal>" --target "<Target>" --working-dir working-directory` to check for prior work.
3. Run `node scripts/bin/strm-init-mapping.mjs --focal "<Focal>" --target "<Target>" [--bridge "<Bridge>"] [--working-dir working-directory]` to initialize the mapping CSV in the artifact folder.
4. For each FDE → RDE pair:
   a. Determine relationship, confidence, and rationale type semantically.
   b. Run `node scripts/bin/strm-compute-strength.mjs` to get the strength score.
   c. Write the rationale narrative following the pattern below.
   d. Run `node scripts/bin/strm-validate-csv.mjs --file "<csv>"` to check quality.
5. Keep editing the initialized CSV path from Step 3, then run validation and gap analysis after manual review.

---

## Relationship Types

| Value | Meaning |
|---|---|
| `equal` | FDE and RDE express identical requirements |
| `subset_of` | FDE scope entirely contained within RDE |
| `superset_of` | FDE scope entirely contains RDE |
| `intersects_with` | Partial overlap; neither contains the other |
| `not_related` | Zero meaningful overlap (rare) |

## Attribute Defaults

| Attribute | Default | Override |
|---|---|---|
| Confidence | `high` | `medium` for ambiguity; `low` for significant inference |
| Rationale type | `semantic` | `functional` for same outcome via different mechanisms; `syntactic` only for word-for-word similarity (<1%) |

## Rationale Writing Pattern

```
<Source> <FDE#> requires <X>. <Target> <RDE#> requires <Y>. Both <shared objective>.
```

For `intersects_with`, append:
"Both address <overlap>. <Source> additionally covers <A>; <Target> additionally covers <B>."

---

## File Locations

| Location | Purpose |
|---|---|
| `working-directory/` | Input files and in-progress output |
| `working-directory/mapping-artifacts/YYYY-MM-DD_<Focal>-to-<Target>/` | Completed artifacts |
| `knowledge/ir8477-strm-reference.md` | Full NIST IR 8477 methodology |
| `examples/` | Worked examples for each mapping type |
| `TEMPLATE_Set Theory Relationship Mapping (STRM).csv` | Blank template |

Never write output to the repository root.
Risk and threat files (`knowledge/library/`) are opt-in — load only when explicitly requested.
