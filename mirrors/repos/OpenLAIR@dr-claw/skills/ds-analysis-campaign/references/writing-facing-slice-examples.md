# Writing-Facing Slice Examples

Use this reference when an analysis campaign is supporting a paper-like deliverable and each slice must bind to the paper contract.

## Good writing-facing todo item

```json
{
  "exp_id": "EXP-ABL-001",
  "todo_id": "todo-ablation-core",
  "slice_id": "ablation-core",
  "title": "Core component ablation",
  "research_question": "RQ2",
  "experimental_design": "Component ablation",
  "tier": "main_required",
  "paper_placement": "main_text",
  "paper_role": "main_text",
  "section_id": "analysis-mechanism",
  "item_id": "AN-ABL-001",
  "claim_links": ["C2"],
  "completion_condition": "Show whether the central gain survives removal of the core component.",
  "why_now": "The draft cannot support the mechanism claim without this slice.",
  "success_criteria": "Produce a fair ablation under the accepted metric contract.",
  "abandonment_criteria": "Stop only if the evaluation contract becomes invalid.",
  "manuscript_targets": ["Results", "Mechanism analysis"]
}
```

## Bad writing-facing todo item

```json
{
  "slice_id": "ablation-core",
  "title": "Try one ablation",
  "research_question": "RQ2"
}
```

Why it is bad:

- no `section_id`
- no `item_id`
- no `claim_links`
- no paper placement
- impossible to write back into the outline cleanly later

## Case guide

- Main claim support:
  use `paper_role=main_text` and make the item part of `required_items`
- Supporting but non-blocking evidence:
  use `paper_role=appendix` and make the item part of `optional_items`
- Useful but paper-excluded result:
  keep the slice durable, but mark it `reference_only` or exclude it with a written reason in the matrix

## Completion rule

After `artifact.record_analysis_slice(...)`:

1. the slice result must exist under the analysis worktree
2. the mirror must exist under `experiments/analysis-results/`
3. the evidence ledger must contain the corresponding `item_id`
4. the selected outline section must show the updated row in `result_table`

If step 3 or 4 is missing, the slice is not paper-ready yet.
