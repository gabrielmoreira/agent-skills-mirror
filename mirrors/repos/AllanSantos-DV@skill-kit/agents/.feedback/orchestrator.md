---
threshold: 5
---

## Feedback Protocol — orchestrator

### How Feedback Works

Feedback is captured **actively via hooks** — NOT passively. The flow:

1. The user works with the orchestrator agent
2. The user validates the result (positive or negative)
3. If the user reports issues, you ask for specifics (if not already clear)
4. You create a structured review in `.vscode/skill-reviews/orchestrator/`

### When to Capture

- The agent routed to the wrong sub-agent
- Task decomposition was incorrect or overly fragmented
- The agent failed to identify when research was needed first
- Handoffs lost critical context between agents
- The user had to manually redirect the workflow

**NEVER** generate feedback without user validation. No complaints = no feedback needed.

### Review Format

Create a JSON file at `.vscode/skill-reviews/orchestrator/{YYYY-MM-DDThh-mm}.json`:

```json
{
  "date": "YYYY-MM-DD",
  "agent": "orchestrator",
  "type": "correction | improvement | bug",
  "what_failed": "Brief description of what went wrong",
  "expected": "What the user expected instead",
  "context": "What the user was trying to do"
}
```

### Consolidation

When 5 reviews accumulate, the skill maintainer consolidates them into actionable improvements to the agent's instructions.

### When to Log

Log feedback when the orchestrator agent is used and:
- A handoff to the wrong sub-agent caused wasted work
- The orchestrator failed to detect when research was needed before implementation
- Task decomposition missed a dependency or sequencing issue
- The orchestrator added unnecessary overhead for a simple task

### Review Format

Create a JSON file in `.vscode/skill-reviews/orchestrator/`:

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
- Are handoff decisions accurate?
- Is the orchestrator scaling effort to task complexity?
- Are sub-agent results being validated before proceeding?
