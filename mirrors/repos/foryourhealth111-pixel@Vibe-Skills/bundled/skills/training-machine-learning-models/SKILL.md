---
name: training-machine-learning-models
description: |
  Train and tune machine learning models from prepared data to usable artifacts.
  Use when the task owner is the training run itself, not post-hoc evaluation, leak checking, or report writing.
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(cmd:*)
version: 1.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
---
# Ml Model Trainer

Use this skill when the user wants to fit a model, choose algorithms, and produce a trained artifact.

## Overview

This skill owns the training loop: selecting candidate models, fitting them with a validation strategy, and producing reusable model outputs.

## When to Use This Skill

- Training a classifier or regressor from prepared data
- Selecting among candidate algorithms and hyperparameters
- Saving a model, pipeline, or reproducible training recipe

## Not For / Boundaries

- Metric selection and benchmark comparison alone: use `evaluating-machine-learning-models`
- Feature creation or transformation strategy alone: use `engineering-features-for-machine-learning`
- Train/test contamination review: use `ml-data-leakage-guard`

## Typical Outputs

- Training plan and candidate model shortlist
- Fitted model or pipeline artifacts
- Notes on validation strategy and handoff to evaluation/reporting

## Related Skills

- `evaluating-machine-learning-models` after fitting
- `ml-data-leakage-guard` before trusting the result
