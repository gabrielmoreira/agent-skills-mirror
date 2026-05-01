---
name: data-normalization-tool
description: |
  Scale and normalize numeric features for model-ready pipelines.
  Use for z-score, min-max, robust scaling, and train-only statistic handling; not for leakage audits or broader feature-engineering ownership.
allowed-tools: Read, Write, Edit, Bash(python:*), Bash(pip:*)
version: 1.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
---

# Data Normalization Tool

## Purpose

Use this skill when the task is specifically about scaling or normalizing features before fitting a model.

## When to Use

Use this skill when:
- Choosing between standardization, min-max, robust scaling, or log transforms
- Normalizing train/test data without contaminating evaluation
- Preparing numeric features for distance-based or gradient-based models

## Not For / Boundaries

- Broader feature creation or encoding: use `engineering-features-for-machine-learning`
- Leakage review of the whole preprocessing chain: use `ml-data-leakage-guard`
- Final model evaluation: use `evaluating-machine-learning-models`

## Typical Outputs

- Normalization strategy recommendations
- Train-only fit / test-only transform workflow
- Warnings about skew, outliers, and metric sensitivity

## Related Skills

- `engineering-features-for-machine-learning` for the surrounding preprocessing plan
- `ml-data-leakage-guard` to verify the normalization order is safe
