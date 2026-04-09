# Strategic Decision Template

Use this when a decision must directly guide the next stage.

## Suggested shape

```json
{
  "verdict": "good",
  "action": "launch_analysis_campaign",
  "reason": "Why this action is justified now.",
  "target_idea_id": "idea-003",
  "target_run_id": "run-017",
  "campaign_id": "campaign-002",
  "reflection": {
    "what_worked": "Specific evidence-backed successes.",
    "what_failed": "Specific failures and why they matter.",
    "learned_constraints": "New boundaries learned from the evidence."
  },
  "next_direction": {
    "objective": "Immediate strategic goal.",
    "key_steps": [
      "Concrete step 1",
      "Concrete step 2",
      "Concrete step 3"
    ],
    "success_criteria": [
      "Quantitative or observable success threshold"
    ],
    "abandonment_criteria": [
      "Explicit stop condition and follow-up action"
    ]
  },
  "expected_roi": {
    "cost_estimate": "LOW",
    "confidence": "MEDIUM",
    "improvement_estimate": "Qualitative or bounded estimate with justification"
  }
}
```

## Use cases

This richer structure is most helpful for:

- choosing among idea candidates
- selecting experiment groups
- launching analysis campaigns
- routing after campaign or run results
- deciding to pivot, reset, write, or finalize
