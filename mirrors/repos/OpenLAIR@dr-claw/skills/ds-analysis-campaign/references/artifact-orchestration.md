# Artifact Orchestration For Analysis Campaigns

Use this reference because the current runtime has no dedicated `campaign` artifact kind.

## Recommended sequence

1. **Launch decision**
   - write `decision(action='launch_analysis_campaign')`
   - include `campaign_id`, `parent_run_id` or `parent_idea_id`, and the reason
2. **Campaign charter**
   - write a `report` artifact for the planned slices
3. **Isolation setup**
   - call `artifact.prepare_branch(...)` only for slices that need code or config divergence
   - reuse the current quest branch for pure reruns when possible
4. **Execution updates**
   - emit `progress` during long-running slices
5. **Per-slice result**
   - write one `run` artifact per slice
6. **Campaign synthesis**
   - write one aggregated `report`
7. **Next-step routing**
   - write one closing `decision`

## Recommended per-slice fields

Because `artifact.record(payload={...})` accepts extra fields, include:

- `campaign_id`
- `slice_id`
- `run_kind`
- `parent_run_id`
- `analysis_question`
- `fixed_conditions`
- `changed_factors`
- `success_criteria`
- `abandonment_criteria`
- `metrics_summary`
- `metric_deltas`
- `verdict`
- `paths`

## Naming guidance

Suggested `run_kind` values:

- `analysis.ablation`
- `analysis.robustness`
- `analysis.sensitivity`
- `analysis.error`
- `analysis.efficiency`
- `analysis.environment`

Suggested durable path layout:

- `.ds/worktrees/<slice_id>/`
- `experiments/analysis/<campaign_id>/<slice_id>/`
- `artifacts/runs/<artifact_id>.json`
- `artifacts/reports/<artifact_id>.json`
