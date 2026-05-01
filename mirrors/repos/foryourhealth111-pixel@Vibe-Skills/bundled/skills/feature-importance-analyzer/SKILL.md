---
name: feature-importance-analyzer
description: |
  Explain which features drive a trained model's predictions.
  Use after a model exists and you need ranking, pruning, or interpretation; not for raw feature engineering or leakage checking.
allowed-tools: Read, Write, Edit, Bash(python:*), Bash(pip:*)
version: 1.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
---

# Feature Importance Analyzer

## Purpose

Use this skill when the user asks why a model depends on some features more than others.

## When to Use

Use this skill when:
- Ranking features after training a tree model, linear model, or ensemble
- Comparing permutation importance, built-in importance, or SHAP-style signals
- Deciding which features to keep, prune, or investigate further

## Not For / Boundaries

- Creating new features from scratch: use `engineering-features-for-machine-learning`
- Checking whether a pipeline leaks future information: use `ml-data-leakage-guard`
- Full model benchmark suites: use `evaluating-machine-learning-models`

## Typical Outputs

- Ranked feature lists with interpretation notes
- Suggested pruning or follow-up analysis
- Warnings when importance may be unstable or misleading

## Related Skills

- `evaluating-machine-learning-models` for the surrounding performance context
- `shap` when deeper explanation plots are required
