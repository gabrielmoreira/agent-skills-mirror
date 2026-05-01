---
threshold: 5
---

## Feedback Protocol — skill-benchmark

### How Feedback Works

Feedback is captured **actively via hooks** — NOT passively. The flow:

1. You use this skill to benchmark a target skill
2. The user validates the result (positive or negative)
3. If the user reports issues, you ask for specifics (if not already clear)
4. You create a structured review in `.vscode/skill-reviews/skill-benchmark/`

### When to Capture

- The user explicitly says the result is wrong, incomplete, or poor quality
- Task provisioning generated irrelevant or trivial tasks
- Scoring rubric missed important quality dimensions
- Report was misleading or hard to interpret
- Benchmark results were inconsistent across runs
- A script failed or produced unexpected output

**NEVER** generate feedback without user validation. No complaints = no feedback needed.

### Review Format

Create a JSON file at `.vscode/skill-reviews/skill-benchmark/{YYYY-MM-DDThh-mm}.json`:

```json
{
  "date": "YYYY-MM-DD",
  "skill": "skill-benchmark",
  "type": "correction | improvement | bug",
  "what_failed": "Brief description of what went wrong",
  "expected": "What the user expected instead",
  "context": "What the user was trying to do"
}
```

### Consolidation

When **5 reviews** accumulate in `.vscode/skill-reviews/skill-benchmark/`, summarize patterns into actionable improvements:

1. Read all review files
2. Group by `type` (correction / improvement / bug)
3. Identify recurring patterns
4. Write a summary at `.vscode/skill-reviews/skill-benchmark/SUMMARY.md`
5. Propose concrete changes to the skill based on the patterns
6. Delete individual review files after consolidation
