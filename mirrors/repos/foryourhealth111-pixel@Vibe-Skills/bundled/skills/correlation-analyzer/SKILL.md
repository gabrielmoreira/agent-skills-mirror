---
name: correlation-analyzer
description: |
  Screen pairwise relationships, collinearity, and simple associations in tabular data.
  Use when the goal is correlation review or feature screening, not causal claims or final regression modeling.
allowed-tools: Read, Write, Edit, Bash, Grep
version: 1.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
---

# Correlation Analyzer

## Purpose

Use this skill when the user wants to know which variables move together before deeper modeling.

## When to Use

Use this skill when:
- Ranking correlated features or spotting multicollinearity
- Choosing variables for follow-up regression or feature engineering
- Building heatmaps or pairwise summaries for exploratory analysis

## Not For / Boundaries

- Causal inference: use `performing-causal-analysis`
- Regression ownership after screening: use `performing-regression-analysis`
- Abnormal-record detection: use `anomaly-detector`

## Typical Outputs

- Correlation tables or heatmaps
- Notes on collinearity risks
- Candidate variables to keep, drop, or inspect further

## Related Skills

- `performing-regression-analysis` for the next modeling step
- `creating-data-visualizations` for general chart production
