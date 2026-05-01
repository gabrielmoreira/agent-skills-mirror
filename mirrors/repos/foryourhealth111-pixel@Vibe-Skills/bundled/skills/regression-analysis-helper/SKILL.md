---
name: regression-analysis-helper
description: |
  Build and diagnose regression analyses for continuous targets or effect estimation.
  Use for coefficient interpretation, residual checks, and model comparison; not for causal identification or clustering.
allowed-tools: Read, Write, Edit, Bash, Grep
version: 1.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
---

# Regression Analysis Helper

## Purpose

Use this skill when the next question is "what does the regression say?" rather than "which broad workflow should own the whole ML task?"
In governed routing, regression ownership normally belongs to `performing-regression-analysis`.

## When to Use

Use this skill when:
- Fitting linear or generalized regression models
- Interpreting coefficients, residuals, and diagnostics
- Comparing alternative regression specifications for a continuous outcome

## Not For / Boundaries

- Main routed ownership of a regression task: use `performing-regression-analysis`
- Causal identification and counterfactual claims: use `performing-causal-analysis`
- Unsupervised grouping: use `running-clustering-algorithms`
- General report packaging: use `scientific-reporting`

## Typical Outputs

- Regression specification recommendations
- Diagnostic summaries for assumptions and fit
- Notes on effect size interpretation and multicollinearity risk

## Related Skills

- `correlation-analyzer` for pre-model screening
- `performing-regression-analysis` as the routed owner when regression is the main task
- `scientific-reporting` when the regression needs to become a deliverable report
