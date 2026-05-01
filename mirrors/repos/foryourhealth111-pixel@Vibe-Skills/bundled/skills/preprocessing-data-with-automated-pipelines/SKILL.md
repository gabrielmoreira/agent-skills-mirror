---
name: preprocessing-data-with-automated-pipelines
description: |
  Design and implement repeatable preprocessing pipelines for cleaning, encoding, transforming, and validating ML input data.
  In governed ML routing this skill is a stage assistant: it helps on preprocessing-heavy steps after the main route owner is chosen, and should not take over the whole ML workflow by itself.
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(cmd:*)
version: 1.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
---
# Data Preprocessing Pipeline

## Positioning

In governed ML routing, treat this skill as a stage assistant.
It is for preprocessing-heavy execution after the pack owner is chosen.

## When to Use

Use this skill when:
- Prepare raw data for machine learning models.
- Automate data cleaning and transformation processes.
- Implement a robust ETL (Extract, Transform, Load) pipeline.

## Not For / Boundaries

- Whole-task ML ownership: use `scikit-learn`, `ml-pipeline-workflow`, or `training-machine-learning-models`
- Leakage and prediction-time auditing: use `ml-data-leakage-guard`
- Grouped scientific preprocessing with stronger methodological constraints: use `scientific-data-preprocessing`

## Typical Outputs

- A preprocessing pipeline plan or implementation sketch
- Clear sequencing for clean, encode, transform, and validate steps
- Handoff notes for leakage review, training, or evaluation

## Related Skills

- `ml-data-leakage-guard` before trusting fitted preprocessing steps
- `splitting-datasets` when the next narrow problem is partition strategy
