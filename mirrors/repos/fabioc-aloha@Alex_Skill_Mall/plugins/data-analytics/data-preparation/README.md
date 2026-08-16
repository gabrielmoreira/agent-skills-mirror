# data-preparation

Data cleaning, profiling, transformation, and quality gates. Prepares raw data
for visualization and analysis.

**Status**: Published (v2.0.1)

## What It Does

- Profiles data (types, nulls, cardinality, ranges, sample values)
- Cleans (dedup, null handling, type coercion, outlier treatment)
- Transforms (aggregation, pivot/unpivot, computed columns)
- Quality gates (assertions that must pass before visualization)

## Pipeline Position

Fires after `datasource-connectors`, before Illustrator chart selection.

## Install

Install `data-preparation` from the Alex ACT Mall.

## Complements

- `data-analysis` (Mall): runs after this module; assumes clean data
- `data-quality-monitoring` (Mall): monitors ongoing quality; this does initial prep
