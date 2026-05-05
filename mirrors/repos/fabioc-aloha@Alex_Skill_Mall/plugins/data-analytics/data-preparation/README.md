# data-preparation

Data cleaning, profiling, transformation, and quality gates. Prepares raw data
for visualization and analysis.

**Status**: Published (v1.0.0)

## What It Does

- Profiles data (types, nulls, cardinality, ranges, sample values)
- Cleans (dedup, null handling, type coercion, outlier treatment)
- Transforms (aggregation, pivot/unpivot, computed columns)
- Quality gates (assertions that must pass before visualization)

## Pipeline Position

Fires after `datasource-connectors`, before `visual-vocabulary`.

## Install

```bash
cp -r plugins/data-preparation/ /your/project/.github/skills/local/data-preparation/
```

## Complements

- `data-analysis` (Mall): runs after this module; assumes clean data
- `data-quality-monitoring` (Mall): monitors ongoing quality; this does initial prep
