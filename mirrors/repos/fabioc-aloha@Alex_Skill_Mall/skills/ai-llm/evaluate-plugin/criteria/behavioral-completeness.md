---
id: behavioral_completeness
name: Behavioral Completeness
---

# Behavioral Completeness

Evaluates whether the plugin handles edge cases, errors, and exit conditions —
not just the happy path.

## What to look for

- **Error handling** — What happens when a tool call fails, a file doesn't exist, or input is malformed?
- **Exit conditions** — Does the plugin define when to stop? Are there cleanup protocols?
- **Edge cases** — Does it account for empty inputs, large files, missing dependencies?
- **Graceful degradation** — When something goes wrong, does the agent know how to recover or report?
- **Failure modes** — Are known failure scenarios documented with remediation steps?

## Scoring rubric

| Score | Criteria |
|-------|----------|
| **5** | Documents ≥3 specific failure scenarios with remediation. Has cleanup/exit protocol. Sets retry limits. Handles empty/missing inputs. |
| **4** | Handles ≥2 common error cases (file not found, malformed input, tool failure). Has an exit condition. |
| **3** | Happy path works. Error handling is implicit — agent might recover, but no explicit guidance for when tools fail or inputs are unexpected. |
| **2** | No error handling instructions. Agent will get stuck when a file doesn't exist or a command fails. |
| **1** | No consideration of failure. Agent may loop indefinitely or silently drop errors. |

## What a 5 looks like

- "If the file cannot be read, report the error and continue to the next file"
- "After completion, delete all temporary files created during analysis"
- "If no files match the pattern, inform the user and suggest alternatives"
- "Maximum 3 retry attempts for API calls before reporting failure"

## Scoring examples

### Score 5 — deep-review

```markdown
Phase 3: SYNTHESIS (you, the orchestrator)
    ├── Reconcile into final review
    └── Delete context file (always)

If the context file is missing, report the error and skip the review.
If an agent fails, continue with the remaining agents and note the gap.
```

Why it scores 5: Documents specific failure scenarios (missing context file,
agent failure), has cleanup protocol (delete context file always), and handles
graceful degradation (continue with remaining agents).

### Score 2 — hello-skills

```markdown
Greet the user warmly and ask how you can help them today.
```

Why it scores 2: No error handling, no exit conditions, no consideration of
what happens when input is missing or malformed. Agent will get stuck on
unexpected inputs.
