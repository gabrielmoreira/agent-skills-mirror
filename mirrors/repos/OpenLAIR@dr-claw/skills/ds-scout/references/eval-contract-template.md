# Evaluation Contract Template

Use this when the `scout` stage needs a durable evaluation contract.

```md
# Evaluation Contract

- task:
- dataset:
- dataset_version:
- split_contract:
- official_or_expected_eval_path:
- primary_metric:
- metric_direction:
- secondary_metrics:
- fair-comparison rule:
- useful-improvement threshold:

## Evidence
- paper paths:
- repo paths:
- benchmark docs:

## Known ambiguities
- ambiguity:

## Decision impact
- blocked_stage:
- why_it_matters:
```

The contract should be concise but explicit enough that `baseline`, `idea`, and `experiment` do not keep re-deriving it.
