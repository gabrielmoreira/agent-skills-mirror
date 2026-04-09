# Artifact Payload Examples

Use this reference when the `baseline` stage needs a stable payload shape without re-expanding the main skill body.

## Route or blocked decision

Keep these fields when route choice or blocking status matters:

- `kind`
- `action`
- `reason`
- `baseline_id`
- `baseline_variant_id` when relevant
- `evidence_paths`
- `next_direction`

## Accepted baseline

Keep these fields when writing the accepted baseline artifact:

- `kind`
- `baseline_id`
- `baseline_kind`
- `path`
- `task`
- `dataset`
- `primary_metric`
- `metrics_summary`
- `default_variant_id` when relevant
- `baseline_variants` when relevant
- `environment`
- `source`
- `summary`

## Rules

- keep payloads compact but audit-friendly
- do not omit the trusted comparison surface just because one headline metric exists
- do not publish a blocked or verification-incomplete baseline payload as if it were accepted
