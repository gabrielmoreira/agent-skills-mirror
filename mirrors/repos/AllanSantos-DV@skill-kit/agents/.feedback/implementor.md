---
threshold: 5
---

## Feedback Protocol — implementor

### How Feedback Works

Feedback is captured **actively via hooks** — NOT passively. The flow:

1. The user works with the implementor agent
2. The user validates the result (positive or negative)
3. If the user reports issues, you ask for specifics (if not already clear)
4. You create a structured review in `.vscode/skill-reviews/implementor/`

### When to Capture

- The agent started coding before confirming intent
- A key decision was made without stating WHY
- An external fact was assumed without verification
- The agent over-engineered or under-planned relative to task complexity
- The user had to manually fix significant parts of the output

**NEVER** generate feedback without user validation. No complaints = no feedback needed.

### Review Format

Create a JSON file at `.vscode/skill-reviews/implementor/{YYYY-MM-DDThh-mm}.json`:

```json
{
  "date": "YYYY-MM-DD",
  "agent": "implementor",
  "type": "correction | improvement | bug",
  "what_failed": "Brief description of what went wrong",
  "expected": "What the user expected instead",
  "context": "What the user was trying to do"
}
```

### Consolidation

When 5 reviews accumulate, the skill maintainer consolidates them into actionable improvements to the agent's instructions.
