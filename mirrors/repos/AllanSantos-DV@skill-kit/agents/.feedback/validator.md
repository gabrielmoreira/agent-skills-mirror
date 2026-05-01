---
threshold: 5
---

## Feedback Protocol — validator

### How Feedback Works

Feedback is captured **actively via hooks** — NOT passively. The flow:

1. The user works with the validator agent
2. The user validates the result (positive or negative)
3. If the user reports issues, you ask for specifics (if not already clear)
4. You create a structured review in `.vscode/skill-reviews/validator/`

### When to Capture

- The agent missed real errors during validation
- False positives — flagged correct code as wrong
- Quality checks were superficial or missed edge cases
- The agent approved output that the user later found broken
- The user had to re-validate manually

**NEVER** generate feedback without user validation. No complaints = no feedback needed.

### Review Format

Create a JSON file at `.vscode/skill-reviews/validator/{YYYY-MM-DDThh-mm}.json`:

```json
{
  "date": "YYYY-MM-DD",
  "agent": "validator",
  "type": "correction | improvement | bug",
  "what_failed": "Brief description of what went wrong",
  "expected": "What the user expected instead",
  "context": "What the user was trying to do"
}
```

### Consolidation

When 5 reviews accumulate, the skill maintainer consolidates them into actionable improvements to the agent's instructions.

### When to Log

Log feedback when the validator agent is used and:
- Validation missed a real issue that was caught later
- Validation flagged a false positive that wasted time
- The agent couldn't verify a claim due to tool restrictions
- The validation checklist was incomplete for the scenario
- The agent approved work that didn't meet the stated success criteria

### Review Format

Create a JSON file in `.vscode/skill-reviews/validator/`:

```json
{
  "date": "YYYY-MM-DD",
  "author": "dev-name",
  "type": "improvement | correction | friction",
  "impact": "high | medium | low",
  "observation": "What happened",
  "suggestion": "What should change in the agent"
}
```

### Consolidation

When 5 reviews accumulate, summarize patterns into actionable improvements:
- Is the validation catching real issues without false positives?
- Are tool restrictions limiting verification ability?
- Is the pass/fail criteria clear and measurable?
