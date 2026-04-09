# Outline Seeding Example

Use this reference when the idea stage is strong enough that the next serious step will likely become a paper-facing line.

## Goal

Before analysis begins, seed one lightweight but structured outline candidate so later experiments are not free-floating.

## Minimal seed

```json
{
  "title": "Evidence-First Outline Seed",
  "research_questions": [
    "RQ1: Does the method outperform the accepted baseline?",
    "RQ2: Which component is responsible for the gain?",
    "RQ3: What boundary or failure regime matters most?"
  ],
  "experimental_designs": [
    "Main benchmark comparison",
    "Component ablation",
    "Boundary analysis"
  ],
  "sections": [
    {
      "section_id": "results-main",
      "title": "Main Results",
      "paper_role": "main_text",
      "claims": ["C1"],
      "required_items": ["run-main-001"]
    },
    {
      "section_id": "analysis-mechanism",
      "title": "Mechanism Analysis",
      "paper_role": "main_text",
      "claims": ["C2"],
      "required_items": ["AN-ABL-001"]
    },
    {
      "section_id": "analysis-boundary",
      "title": "Boundary Analysis",
      "paper_role": "appendix",
      "claims": ["C3"],
      "optional_items": ["AN-BND-001"]
    }
  ]
}
```

## When to seed the outline

- The idea already survived literature and feasibility checks.
- The likely paper contribution is clear enough to name `1-3` research questions.
- You can already anticipate the first main experiment and at least one likely follow-up analysis family.

## When not to seed the outline yet

- The task framing is still unstable.
- The idea frontier is still too wide.
- You still cannot say what the main claim would be if the route worked.
