---
threshold: 5
---

## Feedback Protocol — researcher

### How Feedback Works

Feedback is captured **actively via hooks** — NOT passively. The flow:

1. The user works with the researcher agent
2. The user validates the result (positive or negative)
3. If the user reports issues, you ask for specifics (if not already clear)
4. You create a structured review in `.vscode/skill-reviews/researcher/`

### When to Capture

- The agent returned incorrect or outdated information
- Research was incomplete — missed key sources or APIs
- The agent hallucinated facts instead of verifying them
- Analysis was superficial when depth was needed
- The user had to do their own research to fill gaps

**NEVER** generate feedback without user validation. No complaints = no feedback needed.

### Review Format

Create a JSON file at `.vscode/skill-reviews/researcher/{YYYY-MM-DDThh-mm}.json`:

```json
{
  "date": "YYYY-MM-DD",
  "agent": "researcher",
  "type": "correction | improvement | bug",
  "what_failed": "Brief description of what went wrong",
  "expected": "What the user expected instead",
  "context": "What the user was trying to do"
}
```

### Consolidation

When 5 reviews accumulate, the skill maintainer consolidates them into actionable improvements to the agent's instructions.

### When to Log

Log feedback when the researcher agent is used and:
- Research was too shallow and missed critical context
- Research was too broad, producing noise without actionable findings
- The agent made claims without citing sources or verifying facts
- Tool restrictions prevented gathering necessary information
- The structured output was unclear or missing key sections

### Review Format

Create a JSON file in `.vscode/skill-reviews/researcher/`:

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
- Is research depth calibrated to task complexity?
- Are sources being cited and facts verified?
- Is the output format useful for downstream agents?
