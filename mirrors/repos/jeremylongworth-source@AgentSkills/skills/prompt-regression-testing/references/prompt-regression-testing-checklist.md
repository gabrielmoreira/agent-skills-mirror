# Prompt Regression Testing Checklist

## Prompt Types

- Happy path
- Ambiguous request
- Missing context
- High-risk boundary
- Known prior failure
- Over-triggering negative case
- Host-neutral install/use case

## Invariants

Expected output should:

- produce the target artifact
- use required source material
- label assumptions
- request missing evidence
- respect approval gates
- avoid unsafe actions
- route to the intended skills

## Re-Run Triggers

- Skill frontmatter changes
- Core workflow changes
- New scripts or dependencies
- New bundle composition
- Host setup behavior changes
- Release candidate preparation
- Incident or user report
