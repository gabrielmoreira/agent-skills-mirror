# Outline-Centered Paper Contract Example

Use this reference when the paper line needs a concrete example of:

- what a selected outline should look like before follow-up analysis
- how completed evidence should be written back into the outline
- what should block further drafting

## Minimal selected outline shape

```json
{
  "outline_id": "outline-002",
  "title": "Truth-Preserving Collaboration under Mixed Signals",
  "story": "Motivation -> bottleneck -> remedy -> evidence -> boundary",
  "detailed_outline": {
    "research_questions": [
      "RQ1: Does the method improve the main benchmark under the accepted protocol?",
      "RQ2: Which component actually causes the gain?",
      "RQ3: Where does the method fail or regress?"
    ],
    "experimental_designs": [
      "Main benchmark comparison",
      "Component ablation",
      "Boundary / failure analysis"
    ],
    "contributions": [
      "A new route for source-aware collaboration",
      "A controlled decomposition of the gain",
      "A clearer limitation boundary"
    ]
  },
  "evidence_contract": {
    "main_text_items_must_be_ready": true,
    "appendix_items_may_be_ready_or_reference_only": true,
    "record_results_back_into_outline": true,
    "result_table_required": true
  },
  "sections": [
    {
      "section_id": "results-main",
      "title": "Main Results",
      "paper_role": "main_text",
      "claims": ["C1"],
      "required_items": ["run-main-001"],
      "optional_items": [],
      "status": "pending",
      "result_table": []
    },
    {
      "section_id": "analysis-mechanism",
      "title": "Mechanism Analysis",
      "paper_role": "main_text",
      "claims": ["C2"],
      "required_items": ["AN-ABL-001"],
      "optional_items": [],
      "status": "pending",
      "result_table": []
    },
    {
      "section_id": "analysis-boundary",
      "title": "Boundary and Failure Analysis",
      "paper_role": "appendix",
      "claims": ["C3"],
      "required_items": [],
      "optional_items": ["AN-BND-001"],
      "status": "planned",
      "result_table": []
    }
  ]
}
```

## After one completed analysis slice

Write the result back into the matching `section.result_table`.

```json
{
  "item_id": "AN-ABL-001",
  "title": "Remove corroboration module",
  "kind": "analysis_slice",
  "paper_role": "main_text",
  "status": "completed",
  "claim_links": ["C2"],
  "metric_summary": "acc=0.811; delta=-0.046",
  "result_summary": "Removing the corroboration module eliminates most of the measured gain.",
  "source_paths": [
    "experiments/analysis/analysis-1234/ablation/RESULT.md",
    "experiments/analysis-results/analysis-1234/ablation.md"
  ],
  "updated_at": "2026-03-28T00:00:00Z"
}
```

The matching section should then move from `pending` to:

- `ready` if every required item is ready
- `partial` if some required items are ready
- `pending` if the row exists but the result is not ready

## Drafting rules by case

- If a section has missing required items, stop prose expansion and repair the evidence contract first.
- If an analysis slice is completed but has no `section_id` or `item_id`, do not summarize it in the paper yet; map it first.
- If a result is only useful as support, keep it in `appendix` or `reference_only` instead of inflating the main text.
- If the result weakens the claim, record that downgrade in the outline before rewriting the section prose.
