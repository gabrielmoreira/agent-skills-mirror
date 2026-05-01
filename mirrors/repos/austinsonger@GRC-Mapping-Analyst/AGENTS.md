# STRM Mapping — Agent Instructions

This file is read by OpenAI Codex CLI as a **project-level context document** before
task execution. It applies to all work in this repository regardless of which skill is
active. For on-demand STRM mapping capability via the Agent Skills system, see
`.agents/skills/strm-mapping/SKILL.md`.

This file is also recognized by GitHub Copilot agent mode and other tools that look
for `AGENTS.md` at the project root.

---

## Repository Purpose

This repository produces **Set-Theory Relationship Mapping (STRM)** CSV files between
cybersecurity frameworks, control catalogs, and regulatory requirements, following the
NIST IR 8477 methodology. Your primary output is structured 12-column CSV files.

---

## Project Constraints (Apply to All Work)

- All output files go in `working-directory/` — never the repo root
- Completed artifacts go in `working-directory/mapping-artifacts/YYYY-MM-DD_<Focal>-to-<Target>/`
- Never modify the blank template (`TEMPLATE_Set Theory Relationship Mapping (STRM).csv`)
- Never load `knowledge/library/risks.json` or `knowledge/library/threats.json` unless explicitly requested
- Run from the repository root so relative paths resolve correctly

---

## Activating the STRM Skill (Codex)

OpenAI Codex supports the Agent Skills standard. The STRM skill is in:

```
.agents/skills/strm-mapping/SKILL.md
```

Codex discovers this automatically from the `.agents/skills/` directory. Invoke it
explicitly with `/skills` or `$strm-mapping`, or allow Codex to activate it implicitly
when the task description matches the skill's description.

---

## STRM Methodology Quick Reference

### Relationship Types

| Value | Meaning |
|---|---|
| `equal` | FDE and RDE express identical requirements |
| `subset_of` | FDE scope entirely contained within RDE |
| `superset_of` | FDE scope entirely contains RDE |
| `intersects_with` | Partial overlap; neither contains the other |
| `not_related` | Zero meaningful overlap (rare) |

### Strength Score Formula

```
base:       equal=10  subset_of=7  superset_of=7  intersects_with=4  not_related=0
confidence: high=0    medium=-1    low=-2
rationale:  syntactic=-1   semantic=0   functional=0
result:     clamp(base + confidence + rationale, 1, 10)
```

Confidence defaults to `high`. Rationale type defaults to `semantic`.

### Rationale Writing Pattern

```
<Source> <FDE#> requires <X>. <Target> <RDE#> requires <Y>. Both <shared objective>.
```

For `intersects_with` append:
"Both address <overlap>. <Source> additionally covers <A>; <Target> additionally covers <B>."

### CSV Structure — 12 Columns

```
Row 1: FDE#,FDE Name,Focal Document Element (FDE),Confidence Levels,NIST IR-8477 Rational,STRM Rationale,STRM Relationship,Strength of Relationship,<Target> Requirement Title,Target ID #,<Target> Requirement Description,Notes
Row 2+: <data rows>
```

### File Naming Convention

```
Set Theory Relationship Mapping (STRM)_ [(<Focal>-to-<Bridge>)-to-<Target>] - <Focal> to <Target>.csv
```

For direct mappings, repeat the focal name as bridge.

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
| intersects_with | anything | indeterminate — flag for manual review |

---

## Inverse Mappings

| Forward | Inverse |
|---|---|
| equal | equal |
| subset_of | superset_of |
| superset_of | subset_of |
| intersects_with | intersects_with |
| not_related | not_related |

---

## Quality Rules

1. Every row must have a non-empty Rationale (Column F).
2. Strength score must be computed via formula — never assigned arbitrarily.
3. One FDE may produce multiple rows (one per matching target control).
4. `not_related` is rare — only when there is genuinely zero overlap.
5. Never invent target control IDs — every ID must come from the actual target document.
6. Replace `<Target>` placeholder in column headers with the actual target name.
7. Prioritize baseline/foundational controls when frameworks have maturity tiers.

---

## Resources

| Resource | Purpose |
|---|---|
| `.agents/skills/strm-mapping/SKILL.md` | Full STRM skill (Agent Skills standard) |
| `knowledge/ir8477-strm-reference.md` | Full NIST IR 8477 methodology |
| `examples/` | Worked mapping examples for each type |
| `knowledge/library/risks.json` | SCF 2025.4 risk catalog (opt-in only) |
| `knowledge/library/threats.json` | Threat catalog (opt-in only) |
