---
threshold: 5
---

## Feedback Protocol — safety-check

### How Feedback Works

Feedback is captured **actively via hooks** — NOT passively. The flow:

1. You use this skill to help the user
2. The user validates the result (positive or negative)
3. If the user reports issues, you ask for specifics (if not already clear)
4. You create a structured review in `.vscode/skill-reviews/safety-check/`

### When to Capture

- The user explicitly says the result is wrong, incomplete, or poor quality
- A risk was missed that later caused a problem
- The weight model triggered at the wrong level
- Dimensions selected were irrelevant or important ones were omitted
- The user had to manually identify risks the skill should have caught

**NEVER** generate feedback without user validation. No complaints = no feedback needed.

### Review Format

Create a JSON file at `.vscode/skill-reviews/safety-check/{YYYY-MM-DDThh-mm}.json`:

```json
{
  "date": "YYYY-MM-DD",
  "skill": "safety-check",
  "type": "correction | improvement | bug",
  "what_failed": "Brief description of what went wrong",
  "expected": "What the user expected instead",
  "context": "What the user was trying to do"
}
```

### Consolidation

When 5 reviews accumulate, the skill maintainer consolidates them into actionable improvements to the skill's instructions or scripts.
