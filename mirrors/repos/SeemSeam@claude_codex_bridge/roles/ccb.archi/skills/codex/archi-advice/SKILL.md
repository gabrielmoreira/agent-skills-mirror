---
name: archi-advice
description: Produce architecture improvement advice from Architec evidence and local code reading. Use when the user wants concrete modification suggestions, sequencing advice, redesign direction, or a practical refactor roadmap based on the current codebase rather than only a raw score.
---

# Archi Advice

Use this skill to turn architecture findings into an actionable improvement
plan.

## Workflow

1. Establish a baseline with `archi-full` unless a fresh full report already
exists and is clearly relevant.
2. If the user is asking about active changes, also run or read `archi-diff`.
3. Read `.architec/architec-summary.md` first, then inspect
   `.architec/architec-analysis.json` for exact concerns and scores.
4. Inspect the relevant source files directly before recommending changes.
5. Convert findings into phased work.

## Output

```text
Current Position
- baseline score:
- current reading:

Immediate
- ...

Next
- ...

Later
- ...

Validation
- ...
```

Advice must be grounded in evidence. Do not produce a roadmap from diff context
alone when the user is asking about long-term architecture.

